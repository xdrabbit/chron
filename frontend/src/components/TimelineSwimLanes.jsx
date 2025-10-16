import React, { useMemo } from 'react';

/**
 * TimelineSwimLanes - Revolutionary Horizontal Timeline View
 * 
 * Shows each timeline as a horizontal "swimlane" with events as flags
 * Perfect for seeing patterns across different life areas
 * Like a Gantt chart for your entire life!
 */

const TimelineSwimLanes = ({ events, timelines, onEventClick, selectedEvent }) => {
    // Group events by timeline
    const eventsByTimeline = useMemo(() => {
        const grouped = {};
        timelines.forEach(timeline => {
            grouped[timeline] = events.filter(e => e.timeline === timeline);
        });
        return grouped;
    }, [events, timelines]);

    // Calculate time range for positioning
    const timeRange = useMemo(() => {
        if (events.length === 0) return { min: new Date(), max: new Date() };
        
        const dates = events.map(e => new Date(e.date));
        const min = new Date(Math.min(...dates));
        const max = new Date(Math.max(...dates));
        
        // Add padding
        const padding = (max - min) * 0.1;
        return {
            min: new Date(min.getTime() - padding),
            max: new Date(max.getTime() + padding)
        };
    }, [events]);

    const getEventPosition = (eventDate) => {
        const date = new Date(eventDate);
        const total = timeRange.max - timeRange.min;
        const elapsed = date - timeRange.min;
        return (elapsed / total) * 100;
    };

    // Generate timeline colors
    const getTimelineColor = (timeline, index) => {
        const colors = [
            'from-purple-500 to-blue-500',
            'from-blue-500 to-green-500', 
            'from-green-500 to-yellow-500',
            'from-yellow-500 to-orange-500',
            'from-orange-500 to-red-500',
            'from-red-500 to-pink-500',
            'from-pink-500 to-purple-500',
            'from-indigo-500 to-cyan-500'
        ];
        return colors[index % colors.length];
    };

    if (events.length === 0) {
        return (
            <div className="h-64 flex items-center justify-center text-slate-400">
                <div className="text-center">
                    <div className="text-4xl mb-4">🏊‍♂️</div>
                    <p>No events to display in swimlanes</p>
                    <p className="text-sm">Add events to see timeline swimlanes</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
            {/* Swimlanes Header */}
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="text-lg font-semibold text-white">Timeline Swimlanes</h3>
                    <p className="text-sm text-slate-400">Each timeline as a horizontal lane</p>
                </div>
                <div className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded">
                    🏊‍♂️ Swimlane View
                </div>
            </div>

            {/* Time Scale Header */}
            <div className="relative h-8 mb-4 border-b border-slate-700/50">
                <div className="absolute inset-0 flex items-center justify-between text-xs text-slate-400">
                    <span>{timeRange.min.toLocaleDateString()}</span>
                    <span>Timeline Scale</span>
                    <span>{timeRange.max.toLocaleDateString()}</span>
                </div>
            </div>

            {/* Swimlanes */}
            <div className="space-y-3">
                {timelines.map((timeline, timelineIndex) => {
                    const timelineEvents = eventsByTimeline[timeline] || [];
                    const colorClass = getTimelineColor(timeline, timelineIndex);
                    
                    return (
                        <div key={timeline} className="relative">
                            {/* Timeline Label */}
                            <div className="flex items-center mb-2">
                                <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${colorClass} mr-3`} />
                                <span className="text-sm font-medium text-white min-w-[100px]">
                                    {timeline}
                                </span>
                                <span className="text-xs text-slate-400 ml-2">
                                    ({timelineEvents.length} events)
                                </span>
                            </div>

                            {/* Swimlane Track */}
                            <div className="relative h-12 bg-slate-800/50 rounded-lg border border-slate-700/30 ml-16">
                                {/* Timeline Base Line */}
                                <div className={`absolute top-1/2 left-2 right-2 h-0.5 bg-gradient-to-r ${colorClass} opacity-30`} />
                                
                                {/* Event Flags */}
                                {timelineEvents.map((event) => {
                                    const position = getEventPosition(event.date);
                                    const isSelected = selectedEvent?.id === event.id;
                                    
                                    return (
                                        <div
                                            key={event.id}
                                            onClick={() => onEventClick?.(event)}
                                            className="absolute top-1/2 transform -translate-y-1/2 cursor-pointer group"
                                            style={{ left: `${position}%` }}
                                        >
                                            {/* Event Flag */}
                                            <div className={`
                                                relative w-4 h-4 rounded-full border-2 border-white
                                                bg-gradient-to-r ${colorClass}
                                                transition-all duration-200 group-hover:scale-125
                                                ${isSelected ? 'scale-125 ring-2 ring-white/50' : ''}
                                                ${event.audio_file ? 'animate-pulse' : ''}
                                            `}>
                                                {/* Event Type Indicator */}
                                                <div className="absolute -top-1 -right-1 text-xs">
                                                    {event.audio_file ? '🎤' : '📋'}
                                                </div>
                                            </div>

                                            {/* Event Flag Pole */}
                                            <div className={`
                                                absolute top-4 left-1/2 transform -translate-x-1/2
                                                w-0.5 h-6 bg-gradient-to-b ${colorClass} opacity-60
                                            `} />

                                            {/* Hover Tooltip */}
                                            <div className={`
                                                absolute top-12 left-1/2 transform -translate-x-1/2
                                                bg-slate-800 border border-slate-600 rounded-lg p-2 text-xs
                                                opacity-0 group-hover:opacity-100 transition-opacity
                                                pointer-events-none z-10 min-w-48
                                            `}>
                                                <div className="font-medium text-white mb-1">{event.title}</div>
                                                <div className="text-slate-400 mb-1">
                                                    {new Date(event.date).toLocaleDateString()}
                                                </div>
                                                {event.description && (
                                                    <div className="text-slate-300 text-xs">
                                                        {event.description.substring(0, 100)}
                                                        {event.description.length > 100 ? '...' : ''}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Swimlanes Footer */}
            <div className="mt-4 pt-3 border-t border-slate-700/50 flex items-center justify-between text-xs text-slate-500">
                <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-500 to-blue-500" />
                        Event Flag
                    </span>
                    <span className="flex items-center gap-1">
                        🎤 Audio Event
                    </span>
                    <span className="flex items-center gap-1">
                        📋 Text Event  
                    </span>
                </div>
                <div>
                    Hover flags for details • Click to select
                </div>
            </div>
        </div>
    );
};

export default TimelineSwimLanes;