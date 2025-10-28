import React from 'react';
import SearchPanel from './SearchPanel';
import DraggableEyelidPanel from './DraggableEyelidPanel';

/**
 * FloatingSearchPanel - Draggable Search Interface
 * 
 * FTS5 search as a floating panel - perfect for quick searches
 * while browsing timeline or working with other panels
 */

const FloatingSearchPanel = ({ onClose, isFloating = true }) => {
    return (
        <DraggableEyelidPanel
            title="Search Events"
            icon="🔍"
            width={400}
            height={300}
            isFloating={isFloating}
            onClose={onClose}
            initialPosition={{ x: window.innerWidth - 450, y: 200 }} // Start in top-right
            className="shadow-green-500/20"
        >
            <SearchPanel isFloating={true} />
        </DraggableEyelidPanel>
    );
};

export default FloatingSearchPanel;