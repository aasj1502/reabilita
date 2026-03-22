--
-- PostgreSQL database dump
--

\restrict ucoRhNEUn7YvfWZY1SoW9qWadFL6TWw2qrsNm9K2larfAbJ2oTGdyPlXaPn9KXd

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-03-22 00:20:45

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 943 (class 1259 OID 48376)
-- Name: update_pessoa; Type: TABLE; Schema: espcex; Owner: postgres
--

CREATE TABLE espcex.update_pessoa (
    cod_pessoa integer NOT NULL,
    cod_posto_grad integer NOT NULL,
    cod_sit_g integer DEFAULT 1 NOT NULL,
    cod_sit integer DEFAULT 1 NOT NULL,
    cod_religiao numeric(2,0),
    cod_tp_sang integer,
    cod_sexo character varying(1) NOT NULL,
    cod_pessoal character varying(6),
    cod_est_civ numeric(2,0),
    cod_naturalidade integer,
    nome character varying(70) NOT NULL,
    nome_guerra character varying(20) NOT NULL,
    dt_ult_prom date,
    turma_formacao character varying(4),
    clas_turma character varying(7) DEFAULT '999/999'::character varying,
    dt_nasc date DEFAULT '1900-01-01'::date NOT NULL,
    numero integer,
    ncf numeric(5,3),
    agencia character varying(6),
    conta_corrente character varying(12),
    cod_cidade_eleitor integer,
    zona_eleitor numeric(4,0),
    secao_eleitor numeric(4,0),
    prec_cp character varying(9),
    cpf character varying(11),
    pis_pasep character varying(11),
    titulo_eleitor character varying(12),
    nr_cnh character varying(11),
    valid_cnh date,
    cod_banco integer,
    cod_circ integer,
    cod_categ_cnh integer,
    id_qual integer,
    cod_frc integer DEFAULT 9999 NOT NULL,
    mes_nasc integer,
    usuario text DEFAULT 'postgres'::text NOT NULL,
    idt_mil character varying(10),
    dt_apres date,
    login character varying(50),
    sincronizado boolean DEFAULT false NOT NULL,
    editavel boolean DEFAULT true NOT NULL,
    cod_sit_ant integer DEFAULT 1 NOT NULL,
    cod_alt_sit integer,
    login_antigo character varying(50),
    cep character varying(8),
    num_end character varying(10),
    compl_end character varying,
    cod_alt_sit_pend integer,
    obs_pessoa text,
    nomeado boolean DEFAULT false NOT NULL,
    dt_nomeacao date,
    dt_reconducao date,
    cod_cptm smallint DEFAULT 3 NOT NULL,
    renda_fam double precision,
    ano numeric(1,0),
    pais_sep boolean,
    cod_origem integer,
    doador_org boolean DEFAULT false NOT NULL,
    cod_posto_grad_ant integer,
    rep_espcex boolean DEFAULT false NOT NULL,
    cod_cur_aman integer,
    cod_olho numeric(2,0),
    cod_cutis numeric(2,0),
    cod_cabelo numeric(3,0),
    altura real,
    peso real,
    sin_partic character varying(100),
    nome_pai character varying(150),
    nome_mae character varying(150),
    posto_grad_pai character varying(20),
    posto_grad_mae character varying(20),
    turma_pai numeric(4,0),
    turma_mae numeric(4,0),
    profissao_pai character varying(50),
    profissao_mae character varying(50),
    om_pai character varying(50),
    om_mae character varying(50),
    sit_mil_pai character varying(50),
    sit_mil_mae character varying(50),
    email character varying(50),
    ano_turma_espcex integer NOT NULL,
    nome_ctto_1 character varying(60),
    nome_ctto_2 character varying(60),
    nome_ctto_3 character varying(60),
    tel_ctto_1 character varying(20),
    tel_ctto_2 character varying(20),
    tel_ctto_3 character varying(20),
    cod_parent_ctto_1 integer,
    cod_parent_ctto_2 integer,
    cod_parent_ctto_3 integer,
    CONSTRAINT update_pessoa_sexo_chk CHECK ((((cod_sexo)::text = 'm'::text) OR ((cod_sexo)::text = 'f'::text)))
)
WITH (fillfactor='100');


ALTER TABLE espcex.update_pessoa OWNER TO postgres;

--
-- TOC entry 9961 (class 0 OID 0)
-- Dependencies: 943
-- Name: COLUMN update_pessoa.cod_sit_ant; Type: COMMENT; Schema: espcex; Owner: postgres
--

COMMENT ON COLUMN espcex.update_pessoa.cod_sit_ant IS 'Situação anterior antes da publicação do afastamento ou do retorno do afastamento.';


--
-- TOC entry 9962 (class 0 OID 0)
-- Dependencies: 943
-- Name: COLUMN update_pessoa.cod_alt_sit; Type: COMMENT; Schema: espcex; Owner: postgres
--

COMMENT ON COLUMN espcex.update_pessoa.cod_alt_sit IS 'Código da última alteração que alterou a situação da pessoa';


--
-- TOC entry 9963 (class 0 OID 0)
-- Dependencies: 943
-- Name: COLUMN update_pessoa.cod_alt_sit_pend; Type: COMMENT; Schema: espcex; Owner: postgres
--

