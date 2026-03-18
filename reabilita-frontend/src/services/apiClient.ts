import axios from 'axios';

const env = (import.meta as { env?: Record<string, string | undefined> }).env;

const baseURL = env?.VITE_API_BASE_URL ?? '/api/v1';

export const apiClient = axios.create({
	baseURL,
	headers: {
		'Content-Type': 'application/json',
	},
});
