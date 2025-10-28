import React, { useState, useEffect } from 'react';
import VisualTimeline from '../components/VisualTimeline';
import TimelineSwimLanes from '../components/TimelineSwimLanes';
import { getEvents, getTimelines } from '../services/api';

/**
 * ProfessionalDashboard - SUNO-Inspired Layout
 * 
 * A professional 3-column layout inspired by SUNO's music interface:
 * - Left: Tools & Search (like SUNO's sidebar)
 * - Center: Timeline Visualization (like SUNO's waveform - THE HERO)
 * - Right: Events List (like SUNO's track list)
 */

const ProfessionalDashboard = () => {
    const [events, setEvents] = useState([]);
    const [timelines, setTimelines] = useState(["Default"]);
    const [currentTimeline, setCurrentTimeline] = useState("Default");
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);

    // Load data
    useEffect(() => {
        loadEvents();
        loadTimelines();
    }, [currentTimeline]);

    const loadEvents = async () => {
        setLoading(true);
        try {
            const data = await getEvents(currentTimeline === "All" ? null : currentTimeline);
            setEvents(data);
        } catch (err) {
            console.error("Failed to load events:", err);
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

    // Filter events based on search
    const filteredEvents = events.filter(event => 
        event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        event.description?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="h-screen bg-slate-900 flex overflow-hidden">
            {/* LEFT SIDEBAR - Tools & Search */}
            <div className="w-72 bg-slate-900 border-r border-slate-700/50 flex flex-col">
                {/* Header */}
                <div className="p-6 border-b border-slate-700/50">
                    <h1 className="text-2xl font-bold text-white mb-1">Chronicle</h1>
                    <p className="text-slate-400 text-sm">Professional Timeline</p>
                </div>

                {/* Timeline Selector */}
                <div className="p-4 border-b border-slate-700/50">
                    <label className="block text-sm font-medium text-slate-300 mb-2">Timeline</label>
                    <select
                        value={currentTimeline}
                        onChange={(e) => setCurrentTimeline(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-purple-500"
                    >
                        {timelines.map(timeline => (
                            <option key={timeline} value={timeline}>{timeline}</option>
                        ))}
                    </select>
                </div>

                {/* Search */}
                <div className="p-4 border-b border-slate-700/50">
                    <label className="block text-sm font-medium text-slate-300 mb-2">Search Events</label>
                    <div className="relative">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search timeline..."
                            className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 pl-9 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                        />
                        <span className="absolute left-3 top-2.5 text-slate-400 text-sm">🔍</span>
                    </div>
                </div>

                {/* Tools */}
                <div className="p-4 flex-1">
                    <h3 className="text-sm font-medium text-slate-300 mb-3">Tools</h3>
                    <div className="space-y-2">
                        <button className="w-full text-left px-3 py-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded text-sm transition-colors">
                            📊 Analytics
                        </button>
                        <button className="w-full text-left px-3 py-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded text-sm transition-colors">
                            📤 Export
                        </button>
                        <button className="w-full text-left px-3 py-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded text-sm transition-colors">
                            ⚙️ Settings
                        </button>
                    </div>
                </div>

                {/* Credits - SUNO Style */}
                <div className="p-4 border-t border-slate-700/50">
                    <div className="text-xs text-slate-500">
                        <p>👁️ Eyelid Design by Tom & Claude</p>
                        <p>Inspired by SUNO's beautiful UI</p>
                    </div>
                </div>
            </div>

            {/* CENTER STAGE - Timeline Hero */}
            <div className="flex-1 bg-slate-800 flex flex-col">
                {/* Timeline Header */}
                <div className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 p-4 flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-white">Timeline Visualization</h2>
                        <p className="text-slate-400 text-sm">
                            {filteredEvents.length} events in {currentTimeline}
                        </p>
                    </div>
                    
                    {/* Timeline Controls */}
                    <div className="flex gap-1 bg-slate-700/50 rounded-lg p-1">
                        {['1W', '1M', '3M', '1Y', 'All'].map((period) => (
                            <button
                                key={period}
                                className="px-3 py-1 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-600 rounded transition-colors"
                            >
                                {period}
                            </button>
                        ))}
                    </div>
                </div>

                {/* HERO TIMELINE - Like SUNO's Waveform */}
                <div className="h-80 relative border-b border-slate-700/50">
                    {loading ? (
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-slate-400">Loading timeline...</div>
                        </div>
                    ) : (
                        <div className="h-full">
                            <VisualTimeline
                                events={filteredEvents}
                                onEventClick={setSelectedEvent}
                                currentTimeline={currentTimeline}
                            />
                        </div>
                    )}
                    
                    {/* Floating Timeline Stats */}
                    <div className="absolute top-4 left-4 bg-slate-900/80 backdrop-blur-sm rounded-lg p-3 border border-slate-700/50">
                        <div className="text-xs text-slate-400 space-y-1">
                            <div>📅 {filteredEvents.length} events</div>
                            <div>🎤 {filteredEvents.filter(e => e.audio_file).length} with audio</div>
                            <div>📍 Timeline: {currentTimeline}</div>
                        </div>
                    </div>
                </div>

                {/* REVOLUTIONARY SWIMLANES SECTION */}
                <div className="flex-1 p-4">
                    <TimelineSwimLanes
                        events={filteredEvents}
                        timelines={timelines.filter(t => t !== "All")}
                        onEventClick={setSelectedEvent}
                        selectedEvent={selectedEvent}
                    />
                </div>
            </div>

            {/* RIGHT COLUMN - Events List (Like SUNO's Track List) */}
            <div className="w-96 bg-slate-900 border-l border-slate-700/50 flex flex-col">
                {/* Quick Add Header */}
                <div className="p-4 border-b border-slate-700/50">
                    <button className="w-full bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 shadow-lg">
                        <span>➕</span>
                        <span>Add New Event</span>
                    </button>
                </div>

                {/* Events List Header */}
                <div className="p-4 border-b border-slate-700/50">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-white">Events</h3>
                        <span className="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded">
                            {filteredEvents.length}
                        </span>
                    </div>
                </div>

                {/* Events List - Scrollable */}
                <div className="flex-1 overflow-y-auto">
                    {filteredEvents.length === 0 ? (
                        <div className="p-8 text-center text-slate-400">
                            <p className="mb-2">No events found</p>
                            <p className="text-xs">Add your first event to get started</p>
                        </div>
                    ) : (
                        <div className="p-2 space-y-2">
                            {filteredEvents.map((event) => (
                                <div
                                    key={event.id}
                                    onClick={() => setSelectedEvent(event)}
                                    className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-lg ${
                                        selectedEvent?.id === event.id
                                            ? 'bg-blue-600/20 border-blue-500/50 shadow-blue-500/20'
                                            : 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-800 hover:border-slate-600'
                                    }`}
                                >
                                    {/* Event Card - SUNO Track Style */}
                                    <div className="flex items-start gap-3">
                                        {/* Event Icon/Thumbnail */}
                                        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                                            <span className="text-white text-sm">
                                                {event.audio_file ? '🎤' : '📋'}
                                            </span>
                                        </div>
                                        
                                        {/* Event Details */}
                                        <div className="flex-1 min-w-0">
                                            <h4 className="font-medium text-white text-sm mb-1 truncate">
                                                {event.title}
                                            </h4>
                                            <p className="text-xs text-slate-400 mb-2 line-clamp-2">
                                                {event.description || 'No description'}
                                            </p>
                                            <div className="flex items-center gap-2 text-xs text-slate-500">
                                                <span>📅 {new Date(event.date).toLocaleDateString()}</span>
                                                {event.timeline !== currentTimeline && (
                                                    <span className="bg-slate-700 px-1 rounded">
                                                        {event.timeline}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ProfessionalDashboard;