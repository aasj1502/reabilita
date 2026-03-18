Relatório de Implementação Técnica: Mapeamento e Integração de Dados Ortopédicos (CID-10 e CID-O)

1. Objetivos e Escopo Técnico

O propósito deste documento é estabelecer a lógica de arquitetura e correlação entre a taxonomia ortopédica proprietária, extraída do arquivo sac_convertido.csv, e os padrões internacionais de terminologia clínica: CID-10 (Classificação Internacional de Doenças) e CID-O (Classificação Internacional de Doenças para Oncologia).

A implementação visa estruturar um sistema de apoio à decisão clínica onde a seleção de uma "Lesão" e sua respectiva "Localização" resulte na recuperação automatizada dos códigos de diagnóstico (topografia) e morfologia celular. Este relatório define as regras de integridade, a estrutura de tabelas e a lógica de filtros em cascata para garantir a interoperabilidade dos dados.

2. Análise da Estrutura de Dados de Origem (sac_convertido.csv)

A base proprietária organiza o domínio ortopédico através de cinco categorias de lesão e agrupamentos anatômicos que incluem regiões periféricas e centrais.

Categorias de Lesão:

1. Óssea: Fraturas, osteomielites e neoplasias ósseas.
2. Articular: Artroses, luxações e entorses.
3. Muscular: Estiramentos, miosites e traumas de partes moles.
4. Tendinosa: Tendinopatias e rupturas.
5. Neurológica: Lesões de plexos, raízes e medula.

Mapeamento Anatômico de Segmentos:

Região Principal	Segmentos Específicos Identificados
Membros Superiores	Esternoclavicular (Dir/Esq), Clavícula (Dir/Esq), Ombro (Dir/Esq), Braço (Dir/Esq), Cotovelo (Dir/Esq), Antebraço (Dir/Esq), Punho (Dir/Esq), Mão (Dir/Esq).
Coluna	Cervical, Torácica, Lombar, Sacro, Cóccix.
Bacia	Ilíaco, Ísquio, Púbico.
Membros Inferiores	Quadril (Dir/Esq), Coxa (Dir/Esq), Perna (Dir/Esq), Tornozelo (Dir/Esq), Pé (Dir/Esq).
Tronco e Core	Tórax (Parte muscular), Core (Parte tendinosa).

3. Mapeamento para CID-10 (Classificação Internacional de Doenças)

O mapeamento utiliza a base CID-10-CATEGORIAS.CSV. A implementação deve garantir que a escolha anatômica filtre os intervalos de capítulos específicos (M para patologias não traumáticas, S e T para traumáticas, C para malignas).

Neoplasias Ósseas (C40-C41)

Código	Descrição
C40	Neoplasia maligna dos ossos e cartilagens articulares dos membros
C41	Neoplasia maligna dos ossos e das cartilagens articulares de outras localizações

Doenças Osteomusculares (M00-M99)

Código	Descrição
M16	Coxartrose [artrose do quadril]
M86	Osteomielite
M54	Dorsalgia

Traumatismos (S00-T14)

Código	Descrição
S42	Fratura do ombro e do braço
S72	Fratura do fêmur
S82	Fratura da perna, incluindo tornozelo

4. Mapeamento para CID-O (Oncologia)

Para casos oncológicos, o sistema deve integrar o arquivo CID-O-CATEGORIAS.CSV para definir a morfologia. É imperativo que o sistema aplique a referência cruzada topográfica: muitos códigos CID-O já trazem em sua definição a compatibilidade com o CID-10.

Código CID-O	Descrição Morfológica	Referência Topográfica (CID-10)
M8800/3	Sarcoma SOE	-
M9180/3	Osteossarcoma SOE	C40.-, C41.-
M9220/3	Condrossarcoma SOE	C40.-, C41.-
M9250/3	Tumor maligno de células gigantes do osso	C40.-, C41.-
M8042/3	Carcinoma "oat cell"	C34.-

