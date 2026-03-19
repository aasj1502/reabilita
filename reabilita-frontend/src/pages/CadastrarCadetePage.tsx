import { useState, type FormEvent } from 'react';

import {
	Alert,
	Button,
	Checkbox,
	FormControlLabel,
	Stack,
	TextField,
	Typography,
} from '@mui/material';
import axios from 'axios';
import { Link as RouterLink, useNavigate } from 'react-router-dom';

import { SectionCard, useNotify } from '../design-system';
import { useCreateMilitar } from '../hooks/usePessoal';
import type { CreateMilitarPayload } from '../types/pessoal';

interface FormState {
	nr_militar: string;
	nome_completo: string;
	sexo: string;
	turma: string;
	posto_graduacao: string;
	arma_quadro_servico: string;
	curso: string;
	companhia: string;
	pelotao: string;
	is_instrutor: boolean;
}

const initialFormState: FormState = {
	nr_militar: '',
	nome_completo: '',
	sexo: '',
	turma: '',
	posto_graduacao: '',
	arma_quadro_servico: '',
	curso: '',
	companhia: '',
	pelotao: '',
	is_instrutor: false,
};

const getErrorMessage = (error: unknown): string => {
	if (axios.isAxiosError(error)) {
		const detail = error.response?.data?.detail;
		if (typeof detail === 'string' && detail.trim()) {
			return detail;
		}
	}

	return 'Não foi possível cadastrar o cadete.';
};

export const CadastrarCadetePage = () => {
	const navigate = useNavigate();
	const notify = useNotify();
	const createMilitarMutation = useCreateMilitar();
	const [formData, setFormData] = useState<FormState>(initialFormState);
	const [submitError, setSubmitError] = useState<string | null>(null);

	const handleChange = (field: keyof FormState, value: string | boolean) => {
		setFormData((current) => ({
			...current,
			[field]: value,
		}));
	};

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setSubmitError(null);

		const payload: CreateMilitarPayload = {
			nr_militar: formData.nr_militar.trim(),
			nome_completo: formData.nome_completo.trim(),
			sexo: formData.sexo.trim(),
			turma: formData.turma.trim(),
			posto_graduacao: formData.posto_graduacao.trim(),
			arma_quadro_servico: formData.arma_quadro_servico.trim(),
			curso: formData.curso.trim(),
			companhia: formData.companhia.trim(),
			pelotao: formData.pelotao.trim(),
			is_instrutor: formData.is_instrutor,
		};

		try {
			await createMilitarMutation.mutateAsync(payload);
			notify('Cadete cadastrado com sucesso.', 'success');
			setFormData(initialFormState);
		} catch (error) {
			const message = getErrorMessage(error);
			setSubmitError(message);
			notify(message, 'error');
		}
	};

	return (
		<Stack spacing={2}>
			<Typography variant="h5">+ Cadastrar Cadete</Typography>

			<SectionCard title="Novo Cadastro" subtitle="Preencha os dados do cadete para habilitar atendimentos clínicos.">
				<Stack component="form" spacing={1.5} onSubmit={handleSubmit}>
					<Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
						<TextField
							label="Nº Militar"
							value={formData.nr_militar}
							onChange={(event) => handleChange('nr_militar', event.target.value)}
							required
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
						<TextField
							label="Nome Completo"
							value={formData.nome_completo}
							onChange={(event) => handleChange('nome_completo', event.target.value)}
							required
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
					</Stack>

					<Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
						<TextField
							label="Sexo"
							value={formData.sexo}
							onChange={(event) => handleChange('sexo', event.target.value)}
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
						<TextField
							label="Turma"
							value={formData.turma}
							onChange={(event) => handleChange('turma', event.target.value)}
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
					</Stack>

					<Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
						<TextField
							label="Posto/Graduação"
							value={formData.posto_graduacao}
							onChange={(event) => handleChange('posto_graduacao', event.target.value)}
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
						<TextField
							label="Arma/Quadro/Serviço"
							value={formData.arma_quadro_servico}
							onChange={(event) => handleChange('arma_quadro_servico', event.target.value)}
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
					</Stack>

					<Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
						<TextField
							label="Curso"
							value={formData.curso}
							onChange={(event) => handleChange('curso', event.target.value)}
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
						<TextField
							label="Companhia"
							value={formData.companhia}
							onChange={(event) => handleChange('companhia', event.target.value)}
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
						<TextField
							label="Pelotão"
							value={formData.pelotao}
							onChange={(event) => handleChange('pelotao', event.target.value)}
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>
					</Stack>

					<FormControlLabel
						control={
							<Checkbox
								checked={formData.is_instrutor}
								onChange={(event) => handleChange('is_instrutor', event.target.checked)}
							/>
						}
						label="Marcar como Instrutor"
					/>

					{submitError ? <Alert severity="error">{submitError}</Alert> : null}

					<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
						<Button
							type="submit"
							variant="contained"
							disabled={createMilitarMutation.isPending}
							sx={{ minHeight: 44, minWidth: 44 }}
						>
							{createMilitarMutation.isPending ? 'Salvando...' : 'Salvar Cadete'}
						</Button>
						<Button
							variant="outlined"
							component={RouterLink}
							to="/cadetes-pacientes"
							sx={{ minHeight: 44, minWidth: 44 }}
						>
							Ver Cadetes
						</Button>
						<Button
							variant="text"
							type="button"
							onClick={() => navigate('/dashboard')}
							sx={{ minHeight: 44, minWidth: 44 }}
						>
							Voltar ao Dashboard
						</Button>
					</Stack>
				</Stack>
			</SectionCard>
		</Stack>
	);
};
