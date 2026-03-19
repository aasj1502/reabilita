import { apiClient } from './apiClient';
import type { AuthSession, LoginPayload } from '../types/auth';

const RESOURCE_CSRF = '/auth/csrf/';
const RESOURCE_LOGIN = '/auth/login/';
const RESOURCE_ME = '/auth/me/';
const RESOURCE_LOGOUT = '/auth/logout/';

export const ensureCsrfToken = async (): Promise<void> => {
	await apiClient.get(RESOURCE_CSRF);
};

export const loginWithSession = async (payload: LoginPayload): Promise<AuthSession> => {
	const { data } = await apiClient.post<AuthSession>(RESOURCE_LOGIN, payload);
	return data;
};

export const meWithSession = async (): Promise<AuthSession> => {
	const { data } = await apiClient.get<AuthSession>(RESOURCE_ME);
	return data;
};

export const logoutWithSession = async (): Promise<void> => {
	await apiClient.post(RESOURCE_LOGOUT);
};
