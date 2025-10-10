import React, { useEffect, useState } from 'react';
import EventForm from '../components/EventForm';
import Timeline from '../components/Timeline';
import TestingPanel from '../components/TestingPanel';
import { getEvents, createEvent, updateEvent, deleteEvent, exportTimelinePdf, exportTimelineCsv, importEventsFromCsv } from '../services/api';

const Home = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editing, setEditing] = useState(null);
    const [exporting, setExporting] = useState(false);
    const [exportError, setExportError] = useState(null);
    const [importing, setImporting] = useState(false);
    const [importError, setImportError] = useState(null);
    const [importResult, setImportResult] = useState(null);

    const loadEvents = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getEvents();
            setEvents(data);
        } catch (err) {
            setError("Unable to fetch events. Check that the backend is running.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadEvents();
    }, []);

    const handleSubmit = async (formData) => {
        if (editing) {
            await updateEvent(editing.id, formData);
            setEditing(null);
        } else {
            await createEvent(formData);
        }
        await loadEvents();
    };

    const handleDelete = async (eventId) => {
        await deleteEvent(eventId);
        await loadEvents();
    };

    const handleExport = async () => {
        setExportError(null);
        setExporting(true);
        try {
            const blob = await exportTimelinePdf();
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "chronicle-timeline.pdf";
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            setExportError(
                "Unable to export timeline. Ensure the backend is running and try again.",
            );
        } finally {
            setExporting(false);
        }
    };

    const handleExportCsv = async () => {
        setExportError(null);
        setExporting(true);
        try {
            const blob = await exportTimelineCsv();
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "chronicle-events.csv";
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            setExportError(
                "Unable to export CSV. Ensure the backend is running and try again.",
            );
        } finally {
            setExporting(false);
        }
    };

    const handleImportCsv = async (file) => {
        setImportError(null);
        setImportResult(null);
        setImporting(true);
        try {
            const result = await importEventsFromCsv(file);
            setImportResult(result);
            await loadEvents(); // Reload events to show imported data
        } catch (err) {
            setImportError(
                err.response?.data?.detail || "Unable to import CSV. Check file format and try again.",
            );
        } finally {
            setImporting(false);
        }
    };

    return (
        <>
            <header className="flex flex-col gap-1">
                <h1 className="text-3xl font-bold">Chronicle</h1>
                <p className="text-sm text-slate-400">
                    A local-first narrative timeline.
                </p>
            </header>

            <section className="rounded-lg bg-slate-800 p-4 shadow">
                <EventForm
                    key={editing ? editing.id : "new"}
                    initialData={editing}
                    onSubmit={handleSubmit}
                    onCancel={() => setEditing(null)}
                />
            </section>

            <TestingPanel onDatabaseChange={loadEvents} />

            <section className="rounded-lg bg-slate-800 p-4 shadow">
                <Timeline
                    events={events}
                    loading={loading}
                    error={error}
                    onEdit={setEditing}
                    onDelete={handleDelete}
                    onExport={handleExport}
                    onExportCsv={handleExportCsv}
                    onImportCsv={handleImportCsv}
                    exporting={exporting}
                    importing={importing}
                    exportError={exportError}
                    importError={importError}
                    importResult={importResult}
                />
            </section>
        </>
    );
};

export default Home;
