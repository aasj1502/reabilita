import { useEffect, useMemo, useState } from 'react';

import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined';
import CalendarMonthOutlinedIcon from '@mui/icons-material/CalendarMonthOutlined';
import Diversity3OutlinedIcon from '@mui/icons-material/Diversity3Outlined';
import LoopOutlinedIcon from '@mui/icons-material/LoopOutlined';
import {
	Alert,
	Box,
	Button,
	CircularProgress,
	Dialog,
	DialogContent,
	LinearProgress,
	Stack,
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableRow,
	TableContainer,
	Typography,
} from '@mui/material';
import { alpha } from '@mui/material/styles';

import { SectionCard } from '../design-system';
import { usePainelClinico } from '../hooks/usePainelClinico';
import type { PainelClinicoResponse } from '../types/painelClinico';

const buildFallbackMeses = () => {
	const now = new Date();
	const meses = [] as PainelClinicoResponse['atendimentos_ultimos_6_meses'];

	for (let i = 5; i >= 0; i -= 1) {
		const monthDate = new Date(now.getFullYear(), now.getMonth() - i, 1);
		meses.push({
			mes: `${String(monthDate.getMonth() + 1).padStart(2, '0')}/${monthDate.getFullYear()}`,
			total: 0,
		});
	}

	return meses;
};

const fallbackPainelClinico: PainelClinicoResponse = {
	metricas: {
		cadetes: 0,
		atendimentos: 0,
		por_data: 0,
		retornos: 0,
	},
	atendimentos_ultimos_6_meses: buildFallbackMeses(),
	encaminhamentos_por_perfil: [
		{ perfil: 'Médico', percentual: 0, total: 0 },
		{ perfil: 'Fisioterapeuta', percentual: 0, total: 0 },
		{ perfil: 'Ed. Físico', percentual: 0, total: 0 },
		{ perfil: 'Nutricionista', percentual: 0, total: 0 },
		{ perfil: 'Psicopedagogo', percentual: 0, total: 0 },
	],
	ultimos_atendimentos: [],
};

const formatDate = (value: string) => {
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) {
		return value;
	}
	return date.toLocaleDateString('pt-BR');
};

type MetricPalette = 'primary' | 'success' | 'info' | 'secondary';

interface MetricCardConfig {
	key: string;
	title: string;
	value: number;
	palette: MetricPalette;
	icon: JSX.Element;
}

