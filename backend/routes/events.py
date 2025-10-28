from datetime import datetime
import csv
import io
import os
import json
import uuid
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from fastapi.responses import StreamingResponse, FileResponse
from sqlmodel import Session, select

from ..db.base import get_session
from ..db.fts import index_event, remove_from_index
from ..models import Event, Attachment
from ..services.pdf_utils import build_timeline_pdf
from ..services.whisper_service import whisper_service
from ..services.summary_service import get_summary_service
from ..services.document_parser import parse_uploaded_document, DocumentParser

router = APIRouter()

# Audio upload directory
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Base path handled directly in routes for clarity

def _normalize_date(raw_value):
    if isinstance(raw_value, datetime):
        return raw_value
    if isinstance(raw_value, str):
        cleaned = raw_value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(cleaned)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid date format") from exc
    raise HTTPException(status_code=400, detail="Invalid date value")


@router.post("/events/", response_model=Event)
def create_event(event: Event, session: Session = Depends(get_session)):
    event.date = _normalize_date(event.date)
    session.add(event)
    session.commit()
    session.refresh(event)
    
    # Index event in FTS5 for search
    index_event(
        event_id=event.id,
        title=event.title,
        description=event.description,
        tags=event.tags,
        timeline=event.timeline
    )
    
    return event

@router.get("/timelines/")
def get_timelines(session: Session = Depends(get_session)):
    """Get all unique timeline names"""
    statement = select(Event.timeline).distinct()
    timelines = session.exec(statement).all()
    return sorted(timelines)


@router.get("/events/", response_model=list[Event])
def get_events(timeline: Optional[str] = Query(None), session: Session = Depends(get_session)):
    statement = select(Event).order_by(Event.date)
    if timeline:
        statement = statement.where(Event.timeline == timeline)
    events = session.exec(statement).all()
    return events


@router.get("/events/export/csv")
def export_events_csv(timeline: str = None, session: Session = Depends(get_session)):
    """Export events to CSV format, optionally filtered by timeline"""
    statement = select(Event)
    if timeline and timeline != "All":
        statement = statement.where(Event.timeline == timeline)
    statement = statement.order_by(Event.date)
    events = session.exec(statement).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header with new legal workflow fields
    writer.writerow(['title', 'description', 'date', 'timeline', 'actor', 'emotion', 'tags', 'evidence_links'])
    
    # Write events
    for event in events:
        writer.writerow([
            event.title,
            event.description,
            event.date.strftime('%Y-%m-%d %H:%M:%S'),
            event.timeline,
            event.actor or '',
            event.emotion or '',
            event.tags or '',
            event.evidence_links or ''
        ])
    
    # Create response with timestamped filename
    csv_content = output.getvalue()
    output.close()
    
    # Generate timestamped filename for snapshot versioning
    timestamp = datetime.now().strftime('%Y-%m-%d')
    timeline_suffix = f"_{timeline}" if timeline and timeline != "All" else ""
    filename = f"chronicle{timeline_suffix}_{timestamp}.csv"
    
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    
    return StreamingResponse(
        io.StringIO(csv_content), 
        media_type="text/csv", 
        headers=headers
    )


@router.get("/events/export/pdf")
def export_events_pdf(timeline: str = None, session: Session = Depends(get_session)):
    statement = select(Event)
    if timeline and timeline != "All":
        statement = statement.where(Event.timeline == timeline)
    statement = statement.order_by(Event.date)
    events = session.exec(statement).all()
    payload = [
        {
            "title": event.title,
            "description": event.description,
            "date": event.date,
            "timeline": event.timeline,
            "actor": event.actor,
            "emotion": event.emotion,
            "tags": event.tags,
            "evidence_links": event.evidence_links,
            # NOTE: privileged_notes intentionally excluded from PDF export
        }
        for event in events
    ]
    buffer = build_timeline_pdf(payload)
    
    # Generate timestamped filename for snapshot versioning
    timestamp = datetime.now().strftime('%Y-%m-%d')
    timeline_suffix = f"_{timeline}" if timeline and timeline != "All" else ""
    filename = f"chronicle{timeline_suffix}_{timestamp}.pdf"
    
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)

