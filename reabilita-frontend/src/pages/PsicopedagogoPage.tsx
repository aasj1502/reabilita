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

import type { Atendimento } from '../types/atendimento';

import { FilterActionsRow } from '../components/common';
import { EmptyState, SectionCard } from '../design-system';
import { useAtendimentos } from '../hooks/useAtendimentos';

/** CID-10 R41.8 — Bradifrenia (pensamento lentificado). */
const CID_BRADIFRENIA = 'R41.8';

const formatDate = (value: string) => {
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return value;
	return date.toLocaleDateString('pt-BR');
};

/** Verifica indicadores de saúde mental relevantes no atendimento. */
const classificarSaudeMental = (atendimento: Atendimento): string | null => {
	const cid = (atendimento.codigo_cid10 || '').toUpperCase().trim();

	if (cid.startsWith('R41.8')) return 'Bradifrenia';

	/* Faixas de transtornos mentais F00-F99 */
	if (cid.length >= 3 && cid.startsWith('F')) return 'Transtorno mental';

	/* Lesões graves (S-RED ativo) associadas a impacto psicológico */
	if (atendimento.flag_sred) return 'Acompanhar (S-RED)';

	/* Verificação textual em notas clínicas */
	const notas = (atendimento.notas_clinicas || '').toLowerCase();
	if (/bradifr[eê]nia|lentifica/i.test(notas)) return 'Bradifrenia (notas)';
	if (/sa[uú]de\s*mental|depress|ansiedade|estresse\s*psic/i.test(notas)) return 'Saúde mental (notas)';

	return null;
};

export const PsicopedagogoPage = () => {
	const { data, isLoading, isError, refetch } = useAtendimentos();
	const [busca, setBusca] = useState('');
	const [apenasRelevantes, setApenasRelevantes] = useState(false);

	const atendimentos = useMemo(() => {
		const lista = data ?? [];
		const buscaNorm = busca.trim().toLowerCase();

		return lista.filter((item) => {
			if (apenasRelevantes && !classificarSaudeMental(item)) return false;

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
			<SectionCard title="Psicopedagogia — Módulo Mental">
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
				Módulo Psicopedagogia — Bradifrenia e Saúde Mental
			</Typography>

			<Alert severity="info" variant="outlined">
				Monitoramento de Bradifrenia (CID-10 {CID_BRADIFRENIA} — pensamento lentificado) e saúde
				mental vinculada a lesões graves.
			</Alert>

			<SectionCard title="Filtros">
				<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} mb={1}>
					<TextField
						label="Buscar"
						placeholder="CID-10, notas clínicas…"
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

			<SectionCard title="Atendimentos — Psicopedagogia">
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
									<TableCell>Indicador</TableCell>
									<TableCell>S-RED</TableCell>
									<TableCell>Decisão S-RED</TableCell>
									<TableCell>Notas</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{atendimentos.map((atd) => {
									const indicador = classificarSaudeMental(atd);
									return (
										<TableRow key={atd.id}>
											<TableCell>{formatDate(atd.data_registro)}</TableCell>
											<TableCell>{atd.codigo_cid10 || '—'}</TableCell>
											<TableCell>{atd.tipo_lesao}</TableCell>
											<TableCell>
												{indicador ? (
													<Chip
														label={indicador}
														color={
															indicador === 'Bradifrenia' || indicador === 'Bradifrenia (notas)'
																? 'error'
																: 'warning'
														}
														size="small"
													/>
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
											<TableCell>{atd.decisao_sred || '—'}</TableCell>
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
