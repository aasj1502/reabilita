import { ThemeOptions, createTheme } from '@mui/material/styles';

import { colorTokens, type ColorTokens } from '../tokens';
import { createComponentOverrides } from './componentOverrides';
import { createPalette } from './palette';
import { createTypography } from './typography';
import type { ThemeOption } from './types';

export const buildThemeOption = (tokens: ColorTokens = colorTokens): ThemeOption => ({
	colors: tokens,
	heading: tokens.grey900,
	paper: tokens.paper,
	backgroundDefault: tokens.paper,
	background: tokens.primaryLight,
	darkTextPrimary: tokens.grey700,
	darkTextSecondary: tokens.grey500,
	textDark: tokens.grey900,
	menuSelected: tokens.secondaryDark,
	menuSelectedBack: tokens.secondaryLight,
	divider: tokens.grey200,
});

export const createAppTheme = (tokens: ColorTokens = colorTokens) => {
	const themeOption = buildThemeOption(tokens);

	const baseTheme = createTheme({
		direction: 'ltr',
		shape: {
			borderRadius: 8,
		},
		palette: createPalette(themeOption),
		typography: createTypography(themeOption),
		components: createComponentOverrides(themeOption),
		mixins: {
			toolbar: {
				minHeight: 48,
				padding: '16px',
				'@media (min-width: 600px)': {
					minHeight: 48,
				},
			},
		},
	} as ThemeOptions);

	return baseTheme;
};
