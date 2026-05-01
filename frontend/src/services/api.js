import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const queryDocuments = async (query) => {
  const response = await api.post('/query', { question: query });
  return response.data;
};

export const indexSampleDocs = async () => {
  const response = await api.post('/index-sample-docs');
  return response.data;
};
