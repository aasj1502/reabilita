import type { ReactNode } from 'react';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { DesignSystemProvider } from '../design-system';

const queryClient = new QueryClient();

export interface AppProvidersProps {
	children: ReactNode;
}

export const AppProviders = ({ children }: AppProvidersProps) => {
	return (
		<QueryClientProvider client={queryClient}>
			<DesignSystemProvider>{children}</DesignSystemProvider>
		</QueryClientProvider>
	);
};
