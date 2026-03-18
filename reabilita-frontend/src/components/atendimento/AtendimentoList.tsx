import { Chip, List, ListItem, ListItemText, Stack, Typography } from '@mui/material';

import { SectionCard } from '../../design-system';
import type { Atendimento } from '../../types/atendimento';

export interface AtendimentoListProps {
	items: Atendimento[];
}

export const AtendimentoList = ({ items }: AtendimentoListProps) => {
	return (
		<SectionCard title="Atendimentos" subtitle="Visão inicial do módulo clínico">
			<List disablePadding>
				{items.map((item) => (
					<ListItem
						key={item.id}
						disableGutters
						sx={{
							py: 1.25,
							alignItems: 'flex-start',
							borderBottom: '1px solid',
							borderColor: 'divider',
						}}
					>
						<ListItemText
							primary={
								<Stack direction="row" alignItems="center" spacing={1} flexWrap="wrap">
									<Typography variant="subtitle2">CID-10 {item.codigo_cid10}</Typography>
									{item.flag_sred ? <Chip size="small" color="warning" label="S-RED" /> : null}
								</Stack>
							}
							secondary={`Lesão ${item.tipo_lesao} • ${item.estrutura_anatomica} • ${item.lateralidade}`}
						/>
					</ListItem>
				))}
			</List>
		</SectionCard>
	);
};
