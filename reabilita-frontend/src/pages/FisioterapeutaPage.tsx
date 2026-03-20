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
import type { Atendimento, TipoLesao } from '../types/atendimento';

const formatDate = (value: string) => {
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return value;
	return date.toLocaleDateString('pt-BR');
};

const tipoLesaoOptions: TipoLesao[] = [
	'Óssea',
	'Articular',
	'Muscular',
	'Tendinosa',
	'Neurológica',
];

/** Verifica se o atendimento possui assimetria registrada (pés planos/cavos, hiperlassidão). */
const detectarAssimetria = (atendimento: Atendimento): boolean => {
	const texto = [
		atendimento.estrutura_anatomica,
		atendimento.localizacao_lesao,
		atendimento.notas_clinicas,
	]
		.join(' ')
		.toLowerCase();
	return /p[ée]s?\s*(plano|cavo)|hiperl[ao]ssid[aã]o|instabilidade/i.test(texto);
};

export const FisioterapeutaPage = () => {
	const { data, isLoading, isError, refetch } = useAtendimentos();
	const [busca, setBusca] = useState('');
	const [tipoLesaoFiltro, setTipoLesaoFiltro] = useState<TipoLesao | ''>('');

	const atendimentos = useMemo(() => {
		const lista = data ?? [];
		const buscaNorm = busca.trim().toLowerCase();

		return lista.filter((item) => {
			if (tipoLesaoFiltro && item.tipo_lesao !== tipoLesaoFiltro) return false;

			if (buscaNorm) {
				const texto = [
					item.estrutura_anatomica,
					item.localizacao_lesao,
					item.lateralidade,
					item.codigo_cid10,
					item.notas_clinicas,
				]
					.join(' ')
					.toLowerCase();
				if (!texto.includes(buscaNorm)) return false;
			}
			return true;
		});
	}, [data, busca, tipoLesaoFiltro]);

	if (isLoading) {
		return (
			<Stack alignItems="center" justifyContent="center" py={8}>
				<CircularProgress />
			</Stack>
		);
	}

	if (isError) {
		return (
			<SectionCard title="Fisioterapia — Reabilitação">
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
				Módulo Fisioterapia — Correção de Assimetrias e Instabilidades
			</Typography>

			<SectionCard title="Filtros">
				<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} mb={1}>
					<TextField
						label="Buscar"
						placeholder="Estrutura, localização, CID-10…"
						size="small"
						value={busca}
						onChange={(e) => setBusca(e.target.value)}
						sx={{ minWidth: 220 }}
					/>
					<TextField
						label="Tipo de Lesão"
						select
						size="small"
						value={tipoLesaoFiltro}
						onChange={(e) => setTipoLesaoFiltro(e.target.value as TipoLesao | '')}
						sx={{ minWidth: 160 }}
					>
						<MenuItem value="">Todos</MenuItem>
						{tipoLesaoOptions.map((opt) => (
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
						setTipoLesaoFiltro('');
					}}
				/>
			</SectionCard>

			<SectionCard title="Atendimentos — Fisioterapia">
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
									<TableCell>CID-10</TableCell>
									<TableCell>Assimetria</TableCell>
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
										<TableCell>{atd.lateralidade}</TableCell>
										<TableCell>{atd.codigo_cid10 || '—'}</TableCell>
										<TableCell>
											{detectarAssimetria(atd) ? (
												<Chip label="Sim" color="warning" size="small" />
											) : (
												'—'
											)}
										</TableCell>
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
