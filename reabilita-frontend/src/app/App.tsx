import { CircularProgress, Stack } from '@mui/material';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import { ClinicalLayout } from '../components/common/ClinicalLayout';
import { CadetesPacientesPage } from '../pages/CadetesPacientesPage';
import { CadastrarCadetePage } from '../pages/CadastrarCadetePage';
import { DashboardPage } from '../pages/DashboardPage';
import { LoginPage } from '../pages/LoginPage';
import { MinhaContaPage } from '../pages/MinhaContaPage';
import { NovoAtendimentoPage } from '../pages/NovoAtendimentoPage';
import { UsuariosPerfisPage } from '../pages/UsuariosPerfisPage';
import { useAuth } from '../providers/AuthProvider';

const ProtectedLayoutRoute = () => {
	const { isReady, isAuthenticated } = useAuth();

	if (!isReady) {
		return (
			<Stack alignItems="center" justifyContent="center" minHeight="100vh">
				<CircularProgress />
			</Stack>
		);
	}

	if (!isAuthenticated) {
		return <Navigate to="/login" replace />;
	}

	return <ClinicalLayout />;
};

const PublicLoginRoute = () => {
	const { isReady, isAuthenticated } = useAuth();

	if (!isReady) {
		return (
			<Stack alignItems="center" justifyContent="center" minHeight="100vh">
				<CircularProgress />
			</Stack>
		);
	}

	if (isAuthenticated) {
		return <Navigate to="/dashboard" replace />;
	}

	return <LoginPage />;
};

export const App = () => {
	return (
		<BrowserRouter>
			<Routes>
				<Route path="/login" element={<PublicLoginRoute />} />
				<Route element={<ProtectedLayoutRoute />}>
					<Route path="/" element={<Navigate to="/dashboard" replace />} />
					<Route path="/dashboard" element={<DashboardPage />} />
					<Route path="/cadetes-pacientes" element={<CadetesPacientesPage />} />
					<Route path="/cadetes/novo" element={<CadastrarCadetePage />} />
					<Route path="/atendimentos/novo" element={<NovoAtendimentoPage />} />
					<Route path="/minha-conta" element={<MinhaContaPage />} />
					<Route path="/usuarios-perfis" element={<UsuariosPerfisPage />} />
					<Route path="*" element={<Navigate to="/dashboard" replace />} />
				</Route>
			</Routes>
		</BrowserRouter>
	);
};
