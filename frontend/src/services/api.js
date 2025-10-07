import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getEvents = async () => {
  const response = await api.get('/events/');
  return response.data;
};

export const getEvent = async (id) => {
  const response = await api.get(`/events/${id}`);
  return response.data;
};

export const createEvent = async (event) => {
  const response = await api.post('/events/', event);
  return response.data;
};

export const updateEvent = async (id, event) => {
  const response = await api.put(`/events/${id}`, event);
  return response.data;
};

export const deleteEvent = async (id) => {
  const response = await api.delete(`/events/${id}`);
  return response.data;
};

export default api;
