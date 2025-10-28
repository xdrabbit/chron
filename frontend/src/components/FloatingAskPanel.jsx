import React from 'react';
import AskPanel from './AskPanel';
import DraggableEyelidPanel from './DraggableEyelidPanel';

/**
 * FloatingAskPanel - AI Chat as a Draggable Eyelid Frame
 * 
 * Revolutionary floating AI interface that can be positioned anywhere on screen
 * while maintaining the Eyelid scrolling pattern for optimal UX.
 */

const FloatingAskPanel = ({ currentTimeline, onClose, isFloating = true }) => {
    return (
        <DraggableEyelidPanel
            title="Ask Your Timeline"
            icon="💬"
            width={450}
            height={600}
            isFloating={isFloating}
            onClose={onClose}
            initialPosition={{ x: window.innerWidth - 500, y: 100 }} // Start in top-right
            className="shadow-purple-500/20"
        >
            <AskPanel currentTimeline={currentTimeline} isFloating={true} />
        </DraggableEyelidPanel>
    );
};

export default FloatingAskPanel;