import { apiClient } from './apiClient';
import type {
	Atendimento,
	AtendimentoReferenciasResponse,
	CidAutocompleteItem,
	CreateAtendimentoPayload,
	CSVImportResponse,
	CSVPreviewResponse,
} from '../types/atendimento';

const RESOURCE = '/saude/atendimentos/';
const RESOURCE_REFERENCIAS = '/saude/atendimentos/referencias/';
const RESOURCE_CID10_AUTOCOMPLETE = '/saude/cid10/autocomplete/';
const RESOURCE_CIDO_AUTOCOMPLETE = '/saude/cido/autocomplete/';
const RESOURCE_CSV_PREVIEW = '/saude/importar-csv/preview/';
const RESOURCE_CSV_CONFIRMAR = '/saude/importar-csv/confirmar/';

export const listAtendimentos = async (): Promise<Atendimento[]> => {
	const { data } = await apiClient.get<Atendimento[] | { results: Atendimento[] }>(RESOURCE);
	if (Array.isArray(data)) {
		return data;
	}
	return data.results;
};

export const createAtendimento = async (
	payload: CreateAtendimentoPayload,
): Promise<Atendimento> => {
	const { data } = await apiClient.post<Atendimento>(RESOURCE, payload);
	return data;
};

export const getAtendimentoReferencias = async (): Promise<AtendimentoReferenciasResponse> => {
	const { data } = await apiClient.get<AtendimentoReferenciasResponse>(RESOURCE_REFERENCIAS);
	return data;
};

export const searchCid10 = async (query: string, limit = 12): Promise<CidAutocompleteItem[]> => {
	const { data } = await apiClient.get<{ items: CidAutocompleteItem[] }>(RESOURCE_CID10_AUTOCOMPLETE, {
		params: {
			q: query,
			limit,
		},
	});
	return data.items;
};

export const searchCido = async (query: string, limit = 12): Promise<CidAutocompleteItem[]> => {
	const { data } = await apiClient.get<{ items: CidAutocompleteItem[] }>(RESOURCE_CIDO_AUTOCOMPLETE, {
		params: {
			q: query,
			limit,
		},
	});
	return data.items;
};

export const previewCSVImport = async (file: File): Promise<CSVPreviewResponse> => {
	const form = new FormData();
	form.append('arquivo', file);
	const { data } = await apiClient.post<CSVPreviewResponse>(RESOURCE_CSV_PREVIEW, form, {
		headers: { 'Content-Type': 'multipart/form-data' },
	});
	return data;
};

export const confirmarCSVImport = async (file: File): Promise<CSVImportResponse> => {
	const form = new FormData();
	form.append('arquivo', file);
	const { data } = await apiClient.post<CSVImportResponse>(RESOURCE_CSV_CONFIRMAR, form, {
		headers: { 'Content-Type': 'multipart/form-data' },
	});
	return data;
};
