import React, { useState, useRef } from 'react';

export function VoiceTranscriber({ onTranscription }) {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [audioFile, setAudioFile] = useState(null);
    const [transcription, setTranscription] = useState('');
    const [error, setError] = useState('');
    
    const mediaRecorder = useRef(null);
    const audioChunks = useRef([]);
    const fileInputRef = useRef(null);

    // Start recording
    const startRecording = async () => {
        try {
            // Check if browser supports getUserMedia
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                setError('Your browser does not support microphone access. Please use a modern browser like Chrome, Firefox, or Safari.');
                return;
            }

            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                } 
            });
            
            mediaRecorder.current = new MediaRecorder(stream);
            audioChunks.current = [];
            
            mediaRecorder.current.ondataavailable = (event) => {
                audioChunks.current.push(event.data);
            };
            
            mediaRecorder.current.onstop = () => {
                const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
                setAudioFile(audioBlob);
            };
            
            mediaRecorder.current.start();
            setIsRecording(true);
            setError('');
        } catch (err) {
            console.error('Microphone access error:', err);
            if (err.name === 'NotAllowedError') {
                setError('Microphone access denied. Please allow microphone access in your browser settings and try again.');
            } else if (err.name === 'NotFoundError') {
                setError('No microphone found. Please connect a microphone and try again.');
            } else if (err.name === 'NotSupportedError') {
                setError('Your browser does not support audio recording. Please try a different browser.');
            } else {
                setError('Failed to access microphone: ' + err.message);
            }
        }
    };

    // Stop recording
    const stopRecording = () => {
        if (mediaRecorder.current && isRecording) {
            mediaRecorder.current.stop();
            mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
            setIsRecording(false);
        }
    };

    // Handle file upload
    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            setAudioFile(file);
            setError('');
        }
    };

    // Submit for transcription
    const transcribeAudio = async () => {
        if (!audioFile) {
            setError('No audio file to transcribe');
            return;
        }

        setIsProcessing(true);
        setError('');
        setTranscription('');

        try {
            const formData = new FormData();
            formData.append('audio_file', audioFile, 'audio.wav');

            console.log('Sending audio for transcription...', audioFile.size, 'bytes');

            const response = await fetch('http://192.168.0.15:8000/transcribe/', {
                method: 'POST',
                body: formData,
            });

            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Error response:', errorText);
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            console.log('Transcription result:', data);

            if (data.transcription) {
                setTranscription(data.transcription);
                if (onTranscription) {
                    onTranscription(data.transcription);
                }
            } else {
                setError('No transcription text received');
            }
        } catch (err) {
            console.error('Transcription error:', err);
            setError('Transcription failed: ' + err.message);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md border">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Voice Transcription</h3>
            
            {/* Recording Controls */}
            <div className="space-y-4">
                <div className="flex space-x-3">
                    {!isRecording ? (
                        <button
                            onClick={startRecording}
                            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md font-medium transition-colors"
                            disabled={isProcessing}
                        >
                            🎤 Start Recording
                        </button>
                    ) : (
                        <button
                            onClick={stopRecording}
                            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md font-medium transition-colors animate-pulse"
                        >
                            ⏹️ Stop Recording
                        </button>
                    )}
                    
                    <span className="text-sm text-gray-600 self-center">or</span>
                    
                    <label className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md font-medium cursor-pointer transition-colors">
                        📁 Upload Audio
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="audio/*"
                            onChange={handleFileUpload}
                            className="hidden"
                            disabled={isProcessing}
                        />
                    </label>
                </div>

                {/* Audio file status */}
                {audioFile && (
                    <div className="bg-gray-50 p-3 rounded border">
                        <p className="text-sm text-gray-700">
                            Audio ready: {audioFile.name || 'Recorded audio'} 
                            ({audioFile.size ? Math.round(audioFile.size / 1024) + 'KB' : 'Unknown size'})
                        </p>
                        
                        <button
                            onClick={transcribeAudio}
                            disabled={isProcessing}
                            className="mt-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium transition-colors"
                        >
                            {isProcessing ? '🔄 Transcribing...' : '📝 Transcribe Audio'}
                        </button>
                    </div>
                )}

                {/* Status messages */}
                {isRecording && (
                    <div className="bg-red-50 border border-red-200 p-3 rounded">
                        <p className="text-red-700 text-sm">🔴 Recording in progress...</p>
                    </div>
                )}

                {isProcessing && (
                    <div className="bg-yellow-50 border border-yellow-200 p-3 rounded">
                        <p className="text-yellow-700 text-sm">⏳ Processing audio with Whisper...</p>
                    </div>
                )}

                {error && (
                    <div className="bg-red-50 border border-red-200 p-3 rounded">
                        <p className="text-red-700 text-sm">❌ {error}</p>
                        {error.includes('denied') && (
                            <div className="mt-2 text-xs text-red-600">
                                <p><strong>To fix this:</strong></p>
                                <ul className="list-disc list-inside mt-1">
                                    <li>Click the microphone icon in your browser's address bar</li>
                                    <li>Or go to Site Settings and allow microphone access</li>
                                    <li>Refresh the page and try again</li>
                                </ul>
                            </div>
                        )}
                    </div>
                )}

                {/* Browser compatibility notice */}
                <div className="bg-blue-50 border border-blue-200 p-3 rounded text-xs text-blue-700">
                    <p><strong>💡 Tip:</strong> Microphone recording works best in Chrome, Firefox, and Safari. Make sure to allow microphone access when prompted.</p>
                </div>

                {/* Transcription result */}
                {transcription && (
                    <div className="bg-green-50 border border-green-200 p-4 rounded">
                        <h4 className="font-medium text-green-800 mb-2">Transcription:</h4>
                        <p className="text-green-700 whitespace-pre-wrap">{transcription}</p>
                        
                        <button
                            onClick={() => {
                                setTranscription('');
                                setAudioFile(null);
                                if (fileInputRef.current) fileInputRef.current.value = '';
                            }}
                            className="mt-3 text-sm text-green-600 hover:text-green-800 underline"
                        >
                            Clear and try again
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}