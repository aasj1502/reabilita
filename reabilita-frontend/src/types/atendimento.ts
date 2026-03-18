export type TipoLesao = "Óssea" | "Articular" | "Muscular" | "Tendinosa" | "Neurológica";

export type OrigemLesao = "Por Estresse" | "Traumática" | "Outra";

export type Lateralidade = "Direita" | "Esquerda" | "Bilateral" | "Não é o caso";

export interface Atendimento {
	id: number;
	data_registro: string;
	cadete_id: number;
	medico_id: number;
	tipo_lesao: TipoLesao;
	origem_lesao: OrigemLesao;
	estrutura_anatomica: string;
	lateralidade: Lateralidade;
	codigo_cid10: string;
	codigo_cido: string | null;
	flag_sred: boolean;
}

export interface CreateAtendimentoPayload {
	cadete_id: number;
	medico_id: number;
	tipo_lesao: TipoLesao;
	origem_lesao: OrigemLesao;
	estrutura_anatomica: string;
	lateralidade: Lateralidade;
	codigo_cid10: string;
	codigo_cido?: string | null;
}
