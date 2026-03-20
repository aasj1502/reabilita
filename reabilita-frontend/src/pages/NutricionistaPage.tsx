import { useMemo, useState } from 'react';

import {
	Alert,
	Button,
	Chip,
	CircularProgress,
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
import type { Atendimento } from '../types/atendimento';

/** Faixas CID-10 de interesse nutricional conforme Plan. */
const FAIXAS_CID10_NUTRICIONAL: { faixa: string; descricao: string }[] = [
	{ faixa: 'D50-D53', descricao: 'Anemias nutricionais' },
	{ faixa: 'E40-E46', descricao: 'Desnutrição' },
	{ faixa: 'M80-M85', descricao: 'Transtornos da densidade e estrutura óssea' },
];

const formatDate = (value: string) => {
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return value;
	return date.toLocaleDateString('pt-BR');
};

/** Verifica se o código CID-10 está dentro de uma faixa XX.X–XX.X (apenas prefixo de letra+número). */
const cidDentroFaixa = (codigo: string, faixaInicio: string, faixaFim: string): boolean => {
	const cod = codigo.toUpperCase().replace('.', '').trim();
	const ini = faixaInicio.toUpperCase().replace('.', '').replace('-', '').trim();
	const fim = faixaFim.toUpperCase().replace('.', '').replace('-', '').trim();
	if (cod.length < 3 || ini.length < 3 || fim.length < 3) return false;
	const codPrefix = cod.slice(0, 3);
	return codPrefix >= ini.slice(0, 3) && codPrefix <= fim.slice(0, 3);
};

/** Retorna se o atendimento possui CID-10 em alguma faixa de interesse nutricional. */
const classificarRelevancia = (atendimento: Atendimento): string | null => {
	const cid = atendimento.codigo_cid10;
	if (!cid) return null;
	if (cidDentroFaixa(cid, 'D50', 'D53')) return 'Anemia nutricional';
	if (cidDentroFaixa(cid, 'E40', 'E46')) return 'Desnutrição';
	if (cidDentroFaixa(cid, 'M80', 'M85')) return 'Perda massa óssea';
	return null;
};

export const NutricionistaPage = () => {
	const { data, isLoading, isError, refetch } = useAtendimentos();
	const [busca, setBusca] = useState('');
	const [apenasRelevantes, setApenasRelevantes] = useState(false);

	const atendimentos = useMemo(() => {
		const lista = data ?? [];
		const buscaNorm = busca.trim().toLowerCase();

		return lista.filter((item) => {
			if (apenasRelevantes && !classificarRelevancia(item)) return false;

			if (buscaNorm) {
				const texto = [
					item.codigo_cid10,
					item.estrutura_anatomica,
					item.notas_clinicas,
				]
					.join(' ')
					.toLowerCase();
				if (!texto.includes(buscaNorm)) return false;
			}
			return true;
		});
	}, [data, busca, apenasRelevantes]);

	if (isLoading) {
		return (
			<Stack alignItems="center" justifyContent="center" py={8}>
				<CircularProgress />
			</Stack>
		);
	}

	if (isError) {
		return (
			<SectionCard title="Nutricionista — Módulo Metabólico">
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
				Módulo Nutricionista — Monitoramento Metabólico e Ósseo
			</Typography>

			<Alert severity="info" variant="outlined">
				Faixas CID-10 monitoradas:{' '}
				{FAIXAS_CID10_NUTRICIONAL.map((f) => `${f.faixa} (${f.descricao})`).join(' · ')}
			</Alert>

			<SectionCard title="Filtros">
				<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} mb={1}>
					<TextField
						label="Buscar"
						placeholder="CID-10, estrutura, notas…"
						size="small"
						value={busca}
						onChange={(e) => setBusca(e.target.value)}
						sx={{ minWidth: 220 }}
					/>
					<Button
						variant={apenasRelevantes ? 'contained' : 'outlined'}
						size="small"
						onClick={() => setApenasRelevantes((v) => !v)}
						sx={{ minHeight: 44, minWidth: 44 }}
					>
						{apenasRelevantes ? 'Mostrando relevantes' : 'Filtrar relevantes'}
					</Button>
				</Stack>
				<FilterActionsRow
					refreshLabel="Atualizar"
					onRefresh={() => { refetch(); }}
					onClear={() => {
						setBusca('');
						setApenasRelevantes(false);
					}}
				/>
			</SectionCard>

			<SectionCard title="Atendimentos — Nutrição">
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
									<TableCell>CID-10</TableCell>
									<TableCell>Tipo Lesão</TableCell>
									<TableCell>Estrutura</TableCell>
									<TableCell>Relevância Nutricional</TableCell>
									<TableCell>S-RED</TableCell>
									<TableCell>Notas</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{atendimentos.map((atd) => {
									const relevancia = classificarRelevancia(atd);
									return (
										<TableRow key={atd.id}>
											<TableCell>{formatDate(atd.data_registro)}</TableCell>
											<TableCell>{atd.codigo_cid10 || '—'}</TableCell>
											<TableCell>{atd.tipo_lesao}</TableCell>
											<TableCell>{atd.estrutura_anatomica}</TableCell>
											<TableCell>
												{relevancia ? (
													<Chip label={relevancia} color="warning" size="small" />
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
											<TableCell>
												{atd.notas_clinicas
													? atd.notas_clinicas.length > 60
														? `${atd.notas_clinicas.slice(0, 60)}…`
														: atd.notas_clinicas
													: '—'}
											</TableCell>
										</TableRow>
									);
								})}
							</TableBody>
						</Table>
					</TableContainer>
				)}
			</SectionCard>
		</Stack>
	);
};
