Relatório de Modelagem de Dados: Sistema de Informação Ortopédica

1. Introdução Técnica

Este relatório detalha a arquitetura de dados e o processo de normalização aplicados à transposição dos dados brutos do arquivo sac_convertido.csv para um modelo relacional robusto. A estrutura original, puramente tabular e desnormalizada, apresentava desafios críticos à integridade dos dados, como redundância excessiva e violação de atomicidade.

O objetivo principal desta intervenção é estabelecer uma base de dados que garanta a integridade referencial, elimine anomalias de atualização e facilite a extração de inteligência clínica. Ao segmentar as entidades ortopédicas em tabelas normalizadas, permitimos que o sistema suporte consultas complexas e escalabilidade futura, transformando registros esparsos em ativos de informação estruturada.

2. Análise de Domínio e Identificação de Entidades

A análise temática dos dados brutos revelou uma estrutura hierárquica e multidimensional. Para converter o contexto ortopédico em um modelo relacional, identificamos as seguintes entidades fundamentais:

* Tipos de Lesão: Categorias diagnósticas fundamentais (ex: Óssea, Neurológica).
* Regiões do Corpo: Divisões macro-anatômicas que servem como contêineres lógicos (ex: Membros Superiores, Coluna).
* Estruturas Anatômicas: Entidades específicas subordinadas às regiões (ex: Fêmur, Clavícula).
* Lateralidade: Atributo de especificação direcional (ex: Direita, Esquerda).

Observou-se que a estrutura tabular original misturava localização com lateralidade em uma única string (ex: "Clavícula Direita"). No modelo proposto, essas dimensões são tratadas como entidades distintas, permitindo uma análise granular e precisa.

3. Modelo Lógico e Normalização

A estratégia de modelagem adotada visa a Terceira Forma Normal (3NF). Um dos principais problemas identificados no CSV foi a repetição de macro-regiões (como "Membros Superiores") em colunas de tipos de lesão distintos, o que geraria redundância massiva em um modelo não normalizado.

Estratégia de ETL (Extração, Transformação e Carga)

Como Arquiteto de Dados, implementei uma lógica de limpeza rigorosa para assegurar a atomicidade:

1. Limpeza de Dados: O erro de digitação identificado no campo "Ombro Direto" foi corrigido para o valor canônico "Ombro".
2. Normalização de Atributos: Suffixos de lateralidade (Direita/Esquerda) foram removidos dos nomes das estruturas durante a carga, sendo estas informações movidas para uma tabela de domínio específica (lateralidades).
3. Resolução de Hierarquia: Estruturas foram vinculadas às suas regiões macro via chaves estrangeiras, eliminando a necessidade de repetir o nome da região para cada registro de lesão.

4. Definição do Banco de Dados (DDL SQL)

Abaixo, apresento o esquema SQL utilizando padrões de mercado. Foram incluídas restrições de unicidade (UNIQUE) para prevenir duplicidade de registros e índices para otimização de performance em operações de JOIN.

-- Padrão SQL ANSI - Compatível com PostgreSQL e SQL Server

-- 1. Tabela de Domínio: Categorias de Lesão
CREATE TABLE tipos_lesao (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
);

-- 2. Tabela de Domínio: Regiões Macro
CREATE TABLE regioes_corpo (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
);

-- 3. Tabela de Domínio: Estruturas Anatômicas
CREATE TABLE estruturas_anatomicas (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    regiao_id INT NOT NULL,
    CONSTRAINT fk_regiao FOREIGN KEY (regiao_id) REFERENCES regioes_corpo(id),
    CONSTRAINT uq_estrutura_regiao UNIQUE (nome, regiao_id)
);

-- 4. Tabela de Domínio: Lateralidade
CREATE TABLE lateralidades (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(30) NOT NULL UNIQUE
);

