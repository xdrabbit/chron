import React from 'react';

const EventCard = ({ event }) => {
    // Color mapping for different actors (dark theme compatible)
    const getActorStyle = (actor) => {
        const styles = {
            'Tom': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
            'Lisa': 'bg-purple-500/20 text-purple-300 border-purple-500/30', 
            'Realtor': 'bg-green-500/20 text-green-300 border-green-500/30',
            'Jeff': 'bg-green-500/20 text-green-300 border-green-500/30',
            'Court': 'bg-red-500/20 text-red-300 border-red-500/30',
            'Bank': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
            'Attorney': 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
            'Brody': 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
        };
        return styles[actor] || 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    };

    return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 mb-4 hover:bg-slate-750 transition-colors">
            <div className="flex items-start justify-between mb-2">
                <h3 className="font-bold text-white text-lg">{event.title}</h3>
                {event.actor && (
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getActorStyle(event.actor)}`}>
                        {event.actor}
                    </span>
                )}
            </div>
            
            <div className="flex items-center gap-2 mb-2 text-sm text-slate-400">
                <span>📅 {new Date(event.date).toLocaleDateString()}</span>
                <span>⏰ {new Date(event.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                {event.timeline && event.timeline !== 'Default' && (
                    <span className="bg-slate-700 px-2 py-0.5 rounded text-xs">
                        {event.timeline}
                    </span>
                )}
            </div>
            
            <p className="text-slate-300 mb-3">{event.description}</p>
            
            {/* Additional metadata */}
            <div className="flex flex-wrap gap-2 text-xs">
                {event.emotion && (
                    <span className="bg-amber-900/30 text-amber-300 px-2 py-1 rounded">
                        😊 {event.emotion}
                    </span>
                )}
                {event.tags && (
                    <span className="bg-slate-700 text-slate-300 px-2 py-1 rounded">
                        🏷️ {event.tags}
                    </span>
                )}
                {event.evidence_links && (
                    <span className="bg-emerald-900/30 text-emerald-300 px-2 py-1 rounded">
                        📎 Evidence
                    </span>
                )}
                {event.audio_file && (
                    <span className="bg-purple-900/30 text-purple-300 px-2 py-1 rounded">
                        🎤 Audio
                    </span>
                )}
            </div>
        </div>
    );
};

export default EventCard;
