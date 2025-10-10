import { useEffect, useRef, useState } from "react";

const initialState = {
  title: "",
  description: "",
  date: "",
  time: "",
};

const formatDateInput = (value) => {
  if (!value) {
    return "";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "";
  }
  return parsed.toISOString().slice(0, 10);
};

const formatTimeInput = (value) => {
  if (!value) {
    return "";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "";
  }
  return parsed.toISOString().slice(11, 16); // HH:mm format
};

export default function EventForm({ initialData, onSubmit, onCancel }) {
  const [form, setForm] = useState(initialState);
  const [error, setError] = useState(null);
  const dateInputRef = useRef(null);

  useEffect(() => {
    if (initialData) {
      setForm({
        title: initialData.title ?? "",
        description: initialData.description ?? "",
        date: formatDateInput(initialData.date),
        time: formatTimeInput(initialData.date),
      });
    } else {
      setForm(initialState);
    }
  }, [initialData]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  };

  const openDatePicker = () => {
    if (dateInputRef.current?.showPicker) {
      dateInputRef.current.showPicker();
      return;
    }
    dateInputRef.current?.focus();
  };

  const setCurrentTime = () => {
    const now = new Date();
    const timeString = now.toTimeString().slice(0, 5); // HH:mm format
    setForm(previous => ({ ...previous, time: timeString }));
  };

  const setCurrentDate = () => {
    const now = new Date();
    const dateString = now.toISOString().slice(0, 10); // YYYY-MM-DD format
    setForm(previous => ({ ...previous, date: dateString }));
  };

  const setNow = () => {
    const now = new Date();
    setForm(previous => ({ 
      ...previous, 
      date: now.toISOString().slice(0, 10),
      time: now.toTimeString().slice(0, 5)
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    if (!form.title.trim() || !form.date) {
      setError("Please provide at least a title and date.");
      return;
    }

    try {
      // Combine date and time
      let dateTimeString;
      if (form.time) {
        dateTimeString = `${form.date}T${form.time}:00`;
      } else {
        // If no time specified, default to noon
        dateTimeString = `${form.date}T12:00:00`;
      }

      const payload = {
        title: form.title.trim(),
        description: form.description.trim(),
        date: new Date(dateTimeString).toISOString(),
      };

      await onSubmit(payload);
      setForm(initialState);
    } catch (err) {
      setError("Unable to save event. Try again.");
    }
  };

  const handleCancel = () => {
    setError(null);
    setForm(initialState);
    onCancel?.();
  };

  const isEditing = Boolean(initialData);

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold uppercase tracking-wide text-slate-300">
          Title
        </label>
        <input
          name="title"
          value={form.title}
          onChange={handleChange}
          placeholder="Event title"
          className="rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold uppercase tracking-wide text-slate-300">
          Description
        </label>
        <textarea
          name="description"
          value={form.description}
          onChange={handleChange}
          placeholder="What happened?"
          rows={4}
          className="rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold uppercase tracking-wide text-slate-300">
          Date & Time
        </label>
        <div className="flex gap-2">
          <div className="flex flex-1 gap-2">
            <input
              ref={dateInputRef}
              type="date"
              name="date"
              value={form.date}
              onChange={handleChange}
              className="flex-1 rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-blue-500 focus:outline-none"
            />
            <input
              type="time"
              name="time"
              value={form.time}
              onChange={handleChange}
              placeholder="15:43"
              title="24-hour format (e.g., 15:43 for 3:43 PM)"
              className="w-24 rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <button
            type="button"
            onClick={openDatePicker}
            className="rounded border border-slate-600 px-3 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
            aria-label="Open calendar picker"
          >
            Pick
          </button>
        </div>
        
        {/* Quick Time Presets */}
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={setNow}
            className="rounded border border-green-600 bg-green-600/10 px-2 py-1 text-xs font-semibold text-green-200 hover:bg-green-600/20 focus:outline-none focus:ring-1 focus:ring-green-400"
          >
            Now
          </button>
          <button
            type="button"
            onClick={setCurrentDate}
            className="rounded border border-blue-600 bg-blue-600/10 px-2 py-1 text-xs font-semibold text-blue-200 hover:bg-blue-600/20 focus:outline-none focus:ring-1 focus:ring-blue-400"
          >
            Today
          </button>
          <button
            type="button"
            onClick={setCurrentTime}
            className="rounded border border-purple-600 bg-purple-600/10 px-2 py-1 text-xs font-semibold text-purple-200 hover:bg-purple-600/20 focus:outline-none focus:ring-1 focus:ring-purple-400"
          >
            Current Time
          </button>
        </div>
        
        <p className="text-xs text-slate-400">
          Use 24-hour format (e.g., 15:43 for 3:43 PM). Time is optional - defaults to 12:00 if not specified.
        </p>
      </div>

      {error && (
        <p className="rounded border border-rose-500 bg-rose-500/10 p-2 text-sm text-rose-200">
          {error}
        </p>
      )}

      <div className="flex items-center gap-2">
        <button
          type="submit"
          className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          {isEditing ? "Update Event" : "Add Event"}
        </button>
        {isEditing && (
          <button
            type="button"
            onClick={handleCancel}
            className="rounded border border-slate-600 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-500"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
