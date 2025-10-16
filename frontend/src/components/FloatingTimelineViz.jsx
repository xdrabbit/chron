import React from 'react';
import VisualTimeline from './VisualTimeline';
import DraggableEyelidPanel from './DraggableEyelidPanel';

/**
 * FloatingTimelineViz - Draggable Timeline Visualization
 * 
 * The timeline calendar as a floating, draggable panel
 * Perfect for multi-screen setups or side-by-side analysis
 */

const FloatingTimelineViz = ({ events, onEventClick, currentTimeline, onClose, isFloating = true }) => {
    return (
        <DraggableEyelidPanel
            title="Timeline Visualization"
            icon="📅"
            width={700}
            height={450}
            isFloating={isFloating}
            onClose={onClose}
            initialPosition={{ x: 50, y: 100 }} // Start in top-left
            className="shadow-blue-500/20"
        >
            <div className="h-full">
                <VisualTimeline 
                    events={events}
                    onEventClick={onEventClick}
                    currentTimeline={currentTimeline}
                />
            </div>
        </DraggableEyelidPanel>
    );
};

export default FloatingTimelineViz;