@router.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, payload: Event, session: Session = Depends(get_session)):
    payload.date = _normalize_date(payload.date)
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    event.title = payload.title
    event.description = payload.description
    event.date = payload.date
    event.timeline = payload.timeline or "Default"
    event.actor = payload.actor
    event.emotion = payload.emotion
    event.tags = payload.tags
    event.evidence_links = payload.evidence_links
    event.privileged_notes = payload.privileged_notes

    session.add(event)
    session.commit()
    session.refresh(event)
    
    # Update FTS5 index
    index_event(
        event_id=event.id,
        title=event.title,
        description=event.description,
        tags=event.tags,
        timeline=event.timeline
    )
    
    return event

@router.post("/events/import/csv")
async def import_events_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    Import events from CSV file.
    Expected CSV format: title,description,date,timeline,actor,emotion,tags,evidence_links
    
    Required fields: title, description, date
    Optional fields: timeline (defaults to "Default"), actor, emotion, tags, evidence_links
    
    Actor examples: Tom, Lisa, Realtor, Court, Bank, etc.
    Evidence_links: URLs or file paths to supporting documents
    
    Excel-friendly date formats supported:
    - YYYY-MM-DD (recommended)
    - MM/DD/YYYY (Excel US default)
    - DD/MM/YYYY (Excel international)
    - MM-DD-YYYY, DD-MM-YYYY, YYYY/MM/DD
    - With or without time: HH:MM:SS
    
    Handles Excel encoding (UTF-8, UTF-8-BOM, CP1252, UTF-16)
    Note: privileged_notes field is not imported from CSV for security
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read the CSV content
        content = await file.read()
        
        # Handle different encodings that Excel might use
        try:
            # Try UTF-8 first (most common)
            csv_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Try UTF-8 with BOM (Excel often adds this)
                csv_content = content.decode('utf-8-sig')
            except UnicodeDecodeError:
                try:
                    # Try Windows encoding (Excel default)
                    csv_content = content.decode('cp1252')
                except UnicodeDecodeError:
                    # Try UTF-16 (Excel sometimes uses this)
                    csv_content = content.decode('utf-16')
        
        # Remove BOM if present (Excel compatibility)
        if csv_content.startswith('\ufeff'):
            csv_content = csv_content[1:]
        
        # Parse CSV with Excel dialect for better compatibility
        csv_reader = csv.DictReader(io.StringIO(csv_content), dialect=csv.excel)
        imported_events = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header row
            try:
                # Validate required fields
                if not row.get('title') or not row.get('description') or not row.get('date'):
                    errors.append(f"Row {row_num}: Missing required fields (title, description, date)")
                    continue
                
                # Parse date - handle various formats (Excel-friendly)
                date_str = row['date'].strip()
                event_date = None
                
                # Try multiple date formats (Excel compatibility)
                date_formats = [
                    '%Y-%m-%d %H:%M:%S',    # YYYY-MM-DD HH:MM:SS
                    '%Y-%m-%d',             # YYYY-MM-DD
                    '%m/%d/%Y',             # MM/DD/YYYY (Excel US format)
                    '%m/%d/%Y %H:%M:%S',    # MM/DD/YYYY HH:MM:SS
                    '%d/%m/%Y',             # DD/MM/YYYY (Excel UK format)
                    '%d/%m/%Y %H:%M:%S',    # DD/MM/YYYY HH:MM:SS
                    '%m-%d-%Y',             # MM-DD-YYYY
                    '%d-%m-%Y',             # DD-MM-YYYY
                    '%Y/%m/%d',             # YYYY/MM/DD
                    '%Y/%m/%d %H:%M:%S',    # YYYY/MM/DD HH:MM:SS
                ]
                
                for date_format in date_formats:
                    try:
                        event_date = datetime.strptime(date_str, date_format)
                        # If date-only format, set time to noon
                        if ' ' not in date_format:
                            event_date = event_date.replace(hour=12)
                        break
                    except ValueError:
                        continue
                
                # If none of the standard formats worked, try ISO format
                if event_date is None:
                    try:
                        event_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date format '{date_str}'. Supported formats: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, MM-DD-YYYY, etc.")
                        continue
                
                # Create event (clean up Excel formatting)
                def clean_field(field_value):
                    """Clean up field value from Excel CSV quirks"""
                    if not field_value:
                        return ""
                    # Strip whitespace and remove extra quotes that Excel sometimes adds
                    cleaned = str(field_value).strip()
                    # Remove surrounding quotes if they're doubled up
                    if cleaned.startswith('""') and cleaned.endswith('""'):
                        cleaned = cleaned[2:-2]
                    elif cleaned.startswith('"') and cleaned.endswith('"'):
                        cleaned = cleaned[1:-1]
                    return cleaned
                
                event = Event(
                    title=clean_field(row['title']),
                    description=clean_field(row['description']),
                    date=event_date,
                    timeline=clean_field(row.get('timeline')) or "Default",
                    actor=clean_field(row.get('actor')) or None,
                    emotion=clean_field(row.get('emotion')) or None,
                    tags=clean_field(row.get('tags')) or None,
                    evidence_links=clean_field(row.get('evidence_links')) or None,
                    # privileged_notes is not imported from CSV for security
                )
                
                session.add(event)
                imported_events.append(event)
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        # Commit all valid events
        if imported_events:
            session.commit()
            for event in imported_events:
                session.refresh(event)
                # Index each event in FTS5 for search
                index_event(
                    event_id=str(event.id),
                    title=event.title,
                    description=event.description,
                    tags=event.tags,
                    timeline=event.timeline
                )
        
        return {
            "message": f"Successfully imported {len(imported_events)} events",
            "imported_count": len(imported_events),
            "error_count": len(errors),
            "errors": errors,
            "events": imported_events
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")


@router.get("/events/stats")
def get_database_stats(session: Session = Depends(get_session)):
    """Get database statistics"""
    try:
        # Count total events
        statement = select(Event)
        events = session.exec(statement).all()
        
        # Get date range if events exist
        if events:
            dates = [event.date for event in events]
            earliest_date = min(dates)
            latest_date = max(dates)
        else:
            earliest_date = None
            latest_date = None
        
        return {
            "total_events": len(events),
            "earliest_event": earliest_date,
            "latest_event": latest_date,
            "database_status": "healthy"
        }
    except Exception as e:
        return {
            "total_events": 0,
            "database_status": "error",
            "error": str(e)
        }


@router.post("/events/seed")
def seed_sample_events(session: Session = Depends(get_session)):
    """Add sample events for testing purposes"""
    try:
        # Sample events data with legal workflow fields
        sample_events = [
            {
                "title": "Initial Consultation with Lisa",
                "description": "First meeting to discuss property purchase and legal requirements",
                "date": datetime(2025, 8, 1, 10, 0, 0),
                "timeline": "Property Purchase",
                "actor": "Lisa",
                "emotion": "hopeful",
                "tags": "consultation,initial-meeting",
                "evidence_links": "/documents/consultation_notes.pdf",
                "privileged_notes": "Client expressed concerns about financing timeline"
            },
            {
                "title": "Realtor Property Showing",
                "description": "Toured the main property with Jane (realtor) - seemed promising",
                "date": datetime(2025, 8, 5, 14, 30, 0),
                "timeline": "Property Purchase",
                "actor": "Realtor",
                "emotion": "excited",
                "tags": "property-tour,viewing",
                "evidence_links": "/photos/property_tour_2025_08_05/"
            },
            {
                "title": "Purchase Offer Submitted",
                "description": "Tom submitted formal purchase offer through realtor",
                "date": datetime(2025, 8, 8, 16, 45, 0),
                "timeline": "Property Purchase",
                "actor": "Tom",
                "emotion": "nervous",
                "tags": "offer,formal-submission",
                "evidence_links": "/contracts/purchase_offer_v1.pdf"
            },
            {
                "title": "Bank Pre-Approval Meeting",
                "description": "Meeting with loan officer to discuss financing options and requirements",
                "date": datetime(2025, 8, 12, 11, 0, 0),
                "timeline": "Financing",
                "actor": "Bank",
                "emotion": "cautious",
                "tags": "pre-approval,financing",
                "evidence_links": "/documents/preapproval_letter.pdf"
            },
            {
                "title": "Counter-Offer Received",
                "description": "Seller responded with counter-offer, needs review with attorney",
                "date": datetime(2025, 8, 15, 9, 30, 0),
                "timeline": "Property Purchase",
                "actor": "Realtor",
                "emotion": "thoughtful",
                "tags": "counter-offer,negotiation",
                "evidence_links": "/contracts/counter_offer_v1.pdf",
                "privileged_notes": "Counter-offer includes unusual inspection clause - need to research precedent"
            },
            {
                "title": "Attorney Contract Review",
                "description": "Brody reviewed purchase agreement and identified potential issues",
                "date": datetime(2025, 8, 18, 14, 0, 0),
                "timeline": "Legal Review",
                "actor": "Attorney",
                "emotion": "concerned",
                "tags": "contract-review,legal-analysis",
                "evidence_links": "/legal/contract_review_memo.pdf",
                "privileged_notes": "Identified problematic warranty disclaimers in Section 12.3 - advise renegotiation"
            },
            {
                "title": "Court Filing Deadline",
                "description": "Deadline for filing preliminary injunction papers in unrelated case",
                "date": datetime(2025, 8, 20, 17, 0, 0),
                "timeline": "Other Legal Matters",
                "actor": "Court",
                "emotion": "stressed",
                "tags": "deadline,filing,injunction",
                "evidence_links": "/court_docs/prelim_injunction_draft.pdf"
            },
            {
                "title": "Property Inspection Completed",
                "description": "Professional inspection revealed minor issues, overall positive",
                "date": datetime(2025, 8, 22, 10, 30, 0),
                "timeline": "Property Purchase",
                "actor": "Tom",
                "emotion": "relieved",
                "tags": "inspection,property-condition",
                "evidence_links": "/reports/inspection_report_final.pdf"
            },
            {
                "title": "Final Loan Approval",
                "description": "Bank approved loan with standard conditions",
                "date": datetime(2025, 8, 28, 15, 15, 0),
                "timeline": "Financing",
                "actor": "Bank",
                "emotion": "accomplished",
                "tags": "loan-approval,financing-complete",
                "evidence_links": "/documents/final_loan_approval.pdf"
            },
            {
                "title": "Closing Date Scheduled",
                "description": "All parties agreed on closing date, title company confirmed",
                "date": datetime(2025, 9, 2, 11, 45, 0),
                "timeline": "Property Purchase",
                "actor": "Realtor",
                "emotion": "satisfied",
                "tags": "closing-scheduled,milestone",
                "evidence_links": "/scheduling/closing_confirmation.pdf"
            }
        ]
        
        created_events = []
        for event_data in sample_events:
            event = Event(**event_data)
            session.add(event)
            created_events.append(event)
        
        session.commit()
        
        for event in created_events:
            session.refresh(event)
        
        return {
            "message": f"Successfully seeded {len(created_events)} sample events",
            "created_count": len(created_events),
            "events": created_events
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error seeding data: {str(e)}")


@router.delete("/events/")
def clear_all_events(session: Session = Depends(get_session)):
    """Clear all events from the database - USE WITH CAUTION"""
    try:
        # Get all events
        statement = select(Event)
        events = session.exec(statement).all()
        event_count = len(events)
        
        # Delete all events
        for event in events:
            session.delete(event)
        
        session.commit()
        
        # Clear FTS5 index (rebuild will create empty index)
        from ..db.fts import rebuild_index
        rebuild_index()
        
        return {
            "message": f"Successfully cleared {event_count} events from database",
            "deleted_count": event_count
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")


@router.delete("/events/{event_id}")
def delete_event(event_id: str, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    # Remove from FTS5 index
    remove_from_index(event_id)
    
    session.delete(event)
    session.commit()
    return {"deleted": event_id}


@router.post("/events/with-audio")
async def create_event_with_audio(
    title: str = Form(...),
    description: str = Form(""),
    date: str = Form(...),
    timeline: str = Form("Default"),
    emotion: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    audio_file: UploadFile = File(...),
    transcribe: bool = Form(True),
    session: Session = Depends(get_session)
):
    """
    Create an event with an attached audio file and optional transcription.
    """
    try:
        # Save audio file
        file_ext = os.path.splitext(audio_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        with open(file_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        # Transcribe if requested
        transcription_text = description
        word_timestamps = None
        summary_text = None
        
        if transcribe:
            result = whisper_service.transcribe_audio(str(file_path))
            transcription_text = result["text"]
            word_timestamps = json.dumps(result.get("words", []))
            
            # Generate smart summary
            summary_service = get_summary_service()
            summary_data = summary_service.generate_summary(transcription_text)
            summary_text = json.dumps(summary_data)  # Store as JSON
        
        # Create event
        event = Event(
            title=title,
            description=transcription_text or description,
            date=_normalize_date(date),
            timeline=timeline,
            emotion=emotion,
            tags=tags,
            audio_file=str(file_path.relative_to(Path(__file__).parent.parent)),
            transcription_words=word_timestamps,
            summary=summary_text
        )
        
        session.add(event)
        session.commit()
        session.refresh(event)
        
        # Index event in FTS5 for search
        index_event(
            event_id=event.id,
            title=event.title,
            description=event.description,
            tags=event.tags,
            timeline=event.timeline
        )
        
        return event
        
    except Exception as e:
        # Clean up file if event creation fails
        if file_path.exists():
            os.unlink(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}/audio")
def get_event_audio(event_id: str, session: Session = Depends(get_session)):
    """
    Serve the audio file for an event.
    """
    event = session.get(Event, event_id)
    if not event or not event.audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    audio_path = Path(__file__).parent.parent / event.audio_file
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found on disk")
    
    return FileResponse(audio_path, media_type="audio/mpeg")


@router.post("/events/with-attachments")
async def create_event_with_attachments(
    title: str = Form(...),
    description: str = Form(""),
    date: str = Form(...),
    timeline: str = Form("Default"),
    actor: Optional[str] = Form(None),
    emotion: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    evidence_links: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    files: List[UploadFile] = File(default=[]),
    transcribe: bool = Form(True),
    session: Session = Depends(get_session)
):
    """
    Create an event with optional audio file and/or document attachments.
    Handles mixed attachment types in a single request.
    """
    try:
        created_files = []  # Track files for cleanup on error
        
        # Handle audio file processing
        audio_file_path = None
        transcription_text = description
        word_timestamps = None
        summary_text = None
        
        if audio_file:
            # Save audio file
            file_ext = os.path.splitext(audio_file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            audio_file_path = UPLOAD_DIR / unique_filename
            created_files.append(audio_file_path)
            
            with open(audio_file_path, "wb") as f:
                content = await audio_file.read()
                f.write(content)
            
            # Transcribe if requested
            if transcribe:
                result = whisper_service.transcribe_audio(str(audio_file_path))
                transcription_text = result["text"]
                word_timestamps = json.dumps(result.get("words", []))
                
                # Generate smart summary
                summary_service = get_summary_service()
                summary_data = summary_service.generate_summary(transcription_text)
                summary_text = json.dumps(summary_data)
        
        # Create event first
        event = Event(
            title=title,
            description=transcription_text or description,
            date=_normalize_date(date),
            timeline=timeline,
            actor=actor,
            emotion=emotion,
            tags=tags,
            evidence_links=evidence_links,
            audio_file=str(audio_file_path.relative_to(Path(__file__).parent.parent)) if audio_file_path else None,
            transcription_words=word_timestamps,
            summary=summary_text
        )
        
        session.add(event)
        session.commit()
        session.refresh(event)
        
        # Handle document files
        document_contents = []
        
        for uploaded_file in files:
            if not uploaded_file.filename:
                continue
                
            # Validate file type
            if not DocumentParser.is_supported(uploaded_file.filename):
                supported = ", ".join(DocumentParser.SUPPORTED_EXTENSIONS)
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {uploaded_file.filename}. Supported formats: {supported}"
                )
            
            # Read and parse document
            file_content = await uploaded_file.read()
            parsed_data = parse_uploaded_document(file_content, uploaded_file.filename)
            
            # Create unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(uploaded_file.filename).suffix
            safe_filename = f"{file_id}{file_extension}"
            
            # Create documents directory if it doesn't exist
            doc_upload_dir = UPLOAD_DIR / "documents"
            doc_upload_dir.mkdir(exist_ok=True)
            
            file_path = doc_upload_dir / safe_filename
            created_files.append(file_path)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Create attachment record
            attachment = Attachment(
                event_id=event.id,
                original_filename=uploaded_file.filename,
                file_path=str(file_path.relative_to(Path(__file__).parent.parent)),
                file_type=Path(uploaded_file.filename).suffix,
                file_size=len(file_content),
                mime_type=uploaded_file.content_type or "application/octet-stream",
                parsed_content=parsed_data["content"],
                page_count=parsed_data.get("page_count"),
                word_count=parsed_data.get("word_count")
            )
            
            session.add(attachment)
            document_contents.append(parsed_data["content"])
        
        session.commit()
        
        # Index event and documents in FTS5 for search
        all_content = [event.title, event.description or "", event.tags or ""]
        all_content.extend(document_contents)
        
        index_event(
            event_id=event.id,
            title=event.title,
            description=" ".join(all_content),  # Include document content in searchable text
            tags=event.tags,
            timeline=event.timeline
        )
        
        return event
        
    except Exception as e:
        # Clean up any files that were created
        for file_path in created_files:
            if file_path.exists():
                try:
                    os.unlink(file_path)
                except:
                    pass  # Ignore cleanup errors
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/{event_id}/documents")
async def upload_document(
    event_id: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload and attach a document to an event.
    Supports PDF, DOCX, MD, and TXT files with full-text parsing.
    """
    # Check if event exists
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Validate file type
    if not DocumentParser.is_supported(file.filename):
        supported = ", ".join(DocumentParser.SUPPORTED_EXTENSIONS)
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Supported formats: {supported}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse document content
        parsed_data = parse_uploaded_document(file_content, file.filename)
        
        # Create unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        safe_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / "documents" / safe_filename
        
        # Create documents directory
        file_path.parent.mkdir(exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Create attachment record
        attachment = Attachment(
            event_id=event_id,
            file_path=str(file_path.relative_to(Path(__file__).parent.parent)),
            file_type=parsed_data['file_type'],
            original_filename=file.filename,
            parsed_content=parsed_data['content'],
            page_count=parsed_data.get('page_count'),
            word_count=parsed_data.get('word_count')
        )
        
        session.add(attachment)
        session.commit()
        session.refresh(attachment)
        
        # Index document content in FTS5
        # Use attachment ID for unique identification in search
        index_event(
            event_id=f"doc_{attachment.id}",
            title=f"📄 {file.filename}",
            description=parsed_data['content'],
            tags=f"document,{parsed_data['file_type']},attachment",
            timeline=event.timeline
        )
        
        return {
            "message": "Document uploaded successfully",
            "attachment": attachment,
            "parsed_info": {
                "file_type": parsed_data['file_type'],
                "page_count": parsed_data.get('page_count', 1),
                "word_count": parsed_data.get('word_count', 0)
            }
        }
        
    except Exception as e:
        # Clean up file if attachment creation fails
        if 'file_path' in locals() and file_path.exists():
            os.unlink(file_path)
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")


@router.get("/events/{event_id}/documents")
def get_event_documents(event_id: str, session: Session = Depends(get_session)):
    """Get all documents attached to an event"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event.attachments


@router.get("/documents/{attachment_id}")
def download_document(attachment_id: int, session: Session = Depends(get_session)):
    """Download a document attachment"""
    attachment = session.get(Attachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = Path(__file__).parent.parent / attachment.file_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")
    
    return FileResponse(
        file_path, 
        filename=attachment.original_filename,
        media_type="application/octet-stream"
    )


@router.delete("/documents/{attachment_id}")
def delete_document(attachment_id: int, session: Session = Depends(get_session)):
    """Delete a document attachment"""
    attachment = session.get(Attachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Remove from FTS5 index
        remove_from_index(f"doc_{attachment.id}")
        
        # Delete file
        file_path = Path(__file__).parent.parent / attachment.file_path
        if file_path.exists():
            os.unlink(file_path)
        
        # Delete database record
        session.delete(attachment)
        session.commit()
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
