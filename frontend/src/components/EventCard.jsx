import React, { useState } from 'react';
import AudioPlayer from './AudioPlayer';

const EventCard = ({ event }) => {
    const [showAudio, setShowAudio] = useState(false);
    
    // Color mapping for different actors (IMPROVED CONTRAST)
    const getActorStyle = (actor) => {
        const styles = {
            'Tom': 'bg-blue-500/40 text-blue-200 border-blue-500/50',
            'Lisa': 'bg-purple-500/40 text-purple-200 border-purple-500/50', 
            'Realtor': 'bg-green-500/40 text-green-200 border-green-500/50',
            'Jeff': 'bg-green-500/40 text-green-200 border-green-500/50',
            'Court': 'bg-red-500/40 text-red-200 border-red-500/50',
            'Bank': 'bg-yellow-500/40 text-yellow-200 border-yellow-500/50',
            'Attorney': 'bg-indigo-500/40 text-indigo-200 border-indigo-500/50',
            'Brody': 'bg-indigo-500/40 text-indigo-200 border-indigo-500/50',
        };
        return styles[actor] || 'bg-gray-500/40 text-gray-200 border-gray-500/50';
    };

    // Handle evidence link clicks
    const handleEvidenceClick = (evidenceLinks) => {
        if (!evidenceLinks) return;
        
        // Split multiple links by comma or semicolon
        const links = evidenceLinks.split(/[,;]/).map(link => link.trim());
        
        links.forEach(link => {
            if (link.startsWith('http://') || link.startsWith('https://')) {
                // External URL
                window.open(link, '_blank', 'noopener,noreferrer');
            } else {
                // Local file path - could be enhanced to serve from backend
                console.log('Local evidence file:', link);
                alert(`Evidence file: ${link}\n\nNote: Local file access would require backend file serving.`);
            }
        });
    };

    // Get audio URL for playback
    const getAudioUrl = (audioFile) => {
        if (!audioFile) return null;
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        // Remove the 'backend/' prefix if present
        const cleanPath = audioFile.replace(/^backend\//, '');
        return `${baseUrl}/${cleanPath}`;
    };

    // Parse word timestamps
    const getWordTimestamps = () => {
        if (!event.transcription_words) return [];
        try {
            return JSON.parse(event.transcription_words);
        } catch {
            return [];
        }
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
            
            {/* Show description only if no audio, or if audio player is collapsed */}
            {(!event.audio_file || !showAudio) && (
                <p className="text-slate-300 mb-3 whitespace-pre-wrap">{event.description}</p>
            )}
            
            {/* Audio Player */}
            {event.audio_file && showAudio && (
                <div className="mb-4">
                    <AudioPlayer
                        audioUrl={getAudioUrl(event.audio_file)}
                        transcription={event.description}
                        words={getWordTimestamps()}
                    />
                </div>
            )}
            
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
                    <button
                        onClick={() => handleEvidenceClick(event.evidence_links)}
                        className="bg-emerald-900/30 text-emerald-300 px-2 py-1 rounded hover:bg-emerald-800/40 transition-colors cursor-pointer"
                        title={`Open evidence: ${event.evidence_links}`}
                    >
                        📎 Evidence
                    </button>
                )}
                {event.audio_file && (
                    <button
                        onClick={() => setShowAudio(!showAudio)}
                        className="bg-purple-900/30 text-purple-300 px-2 py-1 rounded hover:bg-purple-800/40 transition-colors cursor-pointer"
                    >
                        🎤 {showAudio ? 'Hide' : 'Show'} Audio
                    </button>
                )}
            </div>
        </div>
    );
};

export default EventCard;