export const DashboardPage = () => {
	const { data, isLoading, isError, refetch } = usePainelClinico();
	const painel = data ?? fallbackPainelClinico;
	const [isSredPopupOpen, setIsSredPopupOpen] = useState(false);

	useEffect(() => {
		const shouldShowPopup = sessionStorage.getItem('show_sred_popup') === '1';
		if (shouldShowPopup) {
			setIsSredPopupOpen(true);
			sessionStorage.removeItem('show_sred_popup');
		}
	}, []);

	const maiorVolumeMensal = useMemo(() => {
		return Math.max(1, ...painel.atendimentos_ultimos_6_meses.map((item) => item.total));
	}, [painel.atendimentos_ultimos_6_meses]);

	const metricCards = useMemo<MetricCardConfig[]>(
		() => [
			{
				key: 'cadetes',
				title: 'CADETES',
				value: painel.metricas.cadetes,
				palette: 'primary',
				icon: <Diversity3OutlinedIcon fontSize="small" />,
			},
			{
				key: 'atendimentos',
				title: 'ATENDIMENTOS',
				value: painel.metricas.atendimentos,
				palette: 'success',
				icon: <AssignmentOutlinedIcon fontSize="small" />,
			},
			{
				key: 'hoje',
				title: 'HOJE',
				value: painel.metricas.por_data,
				palette: 'info',
				icon: <CalendarMonthOutlinedIcon fontSize="small" />,
			},
			{
				key: 'retornos',
				title: 'RETORNOS',
				value: painel.metricas.retornos,
				palette: 'secondary',
				icon: <LoopOutlinedIcon fontSize="small" />,
			},
		],
		[
			painel.metricas.atendimentos,
			painel.metricas.cadetes,
			painel.metricas.por_data,
			painel.metricas.retornos,
		],
	);

	if (isLoading) {
		return (
			<Stack alignItems="center" justifyContent="center" minHeight="45vh">
				<CircularProgress />
			</Stack>
		);
	}

	return (
		<Stack spacing={2}>
			<Dialog open={isSredPopupOpen} onClose={() => setIsSredPopupOpen(false)} maxWidth="md" fullWidth>
				<DialogContent sx={{ p: 0 }}>
					<Box
						component="img"
						src="/pop_pup_srad.png"
						alt="Protocolo S-RED"
						sx={{ width: '100%', height: 'auto', display: 'block' }}
					/>
					<Stack direction="row" justifyContent="flex-end" sx={{ p: 2 }}>
						<Button variant="contained" onClick={() => setIsSredPopupOpen(false)} sx={{ minHeight: 44, minWidth: 44 }}>
							Fechar
						</Button>
					</Stack>
				</DialogContent>
			</Dialog>

			<Typography variant="h4" fontWeight={700} sx={{ fontSize: { xs: '1.75rem', sm: '2.125rem' } }}>
				Painel Clínico
			</Typography>
			<Typography variant="subtitle1" color="text.secondary">
				Protocolo S-RED • Atendimento Multidisciplinar
			</Typography>

			{isError ? (
				<Alert
					severity="warning"
					action={
						<Button color="inherit" size="small" onClick={() => void refetch()}>
							Tentar novamente
						</Button>
					}
				>
					Não foi possível obter os dados do backend. Exibindo fallback previsível do painel.
				</Alert>
			) : null}

			<Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} useFlexGap flexWrap="wrap">
				{metricCards.map((metric) => (
					<SectionCard
						key={metric.key}
						title={
							<Typography variant="overline" color="text.secondary" fontWeight={700}>
								{metric.title}
							</Typography>
						}
						action={
							<Box
								sx={(theme) => ({
									width: 32,
									height: 32,
									borderRadius: 1,
									display: 'flex',
									alignItems: 'center',
									justifyContent: 'center',
									color: theme.palette[metric.palette].main,
									backgroundColor: alpha(theme.palette[metric.palette].main, 0.2),
								})}
							>
								{metric.icon}
							</Box>
						}
						sx={{ flex: '1 1 240px' }}
					>
						<Typography variant="h4" fontWeight={700} color={`${metric.palette}.main`}>
							{metric.value}
						</Typography>
					</SectionCard>
				))}
			</Stack>

			<Stack direction={{ xs: 'column', xl: 'row' }} spacing={2}>
				<SectionCard title="Atendimentos nos últimos 6 meses" sx={{ flex: 2 }}>
					<Box sx={{ width: '100%', overflowX: 'auto', pb: 0.5 }}>
						<Stack
							direction="row"
							alignItems="flex-end"
							spacing={1}
							height={{ xs: 200, sm: 220 }}
							minWidth={{ xs: 360, sm: 0 }}
						>
							{painel.atendimentos_ultimos_6_meses.map((item) => {
								const alturaBarra = Math.max(12, (item.total / maiorVolumeMensal) * 150);
								return (
									<Stack
										key={item.mes}
										alignItems="center"
										justifyContent="flex-end"
										flex={1}
										spacing={0.5}
										sx={{ minWidth: { xs: 48, sm: 0 } }}
									>
										<Typography variant="caption" color="text.secondary">
											{item.total}
										</Typography>
										<Stack
											sx={{
												height: `${alturaBarra}px`,
												width: '100%',
												maxWidth: { xs: 42, sm: 52 },
												bgcolor: 'primary.main',
												borderRadius: 1,
											}}
										/>
										<Typography variant="caption">{item.mes}</Typography>
									</Stack>
								);
							})}
						</Stack>
					</Box>
				</SectionCard>

				<SectionCard title="Encaminhamentos" sx={{ flex: 1 }}>
					<Stack spacing={1.5}>
						{painel.encaminhamentos_por_perfil.map((item) => (
							<Stack key={item.perfil} spacing={0.5}>
								<Stack direction="row" justifyContent="space-between">
									<Typography variant="body2">{item.perfil}</Typography>
									<Typography variant="body2" color="text.secondary">
										{item.total} ({Math.round(item.percentual)}%)
									</Typography>
								</Stack>
								<LinearProgress
									variant="determinate"
									value={Math.min(item.percentual, 100)}
									sx={{ height: 8, borderRadius: 6 }}
								/>
							</Stack>
						))}
					</Stack>
				</SectionCard>
			</Stack>

			<SectionCard
				title="Últimos atendimentos"
				action={
					<Typography variant="body2" color="success.main" fontWeight={700}>
						Ver todos →
					</Typography>
				}
			>
				<TableContainer sx={{ width: '100%', overflowX: 'auto' }}>
					<Table size="small" sx={{ minWidth: 680 }}>
						<TableHead>
							<TableRow>
								<TableCell sx={{ whiteSpace: 'nowrap' }}>CADETE</TableCell>
								<TableCell sx={{ whiteSpace: 'nowrap' }}>DATA</TableCell>
								<TableCell sx={{ whiteSpace: 'nowrap' }}>TIPO</TableCell>
								<TableCell sx={{ whiteSpace: 'nowrap' }}>LESÃO</TableCell>
								<TableCell sx={{ whiteSpace: 'nowrap' }}>CONDUTA</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{painel.ultimos_atendimentos.length === 0 ? (
								<TableRow>
									<TableCell colSpan={5} sx={{ py: 5 }}>
										<Typography variant="body2" color="text.secondary" textAlign="center">
											Nenhum atendimento registrado ainda.
										</Typography>
									</TableCell>
								</TableRow>
							) : (
								painel.ultimos_atendimentos.map((item) => (
									<TableRow key={`${item.cadete}-${item.data}-${item.tipo}`}>
										<TableCell sx={{ whiteSpace: 'nowrap' }}>{item.cadete}</TableCell>
										<TableCell sx={{ whiteSpace: 'nowrap' }}>{formatDate(item.data)}</TableCell>
										<TableCell sx={{ whiteSpace: 'nowrap' }}>{item.tipo}</TableCell>
										<TableCell sx={{ whiteSpace: 'nowrap' }}>{item.lesao}</TableCell>
										<TableCell sx={{ minWidth: 220 }}>{item.conduta}</TableCell>
									</TableRow>
								))
							)}
						</TableBody>
					</Table>
				</TableContainer>
			</SectionCard>
		</Stack>
	);
};
