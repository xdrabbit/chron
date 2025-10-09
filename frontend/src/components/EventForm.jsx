import { useEffect, useRef, useState } from "react";

const initialState = {
  title: "",
  description: "",
  date: "",
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

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    if (!form.title.trim() || !form.date) {
      setError("Please provide at least a title and date.");
      return;
    }

    try {
      const payload = {
        title: form.title.trim(),
        description: form.description.trim(),
        date: new Date(form.date).toISOString(),
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
          Date
        </label>
        <div className="flex gap-2">
          <input
            ref={dateInputRef}
            type="date"
            name="date"
            value={form.date}
            onChange={handleChange}
            className="flex-1 rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-blue-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={openDatePicker}
            className="rounded border border-slate-600 px-3 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
            aria-label="Open calendar picker"
          >
            Pick
          </button>
        </div>
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
