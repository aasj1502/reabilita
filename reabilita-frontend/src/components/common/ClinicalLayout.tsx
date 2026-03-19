import DarkModeOutlinedIcon from '@mui/icons-material/DarkModeOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import GroupOutlinedIcon from '@mui/icons-material/GroupOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import PersonAddAltOutlinedIcon from '@mui/icons-material/PersonAddAltOutlined';
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import WbSunnyOutlinedIcon from '@mui/icons-material/WbSunnyOutlined';
import {
	Box,
	Button,
	Divider,
	List,
	ListItem,
	ListItemButton,
	ListItemIcon,
	ListItemText,
	Stack,
	Typography,
} from '@mui/material';
import { Link as RouterLink, Outlet, useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '../../providers/AuthProvider';
import { useThemeMode } from '../../providers/AppProviders';

const isCurrentRoute = (currentPath: string, targetPath: string): boolean => {
	return currentPath === targetPath;
};

export const ClinicalLayout = () => {
	const navigate = useNavigate();
	const location = useLocation();
	const { mode, toggleMode } = useThemeMode();
	const { logout } = useAuth();

	const handleLogout = async () => {
		await logout();
		navigate('/login', { replace: true });
	};

	return (
		<Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
			<Stack direction={{ xs: 'column', md: 'row' }} minHeight="100vh">
				<Box
					component="aside"
					sx={{
						width: { xs: '100%', md: 280 },
						borderRight: { md: 1 },
						borderBottom: { xs: 1, md: 0 },
						borderColor: 'divider',
						display: 'flex',
						flexDirection: 'column',
					}}
				>
					<Stack direction="row" alignItems="center" spacing={1.5} px={2} py={2}>
						<Box
							component="img"
							src="/logo-reabilita-aman.png"
							alt="Logotipo Reabilita AMAN"
							sx={{ width: 40, height: 40, objectFit: 'contain' }}
						/>
						<Stack spacing={0} sx={{ minWidth: 0 }}>
							<Typography variant="h6" fontWeight={700} lineHeight={1} sx={{ letterSpacing: 0.2 }}>
								Reabilita
							</Typography>
							<Typography
								variant="caption"
								color="success.main"
								fontWeight={700}
								lineHeight={1}
								sx={{ letterSpacing: 1.35, fontSize: '0.72rem', mt: 0.15 }}
							>
								AMAN
							</Typography>
						</Stack>
					</Stack>

					<Divider />

					<List sx={{ px: 1, py: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
						<ListItem disablePadding>
							<ListItemButton
								component={RouterLink}
								to="/dashboard"
								selected={isCurrentRoute(location.pathname, '/dashboard')}
								sx={{ minHeight: 44 }}
							>
								<ListItemIcon>
									<DashboardOutlinedIcon />
								</ListItemIcon>
								<ListItemText primary="Dashboard" />
							</ListItemButton>
						</ListItem>

						<ListItem sx={{ pt: 1, pb: 0.5 }}>
							<Typography variant="caption" color="text.secondary" fontWeight={600}>
								Seção de Saúde
							</Typography>
						</ListItem>

						<ListItem disablePadding>
							<ListItemButton
								component={RouterLink}
								to="/cadetes-pacientes"
								selected={isCurrentRoute(location.pathname, '/cadetes-pacientes')}
								sx={{ minHeight: 44 }}
							>
								<ListItemIcon>
									<GroupOutlinedIcon />
								</ListItemIcon>
								<ListItemText primary="Cadetes / Pacientes" />
							</ListItemButton>
						</ListItem>

						<ListItem disablePadding>
							<ListItemButton
								component={RouterLink}
								to="/cadetes/novo"
								selected={isCurrentRoute(location.pathname, '/cadetes/novo')}
								sx={{ minHeight: 44 }}
							>
								<ListItemIcon>
									<PersonAddAltOutlinedIcon />
								</ListItemIcon>
								<ListItemText primary="+ Cadastrar Cadete" />
							</ListItemButton>
						</ListItem>

						<ListItem sx={{ pt: 1, pb: 0.5 }}>
							<Typography variant="caption" color="text.secondary" fontWeight={600}>
								Atendimentos
							</Typography>
						</ListItem>

						<ListItem disablePadding>
							<ListItemButton
								component={RouterLink}
								to="/atendimentos/novo"
								selected={isCurrentRoute(location.pathname, '/atendimentos/novo')}
								sx={{ minHeight: 44 }}
							>
								<ListItemIcon>
									<PersonAddAltOutlinedIcon />
								</ListItemIcon>
								<ListItemText primary="Novo Atendimento" />
							</ListItemButton>
						</ListItem>

						<ListItem sx={{ pt: 1, pb: 0.5 }}>
							<Typography variant="caption" color="text.secondary" fontWeight={600}>
								Configurações
							</Typography>
						</ListItem>

						<ListItem disablePadding>
							<ListItemButton
								component={RouterLink}
								to="/minha-conta"
								selected={isCurrentRoute(location.pathname, '/minha-conta')}
								sx={{ minHeight: 44 }}
							>
								<ListItemIcon>
									<PersonOutlineOutlinedIcon />
								</ListItemIcon>
								<ListItemText primary="Minha Conta" />
							</ListItemButton>
						</ListItem>

						<ListItem disablePadding>
							<ListItemButton
								component={RouterLink}
								to="/usuarios-perfis"
								selected={isCurrentRoute(location.pathname, '/usuarios-perfis')}
								sx={{ minHeight: 44 }}
							>
								<ListItemIcon>
									<SettingsOutlinedIcon />
								</ListItemIcon>
								<ListItemText primary="Usuários e Perfis" />
							</ListItemButton>
						</ListItem>

						<ListItem disablePadding sx={{ mt: 1 }}>
							<ListItemButton onClick={toggleMode} sx={{ minHeight: 44 }}>
								<ListItemIcon>
									{mode === 'light' ? <DarkModeOutlinedIcon /> : <WbSunnyOutlinedIcon />}
								</ListItemIcon>
								<ListItemText
									primary={mode === 'light' ? 'Modo escuro' : 'Modo claro'}
								/>
							</ListItemButton>
						</ListItem>

						<ListItem disablePadding>
							<ListItemButton onClick={() => void handleLogout()} sx={{ minHeight: 44 }}>
								<ListItemIcon>
									<LogoutOutlinedIcon />
								</ListItemIcon>
								<ListItemText primary="Sair" />
							</ListItemButton>
						</ListItem>
					</List>
				</Box>

				<Box sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
					<Box
						component="header"
						sx={{
							borderBottom: 1,
							borderColor: 'divider',
							px: { xs: 2, md: 3 },
							py: 1.5,
						}}
					>
						<Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="flex-end" spacing={1}>
							<Button
								variant="outlined"
								component={RouterLink}
								to="/cadetes/novo"
								sx={{ minHeight: 44, minWidth: 44 }}
							>
								+ Cadete
							</Button>
							<Button
								variant="contained"
								component={RouterLink}
								to="/atendimentos/novo"
								sx={{ minHeight: 44, minWidth: 44 }}
							>
								+ Novo Atendimento
							</Button>
						</Stack>
					</Box>

					<Box component="main" sx={{ flex: 1, px: { xs: 2, md: 3 }, py: 2 }}>
						<Outlet />
					</Box>
				</Box>
			</Stack>
		</Box>
	);
};
