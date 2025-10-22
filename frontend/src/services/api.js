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

export const getEvents = async (timeline = null) => {
  const params = timeline ? { timeline } : {};
  const { data } = await client.get("/events/", { params });
  return data;
};

export const getTimelines = async () => {
  const { data } = await client.get("/timelines/");
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

export const exportTimelinePdf = async (timeline = null) => {
  const params = timeline && timeline !== "All" ? { timeline } : {};
  const response = await client.get("/events/export/pdf", {
    responseType: "blob",
    params
  });
  return response.data;
};

export const exportTimelineCsv = async (timeline = null) => {
  const params = timeline && timeline !== "All" ? { timeline } : {};
  const response = await client.get("/events/export/csv", {
    responseType: "blob",
    params
  });
  return response.data;
};

export const importEventsFromCsv = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  
  const { data } = await client.post("/events/import/csv", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
};

export const getDatabaseStats = async () => {
  const { data } = await client.get("/events/stats");
  return data;
};

export const clearAllEvents = async () => {
  const { data } = await client.delete("/events/");
  return data;
};

export const seedSampleEvents = async () => {
  const { data } = await client.post("/events/seed");
  return data;
};

// Search API
export const searchEvents = async (query) => {
  const { data } = await client.get("/search", {
    params: { q: query }
  });
  return data;
};

export const rebuildSearchIndex = async () => {
  const { data } = await client.post("/search/rebuild-index");
  return data;
};

// Audio API
export const getEventAudio = (eventId) => {
  const baseUrl = resolveBaseUrl();
  return `${baseUrl}/events/${eventId}/audio`;
};

export const createEventWithAudio = async (formData) => {
  const { data } = await client.post("/events/with-audio", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
};

export const createEventWithAttachments = async (formData) => {
  const { data } = await client.post("/events/with-attachments", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
};

// AI Ask API
export const askTimeline = async (payload) => {
  // First request loads model (60-90s), subsequent requests are fast (5-10s)
  const { data } = await client.post("/ask", payload, {
    timeout: 150000  // 150 seconds (2.5 min) for first request model loading
  });
  return data;
};

export const checkAIStatus = async () => {
  const { data } = await client.get("/ask/status");
  return data;
};
