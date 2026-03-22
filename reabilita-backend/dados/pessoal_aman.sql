--
-- PostgreSQL database dump
--

\restrict td3oeWwkGXpGg4IYDM3MntVLBG79itaUWHclV7ECluBZojhem8fbbIMDVAgjDDM

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-03-22 00:23:50

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
-- TOC entry 314 (class 1259 OID 42574)
-- Name: posto_grad; Type: TABLE; Schema: pessoal; Owner: postgres
--

CREATE TABLE pessoal.posto_grad (
    cod_posto_grad integer NOT NULL,
    cod_circ integer DEFAULT 0,
    abrev_posto_grad character varying(15),
    dcri_posto_grad character varying(30),
    cod_forca integer NOT NULL
);


ALTER TABLE pessoal.posto_grad OWNER TO postgres;

--
-- TOC entry 9505 (class 2606 OID 174778)
-- Name: posto_grad posto_grad_pkey; Type: CONSTRAINT; Schema: pessoal; Owner: postgres
--

ALTER TABLE ONLY pessoal.posto_grad
    ADD CONSTRAINT posto_grad_pkey PRIMARY KEY (cod_posto_grad);


--
-- TOC entry 9506 (class 2606 OID 177594)
-- Name: posto_grad posto_grad_fk; Type: FK CONSTRAINT; Schema: pessoal; Owner: postgres
--

ALTER TABLE ONLY pessoal.posto_grad
    ADD CONSTRAINT posto_grad_fk FOREIGN KEY (cod_circ) REFERENCES pessoal.circulo(cod_circ) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE;


--
-- TOC entry 9507 (class 2606 OID 177599)
-- Name: posto_grad posto_grad_fk1; Type: FK CONSTRAINT; Schema: pessoal; Owner: postgres
--

ALTER TABLE ONLY pessoal.posto_grad
    ADD CONSTRAINT posto_grad_fk1 FOREIGN KEY (cod_forca) REFERENCES pessoal.forca(cod_forca) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE;


-- Completed on 2026-03-22 00:23:50

--
-- PostgreSQL database dump complete
--

\unrestrict td3oeWwkGXpGg4IYDM3MntVLBG79itaUWHclV7ECluBZojhem8fbbIMDVAgjDDM

