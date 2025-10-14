import React, { useRef, useState, useEffect } from 'react';

/**
 * AudioPlayer with Transcript Sync
 * 
 * Features:
 * - Play/pause/seek controls
 * - Playback speed control
 * - Word-level highlighting synchronized with audio
 * - Click on words to jump to that timestamp
 */
export default function AudioPlayer({ audioUrl, transcription, words = [] }) {
    const audioRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [playbackRate, setPlaybackRate] = useState(1.0);
    const [activeWordIndex, setActiveWordIndex] = useState(-1);

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

        const activeIndex = words.findIndex((word, idx) => {
            const nextWord = words[idx + 1];
            return currentTime >= word.start && (!nextWord || currentTime < nextWord.start);
        });

        setActiveWordIndex(activeIndex);
    }, [currentTime, words]);

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

            {/* Transcript with Highlighting */}
            {words && words.length > 0 ? (
                <div className="max-h-96 overflow-y-auto bg-slate-900 rounded p-4">
                    <div className="text-slate-200 leading-relaxed">
                        {words.map((word, index) => (
                            <span
                                key={index}
                                onClick={() => jumpToWord(word)}
                                className={`cursor-pointer transition-colors inline-block mx-0.5 ${
                                    index === activeWordIndex
                                        ? 'bg-yellow-400 text-slate-900 font-semibold px-1 rounded'
                                        : 'hover:bg-slate-700 hover:text-white'
                                }`}
                                title={`${formatTime(word.start)} - ${formatTime(word.end)}`}
                            >
                                {word.word}
                            </span>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="bg-slate-900 rounded p-4">
                    <p className="text-slate-300 whitespace-pre-wrap">{transcription}</p>
                </div>
            )}

            {/* Help Text */}
            <div className="text-xs text-slate-400">
                💡 <strong>Tip:</strong> Click on any word in the transcript to jump to that moment in the audio
            </div>
        </div>
    );
}
