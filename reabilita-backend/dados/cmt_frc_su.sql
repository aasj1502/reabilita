--
-- PostgreSQL database dump
--

\restrict ati2pfYYaeVi5ZSKfWapI833XoxWA2D6lhR1IVj1F1MlP6HWAzH91apW7QK52Vk

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-03-22 00:45:22

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

--
-- TOC entry 1844 (class 1259 OID 53199)
-- Name: mapa_cmt_su_cursos; Type: VIEW; Schema: principal; Owner: postgres
--

CREATE VIEW principal.mapa_cmt_su_cursos AS
 SELECT fracao_curso.sigla_frc AS sigla_frc_curso,
    fracao.sigla_frc,
    fracoes_ocupadas.adm_escolar,
    fracoes_ocupadas.arranch_coletivo,
    fracoes_ocupadas.mcc,
    fracoes_ocupadas.meritocracia,
    fracoes_ocupadas.soc,
    fracao.cod_frc,
    fracoes_ocupadas.cod_pessoa
   FROM ((pessoal.fracao
     JOIN pessoal.fracao fracao_curso ON ((fracao.cod_frc_pai = fracao_curso.cod_frc)))
     LEFT JOIN ( SELECT base_cmt_su.cod_frc,
            max(
                CASE
                    WHEN (base_cmt_su.cod_sist = 12) THEN base_cmt_su.cmt_su
                    ELSE NULL::text
                END) AS adm_escolar,
            max(
                CASE
                    WHEN (base_cmt_su.cod_sist = 7) THEN base_cmt_su.cmt_su
                    ELSE NULL::text
                END) AS arranch_coletivo,
            max(
                CASE
                    WHEN (base_cmt_su.cod_sist = 14) THEN base_cmt_su.cmt_su
                    ELSE NULL::text
                END) AS meritocracia,
            max(
                CASE
                    WHEN (base_cmt_su.cod_sist = 17) THEN base_cmt_su.cmt_su
                    ELSE NULL::text
                END) AS mcc,
            max(
                CASE
                    WHEN (base_cmt_su.cod_sist = 16) THEN base_cmt_su.cmt_su
                    ELSE NULL::text
                END) AS soc,
            base_cmt_su.cod_pessoa
           FROM ( SELECT ct_usuario_fracao.cod_frc,
                    ct_aces_sist_perif.cod_sist,
                    string_agg((((posto_grad.abrev_posto_grad)::text || ' '::text) || (pessoa.nome_guerra)::text), ', '::text) AS cmt_su,
                    pessoa.cod_pessoa
                   FROM (((((pessoal.pessoa
                     JOIN pessoal.posto_grad ON ((posto_grad.cod_posto_grad = pessoa.cod_posto_grad)))
                     JOIN principal.ct_aces_sist_perif ON ((ct_aces_sist_perif.cod_pessoa = pessoa.cod_pessoa)))
                     JOIN principal.ct_usuario_fracao ON (((ct_aces_sist_perif.cod_pessoa = ct_usuario_fracao.cod_pessoa) AND (ct_aces_sist_perif.cod_sist = ct_usuario_fracao.cod_sist))))
                     JOIN principal.ni_aces_sist_perif ON (((ct_aces_sist_perif.cod_sist = ni_aces_sist_perif.cod_sist) AND (ct_aces_sist_perif.cod_ni = ni_aces_sist_perif.cod_ni))))
                     JOIN principal.sistemas_perifericos ON ((ni_aces_sist_perif.cod_sist = sistemas_perifericos.cod_sist)))
                  WHERE ((ct_aces_sist_perif.cod_sist = ANY (ARRAY[12, 14, 16, 17, 7])) AND ((ni_aces_sist_perif.nivel)::text = 'Cmt SU'::text) AND (ct_aces_sist_perif.situacao = 1))
                  GROUP BY ct_usuario_fracao.cod_frc, ct_aces_sist_perif.cod_sist, pessoa.cod_pessoa) base_cmt_su
          GROUP BY base_cmt_su.cod_frc, base_cmt_su.cod_pessoa) fracoes_ocupadas ON ((fracao.cod_frc = fracoes_ocupadas.cod_frc)))
  WHERE (fracao.su_cur_aman IS TRUE)
  ORDER BY fracao_curso.sigla_frc, fracao.sigla_frc;


ALTER VIEW principal.mapa_cmt_su_cursos OWNER TO postgres;

-- Completed on 2026-03-22 00:45:22

--
-- PostgreSQL database dump complete
--

\unrestrict ati2pfYYaeVi5ZSKfWapI833XoxWA2D6lhR1IVj1F1MlP6HWAzH91apW7QK52Vk

