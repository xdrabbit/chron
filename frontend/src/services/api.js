import axios from "axios";

const resolveBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return envUrl;
  }

  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000`;
  }

  return "http://localhost:8000";
};

const client = axios.create({
  baseURL: resolveBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
});

export const getEvents = async () => {
  const { data } = await client.get("/events/");
  return data;
};

export const createEvent = async (payload) => {
  const { data } = await client.post("/events/", payload);
  return data;
};

export const updateEvent = async (id, payload) => {
  const { data } = await client.put(`/events/${id}`, payload);
  return data;
};

export const deleteEvent = async (id) => {
  const { data } = await client.delete(`/events/${id}`);
  return data;
};

export const exportTimelinePdf = async () => {
  const response = await client.get("/events/export/pdf", {
    responseType: "blob",
  });
  return response.data;
};
