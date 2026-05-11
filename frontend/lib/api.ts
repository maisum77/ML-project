import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getTrending = async (platform?: string, limit = 10) => {
  const { data } = await api.get("/trending", { params: { platform, limit } });
  return data;
};

export const getTrendingRealtime = async (hours = 1) => {
  const { data } = await api.get("/trending/realtime", { params: { hours } });
  return data;
};

export const getSentiment = async (topic: string, hours = 24) => {
  const { data } = await api.get(`/sentiment/${topic}`, { params: { hours } });
  return data;
};

export const getOverallSentiment = async (platform?: string, hours = 24) => {
  const { data } = await api.get("/sentiment/overall", { params: { platform, hours } });
  return data;
};

export const classifyText = async (text: string, source?: string) => {
  const { data } = await api.post("/classify", { text, source });
  return data;
};

export const getFeed = async (filters: Record<string, any>) => {
  const { data } = await api.get("/feed", { params: filters });
  return data;
};

export const exportData = async (format = "json", platform?: string, limit = 1000) => {
  const { data } = await api.get("/export", { params: { format, platform, limit } });
  return data;
};

export default api;