Regra de Arquitetura: Ao selecionar uma morfologia como M9180/3, o sistema deve validar se o código CID-10 selecionado pertence ao intervalo C40-C41. Se o usuário selecionar uma localização incompatível com a morfologia (ex: M8042/3 para osso), o sistema deve emitir um alerta de inconsistência de domínio.

5. Lógica de Arquitetura do Banco de Dados

Propõe-se uma estrutura normalizada para suportar o relacionamento N:M (muitos-para-muitos), visto que uma mesma localização anatômica pode ser mapeada para múltiplos códigos CID dependendo da natureza da lesão.

* Tabela_Taxonomia_SAC: Cadastro de Lesão e Parte do Corpo (Origem: sac_convertido.csv).
* Tabela_CID10: Catálogo de doenças com flags para adaga (+) e asterisco (*).
* Tabela_De_De (Mapping): Tabela pivot que armazena os vínculos lógicos entre a Taxonomia SAC e os códigos CID-10/CID-O.

Dicionário de Dados Técnico

Campo	Tipo de Dado	Descrição	Exemplo de Valor
tipo_lesao	VARCHAR(20)	Categoria primária da lesão.	"Óssea"
parte_corpo	VARCHAR(50)	Segmento anatômico específico.	"Quadril Direito"
codigo_cid10	VARCHAR(5)	Código padrão CID-10 (LNN.N).	"S72.0"
codigo_cido	VARCHAR(7)	Código de morfologia com sufixo.	"M9180/3"
lateralidade	VARCHAR(15)	Atributo de lateralidade.	"Esquerda"
classificacao	CHAR(1)	Identificador de Adaga ou Asterisco.	"+"

6. Lógica de Consulta (Query Logic) para Formulários Dinâmicos

O fluxo de dados no formulário deve seguir a seguinte precedência lógica:

1. Passo 1 (Natureza): Usuário define o "Tipo de Lesão".
2. Passo 2 (Filtro Anatômico): O sistema carrega as "Partes do Corpo" associadas àquela lesão no arquivo fonte.
3. Passo 3 (Interação de Lateralidade): Para membros, o sistema exige a lateralidade (Direita/Esquerda). Para estruturas de linha média (Coluna, Core), o sistema deve setar automaticamente como "Não é o caso".
4. Passo 4 (Busca CID): O sistema realiza o JOIN entre a Tabela_Taxonomia_SAC e Tabela_CID10. Se "Tipo de Lesão" = "Óssea" e "Parte do Corpo" = "Mão", o sistema filtra o CID-10 pelo intervalo S62.
5. Passo 5 (Qualificação Oncológica): Se a lesão for "Tumoral", o campo CID-O torna-se obrigatório, filtrando apenas morfologias com comportamento /3 (Maligno) ou /1 (Inerto/Borderline).

Regra de Validação: Se Parte do Corpo = "Coluna", o sistema deve restringir o codigo_cid10 aos intervalos S12 (Cervical), S22 (Torácica), S32 (Lombar/Pelve) ou o intervalo crônico M40-M54.

7. Diretrizes de Implementação e Integridade de Dados

* Fidelidade Estrita ao Fonte: É proibida a inserção de códigos manuais. A integridade referencial deve ser mantida estritamente com os CSVs fornecidos.
* Sistema de Adaga e Asterisco: O sistema deve suportar a codificação dupla. Ao selecionar um código de etiologia (Adaga), o sistema deve obrigar a seleção de um código de manifestação (Asterisco).
  * Exemplo: A17+ (Tuberculose do sistema nervoso) deve ser associado a um código de manifestação correspondente, como G01* (Meningite em doenças bacterianas).
* Tratamento de Lateralidade: A lateralidade é um modificador essencial para faturamento. O sistema deve concatenar a lateralidade ao código final ou armazená-la em campo estruturado para evitar glosas em procedimentos cirúrgicos.
* Segmentos Específicos: Deve-se garantir a inclusão de Tórax e Core conforme mapeado no arquivo sac_convertido.csv, tratando-os como regiões de lateralidade única ("Não é o caso").
