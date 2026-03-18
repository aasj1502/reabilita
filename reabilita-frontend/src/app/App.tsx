import { Container, Stack } from '@mui/material';

import { AtendimentosPage } from '../pages/AtendimentosPage';
import { CargaReferenciasPage } from '../pages/CargaReferenciasPage';

export const App = () => {
	return (
		<Container maxWidth="md" sx={{ py: 2 }}>
			<Stack spacing={2}>
				<AtendimentosPage />
				<CargaReferenciasPage />
			</Stack>
		</Container>
	);
};
