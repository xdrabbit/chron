import React, { useState, useRef } from 'react';

/**
 * SmartCSVImport - AI-Generated CSV Paste Interface
 * 
 * Allows users to paste AI-generated CSV data directly into Chronicle
 * Handles both raw CSV and formatted text from ChatGPT/Claude
 */
export default function SmartCSVImport({ onImport, onClose }) {
    const [csvData, setCsvData] = useState('');
    const [parsedEvents, setParsedEvents] = useState([]);
    const [showPreview, setShowPreview] = useState(false);
    const [isImporting, setIsImporting] = useState(false);
    const [error, setError] = useState('');
    const textareaRef = useRef(null);

    const parseCSVData = (rawData) => {
        try {
            // Clean up the data - remove code block markers, extra whitespace
            let cleanData = rawData
                .replace(/```csv/g, '')
                .replace(/```/g, '')
                .replace(/^\s+|\s+$/gm, '') // trim each line
                .trim();

            // Split into lines
            const lines = cleanData.split('\n').filter(line => line.trim());
            
            if (lines.length === 0) {
                throw new Error('No data found');
            }

            // Get headers
            const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
            
            // Validate required headers
            const requiredHeaders = ['title', 'description', 'date'];
            const missingHeaders = requiredHeaders.filter(h => !headers.includes(h));
            
            if (missingHeaders.length > 0) {
                throw new Error(`Missing required headers: ${missingHeaders.join(', ')}`);
            }

            // Parse data rows
            const events = [];
            for (let i = 1; i < lines.length; i++) {
                const row = lines[i];
                if (!row.trim()) continue;

                // Simple CSV parsing (handles quoted fields)
                const values = [];
                let current = '';
                let inQuotes = false;
                
                for (let j = 0; j < row.length; j++) {
                    const char = row[j];
                    if (char === '"') {
                        inQuotes = !inQuotes;
                    } else if (char === ',' && !inQuotes) {
                        values.push(current.trim().replace(/^"|"$/g, ''));
                        current = '';
                    } else {
                        current += char;
                    }
                }
                values.push(current.trim().replace(/^"|"$/g, '')); // Add the last value

                // Create event object
                const event = {};
                headers.forEach((header, index) => {
                    event[header] = values[index] || '';
                });

                // Validate required fields
                if (event.title && event.description && event.date) {
                    events.push(event);
                }
            }

            if (events.length === 0) {
                throw new Error('No valid events found in CSV data');
            }

            return events;
        } catch (err) {
            throw new Error(`CSV parsing error: ${err.message}`);
        }
    };

    const handlePasteData = (e) => {
        const data = e.target.value;
        setCsvData(data);
        setError('');
        
        if (data.trim()) {
            try {
                const events = parseCSVData(data);
                setParsedEvents(events);
                setShowPreview(true);
            } catch (err) {
                setError(err.message);
                setParsedEvents([]);
                setShowPreview(false);
            }
        } else {
            setParsedEvents([]);
            setShowPreview(false);
        }
    };

    const handleImport = async () => {
        setIsImporting(true);
        try {
            // Import events via the existing CSV import API
            const formData = new FormData();
            const csvBlob = new Blob([csvData], { type: 'text/csv' });
            formData.append('file', csvBlob, 'ai_generated_events.csv');

            const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${baseUrl}/events/import/csv`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Import failed');
            }

            const result = await response.json();
            
            // Notify parent component
            if (onImport) {
                onImport(result);
            }

            // Close the modal
            if (onClose) {
                onClose();
            }

        } catch (err) {
            setError(`Import failed: ${err.message}`);
        } finally {
            setIsImporting(false);
        }
    };

    const handleKeyDown = (e) => {
        // Handle Ctrl+V / Cmd+V paste
        if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
            // Let the browser handle the paste naturally
            setTimeout(() => {
                const value = e.target.value;
                if (value !== csvData) {
                    handlePasteData({ target: { value } });
                }
            }, 10);
        }
    };

    const handleClipboardPaste = async () => {
        try {
            // Check if we have clipboard API access
            if (!navigator.clipboard || !navigator.clipboard.readText) {
                setError('Clipboard access not available. Please paste manually with Ctrl+V.');
                textareaRef.current?.focus();
                return;
            }

            // Try to read from clipboard
            const text = await navigator.clipboard.readText();
            
            if (!text || text.trim().length === 0) {
                setError('Clipboard is empty or could not be read. Try copying the CSV data again.');
                return;
            }

            setCsvData(text);
            handlePasteData({ target: { value: text } });
            
        } catch (err) {
            console.log('Clipboard read error:', err);
            // Focus textarea for manual paste
            setError('Could not read from clipboard. Please paste manually with Ctrl+V in the text area below.');
            textareaRef.current?.focus();
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-slate-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-slate-700">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-bold text-white">🤖 AI Timeline Import</h2>
                            <p className="text-slate-400 mt-1">
                                Paste CSV data from ChatGPT, Claude, or any AI assistant
                            </p>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-slate-400 hover:text-white transition-colors"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
                    {/* Instructions */}
                    <div className="mb-6 p-4 bg-blue-900/30 border border-blue-500/30 rounded-lg">
                        <h3 className="text-blue-300 font-semibold mb-2">📋 How to use:</h3>
                        <ol className="text-blue-200 text-sm space-y-1 list-decimal list-inside">
                            <li>Copy CSV data from your AI assistant (ChatGPT, Claude, etc.)</li>
                            <li><strong>Click in the text area below</strong> and paste with <kbd className="bg-blue-800 px-1 rounded">Ctrl+V</kbd> (or <kbd className="bg-blue-800 px-1 rounded">Cmd+V</kbd> on Mac)</li>
                            <li>Review the preview of parsed events</li>
                            <li>Click "Import Events" to add them to your timeline</li>
                        </ol>
                        <div className="mt-3 p-2 bg-amber-900/30 border border-amber-500/30 rounded text-amber-200 text-xs">
                            💡 <strong>Tip:</strong> If clipboard button doesn't work, manually paste into the text area - this is more reliable across different browsers.
                        </div>
                    </div>

                    {/* CSV Input Area */}
                    <div className="mb-6">
                        <div className="flex items-center justify-between mb-2">
                            <label className="text-white font-medium">CSV Data:</label>
                            <button
                                onClick={handleClipboardPaste}
                                className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded transition-colors"
                            >
                                📋 Try Clipboard Paste
                            </button>
                        </div>
                        <textarea
                            ref={textareaRef}
                            value={csvData}
                            onChange={handlePasteData}
                            onKeyDown={handleKeyDown}
                            placeholder="Paste your AI-generated CSV data here...

👆 CLICK HERE and paste with Ctrl+V (or Cmd+V on Mac)

Example:
title,description,date,timeline,actor,emotion,tags,evidence_links
Meeting with Client,Initial consultation about the case,2025-10-27 10:00:00,Case Name,Attorney,professional,meeting,/docs/consultation.pdf"
                            className="w-full h-48 p-3 bg-slate-900 text-white rounded border-2 border-slate-600 
                                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                                     font-mono text-sm transition-colors"
                        />
                    </div>

                    {/* Error Display */}
                    {error && (
                        <div className="mb-6 p-4 bg-red-900/30 border border-red-500/30 rounded-lg">
                            <div className="flex items-center gap-2">
                                <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span className="text-red-300 font-medium">Error:</span>
                            </div>
                            <p className="text-red-200 mt-1">{error}</p>
                        </div>
                    )}

                    {/* Preview */}
                    {showPreview && parsedEvents.length > 0 && (
                        <div className="mb-6">
                            <h3 className="text-white font-semibold mb-3">
                                📋 Preview ({parsedEvents.length} events found)
                            </h3>
                            <div className="bg-slate-900 rounded border border-slate-600 max-h-64 overflow-y-auto">
                                {parsedEvents.map((event, index) => (
                                    <div key={index} className="p-3 border-b border-slate-700 last:border-b-0">
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="flex-1 min-w-0">
                                                <h4 className="text-white font-medium truncate">{event.title}</h4>
                                                <p className="text-slate-300 text-sm mt-1 line-clamp-2">
                                                    {event.description}
                                                </p>
                                                <div className="flex flex-wrap gap-2 mt-2 text-xs">
                                                    <span className="px-2 py-1 bg-slate-700 text-slate-300 rounded">
                                                        📅 {event.date}
                                                    </span>
                                                    {event.timeline && (
                                                        <span className="px-2 py-1 bg-blue-600/20 text-blue-300 rounded">
                                                            📂 {event.timeline}
                                                        </span>
                                                    )}
                                                    {event.actor && (
                                                        <span className="px-2 py-1 bg-green-600/20 text-green-300 rounded">
                                                            👤 {event.actor}
                                                        </span>
                                                    )}
                                                    {event.tags && (
                                                        <span className="px-2 py-1 bg-purple-600/20 text-purple-300 rounded">
                                                            🏷️ {event.tags}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-700 bg-slate-850">
                    <div className="flex items-center justify-between">
                        <div className="text-slate-400 text-sm">
                            {showPreview ? (
                                <span>✅ Ready to import {parsedEvents.length} events</span>
                            ) : (
                                <span>Paste CSV data to see preview</span>
                            )}
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={onClose}
                                className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleImport}
                                disabled={!showPreview || parsedEvents.length === 0 || isImporting}
                                className="px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 
                                         disabled:cursor-not-allowed text-white rounded transition-colors
                                         flex items-center gap-2"
                            >
                                {isImporting ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                        Importing...
                                    </>
                                ) : (
                                    <>
                                        🚀 Import {parsedEvents.length} Events
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}