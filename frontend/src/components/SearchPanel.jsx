import React, { useState } from 'react';
import AudioPlayer from './AudioPlayer';

/**
 * SearchPanel - Full-text search with FTS5
 * 
 * Features:
 * - Real-time search with debouncing
 * - AND/OR/NOT operator support
 * - Phrase search with quotes
 * - Search result highlighting
 * - Audio playback for results with audio files
 * - Click to jump to event in timeline
 */
export default function SearchPanel({ onEventSelect }) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [showHelp, setShowHelp] = useState(false);
    const [expandedResult, setExpandedResult] = useState(null);

    const performSearch = async (searchQuery) => {
        if (!searchQuery.trim()) {
            setResults([]);
            return;
        }

        setIsSearching(true);
        try {
            const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${baseUrl}/search?q=${encodeURIComponent(searchQuery)}`);
            
            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data = await response.json();
            setResults(data);
        } catch (error) {
            console.error('Search error:', error);
            setResults([]);
        } finally {
            setIsSearching(false);
        }
    };

    // Debounce search
    const handleSearchChange = (e) => {
        const newQuery = e.target.value;
        setQuery(newQuery);

        // Simple debounce - wait 500ms after typing stops
        clearTimeout(window.searchTimeout);
        window.searchTimeout = setTimeout(() => {
            performSearch(newQuery);
        }, 500);
    };

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        clearTimeout(window.searchTimeout);
        performSearch(query);
    };

    const toggleExpanded = (resultId) => {
        setExpandedResult(expandedResult === resultId ? null : resultId);
    };

    const getAudioUrl = (audioFile) => {
        if (!audioFile) return null;
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        // Remove the 'backend/' prefix if present
        const cleanPath = audioFile.replace(/^backend\//, '');
        return `${baseUrl}/${cleanPath}`;
    };

    return (
        <div className="bg-slate-800 rounded-lg shadow-lg p-6 space-y-4">
            {/* Search Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
                    🔍 Search Events
                </h2>
                <button
                    onClick={() => setShowHelp(!showHelp)}
                    className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                >
                    {showHelp ? 'Hide' : 'Show'} Help
                </button>
            </div>

            {/* Search Help */}
            {showHelp && (
                <div className="bg-slate-900 rounded-lg p-4 text-sm space-y-2">
                    <p className="text-slate-300 font-semibold">Search Syntax:</p>
                    <ul className="text-slate-400 space-y-1 ml-4">
                        <li><code className="bg-slate-800 px-2 py-0.5 rounded">"town council"</code> - Exact phrase</li>
                        <li><code className="bg-slate-800 px-2 py-0.5 rounded">ordinance AND 2020</code> - Both terms must appear</li>
                        <li><code className="bg-slate-800 px-2 py-0.5 rounded">meeting OR hearing</code> - Either term</li>
                        <li><code className="bg-slate-800 px-2 py-0.5 rounded">daniel NOT subdivision</code> - Exclude subdivision</li>
                        <li><code className="bg-slate-800 px-2 py-0.5 rounded">ordinance*</code> - Prefix search (matches ordinance, ordinances, etc.)</li>
                    </ul>
                </div>
            )}

            {/* Search Bar */}
            <form onSubmit={handleSearchSubmit} className="relative">
                <input
                    type="text"
                    value={query}
                    onChange={handleSearchChange}
                    placeholder="Search events, transcriptions, tags..."
                    className="w-full px-4 py-3 pr-24 bg-slate-900 text-slate-100 rounded-lg border border-slate-700 
                             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                    {/* Help Icon */}
                    <button
                        type="button"
                        onClick={() => setShowHelp(!showHelp)}
                        className="p-2 text-slate-400 hover:text-blue-400 transition-colors group"
                        title="Search help"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </button>
                    
                    {/* Search Button */}
                    <button
                        type="submit"
                        disabled={isSearching}
                        className="p-2 text-slate-400 hover:text-slate-200 transition-colors"
                    >
                        {isSearching ? (
                            <div className="w-5 h-5 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
                        ) : (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        )}
                    </button>
                </div>
            </form>

            {/* Results Count */}
            {query && (
                <div className="text-sm text-slate-400">
                    {isSearching ? (
                        'Searching...'
                    ) : (
                        <>Found {results.length} result{results.length !== 1 ? 's' : ''}</>
                    )}
                </div>
            )}

            {/* Search Results */}
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {results.map((result) => (
                    <div
                        key={result.event.id}
                        className="bg-slate-900 rounded-lg border border-slate-700 overflow-hidden transition-all hover:border-slate-600"
                    >
                        {/* Result Header */}
                        <div 
                            className="p-4 cursor-pointer"
                            onClick={() => toggleExpanded(result.event.id)}
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1 min-w-0">
                                    {/* Title with highlight */}
                                    <h3 
                                        className="text-lg font-semibold text-slate-100 mb-1"
                                        dangerouslySetInnerHTML={{ __html: result.title_snippet || result.event.title }}
                                    />
                                    
                                    {/* Meta info */}
                                    <div className="flex items-center gap-3 text-xs text-slate-400 mb-2">
                                        <span>📅 {new Date(result.event.date).toLocaleDateString()}</span>
                                        <span>📂 {result.event.timeline}</span>
                                        {result.has_audio && (
                                            <span className="flex items-center gap-1 text-blue-400">
                                                🎤 Audio
                                            </span>
                                        )}
                                    </div>

                                    {/* Smart Summary or Description snippet */}
                                    {result.event.summary ? (
                                        <div className="text-sm space-y-2">
                                            <p className="text-slate-300">
                                                {JSON.parse(result.event.summary).snippet}
                                            </p>
                                            <div className="flex flex-wrap gap-2">
                                                {JSON.parse(result.event.summary).topics.map((topic, idx) => (
                                                    <span 
                                                        key={idx}
                                                        className="px-2 py-0.5 bg-blue-600/20 text-blue-300 rounded text-xs border border-blue-600/30"
                                                    >
                                                        {topic}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (
                                        <div 
                                            className="text-sm text-slate-300 line-clamp-2"
                                            dangerouslySetInnerHTML={{ __html: result.description_snippet || result.event.description }}
                                        />
                                    )}
                                </div>

                                {/* Expand indicator */}
                                <button className="text-slate-400 hover:text-slate-200 transition-colors">
                                    <svg 
                                        className={`w-5 h-5 transition-transform ${expandedResult === result.event.id ? 'rotate-180' : ''}`}
                                        fill="none" 
                                        stroke="currentColor" 
                                        viewBox="0 0 24 24"
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        {/* Expanded Content */}
                        {expandedResult === result.event.id && (
                            <div className="border-t border-slate-700 p-4 space-y-4">
                                {/* Enhanced Audio Player with Search Highlighting */}
                                {result.has_audio && result.event.audio_file ? (
                                    <AudioPlayer
                                        audioUrl={getAudioUrl(result.event.audio_file)}
                                        transcription={result.event.description}
                                        words={result.word_timestamps || []}
                                        searchQuery={query}
                                        searchHighlights={result.description_snippet}
                                    />
                                ) : (
                                    /* Full Description (only for non-audio events) */
                                    <div className="text-sm text-slate-300 whitespace-pre-wrap">
                                        {result.event.description}
                                    </div>
                                )}

                                {/* Tags */}
                                {result.event.tags && (
                                    <div className="flex flex-wrap gap-2">
                                        {result.event.tags.split(',').map((tag, idx) => (
                                            <span 
                                                key={idx}
                                                className="px-2 py-1 bg-slate-800 text-slate-300 rounded text-xs"
                                            >
                                                {tag.trim()}
                                            </span>
                                        ))}
                                    </div>
                                )}

                                {/* Actions */}
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => onEventSelect && onEventSelect(result.event)}
                                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded transition-colors text-sm"
                                    >
                                        View in Timeline
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {/* Empty State */}
                {!isSearching && query && results.length === 0 && (
                    <div className="text-center py-12 text-slate-400">
                        <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <p className="text-lg mb-2">No results found</p>
                        <p className="text-sm">Try adjusting your search terms or using different operators</p>
                    </div>
                )}
            </div>

            {/* Custom styling for search highlights */}
            <style jsx>{`
                :global(mark) {
                    background-color: rgb(251, 191, 36);
                    color: rgb(15, 23, 42);
                    padding: 0 0.25rem;
                    border-radius: 0.25rem;
                    font-weight: 600;
                }
            `}</style>
        </div>
    );
}