COMMENT ON COLUMN espcex.update_pessoa.cod_alt_sit_pend IS 'Código da alteração que modifica a situação da pessoa que está pendente de execução';


--
-- TOC entry 9518 (class 2606 OID 174318)
-- Name: update_pessoa update_pessoa_cpf_key; Type: CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_cpf_key UNIQUE (cpf);


--
-- TOC entry 9520 (class 2606 OID 174320)
-- Name: update_pessoa update_pessoa_idt_mil_key; Type: CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_idt_mil_key UNIQUE (idt_mil);


--
-- TOC entry 9524 (class 2606 OID 174322)
-- Name: update_pessoa update_pessoa_login_antigo_key; Type: CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_login_antigo_key UNIQUE (login_antigo);


--
-- TOC entry 9526 (class 2606 OID 174324)
-- Name: update_pessoa update_pessoa_login_pessoa_idx; Type: CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_login_pessoa_idx UNIQUE (login);


--
-- TOC entry 9528 (class 2606 OID 174326)
-- Name: update_pessoa update_pessoa_pkey; Type: CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_pkey PRIMARY KEY (cod_pessoa);


--
-- TOC entry 9521 (class 1259 OID 175103)
-- Name: update_pessoa_idx; Type: INDEX; Schema: espcex; Owner: postgres
--

CREATE INDEX update_pessoa_idx ON espcex.update_pessoa USING btree (numero);


--
-- TOC entry 9522 (class 1259 OID 175104)
-- Name: update_pessoa_idx1; Type: INDEX; Schema: espcex; Owner: postgres
--

CREATE UNIQUE INDEX update_pessoa_idx1 ON espcex.update_pessoa USING btree (cod_pessoa, idt_mil);


--
-- TOC entry 9541 (class 2620 OID 175297)
-- Name: update_pessoa 1_atualiz_cadastro_pessoa_base_alteracao_al_espcex_tr; Type: TRIGGER; Schema: espcex; Owner: postgres
--

CREATE TRIGGER "1_atualiz_cadastro_pessoa_base_alteracao_al_espcex_tr" AFTER UPDATE ON espcex.update_pessoa FOR EACH ROW EXECUTE FUNCTION espcex.atualiz_cadastro_pessoa_base_update_pessoa();


--
-- TOC entry 9529 (class 2606 OID 176274)
-- Name: update_pessoa cidadepessoa; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT cidadepessoa FOREIGN KEY (cod_naturalidade) REFERENCES pessoal.cidade(cod_cidade) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9530 (class 2606 OID 176299)
-- Name: update_pessoa posto_gradpessoa; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT posto_gradpessoa FOREIGN KEY (cod_posto_grad) REFERENCES pessoal.posto_grad(cod_posto_grad) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9531 (class 2606 OID 176304)
-- Name: update_pessoa tipo_sanguineopessoa; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT tipo_sanguineopessoa FOREIGN KEY (cod_tp_sang) REFERENCES pessoal.tipo_sanguineo(cod_tp_sang) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9532 (class 2606 OID 176309)
-- Name: update_pessoa update_pessoa_fk; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_fk FOREIGN KEY (cod_est_civ) REFERENCES pessoal.estado_civil(cod_est_civ) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9533 (class 2606 OID 176314)
-- Name: update_pessoa update_pessoa_fk1; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_fk1 FOREIGN KEY (cod_sit) REFERENCES pessoal.situacao(cod_sit) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9534 (class 2606 OID 176319)
-- Name: update_pessoa update_pessoa_fk2; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_fk2 FOREIGN KEY (cod_religiao) REFERENCES pessoal.religiao(codigo_religiao) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9535 (class 2606 OID 176324)
-- Name: update_pessoa update_pessoa_fk3; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_fk3 FOREIGN KEY (cod_banco) REFERENCES pessoal.banco(cod_banco) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9536 (class 2606 OID 176329)
-- Name: update_pessoa update_pessoa_fk4; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_fk4 FOREIGN KEY (cod_cidade_eleitor) REFERENCES pessoal.cidade(cod_cidade) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9537 (class 2606 OID 176334)
-- Name: update_pessoa update_pessoa_fk5; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_fk5 FOREIGN KEY (cod_categ_cnh) REFERENCES pessoal.catg_cnh(cod_categ_cnh) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9538 (class 2606 OID 176339)
-- Name: update_pessoa update_pessoa_fk6; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_fk6 FOREIGN KEY (cod_sit_g) REFERENCES pessoal.sit_geral(cod_sit_g) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9539 (class 2606 OID 176344)
-- Name: update_pessoa update_pessoa_fk7; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_fk7 FOREIGN KEY (id_qual) REFERENCES pessoal.qualificacao(id_qual) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9540 (class 2606 OID 176349)
-- Name: update_pessoa update_pessoa_fk8; Type: FK CONSTRAINT; Schema: espcex; Owner: postgres
--

ALTER TABLE ONLY espcex.update_pessoa
    ADD CONSTRAINT update_pessoa_fk8 FOREIGN KEY (cod_frc) REFERENCES pessoal.fracao(cod_frc) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


-- Completed on 2026-03-22 00:20:45

--
-- PostgreSQL database dump complete
--

\unrestrict ucoRhNEUn7YvfWZY1SoW9qWadFL6TWw2qrsNm9K2larfAbJ2oTGdyPlXaPn9KXd

