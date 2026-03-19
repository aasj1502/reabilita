import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useState,
	type ReactNode,
} from 'react';

import axios from 'axios';

import { ensureCsrfToken, loginWithSession, logoutWithSession, meWithSession } from '../services/auth.service';
import type { AuthUser, LoginPayload } from '../types/auth';

export interface AuthContextValue {
	isReady: boolean;
	isAuthenticated: boolean;
	isAuthenticating: boolean;
	user: AuthUser | null;
	loginError: string | null;
	login: (payload: LoginPayload) => Promise<boolean>;
	logout: () => Promise<void>;
}

export interface AuthProviderProps {
	children: ReactNode;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const getErrorMessage = (error: unknown): string => {
	if (axios.isAxiosError(error)) {
		const detail = error.response?.data?.detail;
		if (typeof detail === 'string' && detail.trim()) {
			return detail;
		}
	}

	return 'Falha ao autenticar usuário.';
};

export const AuthProvider = ({ children }: AuthProviderProps) => {
	const [isReady, setIsReady] = useState(false);
	const [isAuthenticating, setIsAuthenticating] = useState(false);
	const [user, setUser] = useState<AuthUser | null>(null);
	const [loginError, setLoginError] = useState<string | null>(null);

	const bootstrapSession = useCallback(async () => {
		try {
			const session = await meWithSession();
			setUser(session.user);
		} catch {
			setUser(null);
		} finally {
			setIsReady(true);
		}
	}, []);

	useEffect(() => {
		void bootstrapSession();
	}, [bootstrapSession]);

	const login = useCallback(async (payload: LoginPayload) => {
		setIsAuthenticating(true);
		setLoginError(null);

		try {
			await ensureCsrfToken();
			const session = await loginWithSession(payload);
			setUser(session.user);
			return true;
		} catch (error) {
			setUser(null);
			setLoginError(getErrorMessage(error));
			return false;
		} finally {
			setIsAuthenticating(false);
		}
	}, []);

	const logout = useCallback(async () => {
		try {
			await ensureCsrfToken();
			await logoutWithSession();
		} catch {
		} finally {
			setUser(null);
			setLoginError(null);
		}
	}, []);

	const contextValue = useMemo<AuthContextValue>(
		() => ({
			isReady,
			isAuthenticated: Boolean(user),
			isAuthenticating,
			user,
			loginError,
			login,
			logout,
		}),
		[isReady, user, isAuthenticating, loginError, login, logout],
	);

	return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
	const context = useContext(AuthContext);
	if (!context) {
		throw new Error('useAuth deve ser usado dentro de AuthProvider.');
	}
	return context;
};
