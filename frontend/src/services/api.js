import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const queryDocuments = async (query, chatHistory = []) => {
  const response = await api.post('/query', {
    question: query,
    chat_history: chatHistory,
  });
  return response.data;
};

export const indexSampleDocs = async () => {
  const response = await api.post('/index-sample-docs');
  return response.data;
};