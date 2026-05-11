import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1`
  : "http://localhost:8000/api/v1";

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

export const getPropagation = async (topic: string) => {
  const { data } = await api.get("/propagation", { params: { topic } });
  return data;
};

export const getPropagationOrigin = async (postId: string) => {
  const { data } = await api.get(`/propagation/origin/${postId}`);
  return data;
};

export const getGeoDistribution = async (topic?: string, platform?: string) => {
  const { data } = await api.get("/geo", { params: { topic, platform } });
  return data;
};

export const getGlobeData = async () => {
  const { data } = await api.get("/geo/globe");
  return data;
};

export const checkAuthority = async (author: string, platform = "twitter") => {
  const { data } = await api.get("/authority/check", { params: { author, platform } });
  return data;
};

export default api;
