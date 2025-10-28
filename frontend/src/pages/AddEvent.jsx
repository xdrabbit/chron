import React from 'react';
import EventForm from '../components/EventForm';

const AddEvent = () => {
    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Add New Event</h1>
            <EventForm />
        </div>
    );
};

export default AddEvent;
