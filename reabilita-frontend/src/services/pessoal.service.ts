import { apiClient } from './apiClient';
import type {
	CreateMilitarPayload,
	Militar,
	ProfissionalSaude,
} from '../types/pessoal';

const RESOURCE_MILITARES = '/pessoal/militares/';
const RESOURCE_PROFISSIONAIS = '/pessoal/profissionais-saude/';

const toArrayResult = <T>(data: T[] | { results: T[] }): T[] => {
	if (Array.isArray(data)) {
		return data;
	}
	return Array.isArray(data.results) ? data.results : [];
};

export const listMilitares = async (): Promise<Militar[]> => {
	const { data } = await apiClient.get<Militar[] | { results: Militar[] }>(RESOURCE_MILITARES);
	return toArrayResult(data);
};

export const createMilitar = async (payload: CreateMilitarPayload): Promise<Militar> => {
	const { data } = await apiClient.post<Militar>(RESOURCE_MILITARES, payload);
	return data;
};

export const listProfissionaisSaude = async (): Promise<ProfissionalSaude[]> => {
	const { data } = await apiClient.get<ProfissionalSaude[] | { results: ProfissionalSaude[] }>(RESOURCE_PROFISSIONAIS);
	return toArrayResult(data);
};
