import React, { useEffect, useRef, useState, useImperativeHandle, forwardRef } from 'react';
import { Timeline } from 'vis-timeline/standalone';
import { DataSet } from 'vis-data';
import 'vis-timeline/styles/vis-timeline-graph2d.min.css';
import './VisualTimeline.css';

const VisualTimeline = forwardRef(({ events, onEventClick, currentTimeline }, ref) => {
    const timelineRef = useRef(null);
    const timelineInstance = useRef(null);
    const [zoomLevel, setZoomLevel] = useState('1month');

    useEffect(() => {
        if (!timelineRef.current || events.length === 0) return;

        // Convert events to vis-timeline format
        const items = new DataSet(
            events.map(event => ({
                id: event.id,
                content: event.title,
                start: new Date(event.date),
                group: event.timeline,
                title: event.description || event.title, // Tooltip
                className: 'timeline-event',
                type: 'point'
            }))
        );

        // Create groups for different timelines
        const uniqueTimelines = [...new Set(events.map(e => e.timeline))];
        const groups = new DataSet(
            uniqueTimelines.map(timeline => ({
                id: timeline,
                content: timeline,
                className: `timeline-group-${timeline.toLowerCase().replace(/\s+/g, '-')}`
            }))
        );

        // Timeline options
        const options = {
            height: '300px',
            margin: {
                item: 10,
                axis: 5
            },
            orientation: 'top',
            zoomable: true,
            zoomMin: 1000 * 60 * 60 * 24, // 1 day
            zoomMax: 1000 * 60 * 60 * 24 * 365 * 10, // 10 years
            moveable: true,
            stack: false,
            showCurrentTime: true,
            format: {
                minorLabels: {
                    minute: 'HH:mm',
                    hour: 'HH:mm',
                    weekday: 'ddd D',
                    day: 'D',
                    week: 'w',
                    month: 'MMM',
                    year: 'YYYY'
                },
                majorLabels: {
                    minute: 'ddd D MMMM',
                    hour: 'ddd D MMMM',
                    weekday: 'MMMM YYYY',
                    day: 'MMMM YYYY',
                    week: 'MMMM YYYY',
                    month: 'YYYY',
                    year: ''
                }
            },
            tooltip: {
                followMouse: true,
                overflowMethod: 'cap'
            }
        };

        // Create or update timeline
        if (timelineInstance.current) {
            timelineInstance.current.setItems(items);
            timelineInstance.current.setGroups(groups);
        } else {
            timelineInstance.current = new Timeline(
                timelineRef.current,
                items,
                groups,
                options
            );

            // Event click handler
            timelineInstance.current.on('select', (properties) => {
                if (properties.items.length > 0 && onEventClick) {
                    const eventId = properties.items[0];
                    const event = events.find(e => e.id === eventId);
                    if (event) {
                        onEventClick(event);
                    }
                }
            });
        }

        // Fit to show all events
        timelineInstance.current.fit();

        return () => {
            if (timelineInstance.current) {
                timelineInstance.current.destroy();
                timelineInstance.current = null;
            }
        };
    }, [events, onEventClick]);

    // Expose methods to parent component
    useImperativeHandle(ref, () => ({
        focusOnEvent: (eventId) => {
            if (!timelineInstance.current) return;
            
            // Select the event
            timelineInstance.current.setSelection(eventId);
            
            // Get the event to find its date
            const event = events.find(e => e.id === eventId);
            if (event) {
                const eventDate = new Date(event.date);
                // Focus on the event with some padding (show ±2 weeks around it)
                const start = new Date(eventDate.getTime() - 14 * 24 * 60 * 60 * 1000);
                const end = new Date(eventDate.getTime() + 14 * 24 * 60 * 60 * 1000);
                timelineInstance.current.setWindow(start, end, { animation: { duration: 500, easingFunction: 'easeInOutQuad' } });
            }
        }
    }));

    const handleZoom = (level) => {
        if (!timelineInstance.current) return;
        
        setZoomLevel(level);
        const now = new Date();
        let range;

        switch (level) {
            case '1week':
                range = { start: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000), end: now };
                break;
            case '1month':
                range = { start: new Date(now.getFullYear(), now.getMonth() - 1, now.getDate()), end: now };
                break;
            case '3months':
                range = { start: new Date(now.getFullYear(), now.getMonth() - 3, now.getDate()), end: now };
                break;
            case '1year':
                range = { start: new Date(now.getFullYear() - 1, now.getMonth(), now.getDate()), end: now };
                break;
            case 'all':
                timelineInstance.current.fit();
                return;
            default:
                return;
        }

        timelineInstance.current.setWindow(range.start, range.end, { animation: true });
    };

    const handleToday = () => {
        if (!timelineInstance.current) return;
        const now = new Date();
        timelineInstance.current.moveTo(now, { animation: true });
    };

    return (
        <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden flex flex-col max-h-[500px]">
            {/* Timeline Controls - EYELID (Frozen Header) */}
            <div className="sticky top-0 z-10 bg-slate-700 px-4 py-3 flex items-center justify-between border-b border-slate-600">
                <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-slate-200">Timeline Visualization</h3>
                    <span className="text-xs text-slate-400">
                        ({events.length} event{events.length !== 1 ? 's' : ''})
                    </span>
                    <span className="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">👁️ Eyelid</span>
                </div>

                <div className="flex items-center gap-2">
                    {/* Zoom Controls */}
                    <div className="flex gap-1 bg-slate-800 rounded p-1">
                        <button
                            onClick={() => handleZoom('1week')}
                            className={`px-2 py-1 text-xs rounded transition-colors ${
                                zoomLevel === '1week'
                                    ? 'bg-blue-600 text-white'
                                    : 'text-slate-300 hover:bg-slate-700'
                            }`}
                        >
                            1W
                        </button>
                        <button
                            onClick={() => handleZoom('1month')}
                            className={`px-2 py-1 text-xs rounded transition-colors ${
                                zoomLevel === '1month'
                                    ? 'bg-blue-600 text-white'
                                    : 'text-slate-300 hover:bg-slate-700'
                            }`}
                        >
                            1M
                        </button>
                        <button
                            onClick={() => handleZoom('3months')}
                            className={`px-2 py-1 text-xs rounded transition-colors ${
                                zoomLevel === '3months'
                                    ? 'bg-blue-600 text-white'
                                    : 'text-slate-300 hover:bg-slate-700'
                            }`}
                        >
                            3M
                        </button>
                        <button
                            onClick={() => handleZoom('1year')}
                            className={`px-2 py-1 text-xs rounded transition-colors ${
                                zoomLevel === '1year'
                                    ? 'bg-blue-600 text-white'
                                    : 'text-slate-300 hover:bg-slate-700'
                            }`}
                        >
                            1Y
                        </button>
                        <button
                            onClick={() => handleZoom('all')}
                            className={`px-2 py-1 text-xs rounded transition-colors ${
                                zoomLevel === 'all'
                                    ? 'bg-blue-600 text-white'
                                    : 'text-slate-300 hover:bg-slate-700'
                            }`}
                        >
                            All
                        </button>
                    </div>

                    {/* Today Button */}
                    <button
                        onClick={handleToday}
                        className="px-3 py-1 text-xs bg-green-600 hover:bg-green-500 text-white rounded transition-colors"
                    >
                        Today
                    </button>
                </div>
            </div>

            {/* Timeline Container - Scrollable Content */}
            <div className="flex-1 overflow-y-auto">
                {events.length === 0 ? (
                    <div className="h-[300px] flex items-center justify-center text-slate-400">
                        <p>No events to display. Add your first event to see the timeline!</p>
                    </div>
                ) : (
                    <div ref={timelineRef} className="vis-timeline-custom" />
                )}
            </div>

            {/* Timeline Help - EYELID (Frozen Footer) */}
            <div className="sticky bottom-0 bg-slate-700 px-4 py-2 text-xs text-slate-400 border-t border-slate-600">
                💡 <strong>Tip:</strong> Scroll to zoom, drag to pan, click events for details
            </div>
        </div>
    );
});

VisualTimeline.displayName = 'VisualTimeline';

export default VisualTimeline;
