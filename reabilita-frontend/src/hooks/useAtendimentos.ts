import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
	createAtendimento,
	getAtendimentoReferencias,
	listAtendimentos,
} from '../services/atendimentos.service';
import type {
	Atendimento,
	AtendimentoReferenciasResponse,
	CreateAtendimentoPayload,
} from '../types/atendimento';

const QUERY_KEY_ATENDIMENTOS = ['atendimentos'];
const QUERY_KEY_ATENDIMENTO_REFERENCIAS = ['atendimentos-referencias'];

export const useAtendimentos = () => {
	return useQuery<Atendimento[]>({
		queryKey: QUERY_KEY_ATENDIMENTOS,
		queryFn: listAtendimentos,
	});
};

export const useAtendimentoReferencias = () => {
	return useQuery<AtendimentoReferenciasResponse>({
		queryKey: QUERY_KEY_ATENDIMENTO_REFERENCIAS,
		queryFn: getAtendimentoReferencias,
	});
};

export const useCreateAtendimento = () => {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (payload: CreateAtendimentoPayload) => createAtendimento(payload),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: QUERY_KEY_ATENDIMENTOS });
		},
	});
};
