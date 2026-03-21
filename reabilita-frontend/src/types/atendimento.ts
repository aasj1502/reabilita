export type TipoLesao = "Óssea" | "Articular" | "Muscular" | "Tendinosa" | "Neurológica";

export type OrigemLesao = "Por Estresse" | "Traumática" | "Outra" | "";

export type DecisaoSred = "Investigação Pendente" | "Em Investigação" | "S-RED Positivo" | "S-RED Negativo";

export type Lateralidade = "Direita" | "Esquerda" | "Bilateral" | "Não é o caso";

export type TipoAtendimento = "Inicial" | "Retorno";

export interface CidAutocompleteItem {
	codigo: string;
	descricao: string;
	referencia?: string;
}

export interface AtendimentoReferenciasResponse {
	tipo_atendimento_options: TipoAtendimento[];
	tipo_lesao_options: TipoLesao[];
	origem_lesao_options: OrigemLesao[];
	decisao_sred_options: DecisaoSred[];
	classificacao_atividade_options: string[];
	tipo_atividade_options: string[];
	tfm_taf_options: string[];
	modalidade_esportiva_options: string[];
	conduta_terapeutica_options: string[];
	exames_complementares_options: string[];
	encaminhamentos_options: string[];
	disposicao_options: string[];
	segmentos_por_tipo_lesao: Record<string, string[]>;
	estruturas_por_tipo_segmento: Record<string, Record<string, string[]>>;
	localizacoes_por_tipo_segmento: Record<string, Record<string, string[]>>;
	lateralidade_por_estrutura: Record<string, Lateralidade>;
}

export interface Atendimento {
	id: number;
	data_registro: string;
	cadete_id: number;
	medico_id: number;
	atendimento_origem_id: number | null;
	tipo_atendimento: TipoAtendimento;
	tipo_lesao: TipoLesao;
	origem_lesao: OrigemLesao;
	segmento_corporal: string;
	estrutura_anatomica: string;
	localizacao_lesao: string;
	lateralidade: Lateralidade;
	classificacao_atividade: string;
	tipo_atividade: string;
	tfm_taf: string;
	modalidade_esportiva: string;
	conduta_terapeutica: string;
	decisao_sred: DecisaoSred | '';
	medicamentoso: boolean;
	solicitar_exames_complementares: boolean;
	exames_complementares: string[];
	encaminhamentos_multidisciplinares: string[];
	disposicao_cadete: string[];
	codigo_cid10: string;
	cid10_secundarios: string[];
	codigo_cido: string | null;
	notas_clinicas: string;
	flag_sred: boolean;
}

export interface CreateAtendimentoPayload {
	cadete_id: number;
	medico_id: number;
	atendimento_origem_id?: number | null;
	tipo_atendimento: TipoAtendimento;
	tipo_lesao: TipoLesao;
	origem_lesao: OrigemLesao;
	segmento_corporal: string;
	estrutura_anatomica: string;
	localizacao_lesao: string;
	lateralidade: Lateralidade;
	classificacao_atividade?: string;
	tipo_atividade?: string;
	tfm_taf?: string;
	modalidade_esportiva?: string;
	conduta_terapeutica?: string;
	decisao_sred?: DecisaoSred | '';
	medicamentoso?: boolean;
	solicitar_exames_complementares?: boolean;
	exames_complementares?: string[];
	encaminhamentos_multidisciplinares?: string[];
	disposicao_cadete?: string[];
	codigo_cid10: string;
	cid10_secundarios?: string[];
	codigo_cido?: string | null;
	notas_clinicas?: string;
}

export interface CSVPreviewRow {
	linha: number;
	data: string;
	atendimento: string;
	lesao: string;
	parte_corpo: string;
	parte_lesionada: string;
	origem: string;
	erros: string[];
}

export interface CSVPreviewResponse {
	total_linhas: number;
	total_erros: number;
	erros: string[];
	preview: CSVPreviewRow[];
	colunas_detectadas: string[];
}

export interface CSVImportResponse {
	criados: number;
	cadetes_novos: number;
	avisos: string[];
}
