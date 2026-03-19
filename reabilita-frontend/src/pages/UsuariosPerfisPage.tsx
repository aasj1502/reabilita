import { useMemo } from 'react';

import {
	Button,
	CircularProgress,
	Stack,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Typography,
} from '@mui/material';

import { EmptyState, SectionCard } from '../design-system';
import { useMilitares, useProfissionaisSaude } from '../hooks/usePessoal';

export const UsuariosPerfisPage = () => {
	const {
		data: profissionais,
		isLoading: isLoadingProfissionais,
		isError: isErrorProfissionais,
		refetch: refetchProfissionais,
	} = useProfissionaisSaude();
	const {
		data: militares,
		isLoading: isLoadingMilitares,
		isError: isErrorMilitares,
		refetch: refetchMilitares,
	} = useMilitares();

	const militarById = useMemo(() => {
		const map = new Map<number, string>();
		for (const item of militares ?? []) {
			map.set(item.id, item.nome_completo);
		}
		return map;
	}, [militares]);

	if (isLoadingProfissionais || isLoadingMilitares) {
		return (
			<Stack alignItems="center" justifyContent="center" minHeight="45vh">
				<CircularProgress />
			</Stack>
		);
	}

	if (isErrorProfissionais || isErrorMilitares) {
		return (
			<EmptyState
				title="Falha ao carregar usuários e perfis"
				description="Verifique a conexão e tente novamente."
				action={
					<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
						<Button variant="contained" onClick={() => void refetchProfissionais()} sx={{ minHeight: 44, minWidth: 44 }}>
							Recarregar Perfis
						</Button>
						<Button variant="outlined" onClick={() => void refetchMilitares()} sx={{ minHeight: 44, minWidth: 44 }}>
							Recarregar Militares
						</Button>
					</Stack>
				}
				height="45vh"
			/>
		);
	}

	const items = profissionais ?? [];
	if (items.length === 0) {
		return (
			<EmptyState
				title="Nenhum perfil cadastrado"
				description="Cadastre profissionais de saúde para distribuição de atendimentos."
				height="45vh"
			/>
		);
	}

	return (
		<Stack spacing={2}>
			<Typography variant="h5">Usuários e Perfis</Typography>

			<SectionCard title="Profissionais de Saúde" subtitle="Perfis ativos e especialidades disponíveis.">
				<TableContainer sx={{ width: '100%', overflowX: 'auto' }}>
					<Table size="small" sx={{ minWidth: 680 }}>
						<TableHead>
							<TableRow>
								<TableCell>Militar</TableCell>
								<TableCell>Especialidade</TableCell>
								<TableCell>Registro Profissional</TableCell>
								<TableCell>Ativo</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{items.map((item) => (
								<TableRow key={item.id}>
									<TableCell>{militarById.get(item.militar) ?? `Militar #${item.militar}`}</TableCell>
									<TableCell>{item.especialidade}</TableCell>
									<TableCell>{item.registro_profissional || '-'}</TableCell>
									<TableCell>{item.ativo ? 'Sim' : 'Não'}</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</TableContainer>
			</SectionCard>
		</Stack>
	);
};
