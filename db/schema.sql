\restrict dbmate

-- Dumped from database version 15.18 (Debian 15.18-1.pgdg12+1)
-- Dumped by pg_dump version 18.4

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
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: app_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.app_user (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    username text NOT NULL,
    email text NOT NULL,
    full_name text NOT NULL,
    hashed_password text NOT NULL,
    role text NOT NULL,
    disabled boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT app_user_role_check CHECK ((role = ANY (ARRAY['operativo'::text, 'analista'::text, 'directivo'::text, 'admin'::text])))
);


--
-- Name: TABLE app_user; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.app_user IS 'Usuarios del portal. Baja logica con disabled, nunca DELETE.';


--
-- Name: COLUMN app_user.hashed_password; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.app_user.hashed_password IS 'argon2id via pwdlib. Jamas texto plano, jamas serializado en una respuesta.';


--
-- Name: COLUMN app_user.role; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.app_user.role IS 'Scope del JWT: operativo | analista | directivo | admin.';


--
-- Name: catalog_field; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.catalog_field (
    id bigint NOT NULL,
    source_id bigint NOT NULL,
    physical_name text NOT NULL,
    business_name text NOT NULL,
    definition text NOT NULL,
    aliases text DEFAULT ''::text NOT NULL,
    domain text NOT NULL,
    data_type text NOT NULL,
    sensitivity text NOT NULL,
    refresh_frequency text NOT NULL,
    certification text NOT NULL,
    unit text,
    metric_agg text,
    steward text,
    valid_from date NOT NULL,
    valid_to date,
    embedding public.vector(768),
    search_document tsvector GENERATED ALWAYS AS (((setweight(to_tsvector('spanish'::regconfig, business_name), 'A'::"char") || setweight(to_tsvector('spanish'::regconfig, ((physical_name || ' '::text) || aliases)), 'B'::"char")) || setweight(to_tsvector('spanish'::regconfig, definition), 'C'::"char"))) STORED,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT catalog_field_certification_check CHECK ((certification = ANY (ARRAY['certificado'::text, 'en_revision'::text, 'obsoleto'::text]))),
    CONSTRAINT catalog_field_data_type_check CHECK ((data_type = ANY (ARRAY['entero'::text, 'decimal'::text, 'texto'::text, 'fecha'::text, 'booleano'::text, 'categoria'::text]))),
    CONSTRAINT catalog_field_domain_check CHECK ((domain = ANY (ARRAY['cartera'::text, 'riesgo'::text, 'liquidez'::text, 'mercado'::text, 'cliente'::text, 'contable'::text, 'operacion'::text, 'regulatorio'::text]))),
    CONSTRAINT catalog_field_metric_agg_check CHECK ((metric_agg = ANY (ARRAY['sum'::text, 'mean'::text, 'count'::text, 'max'::text, 'min'::text]))),
    CONSTRAINT catalog_field_obsolete_chk CHECK (((certification = 'obsoleto'::text) = (valid_to IS NOT NULL))),
    CONSTRAINT catalog_field_refresh_frequency_check CHECK ((refresh_frequency = ANY (ARRAY['intradia'::text, 'diaria'::text, 'semanal'::text, 'mensual'::text]))),
    CONSTRAINT catalog_field_sensitivity_check CHECK ((sensitivity = ANY (ARRAY['publica'::text, 'interna'::text, 'restringida'::text]))),
    CONSTRAINT catalog_field_unit_check CHECK ((unit = ANY (ARRAY['MXN'::text, 'USD'::text, 'porcentaje'::text, 'dias'::text, 'conteo'::text]))),
    CONSTRAINT catalog_field_validity_chk CHECK (((valid_to IS NULL) OR (valid_to >= valid_from)))
);


--
-- Name: TABLE catalog_field; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.catalog_field IS 'Una entrada del catalogo: la traduccion de una columna fisica al lenguaje del negocio.';


--
-- Name: COLUMN catalog_field.aliases; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.catalog_field.aliases IS 'Sinonimos separados por espacio, incluidos los equivalentes en ingles; alimentan el peso B';


--
-- Name: COLUMN catalog_field.embedding; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.catalog_field.embedding IS 'Gemini 768d. Sin escribir en S4: la busqueda hibrida esta diferida por el recorte 1';


--
-- Name: COLUMN catalog_field.search_document; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.catalog_field.search_document IS 'Documento indexado: business_name en A, physical_name y aliases en B, definition en C';


