# Design System (copiável)

Estrutura pronta para reutilização em outra aplicação React + TypeScript + MUI.

## Estrutura

```txt
src/design-system/
  components/
    base/
      BaseAvatar.tsx
      CopyableText.tsx
      EmptyState.tsx
      SectionCard.tsx
      index.ts
    index.ts
  hooks/
    useNotify.tsx
    index.ts
  providers/
    ThemeProvider.tsx
    NotificationProvider.tsx
    DesignSystemProvider.tsx
    index.ts
  styles/
    global.scss
    index.ts
  theme/
    componentOverrides.ts
    createTheme.ts
    palette.ts
    typography.ts
    types.ts
    index.ts
  tokens/
    colors.module.scss
    index.ts
  index.ts
```

## Dependências mínimas

```bash
npm i @mui/material @mui/icons-material @emotion/react @emotion/styled
npm i notistack sass
```

## Uso mínimo

```tsx
import { DesignSystemProvider } from './design-system';
import './design-system/styles';

export function AppRoot() {
  return (
    <DesignSystemProvider>
      <App />
    </DesignSystemProvider>
  );
}
```

## Uso avançado (providers separados)

```tsx
import { ThemeProvider, NotificationProvider } from './design-system';
import './design-system/styles';

export function AppRoot() {
  return (
    <ThemeProvider>
      <NotificationProvider maxSnack={5} autoHideDuration={4000}>
        <App />
      </NotificationProvider>
    </ThemeProvider>
  );
}
```
