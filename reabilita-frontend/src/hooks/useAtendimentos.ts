import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { createAtendimento, listAtendimentos } from '../services/atendimentos.service';
import type { Atendimento, CreateAtendimentoPayload } from '../types/atendimento';

const QUERY_KEY_ATENDIMENTOS = ['atendimentos'];

export const useAtendimentos = () => {
	return useQuery<Atendimento[]>({
		queryKey: QUERY_KEY_ATENDIMENTOS,
		queryFn: listAtendimentos,
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
