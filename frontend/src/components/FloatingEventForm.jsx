import React from 'react';
import EventForm from './EventForm';
import DraggableEyelidPanel from './DraggableEyelidPanel';

/**
 * FloatingEventForm - Draggable Event Creation Panel
 * 
 * Create events in a floating form that doesn't interrupt your workflow
 * Perfect for quickly adding events while reviewing timeline
 */

const FloatingEventForm = ({ 
    onSubmit, 
    editing = null, 
    timelines = [], 
    onClose, 
    isFloating = true 
}) => {
    return (
        <DraggableEyelidPanel
            title={editing ? "Edit Event" : "Add New Event"}
            icon="✏️"
            width={500}
            height={600}
            isFloating={isFloating}
            onClose={onClose}
            initialPosition={{ x: (window.innerWidth - 500) / 2, y: 50 }} // Start in center
            className="shadow-orange-500/20"
        >
            <EventForm 
                onSubmit={onSubmit}
                editing={editing}
                timelines={timelines}
                isFloating={true}
            />
        </DraggableEyelidPanel>
    );
};

export default FloatingEventForm;