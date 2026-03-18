import { apiClient } from './apiClient';
import type { Atendimento, CreateAtendimentoPayload } from '../types/atendimento';

const RESOURCE = '/saude/atendimentos/';

export const listAtendimentos = async (): Promise<Atendimento[]> => {
	const { data } = await apiClient.get<Atendimento[] | { results: Atendimento[] }>(RESOURCE);
	if (Array.isArray(data)) {
		return data;
	}
	return data.results;
};

export const createAtendimento = async (
	payload: CreateAtendimentoPayload,
): Promise<Atendimento> => {
	const { data } = await apiClient.post<Atendimento>(RESOURCE, payload);
	return data;
};
