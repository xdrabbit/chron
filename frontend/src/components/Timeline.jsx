import { format } from "date-fns";
import { useRef } from "react";

const formatDateLabel = (value) => {
  try {
    const date = new Date(value);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    
    // If time is exactly noon (12:00), just show the date
    if (hours === 12 && minutes === 0) {
      return format(date, "PPP");
    }
    
    // Otherwise, show date and time in 24-hour format
    return format(date, "PPP 'at' HH:mm");
  } catch (err) {
    return value;
  }
};

export default function Timeline({
  events,
  loading,
  error,
  onEdit,
  onDelete,
  onExport,
  onExportCsv,
  onImportCsv,
  exporting = false,
  importing = false,
  exportError = null,
  importError = null,
  importResult = null,
}) {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file) {
      onImportCsv?.(file);
      // Reset the input so the same file can be selected again
      event.target.value = '';
    }
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };
  if (loading) {
    return <p className="text-sm text-slate-300">Loading timeline…</p>;
  }

  if (error) {
    return (
      <p className="text-sm text-rose-300">
        {error} The frontend will retry after refresh.
      </p>
    );
  }

  const hasEvents = Boolean(events?.length);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-xl font-semibold text-slate-100">Timeline</h2>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleImportClick}
            disabled={importing}
            className="rounded border border-green-600 px-3 py-1.5 text-xs font-semibold text-green-200 hover:bg-green-600/10 focus:outline-none focus:ring-2 focus:ring-green-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {importing ? "Importing…" : "Import CSV"}
          </button>
          <button
            type="button"
            onClick={onExportCsv}
            disabled={exporting}
            className="rounded border border-blue-600 px-3 py-1.5 text-xs font-semibold text-blue-200 hover:bg-blue-600/10 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {exporting ? "Preparing…" : "Export CSV"}
          </button>
          <button
            type="button"
            onClick={onExport}
            disabled={exporting}
            className="rounded border border-slate-600 px-3 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {exporting ? "Preparing…" : "Export PDF"}
          </button>
        </div>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        className="hidden"
      />
      {exportError && (
        <p className="rounded border border-amber-500 bg-amber-500/10 p-2 text-xs text-amber-200">
          {exportError}
        </p>
      )}
      {importError && (
        <p className="rounded border border-rose-500 bg-rose-500/10 p-2 text-xs text-rose-200">
          {importError}
        </p>
      )}
      {importResult && (
        <div className="rounded border border-green-500 bg-green-500/10 p-3 text-xs text-green-200">
          <p className="font-semibold mb-1">{importResult.message}</p>
          {importResult.error_count > 0 && (
            <div className="mt-2">
              <p className="text-amber-200 mb-1">Errors encountered:</p>
              <ul className="text-xs text-amber-200 ml-2">
                {importResult.errors.slice(0, 5).map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
                {importResult.errors.length > 5 && (
                  <li>• ... and {importResult.errors.length - 5} more errors</li>
                )}
              </ul>
            </div>
          )}
        </div>
      )}
      {hasEvents ? (
        <ul className="flex flex-col gap-3">
          {events.map((event) => (
            <li
              key={event.id}
              className="rounded border border-slate-700 bg-slate-900 p-4 shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold text-slate-100">
                    {event.title}
                  </p>
                  <p className="text-sm text-slate-400">
                    {formatDateLabel(event.date)}
                  </p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit?.(event)}
                    className="rounded border border-blue-500 px-3 py-1 text-xs font-semibold text-blue-200 hover:bg-blue-500/10 focus:outline-none focus:ring-2 focus:ring-blue-400"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete?.(event.id)}
                    className="rounded border border-rose-500 px-3 py-1 text-xs font-semibold text-rose-200 hover:bg-rose-500/10 focus:outline-none focus:ring-2 focus:ring-rose-400"
                  >
                    Delete
                  </button>
                </div>
              </div>
              {event.description && (
                <p className="mt-3 whitespace-pre-wrap text-sm text-slate-200">
                  {event.description}
                </p>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-slate-400">
          No events yet. Add your first milestone using the form above.
        </p>
      )}
    </div>
  );
}
