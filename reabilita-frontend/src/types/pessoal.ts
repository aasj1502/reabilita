export interface Militar {
	id: number;
	nr_militar: string;
	nome_completo: string;
	sexo: string;
	turma: string;
	posto_graduacao: string;
	arma_quadro_servico: string;
	curso: string;
	companhia: string;
	pelotao: string;
	is_instrutor: boolean;
}

export interface CreateMilitarPayload {
	nr_militar: string;
	nome_completo: string;
	sexo?: string;
	turma?: string;
	posto_graduacao?: string;
	arma_quadro_servico?: string;
	curso?: string;
	companhia?: string;
	pelotao?: string;
	is_instrutor?: boolean;
}

export interface ProfissionalSaude {
	id: number;
	militar: number;
	especialidade: string;
	registro_profissional: string;
	ativo: boolean;
}
