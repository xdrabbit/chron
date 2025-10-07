import React from 'react';

const Timeline = ({ events, onEdit, onDelete }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  if (events.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-xl">No events yet. Create your first event!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {events.map((event) => (
        <div
          key={event.id}
          className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-sm font-semibold text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                  {formatDate(event.date)}
                </span>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                {event.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {event.description}
              </p>
            </div>
            <div className="flex gap-2 ml-4">
              <button
                onClick={() => onEdit(event)}
                className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(event.id)}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Timeline;
