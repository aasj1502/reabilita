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

export type SystemUserProfile =
	| 'Administrador'
	| 'Consultor'
	| 'Educador Físico'
	| 'Enfermeiro'
	| 'Fisioterapeuta'
	| 'Instrutor'
	| 'Médico'
	| 'Nutricionista'
	| 'Psicopedagogo';

export type EspecialidadeMedica = 'Ortopedista' | 'Clínico Geral';

export type FuncaoInstrutor =
	| 'Comandante do Corpo de Cadetes'
	| 'Subcomandante do Corpo de Cadetes'
	| 'S1-CC'
	| 'Comandante de Curso'
	| 'Comandante de Subunidade'
	| 'Comandante de Pelotão';

export interface CreateSystemUserPayload {
	nome_completo: string;
	email: string;
	perfil: SystemUserProfile;
	especialidade_medica?: EspecialidadeMedica | '';
	funcao_instrutor?: FuncaoInstrutor | '';
	posto_graduacao?: string;
	nome_guerra?: string;
	setor?: string;
	fracao?: string;
	senha_inicial: string;
	confirmar_senha_inicial: string;
	usuario_ativo: boolean;
}

export interface SystemUserResponse {
	id: number;
	username: string;
	email: string;
	nome_completo: string;
	perfil: SystemUserProfile;
	especialidade_medica: string;
	funcao_instrutor: string;
	posto_graduacao: string;
	nome_guerra: string;
	setor: string;
	fracao: string;
	is_active: boolean;
	is_staff: boolean;
}

export interface SystemUserDetail {
	id: number;
	username: string;
	email: string;
	first_name: string;
	last_name: string;
	perfil: SystemUserProfile;
	especialidade_medica: string;
	funcao_instrutor: string;
	posto_graduacao: string;
	nome_guerra: string;
	setor: string;
	fracao: string;
	is_active: boolean;
	is_staff: boolean;
}

export interface UpdateUserPayload {
	email?: string;
	usuario_ativo?: boolean;
}

export interface ChangePasswordPayload {
	senha_atual: string;
	senha_nova: string;
	confirmar_senha_nova: string;
}

export interface PasswordResetRequestPayload {
	email: string;
}
