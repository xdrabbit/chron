import React, { useState, useEffect } from 'react';
import { getDatabaseStats, clearAllEvents, seedSampleEvents } from '../services/api';

const TestingPanel = ({ onDatabaseChange }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState(null);
  const [clearResult, setClearResult] = useState(null);
  const [seedResult, setSeedResult] = useState(null);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDatabaseStats();
      setStats(data);
    } catch (err) {
      setError("Failed to load database stats");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const handleClearDatabase = async () => {
    if (!window.confirm("Are you sure you want to clear ALL events from the database? This action cannot be undone!")) {
      return;
    }

    setClearing(true);
    setError(null);
    setClearResult(null);
    setSeedResult(null);
    
    try {
      const result = await clearAllEvents();
      setClearResult(result);
      await loadStats(); // Refresh stats
      onDatabaseChange?.(); // Notify parent component
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to clear database");
    } finally {
      setClearing(false);
    }
  };

  const handleSeedDatabase = async () => {
    setSeeding(true);
    setError(null);
    setClearResult(null);
    setSeedResult(null);
    
    try {
      const result = await seedSampleEvents();
      setSeedResult(result);
      await loadStats(); // Refresh stats
      onDatabaseChange?.(); // Notify parent component
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to seed database");
    } finally {
      setSeeding(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="rounded-lg bg-slate-800 p-4 shadow border-l-4 border-yellow-500">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          🧪 Testing Panel
          <span className="text-xs bg-yellow-600 text-yellow-100 px-2 py-1 rounded">DEV</span>
        </h3>
        <button
          onClick={loadStats}
          disabled={loading}
          className="text-xs text-slate-400 hover:text-slate-200 disabled:opacity-50"
        >
          {loading ? "Refreshing..." : "Refresh Stats"}
        </button>
      </div>

      {/* Database Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div className="bg-slate-900 p-3 rounded border border-slate-700">
          <div className="text-xs text-slate-400 mb-1">Total Events</div>
          <div className="text-xl font-bold text-slate-100">
            {loading ? "..." : stats?.total_events || 0}
          </div>
        </div>
        
        <div className="bg-slate-900 p-3 rounded border border-slate-700">
          <div className="text-xs text-slate-400 mb-1">Earliest Event</div>
          <div className="text-sm text-slate-200">
            {loading ? "..." : formatDate(stats?.earliest_event)}
          </div>
        </div>
        
        <div className="bg-slate-900 p-3 rounded border border-slate-700">
          <div className="text-xs text-slate-400 mb-1">Latest Event</div>
          <div className="text-sm text-slate-200">
            {loading ? "..." : formatDate(stats?.latest_event)}
          </div>
        </div>
      </div>

      {/* Status Indicator */}
      <div className="flex items-center gap-2 mb-4">
        <div className={`w-3 h-3 rounded-full ${
          stats?.database_status === 'healthy' ? 'bg-green-500' : 
          stats?.database_status === 'error' ? 'bg-red-500' : 'bg-yellow-500'
        }`}></div>
        <span className="text-sm text-slate-300">
          Database Status: {stats?.database_status || 'Unknown'}
        </span>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleSeedDatabase}
          disabled={seeding}
          className="flex items-center gap-2 rounded border border-green-600 bg-green-600/10 px-4 py-2 text-sm font-semibold text-green-200 hover:bg-green-600/20 focus:outline-none focus:ring-2 focus:ring-green-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          🌱 {seeding ? "Seeding..." : "Add Sample Data"}
        </button>
        
        <button
          onClick={handleClearDatabase}
          disabled={clearing || stats?.total_events === 0}
          className="flex items-center gap-2 rounded border border-red-600 bg-red-600/10 px-4 py-2 text-sm font-semibold text-red-200 hover:bg-red-600/20 focus:outline-none focus:ring-2 focus:ring-red-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          🗑️ {clearing ? "Clearing..." : "Clear All Events"}
        </button>
        
        <div className="text-xs text-slate-400 flex items-center">
          ⚠️ These actions affect the database permanently
        </div>
      </div>

      {/* Results and Errors */}
      {error && (
        <div className="mt-4 rounded border border-red-500 bg-red-500/10 p-3 text-sm text-red-200">
          ❌ {error}
        </div>
      )}

      {clearResult && (
        <div className="mt-4 rounded border border-green-500 bg-green-500/10 p-3 text-sm text-green-200">
          ✅ {clearResult.message}
        </div>
      )}

      {seedResult && (
        <div className="mt-4 rounded border border-blue-500 bg-blue-500/10 p-3 text-sm text-blue-200">
          🌱 {seedResult.message}
        </div>
      )}
    </div>
  );
};

export default TestingPanel;