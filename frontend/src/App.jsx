import { useEffect, useState } from "react";

import EventForm from "./components/EventForm.jsx";
import Timeline from "./components/Timeline.jsx";
import {
  createEvent,
  deleteEvent,
  getEvents,
  updateEvent,
} from "./services/api.js";

export default function App() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(null);

  const loadEvents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getEvents();
      setEvents(data);
    } catch (err) {
      setError("Unable to fetch events. Check that the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  const handleSubmit = async (formData) => {
    if (editing) {
      await updateEvent(editing.id, formData);
      setEditing(null);
    } else {
      await createEvent(formData);
    }
    await loadEvents();
  };

  const handleDelete = async (eventId) => {
    await deleteEvent(eventId);
    await loadEvents();
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
        <header className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold">Chronicle MVP</h1>
          <p className="text-sm text-slate-400">
            Local event diary prototype — add, update, and review moments.
          </p>
        </header>

        <section className="rounded-lg bg-slate-800 p-4 shadow">
          <EventForm
            key={editing ? editing.id : "new"}
            initialData={editing}
            onSubmit={handleSubmit}
            onCancel={() => setEditing(null)}
          />
        </section>

        <section className="rounded-lg bg-slate-800 p-4 shadow">
          <Timeline
            events={events}
            loading={loading}
            error={error}
            onEdit={setEditing}
            onDelete={handleDelete}
          />
        </section>
      </main>
    </div>
  );
}
