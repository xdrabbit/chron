import React, { useState } from 'react';
import { VoiceTranscriber } from '../components/VoiceTranscriber';

export default function VoiceTranscription() {
  const [transcriptions, setTranscriptions] = useState([]);

  const handleTranscription = (text) => {
    const timestamp = new Date().toLocaleString();
    setTranscriptions(prev => [
      { id: Date.now(), text, timestamp },
      ...prev
    ]);
  };

  const clearTranscriptions = () => {
    setTranscriptions([]);
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">Voice Transcription</h1>
          <p className="text-slate-300">
            Record or upload audio to transcribe with Whisper AI
          </p>
        </div>

        <div className="space-y-6">
          {/* Voice Transcriber Component */}
          <VoiceTranscriber onTranscription={handleTranscription} />

          {/* Transcription History */}
          {transcriptions.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  Transcription History ({transcriptions.length})
                </h3>
                <button
                  onClick={clearTranscriptions}
                  className="text-sm text-red-600 hover:text-red-800 underline"
                >
                  Clear All
                </button>
              </div>

              <div className="space-y-4 max-h-96 overflow-y-auto">
                {transcriptions.map((item) => (
                  <div key={item.id} className="border-l-4 border-blue-400 pl-4 py-2">
                    <div className="text-xs text-gray-500 mb-1">
                      {item.timestamp}
                    </div>
                    <div className="text-gray-800 whitespace-pre-wrap">
                      {item.text}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Usage Instructions */}
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-3">How to Use</h3>
            <div className="space-y-2 text-slate-300 text-sm">
              <p>• <strong>Recording:</strong> Click "Start Recording" to capture audio from your microphone</p>
              <p>• <strong>File Upload:</strong> Use "Upload Audio" to transcribe existing audio files</p>
              <p>• <strong>Supported Formats:</strong> MP3, WAV, M4A, and most common audio formats</p>
              <p>• <strong>Processing:</strong> Transcription is powered by OpenAI Whisper AI</p>
              <p>• <strong>Timeline Integration:</strong> Transcriptions can be added to event descriptions</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}