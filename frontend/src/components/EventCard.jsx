import React from 'react';

const EventCard = ({ event }) => {
    return (
        <div className="bg-white shadow-md rounded-lg p-4 mb-4">
            <h3 className="font-bold">{event.title}</h3>
            <p className="text-gray-600">{new Date(event.date).toLocaleDateString()}</p>
            <p>{event.description}</p>
        </div>
    );
};

export default EventCard;
