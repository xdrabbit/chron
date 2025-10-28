import React, { useRef, useState, useEffect } from 'react';

/**
 * AudioPlayer with Transcript Sync & Search Integration
 * 
 * Features:
 * - Play/pause/seek controls
 * - Playback speed control
 * - Word-level highlighting synchronized with audio
 * - Click on words to jump to that timestamp
 * - Search term highlighting in transcript
 * - Jump to search matches in audio
 */
export default function AudioPlayer({ 
    audioUrl, 
    transcription, 
    words = [],
    searchQuery = '',
    searchHighlights = ''
}) {
    const audioRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [playbackRate, setPlaybackRate] = useState(1.0);
    const [activeWordIndex, setActiveWordIndex] = useState(-1);
    const [searchMatches, setSearchMatches] = useState([]);

    // Update current time as audio plays
    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const updateTime = () => setCurrentTime(audio.currentTime);
        const updateDuration = () => setDuration(audio.duration);
        const handleEnded = () => setIsPlaying(false);

        audio.addEventListener('timeupdate', updateTime);
        audio.addEventListener('loadedmetadata', updateDuration);
        audio.addEventListener('ended', handleEnded);

        return () => {
            audio.removeEventListener('timeupdate', updateTime);
            audio.removeEventListener('loadedmetadata', updateDuration);
            audio.removeEventListener('ended', handleEnded);
        };
    }, []);

    // Find the active word based on current time
    useEffect(() => {
        if (!words || words.length === 0) return;

        // Find the word that contains the current time
        const activeIndex = words.findIndex((word, idx) => {
            // Word is active if currentTime is between its start and end
            return currentTime >= word.start && currentTime <= word.end;
        });

        setActiveWordIndex(activeIndex);
    }, [currentTime, words]);

    // Find search matches in word timestamps
    useEffect(() => {
        if (!searchQuery || !words || words.length === 0) {
            setSearchMatches([]);
            return;
        }

        const query = searchQuery.toLowerCase().trim();
        if (!query) {
            setSearchMatches([]);
            return;
        }

        // Find all words that match the search query
        const matches = words
            .map((word, index) => ({ ...word, index }))
            .filter(word => word.word.toLowerCase().includes(query));

        setSearchMatches(matches);
    }, [searchQuery, words]);

    // Debug: Log words on mount
    useEffect(() => {
        console.log('AudioPlayer received words:', words?.length || 0, 'words');
        if (words && words.length > 0) {
            console.log('First word:', words[0]);
            console.log('Last word:', words[words.length - 1]);
        }
    }, [words]);

    const togglePlay = () => {
        const audio = audioRef.current;
        if (isPlaying) {
            audio.pause();
        } else {
            audio.play();
        }
        setIsPlaying(!isPlaying);
    };

    const handleSeek = (e) => {
        const audio = audioRef.current;
        const newTime = parseFloat(e.target.value);
        audio.currentTime = newTime;
        setCurrentTime(newTime);
    };

    const handlePlaybackRate = (rate) => {
        const audio = audioRef.current;
        audio.playbackRate = rate;
        setPlaybackRate(rate);
    };

    const jumpToWord = (word) => {
        const audio = audioRef.current;
        audio.currentTime = word.start;
        setCurrentTime(word.start);
        if (!isPlaying) {
            audio.play();
            setIsPlaying(true);
        }
    };

    const formatTime = (seconds) => {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="bg-slate-800 rounded-lg p-4 space-y-4">
            {/* Audio element */}
            <audio ref={audioRef} src={audioUrl} preload="metadata" />

            {/* Controls */}
            <div className="flex items-center gap-4">
                {/* Play/Pause Button */}
                <button
                    onClick={togglePlay}
                    className="w-12 h-12 rounded-full bg-blue-600 hover:bg-blue-500 flex items-center justify-center text-white transition-colors"
                >
                    {isPlaying ? (
                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                        </svg>
                    ) : (
                        <svg className="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                        </svg>
                    )}
                </button>

                {/* Time Display */}
                <div className="text-sm text-slate-300 min-w-[100px]">
                    {formatTime(currentTime)} / {formatTime(duration)}
                </div>

                {/* Seek Bar */}
                <input
                    type="range"
                    min="0"
                    max={duration || 0}
                    value={currentTime}
                    onChange={handleSeek}
                    className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer
                             [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 
                             [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-blue-600 
                             [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer"
                />

                {/* Playback Speed */}
                <div className="flex gap-1">
                    {[0.5, 0.75, 1.0, 1.25, 1.5, 2.0].map((rate) => (
                        <button
                            key={rate}
                            onClick={() => handlePlaybackRate(rate)}
                            className={`px-2 py-1 text-xs rounded transition-colors ${
                                playbackRate === rate
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                            }`}
                        >
                            {rate}x
                        </button>
                    ))}
                </div>
            </div>

            {/* Search Match Navigation */}
            {searchMatches.length > 0 && (
                <div className="flex items-center gap-3 p-3 bg-orange-500/10 border border-orange-500/30 rounded">
                    <span className="text-orange-300 text-sm font-medium">
                        🔍 {searchMatches.length} match{searchMatches.length !== 1 ? 'es' : ''} found
                    </span>
                    <div className="flex gap-1">
                        {searchMatches.map((match, idx) => (
                            <button
                                key={idx}
                                onClick={() => jumpToWord(match)}
                                className="px-2 py-1 text-xs bg-orange-600 hover:bg-orange-500 text-white rounded transition-colors"
                                title={`Jump to "${match.word}" at ${formatTime(match.start)}`}
                            >
                                {idx + 1}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Transcript with Highlighting */}
            {words && words.length > 0 ? (
                <div className="max-h-96 overflow-y-auto bg-slate-900 rounded p-4">
                    <div className="text-slate-200 leading-relaxed">
                        {words.map((word, index) => {
                            const isActive = index === activeWordIndex;
                            const isSearchMatch = searchMatches.some(match => match.index === index);
                            
                            return (
                                <span
                                    key={index}
                                    onClick={() => jumpToWord(word)}
                                    className={`cursor-pointer transition-colors inline-block mx-0.5 px-1 rounded ${
                                        isActive
                                            ? 'bg-yellow-400 text-slate-900 font-semibold'
                                            : isSearchMatch
                                            ? 'bg-orange-500 text-white font-medium ring-2 ring-orange-300'
                                            : 'hover:bg-slate-700 hover:text-white'
                                    }`}
                                    title={`${formatTime(word.start)} - ${formatTime(word.end)}${isSearchMatch ? ' (Search Match)' : ''}`}
                                >
                                    {word.word}
                                </span>
                            );
                        })}
                    </div>
                </div>
            ) : (
                <div className="bg-slate-900 rounded p-4">
                    {searchHighlights ? (
                        <p 
                            className="text-slate-300 whitespace-pre-wrap"
                            dangerouslySetInnerHTML={{ __html: searchHighlights }}
                        />
                    ) : (
                        <p className="text-slate-300 whitespace-pre-wrap">{transcription}</p>
                    )}
                </div>
            )}

            {/* Help Text */}
            <div className="text-xs text-slate-400 space-y-1">
                <div>💡 <strong>Tip:</strong> Click on any word in the transcript to jump to that moment in the audio</div>
                {searchMatches.length > 0 && (
                    <div>🎯 <strong>Search:</strong> Orange highlighted words match your query - click numbered buttons to jump between matches</div>
                )}
            </div>
        </div>
    );
}