--
-- Name: catalog_field_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.catalog_field_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: catalog_field_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.catalog_field_id_seq OWNED BY public.catalog_field.id;


--
-- Name: catalog_source; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.catalog_source (
    id bigint NOT NULL,
    code text NOT NULL,
    display_name text NOT NULL,
    description text NOT NULL,
    owner_area text NOT NULL,
    owner_name text NOT NULL,
    system_of_record text NOT NULL,
    has_extract boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE catalog_source; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.catalog_source IS 'Fuentes de datos que el portal documenta, con extracto o sin el.';


--
-- Name: COLUMN catalog_source.has_extract; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.catalog_source.has_extract IS 'true solo en los silos con Parquet generado por US-006; el resto se documenta sin extracto';


--
-- Name: catalog_source_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.catalog_source_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: catalog_source_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.catalog_source_id_seq OWNED BY public.catalog_source.id;


--
-- Name: catalog_tribal_note; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.catalog_tribal_note (
    id bigint NOT NULL,
    field_id bigint NOT NULL,
    note text NOT NULL,
    applicability text NOT NULL,
    applicability_terms text DEFAULT ''::text NOT NULL,
    author text NOT NULL,
    recorded_at date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE catalog_tribal_note; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.catalog_tribal_note IS 'Conocimiento tribal con condicion de aplicabilidad (patron Tk-Boost).';


--
-- Name: COLUMN catalog_tribal_note.applicability_terms; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.catalog_tribal_note.applicability_terms IS 'Terminos disparadores (patron Tk-Boost); cadena vacia significa que la nota aplica siempre';


--
-- Name: catalog_tribal_note_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.catalog_tribal_note_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: catalog_tribal_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.catalog_tribal_note_id_seq OWNED BY public.catalog_tribal_note.id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


--
-- Name: catalog_field id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_field ALTER COLUMN id SET DEFAULT nextval('public.catalog_field_id_seq'::regclass);


--
-- Name: catalog_source id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_source ALTER COLUMN id SET DEFAULT nextval('public.catalog_source_id_seq'::regclass);


--
-- Name: catalog_tribal_note id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_tribal_note ALTER COLUMN id SET DEFAULT nextval('public.catalog_tribal_note_id_seq'::regclass);


--
-- Name: app_user app_user_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_email_key UNIQUE (email);


--
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (id);


--
-- Name: app_user app_user_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_username_key UNIQUE (username);


--
-- Name: catalog_field catalog_field_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_field
    ADD CONSTRAINT catalog_field_pkey PRIMARY KEY (id);


--
-- Name: catalog_field catalog_field_source_physical_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_field
    ADD CONSTRAINT catalog_field_source_physical_key UNIQUE (source_id, physical_name);


--
-- Name: catalog_source catalog_source_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_source
    ADD CONSTRAINT catalog_source_code_key UNIQUE (code);


--
-- Name: catalog_source catalog_source_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_source
    ADD CONSTRAINT catalog_source_pkey PRIMARY KEY (id);


--
-- Name: catalog_tribal_note catalog_tribal_note_field_note_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_tribal_note
    ADD CONSTRAINT catalog_tribal_note_field_note_key UNIQUE (field_id, note);


--
-- Name: catalog_tribal_note catalog_tribal_note_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_tribal_note
    ADD CONSTRAINT catalog_tribal_note_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: catalog_field_embedding_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX catalog_field_embedding_idx ON public.catalog_field USING hnsw (embedding public.vector_cosine_ops) WITH (m='16', ef_construction='64');


--
-- Name: catalog_field_search_document_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX catalog_field_search_document_idx ON public.catalog_field USING gin (search_document);


--
-- Name: catalog_field_source_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX catalog_field_source_id_idx ON public.catalog_field USING btree (source_id);


--
-- Name: catalog_tribal_note_field_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX catalog_tribal_note_field_id_idx ON public.catalog_tribal_note USING btree (field_id);


--
-- Name: catalog_field catalog_field_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_field
    ADD CONSTRAINT catalog_field_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.catalog_source(id) ON DELETE CASCADE;


--
-- Name: catalog_tribal_note catalog_tribal_note_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_tribal_note
    ADD CONSTRAINT catalog_tribal_note_field_id_fkey FOREIGN KEY (field_id) REFERENCES public.catalog_field(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict dbmate


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20260811005732'),
    ('20260811211250'),
    ('20260812065546');
