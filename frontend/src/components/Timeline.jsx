import { format } from "date-fns";

const formatDateLabel = (value) => {
  try {
    return format(new Date(value), "PPP");
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
}) {
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

  if (!events?.length) {
    return (
      <p className="text-sm text-slate-400">
        No events yet. Add your first milestone using the form above.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold text-slate-100">Timeline</h2>
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
    </div>
  );
}
