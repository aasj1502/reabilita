import { Button, Stack, Typography } from '@mui/material';

import { SectionCard } from '../design-system';
import { useAuth } from '../providers/AuthProvider';

export const MinhaContaPage = () => {
	const { user, logout } = useAuth();

	return (
		<Stack spacing={2}>
			<Typography variant="h5">Minha Conta</Typography>

			<SectionCard title="Dados da Sessão" subtitle="Informações do usuário autenticado no sistema.">
				<Stack spacing={1}>
					<Typography>
						<strong>Usuário:</strong> {user?.username ?? '-'}
					</Typography>
					<Typography>
						<strong>Nome:</strong> {[user?.first_name, user?.last_name].filter(Boolean).join(' ') || '-'}
					</Typography>
					<Typography>
						<strong>Perfil administrativo:</strong> {user?.is_staff ? 'Sim' : 'Não'}
					</Typography>

					<Button
						variant="outlined"
						onClick={() => void logout()}
						sx={{ minHeight: 44, minWidth: 44, alignSelf: 'flex-start', mt: 1 }}
					>
						Encerrar sessão
					</Button>
				</Stack>
			</SectionCard>
		</Stack>
	);
};
