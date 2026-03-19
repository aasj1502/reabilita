import { useEffect, useMemo, useState, type FormEvent } from 'react';

import {
	Alert,
	Button,
	Checkbox,
	Chip,
	CircularProgress,
	FormControlLabel,
	MenuItem,
	Stack,
	TextField,
	Typography,
} from '@mui/material';
import axios from 'axios';

import { SectionCard, useNotify } from '../design-system';
import { useAtendimentoReferencias, useCreateAtendimento } from '../hooks/useAtendimentos';
import { useMilitares, useProfissionaisSaude } from '../hooks/usePessoal';
import { searchCid10, searchCido } from '../services/atendimentos.service';
import type {
	CidAutocompleteItem,
	CreateAtendimentoPayload,
	DecisaoSred,
	Lateralidade,
	OrigemLesao,
	TipoAtendimento,
	TipoLesao,
} from '../types/atendimento';

type TipoAtendimentoForm = TipoAtendimento | '';
type TipoLesaoForm = TipoLesao | '';
type OrigemLesaoForm = OrigemLesao | '';
type DecisaoSredForm = DecisaoSred | '';

interface FormState {
	cadete_id: string;
	medico_id: string;
	tipo_atendimento: TipoAtendimentoForm;
	tipo_lesao: TipoLesaoForm;
	origem_lesao: OrigemLesaoForm;
	segmento_corporal: string;
	estrutura_anatomica: string;
	localizacao_lesao: string;
	decisao_sred: DecisaoSredForm;
	classificacao_atividade: string;
	tipo_atividade: string;
	tfm_taf: string;
	modalidade_esportiva: string;
	conduta_terapeutica: string;
	solicitar_exames_complementares: boolean;
	exames_complementares: string[];
	encaminhamentos_multidisciplinares: string[];
	disposicao_cadete: string[];
	codigo_cido: string;
	codigo_cid10: string;
	cid10_secundario_input: string;
	cid10_secundarios: string[];
	notas_clinicas: string;
}

const fallbackTipoLesaoOptions: TipoLesao[] = [
	'Óssea',
	'Articular',
	'Muscular',
	'Tendinosa',
	'Neurológica',
];

const initialFormState: FormState = {
	cadete_id: '',
	medico_id: '',
	tipo_atendimento: 'Inicial',
	tipo_lesao: '',
	origem_lesao: 'Outra',
	segmento_corporal: '',
	estrutura_anatomica: '',
	localizacao_lesao: '',
	decisao_sred: '',
	classificacao_atividade: 'Não informado',
	tipo_atividade: 'Não informado',
	tfm_taf: 'Não informado',
	modalidade_esportiva: 'Não informado',
	conduta_terapeutica: 'Não definido',
	solicitar_exames_complementares: false,
	exames_complementares: [],
	encaminhamentos_multidisciplinares: [],
	disposicao_cadete: [],
	codigo_cido: '',
	codigo_cid10: '',
	cid10_secundario_input: '',
	cid10_secundarios: [],
	notas_clinicas: '',
};

const formatDateBr = (date: Date): string => {
	return date.toLocaleDateString('pt-BR');
};

