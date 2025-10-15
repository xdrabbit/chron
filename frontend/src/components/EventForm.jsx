import { useEffect, useRef, useState } from "react";
import { VoiceTranscriber } from "./VoiceTranscriber";

const initialState = {
  title: "",
  description: "",
  date: "",
  time: "",
  timeline: "Default",
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

export default function EventForm({ initialData, onSubmit, onCancel, availableTimelines = [] }) {
  const [form, setForm] = useState(initialState);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showVoiceTranscription, setShowVoiceTranscription] = useState(false);
  const [transcriptionData, setTranscriptionData] = useState(null); // Store audio file and metadata
  const dateInputRef = useRef(null);

  useEffect(() => {
    if (initialData) {
      setForm({
        title: initialData.title ?? "",
        description: initialData.description ?? "",
        date: formatDateInput(initialData.date),
        time: formatTimeInput(initialData.date),
        timeline: initialData.timeline ?? "Default",
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

  const handleVoiceTranscription = (data) => {
    // Store the full transcription data including audio file and word timestamps
    setTranscriptionData(data);
    
    // Put the transcription text in the description field
    setForm(previous => ({ 
      ...previous, 
      description: previous.description ? 
        `${previous.description}\n\n${data.transcription}` : 
        data.transcription
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    if (!form.title.trim() || !form.date || !form.timeline.trim()) {
      setError("Please provide at least a title, date, and timeline.");
      setIsSubmitting(false);
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
        timeline: form.timeline.trim(),
        date: new Date(dateTimeString).toISOString(),
      };

      // If we have transcription data with audio, use the with-audio endpoint
      if (transcriptionData && transcriptionData.audioFile) {
        const formData = new FormData();
        formData.append('audio_file', transcriptionData.audioFile, 'audio.mp3');
        formData.append('title', payload.title);
        formData.append('description', payload.description);
        formData.append('timeline', payload.timeline);
        formData.append('date', payload.date);
        
        await onSubmit(formData, true); // Pass flag indicating it's formData with audio
      } else {
        await onSubmit(payload);
      }
      
      setForm(initialState);
      setTranscriptionData(null);
    } catch (err) {
      setError("Unable to save event. Try again.");
    } finally {
      setIsSubmitting(false);
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
          Timeline
        </label>
        <div className="flex gap-2">
          <select
            name="timeline"
            value={form.timeline}
            onChange={handleChange}
            className="flex-1 rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-blue-500 focus:outline-none"
          >
            <option value="Default">Default</option>
            {availableTimelines.map((timeline) => (
              <option key={timeline} value={timeline}>
                {timeline}
              </option>
            ))}
          </select>
          <input
            type="text"
            name="timeline"
            value={form.timeline}
            onChange={handleChange}
            placeholder="Or type new timeline"
            className="flex-1 rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-blue-500 focus:outline-none"
          />
        </div>
        <p className="text-xs text-slate-400">
          Select existing timeline or type a new one (e.g., "Work Projects", "Personal Life").
        </p>
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

      {/* Voice Transcription Section - Collapsible */}
      <div className="border-t border-amber-600/30 pt-4">
        <button
          type="button"
          onClick={() => setShowVoiceTranscription(!showVoiceTranscription)}
          className="w-full flex items-center justify-between p-3 bg-slate-900/50 hover:bg-slate-900 rounded-lg transition-colors border border-slate-700"
        >
          <div className="flex items-center gap-2">
            <span className="text-purple-400">🎤</span>
            <span className="text-sm font-semibold text-slate-200">Voice Transcription</span>
            <span className="text-xs text-slate-400">(Optional)</span>
          </div>
          <span className="text-slate-400 text-lg">
            {showVoiceTranscription ? '−' : '+'}
          </span>
        </button>
        
        {showVoiceTranscription && (
          <div className="mt-3">
            <VoiceTranscriber onTranscription={handleVoiceTranscription} />
          </div>
        )}
      </div>

      {error && (
        <p className="rounded border border-rose-500 bg-rose-500/10 p-2 text-sm text-rose-200">
          {error}
        </p>
      )}

      <div className="flex items-center gap-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className={`rounded px-4 py-2 text-sm font-semibold text-white focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all flex items-center gap-2 ${
            isSubmitting 
              ? 'bg-blue-700 animate-pulse cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-500'
          }`}
        >
          {isSubmitting ? (
            <>
              <span className="animate-spin-slow">⏳</span>
              <span>{transcriptionData ? 'Transcribing & Saving...' : 'Saving...'}</span>
            </>
          ) : (
            <span>{isEditing ? "Update Event" : "Add Event"}</span>
          )}
        </button>
        {isEditing && (
          <button
            type="button"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="rounded border border-slate-600 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
