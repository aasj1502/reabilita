import { useMemo, useState } from 'react';

import {
	Button,
	Chip,
	CircularProgress,
	MenuItem,
	Stack,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	TextField,
	Typography,
} from '@mui/material';

import { FilterActionsRow } from '../components/common';
import { EmptyState, SectionCard } from '../design-system';
import { useAtendimentos } from '../hooks/useAtendimentos';
import type { Lateralidade } from '../types/atendimento';

const lateralidadeOptions: Lateralidade[] = ['Direita', 'Esquerda', 'Bilateral', 'Não é o caso'];

const formatDate = (value: string) => {
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return value;
	return date.toLocaleDateString('pt-BR');
};

/** Chip colorido conforme lateralidade para facilitar leitura rápida do Educador Físico. */
const lateralidadeColor = (lat: Lateralidade): 'info' | 'warning' | 'secondary' | 'default' => {
	switch (lat) {
		case 'Direita':
			return 'info';
		case 'Esquerda':
			return 'warning';
		case 'Bilateral':
			return 'secondary';
		default:
			return 'default';
	}
};

export const EducadorFisicoPage = () => {
	const { data, isLoading, isError, refetch } = useAtendimentos();
	const [busca, setBusca] = useState('');
	const [lateralidadeFiltro, setLateralidadeFiltro] = useState<Lateralidade | ''>('');

	const atendimentos = useMemo(() => {
		const lista = data ?? [];
		const buscaNorm = busca.trim().toLowerCase();

		return lista.filter((item) => {
			if (lateralidadeFiltro && item.lateralidade !== lateralidadeFiltro) return false;

			if (buscaNorm) {
				const texto = [
					item.estrutura_anatomica,
					item.localizacao_lesao,
					item.tipo_lesao,
					item.lateralidade,
					item.notas_clinicas,
				]
					.join(' ')
					.toLowerCase();
				if (!texto.includes(buscaNorm)) return false;
			}
			return true;
		});
	}, [data, busca, lateralidadeFiltro]);

	if (isLoading) {
		return (
			<Stack alignItems="center" justifyContent="center" py={8}>
				<CircularProgress />
			</Stack>
		);
	}

	if (isError) {
		return (
			<SectionCard title="Educador Físico — Reabilitação">
				<EmptyState
					title="Erro ao carregar atendimentos"
					description="Não foi possível obter os dados. Tente novamente."
					action={<Button onClick={() => refetch()}>Tentar novamente</Button>}
				/>
			</SectionCard>
		);
	}

	return (
		<Stack spacing={3} p={2}>
			<Typography variant="h5" fontWeight={600}>
				Módulo Educador Físico — Periodização e Fortalecimento Individualizado
			</Typography>

			<SectionCard title="Filtros">
				<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} mb={1}>
					<TextField
						label="Buscar"
						placeholder="Estrutura, tipo lesão, notas…"
						size="small"
						value={busca}
						onChange={(e) => setBusca(e.target.value)}
						sx={{ minWidth: 220 }}
					/>
					<TextField
						label="Lateralidade"
						select
						size="small"
						value={lateralidadeFiltro}
						onChange={(e) => setLateralidadeFiltro(e.target.value as Lateralidade | '')}
						sx={{ minWidth: 180 }}
					>
						<MenuItem value="">Todas</MenuItem>
						{lateralidadeOptions.map((opt) => (
							<MenuItem key={opt} value={opt}>
								{opt}
							</MenuItem>
						))}
					</TextField>
				</Stack>
				<FilterActionsRow
					refreshLabel="Atualizar"
					onRefresh={() => { refetch(); }}
					onClear={() => {
						setBusca('');
						setLateralidadeFiltro('');
					}}
				/>
			</SectionCard>

			<SectionCard title="Atendimentos — Educador Físico">
				{atendimentos.length === 0 ? (
					<EmptyState
						title="Nenhum atendimento encontrado"
						description="Ajuste os filtros ou aguarde novos registros."
					/>
				) : (
					<TableContainer>
						<Table size="small">
							<TableHead>
								<TableRow>
									<TableCell>Data</TableCell>
									<TableCell>Tipo Lesão</TableCell>
									<TableCell>Estrutura Anatômica</TableCell>
									<TableCell>Localização</TableCell>
									<TableCell>Lateralidade</TableCell>
									<TableCell>Conduta</TableCell>
									<TableCell>S-RED</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{atendimentos.map((atd) => (
									<TableRow key={atd.id}>
										<TableCell>{formatDate(atd.data_registro)}</TableCell>
										<TableCell>{atd.tipo_lesao}</TableCell>
										<TableCell>{atd.estrutura_anatomica}</TableCell>
										<TableCell>{atd.localizacao_lesao || '—'}</TableCell>
										<TableCell>
											<Chip
												label={atd.lateralidade}
												color={lateralidadeColor(atd.lateralidade)}
												size="small"
											/>
										</TableCell>
										<TableCell>{atd.conduta_terapeutica || '—'}</TableCell>
										<TableCell>
											{atd.flag_sred ? (
												<Chip label="S-RED" color="error" size="small" />
											) : (
												'—'
											)}
										</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</TableContainer>
				)}
			</SectionCard>
		</Stack>
	);
};