-- 5. Tabela de Interseção: Diagnósticos Clínicos (Tabela de Fatos)
CREATE TABLE diagnosticos_clinicos (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_lesao_id INT NOT NULL,
    estrutura_id INT NOT NULL,
    lateralidade_id INT NOT NULL,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tipo FOREIGN KEY (tipo_lesao_id) REFERENCES tipos_lesao(id),
    CONSTRAINT fk_estrutura FOREIGN KEY (estrutura_id) REFERENCES estruturas_anatomicas(id),
    CONSTRAINT fk_lateralidade FOREIGN KEY (lateralidade_id) REFERENCES lateralidades(id)
);

-- Criação de Índices para performance
CREATE INDEX idx_estrutura_regiao ON estruturas_anatomicas(regiao_id);
CREATE INDEX idx_diag_tipo ON diagnosticos_clinicos(tipo_lesao_id);
CREATE INDEX idx_diag_estrutura ON diagnosticos_clinicos(estrutura_id);


5. Mapeamento e Carga de Dados Base

Os dados abaixo representam a exaustão do contexto fornecido, já processados e normalizados.

Tabela 1: Tipos de Lesão

ID	Nome
1	Óssea
2	Articular
3	Muscular
4	Tendinosa
5	Neurológica

Tabela 2: Regiões do Corpo

ID	Nome
1	Membros Superiores
2	Coluna
3	Bacia
4	Membros Inferiores
5	Tórax
6	Core

Tabela 3: Estruturas Anatômicas (Mapeamento Completo e Higienizado)

Nota: Suffixos "Direita/Esquerda" removidos e erro "Direto" corrigido para "Ombro".

Estrutura	Região Pertencente
Esternoclavicular	Membros Superiores
Clavícula	Membros Superiores
Ombro	Membros Superiores
Braço	Membros Superiores
Cotovelo	Membros Superiores
Antebraço	Membros Superiores
Punho	Membros Superiores
Mão	Membros Superiores
Cervical	Coluna
Torácica	Coluna
Lombar	Coluna
Sacro	Coluna
Cóccix	Coluna
Ilíaco	Bacia
Ísquio	Bacia
Púbico	Bacia
Quadril	Membros Inferiores
Coxa	Membros Inferiores
Perna	Membros Inferiores
Tornozelo	Membros Inferiores
Pé	Membros Inferiores
Tórax (Geral)	Tórax
Core (Geral)	Core

Tabela 4: Lateralidade

ID	Opção
1	Direita
2	Esquerda
3	Bilateral
4	Não é o caso

6. Considerações sobre Integridade e Expansão

A arquitetura proposta soluciona a fragmentação do CSV original. Anteriormente, se uma estrutura (como o Ombro) sofresse uma lesão óssea e uma tendinosa, os dados estariam em colunas separadas sem relação direta. Agora, através da tabela diagnosticos_clinicos, podemos registrar múltiplos tipos de lesão para a mesma estrutura anatômica de forma coesa.

Master Query: Reconstrução de Diagnóstico

Para gerar um relatório completo que converta IDs em termos clínicos legíveis, utiliza-se a seguinte consulta:

SELECT 
    d.data_registro AS Data,
    t.nome AS Tipo_Lesao,
    r.nome AS Regiao,
    e.nome AS Estrutura,
    l.nome AS Lado
FROM diagnosticos_clinicos d
JOIN tipos_lesao t ON d.tipo_lesao_id = t.id
JOIN estruturas_anatomicas e ON d.estrutura_id = e.id
JOIN regioes_corpo r ON e.regiao_id = r.id
JOIN lateralidades l ON d.lateralidade_id = l.id
ORDER BY d.data_registro DESC;


7. Conclusão Técnica

O modelo relacional aqui apresentado supera as limitações da estrutura tabular ao instituir uma separação clara de preocupações. A normalização para 3NF não apenas elimina redundâncias, mas protege o sistema contra anomalias de dados e facilita a manutenção. Com o uso de chaves estrangeiras, restrições de unicidade e uma tabela de fatos para diagnósticos, a estrutura está pronta para implementação em ambientes de alta criticidade, garantindo que o Sistema de Informação Ortopédica possua uma base de dados escalável, performática e confiável.
