export interface AuthUser {
	id: number;
	username: string;
	first_name: string;
	last_name: string;
	is_staff: boolean;
}

export interface AuthSession {
	is_authenticated: boolean;
	user: AuthUser | null;
}

export interface LoginPayload {
	username: string;
	password: string;
}
