import React, { useState, useEffect } from 'react';
import EventForm from './components/EventForm';
import Timeline from './components/Timeline';
import { getEvents, createEvent, updateEvent, deleteEvent } from './services/api';

function App() {
  const [events, setEvents] = useState([]);
  const [editingEvent, setEditingEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getEvents();
      setEvents(data);
    } catch (err) {
      setError('Failed to load events. Make sure the backend is running.');
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEvent = async (eventData) => {
    try {
      setError(null);
      await createEvent(eventData);
      await fetchEvents();
    } catch (err) {
      setError('Failed to create event.');
      console.error('Error creating event:', err);
    }
  };

  const handleUpdateEvent = async (eventData) => {
    try {
      setError(null);
      await updateEvent(editingEvent.id, eventData);
      setEditingEvent(null);
      await fetchEvents();
    } catch (err) {
      setError('Failed to update event.');
      console.error('Error updating event:', err);
    }
  };

  const handleDeleteEvent = async (id) => {
    if (!window.confirm('Are you sure you want to delete this event?')) {
      return;
    }
    try {
      setError(null);
      await deleteEvent(id);
      await fetchEvents();
    } catch (err) {
      setError('Failed to delete event.');
      console.error('Error deleting event:', err);
    }
  };

  const handleEdit = (event) => {
    setEditingEvent(event);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCancelEdit = () => {
    setEditingEvent(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🧱 Chron
          </h1>
          <p className="text-gray-600">Your minimal event diary</p>
        </header>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <EventForm
          onSubmit={editingEvent ? handleUpdateEvent : handleCreateEvent}
          onCancel={handleCancelEdit}
          initialData={editingEvent}
        />

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading events...</p>
          </div>
        ) : (
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Timeline
            </h2>
            <Timeline
              events={events}
              onEdit={handleEdit}
              onDelete={handleDeleteEvent}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
