import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

/**
 * DraggableEyelidPanel - Revolutionary UI Component
 * 
 * The world's first implementation of "Draggable Eyelid Frames"
 * Coined by Tom & Claude on October 14, 2025
 * 
 * Features:
 * - Draggable anywhere on screen
 * - Eyelid scrolling (frozen header/footer)
 * - Persistent positioning
 * - Snap-to-edge behavior
 * - Smooth animations
 */

const DraggableEyelidPanel = ({ 
    children, 
    title, 
    icon = "📋",
    initialPosition = { x: 50, y: 50 },
    width = 400,
    height = 500,
    isFloating = false,
    onClose,
    className = ""
}) => {
    const [position, setPosition] = useState(initialPosition);
    const [isDragging, setIsDragging] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);

    // Save position to localStorage
    const savePosition = (newPosition) => {
        localStorage.setItem(`panel-${title}`, JSON.stringify(newPosition));
    };

    // Load position from localStorage
    useEffect(() => {
        const saved = localStorage.getItem(`panel-${title}`);
        if (saved) {
            try {
                setPosition(JSON.parse(saved));
            } catch (e) {
                console.error('Failed to load panel position:', e);
            }
        }
    }, [title]);

    // Snap to edges when close
    const snapToEdge = (newPosition) => {
        const snapDistance = 20;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        let snappedX = newPosition.x;
        let snappedY = newPosition.y;

        // Snap to left edge
        if (newPosition.x < snapDistance) {
            snappedX = 0;
        }
        // Snap to right edge
        else if (newPosition.x + width > windowWidth - snapDistance) {
            snappedX = windowWidth - width;
        }

        // Snap to top edge
        if (newPosition.y < snapDistance) {
            snappedY = 0;
        }
        // Snap to bottom edge
        else if (newPosition.y + height > windowHeight - snapDistance) {
            snappedY = windowHeight - height;
        }

        return { x: snappedX, y: snappedY };
    };

    const handleDragEnd = (event, info) => {
        setIsDragging(false);
        
        const newPosition = {
            x: position.x + info.offset.x,
            y: position.y + info.offset.y
        };

        const snappedPosition = snapToEdge(newPosition);
        setPosition(snappedPosition);
        savePosition(snappedPosition);
    };

    if (!isFloating) {
        // Regular embedded mode
        return (
            <div className={`bg-slate-800 rounded-lg shadow-lg ${className}`}>
                {children}
            </div>
        );
    }

    return (
        <motion.div
            drag
            dragMomentum={false}
            dragElastic={0.1}
            onDragStart={() => setIsDragging(true)}
            onDragEnd={handleDragEnd}
            initial={position}
            animate={position}
            style={{
                position: 'fixed',
                width: width,
                height: isMinimized ? 'auto' : height,
                zIndex: 1000,
                cursor: isDragging ? 'grabbing' : 'grab'
            }}
            className={`bg-slate-800/95 backdrop-blur-md rounded-lg shadow-2xl border border-slate-600 ${className}`}
            whileHover={{ scale: 1.02 }}
            whileDrag={{ scale: 1.05 }}
        >
            {/* Drag Handle Header - EYELID */}
            <div className="sticky top-0 z-10 bg-slate-700/95 backdrop-blur-sm rounded-t-lg px-4 py-3 flex items-center justify-between border-b border-slate-600">
                <div className="flex items-center gap-2">
                    <span className="text-lg">{icon}</span>
                    <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
                    <span className="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">
                        👁️ Draggable Eyelid
                    </span>
                </div>
                
                <div className="flex items-center gap-2">
                    {/* Minimize Button */}
                    <button
                        onClick={() => setIsMinimized(!isMinimized)}
                        className="w-6 h-6 rounded bg-slate-600 hover:bg-slate-500 flex items-center justify-center text-xs text-slate-300 transition-colors"
                        title={isMinimized ? "Expand" : "Minimize"}
                    >
                        {isMinimized ? "⬆" : "⬇"}
                    </button>
                    
                    {/* Close Button */}
                    {onClose && (
                        <button
                            onClick={onClose}
                            className="w-6 h-6 rounded bg-red-600 hover:bg-red-500 flex items-center justify-center text-xs text-white transition-colors"
                            title="Close"
                        >
                            ✕
                        </button>
                    )}
                    
                    {/* Drag Indicator */}
                    <div className="text-slate-400 cursor-grab active:cursor-grabbing">
                        ⋮⋮
                    </div>
                </div>
            </div>

            {/* Content Area - Scrollable when not minimized */}
            {!isMinimized && (
                <div className="flex-1 overflow-hidden flex flex-col" style={{ height: height - 60 }}>
                    <div className="flex-1 overflow-y-auto p-4">
                        {children}
                    </div>
                </div>
            )}

            {/* Floating Panel Glow Effect */}
            <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-500/10 to-blue-500/10 pointer-events-none" />
        </motion.div>
    );
};

export default DraggableEyelidPanel;