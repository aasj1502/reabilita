Este documento serve como guia técnico para a construção do diagrama do banco de dados relacional do **Sistema Reabilita**, utilizando o **PostgreSQL** como motor de banco de dados. A modelagem aqui apresentada busca a Terceira Forma Normal (3NF) para garantir a integridade referencial e facilitar consultas estatísticas complexas.

# Diretrizes para o Diagrama do Banco de Dados: Reabilita

## 1. Parâmetros Gerais
*   **Nome do Banco de Dados:** `reabilita`
*   **Arquitetura:** Baseada em esquemas para separação lógica de domínios (Administrativo vs. Clínico).
*   **Motor:** PostgreSQL.

---

## 2. Esquema: `pessoal`
Este esquema gerencia os usuários, militares e seus respectivos perfis de acesso.

### Tabelas Sugeridas:
1.  **`militares`**: Cadastro geral dos cadetes e instrutores.
    *   Campos: `id (PK)`, `nr_militar (Unique)`, `nome_completo`, `posto_graduacao`, `arma_quadro_servico`, `curso`, `companhia`, `pelotao`.
2.  **`profissionais_saude`**: Especialistas que realizam o atendimento.
    *   Campos: `id (PK)`, `militar_id (FK)`, `especialidade` (Médico, Fisioterapeuta, Nutricionista, Psicopedagogo, Estatístico), `registro_profissional` (Ex: CRM, CREFITO).
3.  **`usuarios`**: Gestão de credenciais para acesso via Django.
    *   Campos: `id (PK)`, `militar_id (FK)`, `login`, `senha_hash`, `perfil_acesso` (Admin, Saúde, Instrutor, Comando).

---

## 3. Esquema: `saude`
Centraliza o catálogo de diagnósticos, a taxonomia ortopédica e os registros de atendimento.

### Tabelas de Referência (Static Data):
1.  **`cid10_categorias`**: Importação do arquivo `CID-10-CATEGORIAS.CSV`.
    *   Campos: `codigo (PK)`, `descricao`, `capitulo`, `grupo`, `flag_adaga_asterisco`.
2.  **`cido_morfologias`**: Importação do arquivo `CID-O-CATEGORIAS.CSV`.
    *   Campos: `codigo (PK)`, `descricao_morfologica`, `comportamento` (Ex: /3 para maligno).
3.  **`tipos_lesao`**: Categorias do arquivo SAC.
    *   Valores: Óssea, Articular, Muscular, Tendinosa, Neurológica.
4.  **`regioes_corpo`**: Divisões macro-anatômicas.
    *   Valores: Membros Superiores, Coluna, Bacia, Membros Inferiores, Tórax, Core.
5.  **`estruturas_anatomicas`**: Segmentos específicos vinculados às regiões.
    *   Campos: `id (PK)`, `nome`, `regiao_id (FK)`. (Ex: Fêmur vinculado a Membros Inferiores).
6.  **`lateralidades`**: Atributo direcional mandatório.
    *   Valores: Direita, Esquerda, Bilateral, Não é o caso.

### Tabelas de Atendimento (Transaction Data):
7.  **`atendimentos` (Tabela Fato)**: Registro central que dispara o protocolo multidisciplinar.
    *   Campos:
        *   `id (PK)`, `data_registro`.
        *   `cadete_id (FK)`, `medico_id (FK)` (**Obrigatório**).
        *   `tipo_lesao_id (FK)`, `estrutura_id (FK)`, `lateralidade_id (FK)`.
        *   `origem_lesao` (Ex: "Por Estresse").
        *   `codigo_cid10 (FK)`, `codigo_cido (FK, Nullable)`.
        *   `flag_sred (Boolean)`: Ativado automaticamente se Tipo=Óssea + Origem=Estresse.
8.  **`evolucao_multidisciplinar`**: Acompanhamento dos demais profissionais.
    *   Campos: `id (PK)`, `atendimento_id (FK)`, `profissional_id (FK)`, `parecer_tecnico`, `data_evolucao`.

---

## 4. Esquema: `estatistica` (Sugerido)
Esquema dedicado para armazenamento de views materializadas e dados processados para os dashboards.

### Objetos Sugeridos:
1.  **`view_sred_anual`**: Consolidação de diagnósticos de S-RED por ano para o gráfico evolutivo.
2.  **`view_eficacia_reabilitacao`**: Cálculo do percentual de lesões preveníveis sem retorno.

---

## 5. Regras de Integridade e Gatilhos (Triggers)
*   **Trava Médica**: O sistema deve possuir uma constraint no banco (ou validação no backend) que impeça a inserção na tabela `atendimentos` sem um `medico_id` válido.
*   **Gatilho S-RED**: Implementar lógica (Trigger ou Django Signal) que, ao detectar uma inserção de lesão "Óssea" com origem "Por Estresse" ou CID-10 "M84.3", marque o campo `flag_sred` como verdadeiro e notifique a equipe de Nutrição e Psicopedagogia.
*   **Consistência Oncológica**: Validação para garantir que códigos CID-O de morfologia celular óssea (ex: M9180/3) sejam associados apenas a topografias CID-10 nos intervalos C40-C41.
*   **Lateralidade Mandatória**: Para estruturas em Membros Superiores/Inferiores, o sistema deve exigir Direita/Esquerda/Bilateral, impedindo o valor "Não é o caso".

---

## 6. Otimização de Performance
*   **Índices**: Criar índices compostos nas chaves estrangeiras de `atendimentos` e em campos de data para agilizar o carregamento dos dashboards do Estatístico.
*   **Normalização**: Manter o modelo em 3NF para eliminar redundâncias e proteger contra anomalias de atualização.