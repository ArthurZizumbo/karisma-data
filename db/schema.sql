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
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
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
-- Name: COLUMN app_user.updated_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.app_user.updated_at IS 'Ultima modificacion administrativa: cambio de rol, desactivacion o reactivacion. La fija el servicio, nunca un disparador.';


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
-- Name: catalog_lineage_step; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.catalog_lineage_step (
    id bigint NOT NULL,
    source_id bigint NOT NULL,
    step_order smallint NOT NULL,
    stage text NOT NULL,
    system_code text NOT NULL,
    system_name text NOT NULL,
    transformation_code text NOT NULL,
    transformation_detail text NOT NULL,
    owner_area text NOT NULL,
    owner_name text NOT NULL,
    effective_from date NOT NULL,
    effective_to date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT catalog_lineage_step_stage_check CHECK ((stage = ANY (ARRAY['origen'::text, 'extraccion'::text, 'transformacion'::text, 'calidad'::text]))),
    CONSTRAINT catalog_lineage_step_step_order_check CHECK (((step_order >= 1) AND (step_order <= 9))),
    CONSTRAINT catalog_lineage_step_system_code_check CHECK ((system_code <> ''::text)),
    CONSTRAINT catalog_lineage_step_system_name_check CHECK ((system_name <> ''::text)),
    CONSTRAINT catalog_lineage_step_transformation_code_check CHECK ((transformation_code = ANY (ARRAY['origin_capture'::text, 'batch_extract'::text, 'stream_extract'::text, 'type_normalization'::text, 'currency_conversion'::text, 'deduplication'::text, 'business_rule'::text, 'reconciliation'::text, 'quality_rule'::text]))),
    CONSTRAINT catalog_lineage_step_transformation_detail_check CHECK ((transformation_detail <> ''::text)),
    CONSTRAINT catalog_lineage_step_validity_chk CHECK (((effective_to IS NULL) OR (effective_to >= effective_from)))
);


--
-- Name: TABLE catalog_lineage_step; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.catalog_lineage_step IS 'Tramo aguas arriba del linaje, por fuente. El paso de presentacion se deriva de catalog_field y no se guarda aqui';


--
-- Name: COLUMN catalog_lineage_step.stage; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.catalog_lineage_step.stage IS 'presentacion no aparece en el CHECK a proposito: esa etapa se compone en el servicio';


--
-- Name: COLUMN catalog_lineage_step.transformation_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.catalog_lineage_step.transformation_code IS 'Codigo cerrado; la prosa visible vive en las claves i18n lineage.transformation.*';


--
-- Name: COLUMN catalog_lineage_step.transformation_detail; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.catalog_lineage_step.transformation_detail IS 'Dato no traducible interpolado en la plantilla: nombre de trabajo, de regla o de control';


--
-- Name: catalog_lineage_step_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.catalog_lineage_step_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: catalog_lineage_step_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.catalog_lineage_step_id_seq OWNED BY public.catalog_lineage_step.id;


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
-- Name: export_job; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.export_job (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    requested_by uuid NOT NULL,
    dataset text NOT NULL,
    export_format text NOT NULL,
    filters jsonb DEFAULT '{}'::jsonb NOT NULL,
    status text DEFAULT 'pendiente'::text NOT NULL,
    row_count bigint,
    byte_size bigint,
    object_key text,
    error_code text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    started_at timestamp with time zone,
    finished_at timestamp with time zone,
    expires_at timestamp with time zone,
    CONSTRAINT export_job_completado_coherente CHECK (((status <> 'completado'::text) OR ((object_key IS NOT NULL) AND (expires_at IS NOT NULL) AND (finished_at IS NOT NULL)))),
    CONSTRAINT export_job_export_format_check CHECK ((export_format = ANY (ARRAY['csv'::text, 'xlsx'::text]))),
    CONSTRAINT export_job_fallido_coherente CHECK (((status <> 'fallido'::text) OR (error_code IS NOT NULL))),
    CONSTRAINT export_job_status_check CHECK ((status = ANY (ARRAY['pendiente'::text, 'en_proceso'::text, 'completado'::text, 'fallido'::text])))
);


--
-- Name: TABLE export_job; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.export_job IS 'Trabajos de exportacion en segundo plano. Nunca se borran: caducan.';


--
-- Name: COLUMN export_job.filters; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.export_job.filters IS 'Consulta estructurada validada por Pydantic. Nunca SQL ni Polars libre.';


--
-- Name: COLUMN export_job.object_key; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.export_job.object_key IS 'Clave opaca en el almacen. Jamas se serializa en una respuesta.';


--
-- Name: COLUMN export_job.expires_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.export_job.expires_at IS 'Instante en que el enlace firmado deja de servir. created_at + 24 h.';


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
-- Name: catalog_lineage_step id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_lineage_step ALTER COLUMN id SET DEFAULT nextval('public.catalog_lineage_step_id_seq'::regclass);


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
-- Name: catalog_lineage_step catalog_lineage_step_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_lineage_step
    ADD CONSTRAINT catalog_lineage_step_pkey PRIMARY KEY (id);


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
-- Name: export_job export_job_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.export_job
    ADD CONSTRAINT export_job_pkey PRIMARY KEY (id);


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
-- Name: catalog_lineage_step_source_order_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX catalog_lineage_step_source_order_key ON public.catalog_lineage_step USING btree (source_id, step_order);


--
-- Name: catalog_tribal_note_field_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX catalog_tribal_note_field_id_idx ON public.catalog_tribal_note USING btree (field_id);


--
-- Name: export_job_expires_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX export_job_expires_at_idx ON public.export_job USING btree (expires_at) WHERE (status = 'completado'::text);


--
-- Name: export_job_requested_by_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX export_job_requested_by_created_at_idx ON public.export_job USING btree (requested_by, created_at DESC);


--
-- Name: export_job_status_vivos_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX export_job_status_vivos_idx ON public.export_job USING btree (status) WHERE (status = ANY (ARRAY['pendiente'::text, 'en_proceso'::text]));


--
-- Name: catalog_field catalog_field_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_field
    ADD CONSTRAINT catalog_field_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.catalog_source(id) ON DELETE CASCADE;


--
-- Name: catalog_lineage_step catalog_lineage_step_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_lineage_step
    ADD CONSTRAINT catalog_lineage_step_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.catalog_source(id) ON DELETE CASCADE;


--
-- Name: catalog_tribal_note catalog_tribal_note_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalog_tribal_note
    ADD CONSTRAINT catalog_tribal_note_field_id_fkey FOREIGN KEY (field_id) REFERENCES public.catalog_field(id) ON DELETE CASCADE;


--
-- Name: export_job export_job_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.export_job
    ADD CONSTRAINT export_job_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.app_user(id) ON DELETE RESTRICT;


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
    ('20260812065546'),
    ('20260812121501'),
    ('20260813204211'),
    ('20260813205114');
