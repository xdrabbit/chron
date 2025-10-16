import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import EventForm from '../components/EventForm';
import Timeline from '../components/Timeline';
import VisualTimeline from '../components/VisualTimeline';
import TestingPanel from '../components/TestingPanel';
import SearchPanel from '../components/SearchPanel';
// AI components disabled - FTS5 search is sufficient
// import AskPanel from '../components/AskPanel';
// import FloatingAskPanel from '../components/FloatingAskPanel';
import FloatingTimelineViz from '../components/FloatingTimelineViz';
import FloatingSearchPanel from '../components/FloatingSearchPanel';
import FloatingEventForm from '../components/FloatingEventForm';
import { getEvents, createEvent, createEventWithAudio, updateEvent, deleteEvent, exportTimelinePdf, exportTimelineCsv, importEventsFromCsv, getTimelines } from '../services/api';

const Home = () => {
    const [events, setEvents] = useState([]);
    const [timelines, setTimelines] = useState(["Default"]);
    const [currentTimeline, setCurrentTimeline] = useState("Default");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editing, setEditing] = useState(null);
    const [exporting, setExporting] = useState(false);
    const [exportError, setExportError] = useState(null);
    const [importing, setImporting] = useState(false);
    const [importError, setImportError] = useState(null);
    const [importResult, setImportResult] = useState(null);
    const eventListRef = useRef(null);
    const visualTimelineRef = useRef(null);
    const [showTestingPanel, setShowTestingPanel] = useState(false);
    const [showSearchPanel, setShowSearchPanel] = useState(false);
    // const [showAskPanel, setShowAskPanel] = useState(false);
    // const [showFloatingAI, setShowFloatingAI] = useState(false);
    const [showFloatingTimeline, setShowFloatingTimeline] = useState(false);
    const [showFloatingSearch, setShowFloatingSearch] = useState(false);
    const [showFloatingForm, setShowFloatingForm] = useState(false);
    const [successMessage, setSuccessMessage] = useState(null);

    const loadEvents = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getEvents(currentTimeline === "All" ? null : currentTimeline);
            setEvents(data);
        } catch (err) {
            setError("Unable to fetch events. Check that the backend is running.");
        } finally {
            setLoading(false);
        }
    };

    const loadTimelines = async () => {
        try {
            const data = await getTimelines();
            setTimelines(["All", "Default", ...data.filter(t => t !== "Default")]);
        } catch (err) {
            console.error("Failed to load timelines:", err);
        }
    };

    useEffect(() => {
        loadTimelines();
        loadEvents();
    }, [currentTimeline]);

    useEffect(() => {
        loadTimelines();
    }, []);

    const handleSubmit = async (formData, isAudio = false) => {
        if (editing) {
            await updateEvent(editing.id, formData);
            setEditing(null);
            showSuccessToast('Event updated successfully!');
        } else {
            // Use appropriate API based on whether we have audio
            if (isAudio) {
                await createEventWithAudio(formData);
                showSuccessToast('Event created with audio transcription!');
            } else {
                await createEvent(formData);
                showSuccessToast('Event created successfully!');
            }
        }
        await loadEvents();
        await loadTimelines();
    };

    const showSuccessToast = (message) => {
        setSuccessMessage(message);
        setTimeout(() => setSuccessMessage(null), 3000); // Hide after 3 seconds
    };

    const handleDelete = async (eventId) => {
        await deleteEvent(eventId);
        await loadEvents();
    };

    const handleTimelineEventClick = (event) => {
        // Scroll to the event in the list
        const eventElement = document.getElementById(`event-${event.id}`);
        if (eventElement) {
            eventElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Briefly highlight the event
            eventElement.classList.add('ring-2', 'ring-green-500');
            setTimeout(() => {
                eventElement.classList.remove('ring-2', 'ring-green-500');
            }, 2000);
        }
    };

    const handleEventCardClick = (event) => {
        // Focus the visual timeline on this event
        if (visualTimelineRef.current) {
            visualTimelineRef.current.focusOnEvent(event.id);
        }
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
            await loadTimelines(); // Reload timelines as new ones might be imported
            await loadEvents(); // Reload events to show imported data
        } catch (err) {
            setImportError(
                err.response?.data?.detail || "Unable to import CSV. Check file format and try again.",
            );
        } finally {
            setImporting(false);
        }
    };

    const handleSearchResultSelect = (event) => {
        // Scroll to the event in the timeline
        handleEventCardClick(event);
        // Optionally close search panel
        // setShowSearchPanel(false);
    };

    return (
        <>
            <header className="flex flex-col gap-1">
                <div className="flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-bold">Chronicle</h1>
                        <p className="text-sm text-slate-400">
                            A local-first narrative timeline.
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <Link
                            to="/voice"
                            className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-md font-medium transition-colors text-sm"
                        >
                            🎤 Voice Transcription
                        </Link>
                        
                        {/* Floating Panel Controls */}
                        <div className="flex gap-1 bg-slate-700 rounded-md p-1">
                            <button
                                onClick={() => setShowFloatingTimeline(!showFloatingTimeline)}
                                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                    showFloatingTimeline 
                                        ? 'bg-blue-600 text-white' 
                                        : 'text-slate-300 hover:bg-slate-600'
                                }`}
                                title="Float Timeline Viz"
                            >
                                📅 Timeline
                            </button>
                            <button
                                onClick={() => setShowFloatingSearch(!showFloatingSearch)}
                                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                    showFloatingSearch 
                                        ? 'bg-green-600 text-white' 
                                        : 'text-slate-300 hover:bg-slate-600'
                                }`}
                                title="Float Search Panel"
                            >
                                🔍 Search
                            </button>
                            <button
                                onClick={() => setShowFloatingForm(!showFloatingForm)}
                                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                    showFloatingForm 
                                        ? 'bg-orange-600 text-white' 
                                        : 'text-slate-300 hover:bg-slate-600'
                                }`}
                                title="Float Event Form"
                            >
                                ✏️ Form
                            </button>
                        </div>
                        
                        <span className="text-xs bg-purple-900/50 text-purple-300 px-2 py-1 rounded self-center">
                            👁️ Draggable Eyelids
                        </span>
                        
                        <Link
                            to="/pro"
                            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-4 py-2 rounded-md font-medium transition-all duration-200 text-sm shadow-lg"
                            title="Professional SUNO-inspired Layout"
                        >
                            🎵 Pro Dashboard
                        </Link>
                    </div>
                </div>
            </header>

            {/* Timeline Selector */}
            <section className="rounded-lg bg-slate-800 p-4 shadow">
                <div className="flex items-center gap-4">
                    <label className="text-sm font-semibold text-slate-300">
                        Timeline:
                    </label>
                    <select
                        value={currentTimeline}
                        onChange={(e) => setCurrentTimeline(e.target.value)}
                        className="rounded border border-slate-600 bg-slate-900 px-3 py-2 text-slate-100 focus:border-blue-500 focus:outline-none"
                    >
                        {timelines.map((timeline) => (
                            <option key={timeline} value={timeline}>
                                {timeline}
                            </option>
                        ))}
                    </select>
                    <span className="text-xs text-slate-400">
                        {currentTimeline === "All" 
                            ? `Showing all events from ${timelines.length - 1} timeline(s)`
                            : `Viewing: ${currentTimeline}`
                        }
                    </span>
                </div>
            </section>

            {/* Visual Timeline Viewer */}
            {events.length > 0 && (
                <section>
                    <VisualTimeline
                        ref={visualTimelineRef}
                        events={events}
                        onEventClick={handleTimelineEventClick}
                        currentTimeline={currentTimeline}
                    />
                </section>
            )}

            {/* Search Panel - Collapsible */}
            <section className="rounded-lg bg-slate-800 border border-slate-700 shadow">
                <button
                    onClick={() => setShowSearchPanel(!showSearchPanel)}
                    className="w-full flex items-center justify-between p-4 hover:bg-slate-700 transition-colors"
                >
                    <div className="flex items-center gap-3">
                        <span className="text-blue-400 text-xl">🔍</span>
                        <h3 className="text-lg font-semibold text-slate-200">Search Events</h3>
                        <span className="text-xs bg-blue-600 text-blue-100 px-2 py-0.5 rounded">FTS5</span>
                    </div>
                    <span className="text-slate-400 text-xl">
                        {showSearchPanel ? '−' : '+'}
                    </span>
                </button>
                {showSearchPanel && (
                    <div className="p-4 border-t border-slate-700">
                        <SearchPanel onEventSelect={handleSearchResultSelect} />
                    </div>
                )}
            </section>

            {/* Event List */}
            <section className="rounded-lg bg-slate-800 p-4 shadow">
                <Timeline
                    events={events}
                    loading={loading}
                    error={error}
                    onEdit={setEditing}
                    onDelete={handleDelete}
                    onEventClick={handleEventCardClick}
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

            {/* Event Form - Highlighted for data entry */}
            <section className="rounded-lg bg-gradient-to-br from-amber-900/30 to-slate-800 border-2 border-amber-600/50 p-4 shadow-lg">
                <div className="flex items-center gap-2 mb-4">
                    <span className="text-amber-400 text-xl">✏️</span>
                    <h3 className="text-lg font-semibold text-amber-200">
                        {editing ? 'Edit Event' : 'Add New Event'}
                    </h3>
                </div>
                <EventForm
                    key={editing ? editing.id : "new"}
                    initialData={editing}
                    onSubmit={handleSubmit}
                    onCancel={() => setEditing(null)}
                    availableTimelines={timelines.filter(t => t !== "All")}
                />
            </section>

            {/* Testing Panel - Collapsible */}
            <section className="rounded-lg bg-slate-800 border border-slate-700 shadow">
                <button
                    onClick={() => setShowTestingPanel(!showTestingPanel)}
                    className="w-full flex items-center justify-between p-4 hover:bg-slate-700 transition-colors"
                >
                    <div className="flex items-center gap-3">
                        <span className="text-yellow-400 text-xl">🧪</span>
                        <h3 className="text-lg font-semibold text-slate-200">Testing Panel</h3>
                        <span className="text-xs bg-yellow-600 text-yellow-100 px-2 py-0.5 rounded">DEV</span>
                    </div>
                    <span className="text-slate-400 text-xl">
                        {showTestingPanel ? '−' : '+'}
                    </span>
                </button>
                {showTestingPanel && (
                    <div className="p-4 border-t border-slate-700">
                        <TestingPanel onDatabaseChange={() => { loadEvents(); loadTimelines(); }} />
                    </div>
                )}
            </section>

            {/* Success Toast Notification */}
            {successMessage && (
                <div className="fixed bottom-8 right-8 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-slide-up z-50">
                    <span className="text-xl">✓</span>
                    <span className="font-medium">{successMessage}</span>
                </div>
            )}

            {/* Revolutionary Floating Panels */}
            {showFloatingTimeline && (
                <FloatingTimelineViz
                    events={events}
                    onEventClick={(event) => {
                        // Scroll to event in main timeline
                        if (eventListRef.current) {
                            const element = document.getElementById(`event-${event.id}`);
                            if (element) {
                                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }
                        }
                    }}
                    currentTimeline={currentTimeline}
                    onClose={() => setShowFloatingTimeline(false)}
                    isFloating={true}
                />
            )}
            
            {showFloatingSearch && (
                <FloatingSearchPanel
                    onClose={() => setShowFloatingSearch(false)}
                    isFloating={true}
                />
            )}
            
            {showFloatingForm && (
                <FloatingEventForm
                    onSubmit={async (formData, isAudio) => {
                        await handleSubmit(formData, isAudio);
                        setShowFloatingForm(false); // Close after creating
                    }}
                    editing={editing}
                    timelines={timelines}
                    onClose={() => setShowFloatingForm(false)}
                    isFloating={true}
                />
            )}
        </>
    );
};

export default Home;
