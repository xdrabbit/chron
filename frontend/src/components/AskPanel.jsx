import { useState, useRef, useEffect } from 'react';
import { askTimeline, checkAIStatus } from '../services/api';

export default function AskPanel({ currentTimeline, isFloating = false }) {
    const [question, setQuestion] = useState('');
    const [conversation, setConversation] = useState([]);
    const [isAsking, setIsAsking] = useState(false);
    const [aiStatus, setAiStatus] = useState(null);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    // Check AI status on mount
    useEffect(() => {
        checkStatus();
    }, []);

    const checkStatus = async () => {
        try {
            const status = await checkAIStatus();
            setAiStatus(status);
        } catch (err) {
            console.error('Failed to check AI status:', err);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [conversation]);

    const handleAsk = async (e) => {
        e.preventDefault();
        if (!question.trim() || isAsking) return;

        const userQuestion = question.trim();
        setQuestion('');
        setError(null);
        setIsAsking(true);

        // Add user message to conversation
        const userMessage = {
            type: 'user',
            question: userQuestion,
            timestamp: new Date().toISOString()
        };
        setConversation(prev => [...prev, userMessage]);

        try {
            // Send to API with timeline context
            const response = await askTimeline({
                question: userQuestion,
                timeline: currentTimeline === "All" ? null : currentTimeline,
                conversation_history: conversation
            });

            // Add AI response to conversation
            const aiMessage = {
                type: 'assistant',
                answer: response.answer,
                sources: response.sources || [],
                model: response.model,
                context_used: response.context_used,
                search_results_count: response.search_results_count,
                timestamp: new Date().toISOString()
            };
            setConversation(prev => [...prev, aiMessage]);

        } catch (err) {
            setError(err.message || 'Failed to get answer');
            // Remove the user message if request failed
            setConversation(prev => prev.slice(0, -1));
        } finally {
            setIsAsking(false);
        }
    };

    const handleClear = () => {
        setConversation([]);
        setError(null);
    };

    const exampleQuestions = [
        "What meetings did I have about funding?",
        "Summarize my bank calls from this month",
        "What were the action items from recent meetings?",
        "Show me all conversations about Daniel County"
    ];

    return (
        <div className={`flex flex-col h-full ${isFloating ? 'max-h-none' : 'max-h-[600px]'}`}>
            {/* Header - EYELID (Frozen) - Only show in embedded mode */}
            {!isFloating && (
                <div className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur-sm pb-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">💬</span>
                        <h3 className="text-lg font-semibold text-slate-100">Ask Your Timeline</h3>
                        <span className="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">👁️ Eyelid</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs">
                        {aiStatus && (
                            <>
                                <span className={`w-2 h-2 rounded-full ${aiStatus.available ? 'bg-green-500' : 'bg-red-500'}`} />
                                <span className="text-slate-400">
                                    {aiStatus.available ? 'AI Ready' : 'AI Offline'}
                                </span>
                            </>
                        )}
                        {currentTimeline && (
                            <span className="text-purple-400 bg-purple-900/30 px-2 py-0.5 rounded">
                                📍 {currentTimeline}
                            </span>
                        )}
                    </div>
                </div>
            )}

            {/* AI Status Warning */}
            {aiStatus && !aiStatus.available && (
                <div className={`${isFloating ? '' : 'mb-4'} p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-sm text-amber-200`}>
                    <p className="font-semibold mb-1">⚠️ AI Service Not Available</p>
                    <p className="text-xs">{aiStatus.message}</p>
                    <p className="text-xs mt-1">Run: <code className="bg-slate-900 px-1 py-0.5 rounded">ollama serve</code></p>
                </div>
            )}

            {/* Conversation */}
            <div className={`flex-1 overflow-y-auto ${isFloating ? 'bg-transparent' : 'bg-slate-900 rounded-lg'} ${isFloating ? 'p-0' : 'p-4 mb-4'} space-y-4`}>
                {conversation.length === 0 ? (
                    <div className="text-center py-8">
                        <p className="text-slate-400 mb-4">Ask me anything about your timeline!</p>
                        <div className="space-y-2">
                            <p className="text-xs text-slate-500 mb-2">Try these examples:</p>
                            {exampleQuestions.map((q, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setQuestion(q)}
                                    className="block w-full text-left px-3 py-2 text-sm text-blue-300 hover:bg-slate-800 rounded transition-colors"
                                >
                                    "{q}"
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <>
                        {conversation.map((msg, idx) => (
                            <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] rounded-lg p-3 ${
                                    msg.type === 'user' 
                                        ? 'bg-blue-600 text-white' 
                                        : 'bg-slate-800 text-slate-200'
                                }`}>
                                    {msg.type === 'user' ? (
                                        <p className="text-sm">{msg.question}</p>
                                    ) : (
                                        <div>
                                            <p className="text-sm whitespace-pre-wrap">{msg.answer}</p>
                                            
                                            {/* Sources */}
                                            {msg.sources && msg.sources.length > 0 && (
                                                <div className="mt-3 pt-3 border-t border-slate-700">
                                                    <p className="text-xs text-slate-400 mb-2">📎 Referenced events:</p>
                                                    <div className="space-y-1">
                                                        {msg.sources.map((source, sidx) => (
                                                            <div key={sidx} className="flex items-center gap-2 text-xs">
                                                                <span className="text-blue-400">•</span>
                                                                <span className="text-slate-300">{source.title}</span>
                                                                {source.has_audio && <span className="text-xs">🎤</span>}
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                            
                                            {/* Metadata */}
                                            <div className="mt-2 text-xs text-slate-500">
                                                {msg.context_used > 0 && (
                                                    <span>Used {msg.context_used} events from {msg.search_results_count} search results</span>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        {isAsking && (
                            <div className="flex justify-start">
                                <div className="bg-slate-800 rounded-lg p-3">
                                    <div className="flex flex-col gap-1">
                                        <div className="flex items-center gap-2">
                                            <span className="animate-spin-slow text-lg">🤔</span>
                                            <span className="text-sm text-slate-400">Thinking...</span>
                                        </div>
                                        <span className="text-xs text-slate-500">First query may take 30-60s while loading AI model</span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            {/* Error */}
            {error && (
                <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-200">
                    ❌ {error}
                </div>
            )}

            {/* Input - EYELID (Frozen Footer) - Only show footer styling in embedded mode */}
            <form onSubmit={handleAsk} className={`${isFloating ? 'pt-4' : 'sticky bottom-0 z-10 bg-slate-900/95 backdrop-blur-sm pt-4'} flex gap-2`}>
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask about your timeline..."
                    disabled={isAsking || (aiStatus && !aiStatus.available)}
                    className="flex-1 bg-slate-900 text-slate-100 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <button
                    type="submit"
                    disabled={!question.trim() || isAsking || (aiStatus && !aiStatus.available)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                    {isAsking ? (
                        <>
                            <span className="animate-spin-slow">⏳</span>
                            <span>Asking...</span>
                        </>
                    ) : (
                        <>
                            <span>💬</span>
                            <span>Ask</span>
                        </>
                    )}
                </button>
                {conversation.length > 0 && (
                    <button
                        type="button"
                        onClick={handleClear}
                        className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition-colors"
                    >
                        Clear
                    </button>
                )}
            </form>
        </div>
    );
}