const formatTimeBr = (date: Date): string => {
	return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

const getErrorMessage = (error: unknown): string => {
	if (axios.isAxiosError(error)) {
		const detail = error.response?.data?.detail;
		if (typeof detail === 'string' && detail.trim()) {
			return detail;
		}
	}

	return 'Não foi possível registrar o atendimento.';
};

export const NovoAtendimentoPage = () => {
	const notify = useNotify();
	const [carimboSistema] = useState<Date>(() => new Date());
	const createAtendimentoMutation = useCreateAtendimento();
	const {
		data: militares,
		isLoading: isLoadingMilitares,
		isError: isErrorMilitares,
		refetch: refetchMilitares,
	} = useMilitares();
	const {
		data: profissionais,
		isLoading: isLoadingProfissionais,
		isError: isErrorProfissionais,
		refetch: refetchProfissionais,
	} = useProfissionaisSaude();
	const {
		data: referencias,
		isLoading: isLoadingReferencias,
		isError: isErrorReferencias,
		refetch: refetchReferencias,
	} = useAtendimentoReferencias();

	const [formData, setFormData] = useState<FormState>(initialFormState);
	const [submitError, setSubmitError] = useState<string | null>(null);
	const [cid10PrincipalSugestoes, setCid10PrincipalSugestoes] = useState<CidAutocompleteItem[]>([]);
	const [cid10SecundarioSugestoes, setCid10SecundarioSugestoes] = useState<CidAutocompleteItem[]>([]);
	const [cidoSugestoes, setCidoSugestoes] = useState<CidAutocompleteItem[]>([]);

	const medicos = useMemo(() => {
		const list = profissionais ?? [];
		const filtrados = list.filter((item) => {
			const especialidade = item.especialidade.toLowerCase();
			return especialidade === 'médico' || especialidade === 'medico';
		});
		return filtrados.length > 0 ? filtrados : list;
	}, [profissionais]);

	useEffect(() => {
		if (!formData.medico_id && medicos.length > 0) {
			setFormData((current) => ({
				...current,
				medico_id: String(medicos[0].id),
			}));
		}
	}, [medicos, formData.medico_id]);

	useEffect(() => {
		if (!referencias) {
			return;
		}

		const resolveValue = (currentValue: string, options: string[], fallbackValue: string): string => {
			if (options.includes(currentValue)) {
				return currentValue;
			}
			return options[0] || fallbackValue;
		};

		setFormData((current) => ({
			...current,
			origem_lesao: resolveValue(current.origem_lesao, referencias.origem_lesao_options, 'Outra') as OrigemLesaoForm,
			classificacao_atividade: resolveValue(
				current.classificacao_atividade,
				referencias.classificacao_atividade_options,
				'Não informado',
			),
			tipo_atividade: resolveValue(current.tipo_atividade, referencias.tipo_atividade_options, 'Não informado'),
			tfm_taf: resolveValue(current.tfm_taf, referencias.tfm_taf_options, 'Não informado'),
			modalidade_esportiva: resolveValue(
				current.modalidade_esportiva,
				referencias.modalidade_esportiva_options,
				'Não informado',
			),
			conduta_terapeutica: resolveValue(
				current.conduta_terapeutica,
				referencias.conduta_terapeutica_options,
				'Não definido',
			),
			decisao_sred: (referencias.decisao_sred_options ?? []).includes(current.decisao_sred as DecisaoSred)
				? current.decisao_sred
				: '',
		}));
	}, [referencias]);

	useEffect(() => {
		let ativo = true;
		const termo = formData.codigo_cid10.trim();
		if (termo.length < 2) {
			setCid10PrincipalSugestoes([]);
			return;
		}

		const timer = window.setTimeout(async () => {
			try {
				const items = await searchCid10(termo);
				if (ativo) {
					setCid10PrincipalSugestoes(items);
				}
			} catch {
				if (ativo) {
					setCid10PrincipalSugestoes([]);
				}
			}
		}, 250);

		return () => {
			ativo = false;
			window.clearTimeout(timer);
		};
	}, [formData.codigo_cid10]);

	useEffect(() => {
		let ativo = true;
		const termo = formData.codigo_cido.trim();
		if (termo.length < 2) {
			setCidoSugestoes([]);
			return;
		}

		const timer = window.setTimeout(async () => {
			try {
				const items = await searchCido(termo);
				if (ativo) {
					setCidoSugestoes(items);
				}
			} catch {
				if (ativo) {
					setCidoSugestoes([]);
				}
			}
		}, 250);

		return () => {
			ativo = false;
			window.clearTimeout(timer);
		};
	}, [formData.codigo_cido]);

	useEffect(() => {
		let ativo = true;
		const termo = formData.cid10_secundario_input.trim();
		if (termo.length < 2) {
			setCid10SecundarioSugestoes([]);
			return;
		}

		const timer = window.setTimeout(async () => {
			try {
				const items = await searchCid10(termo);
				if (ativo) {
					setCid10SecundarioSugestoes(items);
				}
			} catch {
				if (ativo) {
					setCid10SecundarioSugestoes([]);
				}
			}
		}, 250);

		return () => {
			ativo = false;
			window.clearTimeout(timer);
		};
	}, [formData.cid10_secundario_input]);

	const tipoAtendimentoOptions = referencias?.tipo_atendimento_options ?? ['Inicial', 'Retorno'];
	const tipoLesaoOptions = referencias?.tipo_lesao_options ?? fallbackTipoLesaoOptions;
	const origemLesaoOptions = referencias?.origem_lesao_options ?? ['Por Estresse', 'Traumática', 'Outra'];
	const decisaoSredOptions = referencias?.decisao_sred_options ?? ['S-RED Positivo', 'S-RED Negativo'];

	const segmentoOptions = useMemo(() => {
		if (!formData.tipo_lesao) {
			return [];
		}
		return referencias?.segmentos_por_tipo_lesao?.[formData.tipo_lesao] ?? [];
	}, [formData.tipo_lesao, referencias]);

	const estruturaOptions = useMemo(() => {
		if (!formData.tipo_lesao || !formData.segmento_corporal) {
			return [];
		}
		return (
			referencias?.estruturas_por_tipo_segmento?.[formData.tipo_lesao]?.[formData.segmento_corporal] ?? []
		);
	}, [formData.tipo_lesao, formData.segmento_corporal, referencias]);

	const localizacaoOptions = useMemo(() => {
		if (!formData.tipo_lesao || !formData.segmento_corporal) {
			return [];
		}
		return (
			referencias?.localizacoes_por_tipo_segmento?.[formData.tipo_lesao]?.[formData.segmento_corporal] ??
			[]
		);
	}, [formData.tipo_lesao, formData.segmento_corporal, referencias]);

	const classificacaoAtividadeOptions = referencias?.classificacao_atividade_options ?? ['Não informado'];
	const tipoAtividadeOptions = referencias?.tipo_atividade_options ?? ['Não informado'];
	const tfmTafOptions = referencias?.tfm_taf_options ?? ['Não informado'];
	const modalidadeOptions = referencias?.modalidade_esportiva_options ?? ['Não informado'];
	const condutaOptions = referencias?.conduta_terapeutica_options ?? [
		'Não definido',
		'Cirurgico',
		'Conservador',
		'Pós-operatório',
		'Aguardando Exame',
	];
	const examesComplementaresOptions = referencias?.exames_complementares_options ?? [
		'RX',
		'USG',
		'TC',
		'RM',
		'DEXA',
		'Sangue',
	];
	const encaminhamentoOptions = referencias?.encaminhamentos_options ?? [
		'Fisioterapia',
		'Educador Físico',
		'Nutricionista',
		'Psicopedagogo',
	];
	const disposicaoOptions = referencias?.disposicao_options ?? [
		'Dispensado',
		'Regime Limitado',
		'Alta',
		'Risco Cirúrgico',
		'VCL',
	];

	const gatilhoSredPorLesaoOrigem =
		formData.tipo_lesao === 'Óssea' && formData.origem_lesao === 'Por Estresse';
	const gatilhoSredPorCid10 = formData.codigo_cid10.trim().toUpperCase().startsWith('M84.3');
	const exigeDecisaoSred = gatilhoSredPorLesaoOrigem || gatilhoSredPorCid10;

	useEffect(() => {
		if (!exigeDecisaoSred && formData.decisao_sred) {
			setFormData((current) => ({
				...current,
				decisao_sred: '',
			}));
		}
	}, [exigeDecisaoSred, formData.decisao_sred]);

	const inferLateralidade = (segmento: string, estrutura: string): Lateralidade => {
		const lateralidadeByEstrutura = referencias?.lateralidade_por_estrutura ?? {};
		const estruturaTrim = estrutura.trim();
		if (estruturaTrim && lateralidadeByEstrutura[estruturaTrim]) {
			return lateralidadeByEstrutura[estruturaTrim];
		}

		const estruturaNormalizada = estruturaTrim.toLowerCase();
		if (estruturaNormalizada.includes('direit')) {
			return 'Direita';
		}
		if (estruturaNormalizada.includes('esquerd')) {
			return 'Esquerda';
		}

		const segmentoNormalizado = segmento.trim().toLowerCase();
		if (
			segmentoNormalizado === 'coluna' ||
			segmentoNormalizado === 'bacia' ||
			segmentoNormalizado === 'tórax' ||
			segmentoNormalizado === 'torax' ||
			segmentoNormalizado === 'core'
		) {
			return 'Não é o caso';
		}

		return 'Bilateral';
	};

	const toggleListOption = (
		field: 'exames_complementares' | 'encaminhamentos_multidisciplinares' | 'disposicao_cadete',
		option: string,
		checked: boolean,
	) => {
		setFormData((current) => {
			const atual = current[field];
			const next = checked
				? atual.includes(option)
					? atual
					: [...atual, option]
				: atual.filter((item) => item !== option);

			return {
				...current,
				[field]: next,
			};
		});
	};

	const handleAdicionarCid10Secundario = () => {
		const codigo = formData.cid10_secundario_input.trim().toUpperCase();
		if (!codigo) {
			return;
		}

		if (codigo === formData.codigo_cid10.trim().toUpperCase()) {
			notify('O CID-10 secundário não pode ser igual ao código principal.', 'warning');
			return;
		}

		if (formData.cid10_secundarios.some((item) => item.toUpperCase() === codigo)) {
			return;
		}

		setFormData((current) => ({
			...current,
			cid10_secundarios: [...current.cid10_secundarios, codigo],
			cid10_secundario_input: '',
		}));
	};

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setSubmitError(null);

		if (!formData.cadete_id) {
			const message = 'Selecione o cadete/paciente antes de registrar.';
			setSubmitError(message);
			notify(message, 'error');
			return;
		}

		if (!formData.medico_id) {
			const message = 'Nenhum médico disponível para vínculo do atendimento.';
			setSubmitError(message);
			notify(message, 'error');
			return;
		}

		if (!formData.tipo_atendimento) {
			const message = 'Informe o tipo de atendimento (Inicial ou Retorno).';
			setSubmitError(message);
			notify(message, 'error');
			return;
		}

		if (!formData.tipo_lesao || !formData.segmento_corporal || !formData.estrutura_anatomica) {
			const message =
				'Preencha Tipo de Lesão, Segmento Corporal e Estrutura Lesionada para classificar o caso.';
			setSubmitError(message);
			notify(message, 'error');
			return;
		}

		if (exigeDecisaoSred && !formData.decisao_sred) {
			const message = 'Selecione a Decisão S-RED (S-RED Positivo ou S-RED Negativo).';
			setSubmitError(message);
			notify(message, 'error');
			return;
		}

		const payload: CreateAtendimentoPayload = {
			cadete_id: Number(formData.cadete_id),
			medico_id: Number(formData.medico_id),
			tipo_atendimento: formData.tipo_atendimento,
			tipo_lesao: formData.tipo_lesao,
			origem_lesao: (formData.origem_lesao || 'Outra') as OrigemLesao,
			segmento_corporal: formData.segmento_corporal.trim(),
			estrutura_anatomica: formData.estrutura_anatomica.trim(),
			localizacao_lesao: formData.localizacao_lesao.trim() || formData.estrutura_anatomica.trim(),
			lateralidade: inferLateralidade(formData.segmento_corporal, formData.estrutura_anatomica),
			decisao_sred: exigeDecisaoSred ? formData.decisao_sred : '',
			classificacao_atividade: formData.classificacao_atividade,
			tipo_atividade: formData.tipo_atividade,
			tfm_taf: formData.tfm_taf,
			modalidade_esportiva: formData.modalidade_esportiva,
			conduta_terapeutica: formData.conduta_terapeutica,
			solicitar_exames_complementares: formData.solicitar_exames_complementares,
			exames_complementares: formData.solicitar_exames_complementares
				? formData.exames_complementares
				: [],
			encaminhamentos_multidisciplinares: formData.encaminhamentos_multidisciplinares,
			disposicao_cadete: formData.disposicao_cadete,
			codigo_cid10: formData.codigo_cid10.trim(),
			cid10_secundarios: formData.cid10_secundarios,
			codigo_cido: formData.codigo_cido.trim() || null,
			notas_clinicas: formData.notas_clinicas.trim(),
		};

		try {
			await createAtendimentoMutation.mutateAsync(payload);
			notify('Atendimento registrado com sucesso.', 'success');
			setFormData((current) => ({
				...initialFormState,
				cadete_id: current.cadete_id,
				medico_id: current.medico_id,
			}));
			setCid10PrincipalSugestoes([]);
			setCid10SecundarioSugestoes([]);
			setCidoSugestoes([]);
		} catch (error) {
			const message = getErrorMessage(error);
			setSubmitError(message);
			notify(message, 'error');
		}
	};

	if (isLoadingMilitares || isLoadingProfissionais || isLoadingReferencias) {
		return (
			<Stack alignItems="center" justifyContent="center" minHeight="45vh">
				<CircularProgress />
			</Stack>
		);
	}

	if (isErrorMilitares || isErrorProfissionais || isErrorReferencias) {
		return (
			<SectionCard title="Falha ao carregar dados de apoio">
				<Stack spacing={1.5}>
					<Typography color="text.secondary">
						Não foi possível carregar cadetes, profissionais e referências clínicas.
					</Typography>
					<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
						<Button variant="contained" onClick={() => void refetchMilitares()} sx={{ minHeight: 44, minWidth: 44 }}>
							Recarregar Cadetes
						</Button>
						<Button variant="outlined" onClick={() => void refetchProfissionais()} sx={{ minHeight: 44, minWidth: 44 }}>
							Recarregar Profissionais
						</Button>
						<Button variant="outlined" onClick={() => void refetchReferencias()} sx={{ minHeight: 44, minWidth: 44 }}>
							Recarregar Referências
						</Button>
					</Stack>
				</Stack>
			</SectionCard>
		);
	}

	return (
		<Stack spacing={2}>
			<Typography variant="h5">Novo Atendimento</Typography>
			<Typography variant="subtitle2" color="text.secondary">
				Protocolo S-RED • Registro clínico
			</Typography>

			<Stack component="form" spacing={2} onSubmit={handleSubmit}>
				<SectionCard title="1 · Identificação">
					<Stack spacing={1.5}>
						<Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
							<TextField
								select
								label="Cadete / Paciente"
								value={formData.cadete_id}
								onChange={(event) => setFormData((current) => ({ ...current, cadete_id: event.target.value }))}
								required
								fullWidth
								helperText={militares && militares.length === 0 ? 'Cadastre um cadete primeiro' : undefined}
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{(militares ?? []).map((item) => (
									<MenuItem key={item.id} value={String(item.id)}>
										{item.nome_completo}
									</MenuItem>
								))}
							</TextField>

							<TextField
								select
								label="Tipo"
								value={formData.tipo_atendimento}
								onChange={(event) =>
									setFormData((current) => ({
										...current,
										tipo_atendimento: event.target.value as TipoAtendimentoForm,
									}))
								}
								required
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{tipoAtendimentoOptions.map((item) => (
									<MenuItem key={item} value={item}>
										{item}
									</MenuItem>
								))}
							</TextField>
						</Stack>

						<Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
							<TextField
								label="Data"
								value={formatDateBr(carimboSistema)}
								InputProps={{ readOnly: true }}
								required
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							/>
							<TextField
								label="Hora"
								value={formatTimeBr(carimboSistema)}
								InputProps={{ readOnly: true }}
								required
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							/>
						</Stack>
					</Stack>
				</SectionCard>

				<SectionCard title="2 · Classificação da Lesão">
					<Stack spacing={1.5}>
						<Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
							<TextField
								select
								label="Tipo de Lesão"
								value={formData.tipo_lesao}
								onChange={(event) =>
									setFormData((current) => ({
										...current,
										tipo_lesao: event.target.value as TipoLesaoForm,
										segmento_corporal: '',
										estrutura_anatomica: '',
										localizacao_lesao: '',
									}))
								}
								required
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{tipoLesaoOptions.map((item) => (
									<MenuItem key={item} value={item}>
										{item}
									</MenuItem>
								))}
							</TextField>

							<TextField
								select
								label="Origem da Lesão"
								value={formData.origem_lesao}
								onChange={(event) =>
									setFormData((current) => ({
										...current,
										origem_lesao: event.target.value as OrigemLesaoForm,
									}))
								}
								required
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{origemLesaoOptions.map((item) => (
									<MenuItem key={item} value={item}>
										{item}
									</MenuItem>
								))}
							</TextField>

							<TextField
								select
								label="Segmento Corporal"
								value={formData.segmento_corporal}
								onChange={(event) =>
									setFormData((current) => ({
										...current,
										segmento_corporal: event.target.value,
										estrutura_anatomica: '',
										localizacao_lesao: '',
									}))
								}
								required
								disabled={!formData.tipo_lesao}
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{segmentoOptions.map((item) => (
									<MenuItem key={item} value={item}>
										{item}
									</MenuItem>
								))}
							</TextField>
						</Stack>

						<TextField
							select
							label="Estrutura Lesionada"
							value={formData.estrutura_anatomica}
							onChange={(event) =>
								setFormData((current) => ({
									...current,
									estrutura_anatomica: event.target.value,
									localizacao_lesao: current.localizacao_lesao || event.target.value,
								}))
							}
							required
							disabled={!formData.segmento_corporal}
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						>
							{estruturaOptions.map((item) => (
								<MenuItem key={item} value={item}>
									{item}
								</MenuItem>
							))}
						</TextField>

						<TextField
							label="Localização / Sítio da Lesão"
							value={formData.localizacao_lesao}
							onChange={(event) =>
								setFormData((current) => ({ ...current, localizacao_lesao: event.target.value }))
							}
							required
							placeholder="Ex: Porção médio-distal, inserção calcaneana"
							fullWidth
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>

						{localizacaoOptions.length > 0 ? (
							<Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
								{localizacaoOptions.slice(0, 8).map((item) => (
									<Button
										key={item}
										type="button"
										variant="outlined"
										size="small"
										onClick={() =>
											setFormData((current) => ({ ...current, localizacao_lesao: item }))
										}
										sx={{ minHeight: 32 }}
									>
										{item}
									</Button>
								))}
							</Stack>
						) : null}

						{exigeDecisaoSred ? (
							<Stack spacing={1}>
								<Typography variant="subtitle2">Decisão S-RED</Typography>
								<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
									{decisaoSredOptions.map((item) => {
										const isSelected = formData.decisao_sred === item;
										return (
											<Button
												key={item}
												type="button"
												variant={isSelected ? 'contained' : 'outlined'}
												onClick={() =>
													setFormData((current) => ({
														...current,
														decisao_sred: item,
													}))
												}
												sx={{ minHeight: 44, minWidth: 44 }}
											>
												{item}
											</Button>
										);
									})}
								</Stack>
							</Stack>
						) : null}
					</Stack>
				</SectionCard>

				<SectionCard title="3 · Atividade e Contexto">
					<Stack spacing={1.5}>
						<Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
							<TextField
								select
								label="Classificação da Atividade"
								value={formData.classificacao_atividade}
								onChange={(event) =>
									setFormData((current) => ({ ...current, classificacao_atividade: event.target.value }))
								}
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{classificacaoAtividadeOptions.map((item) => (
									<MenuItem key={item} value={item}>
										{item}
									</MenuItem>
								))}
							</TextField>

							<TextField
								select
								label="Tipo de Atividade"
								value={formData.tipo_atividade}
								onChange={(event) =>
									setFormData((current) => ({ ...current, tipo_atividade: event.target.value }))
								}
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{tipoAtividadeOptions.map((item) => (
									<MenuItem key={item} value={item}>
										{item}
									</MenuItem>
								))}
							</TextField>

							<TextField
								select
								label="TFM / TAF"
								value={formData.tfm_taf}
								onChange={(event) =>
									setFormData((current) => ({ ...current, tfm_taf: event.target.value }))
								}
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{tfmTafOptions.map((item) => (
									<MenuItem key={item} value={item}>
										{item}
									</MenuItem>
								))}
							</TextField>
						</Stack>

						<Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
							<TextField
								select
								label="Modalidade Esportiva"
								value={formData.modalidade_esportiva}
								onChange={(event) =>
									setFormData((current) => ({ ...current, modalidade_esportiva: event.target.value }))
								}
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{modalidadeOptions.map((item) => (
									<MenuItem key={item} value={item}>
										{item}
									</MenuItem>
								))}
							</TextField>

							<TextField
								select
								label="Conduta Terapêutica"
								value={formData.conduta_terapeutica}
								onChange={(event) =>
									setFormData((current) => ({ ...current, conduta_terapeutica: event.target.value }))
								}
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							>
								{condutaOptions.map((item) => (
									<MenuItem key={item} value={item}>
										{item}
									</MenuItem>
								))}
							</TextField>
						</Stack>
					</Stack>
				</SectionCard>

				<SectionCard title="4 · Exames Complementares e Encaminhamentos">
					<Stack spacing={1.5}>
						<FormControlLabel
							control={
								<Checkbox
									checked={formData.solicitar_exames_complementares}
									onChange={(event) =>
										setFormData((current) => ({
											...current,
											solicitar_exames_complementares: event.target.checked,
											exames_complementares: event.target.checked
												? current.exames_complementares
												: [],
										}))
									}
								/>
							}
							label="Solicitar Exames Complementares"
						/>

						{formData.solicitar_exames_complementares ? (
							<>
								<Typography variant="subtitle2">Exames Complementares</Typography>
								<Stack direction="row" useFlexGap flexWrap="wrap" spacing={1}>
									{examesComplementaresOptions.map((item) => (
										<FormControlLabel
											key={item}
											control={
												<Checkbox
													checked={formData.exames_complementares.includes(item)}
													onChange={(event) =>
														toggleListOption(
															'exames_complementares',
															item,
															event.target.checked,
														)
													}
												/>
											}
											label={item}
										/>
									))}
								</Stack>
							</>
						) : null}

						<Typography variant="subtitle2">Encaminhamentos Multidisciplinares</Typography>
						<Stack direction="row" useFlexGap flexWrap="wrap" spacing={1}>
							{encaminhamentoOptions.map((item) => (
								<FormControlLabel
									key={item}
									control={
										<Checkbox
											checked={formData.encaminhamentos_multidisciplinares.includes(item)}
											onChange={(event) =>
												toggleListOption(
													'encaminhamentos_multidisciplinares',
													item,
													event.target.checked,
												)
											}
										/>
									}
									label={item}
								/>
							))}
						</Stack>

						<Typography variant="subtitle2">Disposição / Situação do Cadete</Typography>
						<Stack direction="row" useFlexGap flexWrap="wrap" spacing={1}>
							{disposicaoOptions.map((item) => (
								<FormControlLabel
									key={item}
									control={
										<Checkbox
											checked={formData.disposicao_cadete.includes(item)}
											onChange={(event) =>
												toggleListOption(
													'disposicao_cadete',
													item,
													event.target.checked,
												)
											}
										/>
									}
									label={item}
								/>
							))}
						</Stack>
					</Stack>
				</SectionCard>

				<SectionCard title="5 · CID-10 e Notas Clínicas">
					<Stack spacing={1.5}>
						<TextField
							label="Código CID-O (Morfologia)"
							placeholder="Ex: M9180/3 ou osteossarcoma"
							value={formData.codigo_cido}
							onChange={(event) =>
								setFormData((current) => ({ ...current, codigo_cido: event.target.value }))
							}
							fullWidth
							helperText="Campo opcional. Digite código ou descrição para sugestão da base CID-O."
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>

						{cidoSugestoes.length > 0 ? (
							<Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
								{cidoSugestoes.slice(0, 8).map((item) => (
									<Button
										key={`${item.codigo}-${item.descricao}`}
										type="button"
										variant="outlined"
										size="small"
										onClick={() =>
											setFormData((current) => ({ ...current, codigo_cido: item.codigo }))
										}
										sx={{ minHeight: 32 }}
									>
										{item.codigo} — {item.descricao}
									</Button>
								))}
							</Stack>
						) : null}

						<TextField
							label="CID-10 Principal"
							placeholder="Ex: S52.0 ou fratura"
							value={formData.codigo_cid10}
							onChange={(event) =>
								setFormData((current) => ({ ...current, codigo_cid10: event.target.value }))
							}
							fullWidth
							helperText="Campo opcional. Digite código ou descrição para sugestão da base CID-10."
							sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
						/>

						{cid10PrincipalSugestoes.length > 0 ? (
							<Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
								{cid10PrincipalSugestoes.slice(0, 8).map((item) => (
									<Button
										key={`${item.codigo}-${item.descricao}`}
										type="button"
										variant="outlined"
										size="small"
										onClick={() =>
											setFormData((current) => ({ ...current, codigo_cid10: item.codigo }))
										}
										sx={{ minHeight: 32 }}
									>
										{item.codigo} — {item.descricao}
									</Button>
								))}
							</Stack>
						) : null}

						<Typography variant="caption" color="text.secondary" sx={{ mt: -0.5 }}>
							Principal
						</Typography>

						<Stack direction={{ xs: 'column', md: 'row' }} spacing={1} alignItems={{ md: 'center' }}>
							<TextField
								label="Adicionar CID-10 secundário"
								placeholder="Ex: M76.6"
								value={formData.cid10_secundario_input}
								onChange={(event) =>
									setFormData((current) => ({
										...current,
										cid10_secundario_input: event.target.value,
									}))
								}
								fullWidth
								sx={{ '& .MuiInputBase-root': { minHeight: 44 } }}
							/>
							<Button
								type="button"
								variant="outlined"
								onClick={handleAdicionarCid10Secundario}
								sx={{ minHeight: 44, minWidth: 44 }}
							>
								+ Adicionar código
							</Button>
						</Stack>

						{cid10SecundarioSugestoes.length > 0 ? (
							<Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
								{cid10SecundarioSugestoes.slice(0, 8).map((item) => (
									<Button
										key={`${item.codigo}-${item.descricao}`}
										type="button"
										variant="outlined"
										size="small"
										onClick={() =>
											setFormData((current) => ({
												...current,
												cid10_secundario_input: item.codigo,
											}))
										}
										sx={{ minHeight: 32 }}
									>
										{item.codigo} — {item.descricao}
									</Button>
								))}
							</Stack>
						) : null}

						{formData.cid10_secundarios.length > 0 ? (
							<Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
								{formData.cid10_secundarios.map((codigo) => (
									<Chip
										key={codigo}
										label={codigo}
										onDelete={() =>
											setFormData((current) => ({
												...current,
												cid10_secundarios: current.cid10_secundarios.filter((item) => item !== codigo),
											}))
										}
										size="small"
									/>
								))}
							</Stack>
						) : null}

						<TextField
							label="Notas Clínicas"
							value={formData.notas_clinicas}
							onChange={(event) =>
								setFormData((current) => ({ ...current, notas_clinicas: event.target.value }))
							}
							placeholder="Observações clínicas, anamnese, evolução..."
							multiline
							minRows={3}
							fullWidth
						/>
					</Stack>
				</SectionCard>

				{submitError ? <Alert severity="error">{submitError}</Alert> : null}

				<Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} justifyContent="flex-end">
					<Button
						type="button"
						variant="text"
						onClick={() =>
							setFormData((current) => ({
								...initialFormState,
								cadete_id: current.cadete_id,
								medico_id: current.medico_id,
							}))
						}
						sx={{ minHeight: 44, minWidth: 44 }}
					>
						Cancelar
					</Button>
					<Button
						type="submit"
						variant="contained"
						disabled={createAtendimentoMutation.isPending}
						sx={{ minHeight: 44, minWidth: 44 }}
					>
						{createAtendimentoMutation.isPending ? 'Registrando...' : 'Registrar Atendimento'}
					</Button>
				</Stack>
			</Stack>
		</Stack>
	);
};
