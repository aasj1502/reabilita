import { useMemo, useState } from 'react';

import {
	Button,
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
import { Link as RouterLink } from 'react-router-dom';

import { FilterActionsRow } from '../components/common';
import { EmptyState, SectionCard } from '../design-system';
import { useMilitares } from '../hooks/usePessoal';

type InstrutorFiltro = '' | 'sim' | 'nao';

export const CadetesPacientesPage = () => {
	const { data, isLoading, isError, refetch } = useMilitares();
	const [busca, setBusca] = useState('');
	const [instrutorFiltro, setInstrutorFiltro] = useState<InstrutorFiltro>('');

	const items = useMemo(() => {
		const militares = data ?? [];
		const buscaNormalizada = busca.trim().toLowerCase();

		return militares.filter((item) => {
			if (instrutorFiltro === 'sim' && !item.is_instrutor) {
				return false;
			}
			if (instrutorFiltro === 'nao' && item.is_instrutor) {
				return false;
			}

			if (!buscaNormalizada) {
				return true;
			}

			const texto = [
				item.nr_militar,
				item.nome_completo,
				item.sexo,
				item.turma,
				item.posto_graduacao,
				item.companhia,
				item.pelotao,
			]
				.join(' ')
				.toLowerCase();

			return texto.includes(buscaNormalizada);
		});
	}, [data, busca, instrutorFiltro]);

	const handleLimpar = () => {
		setBusca('');
		setInstrutorFiltro('');
	};

	if (isLoading) {
		return (
			<Stack alignItems="center" justifyContent="center" minHeight="45vh">
				<CircularProgress />
			</Stack>
		);
	}

	if (isError) {
		return (
			<EmptyState
				title="Falha ao carregar cadetes"
				description="Verifique a conexão e tente novamente."
				action={
					<Button variant="contained" onClick={() => void refetch()} sx={{ minHeight: 44, minWidth: 44 }}>
						Tentar novamente
					</Button>
				}
				height="45vh"
			/>
		);
	}

	if (!data || data.length === 0) {
		return (
			<EmptyState
				title="Nenhum cadete cadastrado"
				description="Cadastre o primeiro cadete para começar os atendimentos clínicos."
				action={
					<Button
						variant="contained"
						component={RouterLink}
						to="/cadetes/novo"
						sx={{ minHeight: 44, minWidth: 44 }}
					>
						+ Cadastrar Cadete
					</Button>
				}
				height="45vh"
			/>
		);
	}

	return (
		<Stack spacing={2}>
			<Typography variant="h5">Cadetes / Pacientes</Typography>

			<SectionCard title="Cadastro de Cadetes" subtitle="Consulta de militares cadastrados no sistema.">
				<Stack spacing={1.5}>
					<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
						<TextField
							label="Buscar"
							value={busca}
							onChange={(event) => setBusca(event.target.value)}
							sx={{ minWidth: { xs: '100%', sm: 280 }, '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
						<TextField
							select
							label="Instrutor"
							value={instrutorFiltro}
							onChange={(event) => setInstrutorFiltro(event.target.value as InstrutorFiltro)}
							sx={{ minWidth: { xs: '100%', sm: 180 }, '& .MuiInputBase-root': { minHeight: 44 } }}
						>
							<MenuItem value="">Todos</MenuItem>
							<MenuItem value="sim">Somente instrutores</MenuItem>
							<MenuItem value="nao">Somente cadetes</MenuItem>
						</TextField>
					</Stack>

					<FilterActionsRow
						refreshLabel="Atualizar lista"
						onRefresh={() => void refetch()}
						onClear={handleLimpar}
					/>

					<Typography variant="body2" color="text.secondary">
						Total encontrado: {items.length}
					</Typography>

					{items.length === 0 ? (
						<EmptyState
							title="Nenhum resultado"
							description="Ajuste os filtros para localizar cadetes."
							height="26vh"
						/>
					) : (
						<TableContainer sx={{ width: '100%', overflowX: 'auto' }}>
							<Table size="small" sx={{ minWidth: 980 }}>
								<TableHead>
									<TableRow>
										<TableCell>Nº Militar</TableCell>
										<TableCell>Nome</TableCell>
										<TableCell>Sexo</TableCell>
										<TableCell>Turma</TableCell>
										<TableCell>Posto/Graduação</TableCell>
										<TableCell>Companhia</TableCell>
										<TableCell>Pelotão</TableCell>
										<TableCell>Instrutor</TableCell>
									</TableRow>
								</TableHead>
								<TableBody>
									{items.map((item) => (
										<TableRow key={item.id}>
											<TableCell sx={{ whiteSpace: 'nowrap' }}>{item.nr_militar}</TableCell>
											<TableCell sx={{ whiteSpace: 'nowrap' }}>{item.nome_completo}</TableCell>
											<TableCell>{item.sexo || '-'}</TableCell>
											<TableCell>{item.turma || '-'}</TableCell>
											<TableCell>{item.posto_graduacao || '-'}</TableCell>
											<TableCell>{item.companhia || '-'}</TableCell>
											<TableCell>{item.pelotao || '-'}</TableCell>
											<TableCell>{item.is_instrutor ? 'Sim' : 'Não'}</TableCell>
										</TableRow>
									))}
								</TableBody>
							</Table>
						</TableContainer>
					)}
				</Stack>
			</SectionCard>
		</Stack>
	);
};
