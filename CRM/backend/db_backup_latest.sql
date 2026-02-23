--
-- PostgreSQL database dump
--

\restrict NKjvCW5buHtmztcvtCzPheGpkTdYcgsHjKT2KWTMzXNyZ5sAYcc0bjjfeubd5k6

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: contact_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.contact_type AS ENUM (
    'PRIMARY',
    'BILLING',
    'TECHNICAL',
    'COMPLIANCE',
    'OTHER'
);


ALTER TYPE public.contact_type OWNER TO postgres;

--
-- Name: contacttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.contacttype AS ENUM (
    'PRIMARY',
    'BILLING',
    'TECHNICAL',
    'COMPLIANCE',
    'OTHER'
);


ALTER TYPE public.contacttype OWNER TO postgres;

--
-- Name: email_provider_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.email_provider_type AS ENUM (
    'GMAIL',
    'OUTLOOK',
    'CUSTOM'
);


ALTER TYPE public.email_provider_type OWNER TO postgres;

--
-- Name: emailprovidertype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.emailprovidertype AS ENUM (
    'GMAIL',
    'OUTLOOK',
    'CUSTOM'
);


ALTER TYPE public.emailprovidertype OWNER TO postgres;

--
-- Name: step_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.step_type AS ENUM (
    'START',
    'NORMAL',
    'QUERY',
    'END'
);


ALTER TYPE public.step_type OWNER TO postgres;

--
-- Name: steptype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.steptype AS ENUM (
    'START',
    'NORMAL',
    'QUERY',
    'END'
);


ALTER TYPE public.steptype OWNER TO postgres;

--
-- Name: storage_provider_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.storage_provider_type AS ENUM (
    'SHAREPOINT',
    'ZOHO_DRIVE',
    'AZURE_BLOB',
    'LOCAL',
    'GOOGLE_DRIVE'
);


ALTER TYPE public.storage_provider_type OWNER TO postgres;

--
-- Name: storageprovidertype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.storageprovidertype AS ENUM (
    'SHAREPOINT',
    'ZOHO_DRIVE',
    'AZURE_BLOB',
    'LOCAL'
);


ALTER TYPE public.storageprovidertype OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: access_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.access_logs (
    id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    access_type character varying(50) NOT NULL,
    ip_address character varying(50) NOT NULL,
    ip_type character varying(20),
    country character varying(100),
    country_code character varying(10),
    region character varying(100),
    region_code character varying(20),
    city character varying(100),
    postal_code character varying(20),
    latitude double precision,
    longitude double precision,
    timezone character varying(50),
    isp character varying(200),
    organization character varying(200),
    as_number character varying(50),
    user_agent character varying(500),
    browser character varying(100),
    browser_version character varying(50),
    operating_system character varying(100),
    os_version character varying(50),
    device_type character varying(50),
    device_brand character varying(100),
    device_model character varying(100),
    session_id character varying(100),
    is_successful boolean,
    failure_reason character varying(200),
    is_vpn boolean,
    is_proxy boolean,
    is_tor boolean,
    is_suspicious boolean,
    threat_level character varying(20),
    company_id character varying(36),
    created_at timestamp without time zone
);


ALTER TABLE public.access_logs OWNER TO postgres;

--
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_logs (
    id character varying(36) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id character varying(36) NOT NULL,
    action character varying(50) NOT NULL,
    details json,
    performed_by_id character varying(36),
    company_id character varying(36),
    ip_address character varying(50),
    user_agent character varying(500),
    created_at timestamp without time zone
);


ALTER TABLE public.activity_logs OWNER TO postgres;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: assignment_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assignment_history (
    id integer NOT NULL,
    service_request_id character varying(36) NOT NULL,
    from_user_id character varying(36),
    to_user_id character varying(36),
    assigned_by_id character varying(36),
    assignment_type character varying(50) DEFAULT 'reassignment'::character varying NOT NULL,
    reason text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.assignment_history OWNER TO postgres;

--
-- Name: assignment_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.assignment_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.assignment_history_id_seq OWNER TO postgres;

--
-- Name: assignment_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.assignment_history_id_seq OWNED BY public.assignment_history.id;


--
-- Name: client_notes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_notes (
    id integer NOT NULL,
    user_id character varying(36) NOT NULL,
    created_by_id character varying(36),
    content text NOT NULL,
    is_pinned boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.client_notes OWNER TO postgres;

--
-- Name: client_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.client_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.client_notes_id_seq OWNER TO postgres;

--
-- Name: client_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.client_notes_id_seq OWNED BY public.client_notes.id;


--
-- Name: client_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_tags (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    color character varying(20),
    company_id character varying(36) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.client_tags OWNER TO postgres;

--
-- Name: client_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.client_tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.client_tags_id_seq OWNER TO postgres;

--
-- Name: client_tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.client_tags_id_seq OWNED BY public.client_tags.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.companies (
    id character varying(36) NOT NULL,
    name character varying(200) NOT NULL,
    trading_name character varying(200),
    abn character varying(20),
    acn character varying(20),
    email character varying(120),
    phone character varying(20),
    website character varying(200),
    address_line1 character varying(200),
    address_line2 character varying(200),
    city character varying(100),
    state character varying(50),
    postcode character varying(10),
    country character varying(100),
    owner_id character varying(36),
    plan_type character varying(50),
    max_users integer,
    max_clients integer,
    is_active boolean,
    logo_url character varying(500),
    primary_color character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    invoice_prefix character varying(20) DEFAULT 'INV'::character varying,
    invoice_footer text,
    invoice_notes text,
    invoice_bank_details text,
    invoice_payment_terms character varying(100) DEFAULT 'Due within 14 days'::character varying,
    invoice_email_subject character varying(200) DEFAULT 'Invoice from {company_name}'::character varying,
    invoice_email_body text,
    secondary_color character varying(20) DEFAULT '#10B981'::character varying,
    tertiary_color character varying(20) DEFAULT '#6366F1'::character varying,
    company_type character varying(50) DEFAULT 'tax_agent'::character varying,
    currency character varying(3) DEFAULT 'AUD'::character varying,
    currency_symbol character varying(5) DEFAULT '$'::character varying,
    tax_type character varying(20) DEFAULT 'GST'::character varying,
    tax_label character varying(50) DEFAULT 'GST'::character varying,
    default_tax_rate numeric(5,2) DEFAULT 10.00,
    logo_data bytea,
    logo_mime_type character varying(50),
    logo_storage_type character varying(50),
    logo_blob_name character varying(255),
    theme_primary_color character varying(20),
    theme_secondary_color character varying(20),
    sidebar_bg_color character varying(20) DEFAULT '#0f172a'::character varying,
    sidebar_text_color character varying(20) DEFAULT '#ffffff'::character varying,
    sidebar_hover_bg_color character varying(20) DEFAULT '#334155'::character varying,
    invoice_show_logo boolean DEFAULT true,
    invoice_show_company_details boolean DEFAULT true,
    invoice_show_client_details boolean DEFAULT true,
    invoice_show_bank_details boolean DEFAULT true,
    invoice_show_payment_terms boolean DEFAULT true,
    invoice_show_notes boolean DEFAULT true,
    invoice_show_footer boolean DEFAULT true,
    invoice_show_tax boolean DEFAULT true
);


ALTER TABLE public.companies OWNER TO postgres;

--
-- Name: COLUMN companies.invoice_prefix; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.companies.invoice_prefix IS 'Prefix for invoice numbers (e.g., INV, BILL)';


--
-- Name: COLUMN companies.invoice_footer; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.companies.invoice_footer IS 'Footer text displayed on invoices';


--
-- Name: COLUMN companies.invoice_notes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.companies.invoice_notes IS 'Default notes/terms for invoices';


--
-- Name: COLUMN companies.invoice_bank_details; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.companies.invoice_bank_details IS 'Bank account details for payment';


--
-- Name: COLUMN companies.invoice_payment_terms; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.companies.invoice_payment_terms IS 'Payment terms text';


--
-- Name: COLUMN companies.invoice_email_subject; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.companies.invoice_email_subject IS 'Email subject template for invoice emails';


--
-- Name: COLUMN companies.invoice_email_body; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.companies.invoice_email_body IS 'Email body template for invoice emails';


--
-- Name: COLUMN companies.logo_data; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.companies.logo_data IS 'Binary data of company logo image';


--
-- Name: COLUMN companies.logo_mime_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.companies.logo_mime_type IS 'MIME type of logo image (e.g., image/png, image/jpeg)';


--
-- Name: company_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_contacts (
    id character varying(36) NOT NULL,
    company_id character varying(36) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(120),
    phone character varying(20),
    "position" character varying(100),
    contact_type public.contact_type DEFAULT 'PRIMARY'::public.contact_type,
    is_primary boolean DEFAULT false,
    effective_from date,
    effective_to date,
    is_active boolean DEFAULT true,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.company_contacts OWNER TO postgres;

--
-- Name: TABLE company_contacts; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.company_contacts IS 'Stores multiple contacts per company with role-based types and historical tracking';


--
-- Name: COLUMN company_contacts.contact_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_contacts.contact_type IS 'Classification of the contact: PRIMARY, BILLING, TECHNICAL, COMPLIANCE, or OTHER';


--
-- Name: COLUMN company_contacts.is_primary; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_contacts.is_primary IS 'Whether this is the primary contact for the company';


--
-- Name: COLUMN company_contacts.effective_from; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_contacts.effective_from IS 'Date from which this contact is effective';


--
-- Name: COLUMN company_contacts.effective_to; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_contacts.effective_to IS 'Date until which this contact is effective. NULL means currently active';


--
-- Name: company_email_configs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_email_configs (
    id character varying(36) NOT NULL,
    company_id character varying(36) NOT NULL,
    provider public.email_provider_type DEFAULT 'GMAIL'::public.email_provider_type,
    is_enabled boolean DEFAULT false,
    smtp_host character varying(255),
    smtp_port integer DEFAULT 587,
    smtp_username character varying(255),
    smtp_password character varying(500),
    smtp_use_tls boolean DEFAULT true,
    smtp_use_ssl boolean DEFAULT false,
    sender_email character varying(255),
    sender_name character varying(255),
    reply_to_email character varying(255),
    oauth_access_token text,
    oauth_refresh_token text,
    oauth_token_expires_at timestamp without time zone,
    last_test_at timestamp without time zone,
    last_test_success boolean,
    last_error text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.company_email_configs OWNER TO postgres;

--
-- Name: TABLE company_email_configs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.company_email_configs IS 'SMTP email configuration for companies - Gmail/Outlook/Custom SMTP';


--
-- Name: company_service_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_service_settings (
    id integer NOT NULL,
    company_id character varying(36) NOT NULL,
    service_id integer NOT NULL,
    is_active boolean,
    custom_name character varying(200),
    custom_description text,
    custom_price numeric(10,2),
    display_order integer,
    is_featured boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    cost_percentage numeric(5,2)
);


ALTER TABLE public.company_service_settings OWNER TO postgres;

--
-- Name: company_service_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_service_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.company_service_settings_id_seq OWNER TO postgres;

--
-- Name: company_service_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_service_settings_id_seq OWNED BY public.company_service_settings.id;


--
-- Name: company_storage_configs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_storage_configs (
    id character varying(36) NOT NULL,
    company_id character varying(36) NOT NULL,
    provider public.storage_provider_type DEFAULT 'LOCAL'::public.storage_provider_type,
    is_enabled boolean DEFAULT false,
    sharepoint_site_id character varying(255),
    sharepoint_drive_id character varying(255),
    sharepoint_root_folder character varying(255) DEFAULT 'CRM_Documents'::character varying,
    zoho_client_id character varying(255),
    zoho_client_secret character varying(500),
    zoho_access_token text,
    zoho_refresh_token text,
    zoho_token_expires_at timestamp without time zone,
    zoho_root_folder_id character varying(255),
    zoho_org_id character varying(255),
    azure_connection_string text,
    azure_container_name character varying(255),
    last_sync_at timestamp without time zone,
    last_error text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    google_client_id character varying(255),
    google_client_secret character varying(500),
    google_access_token text,
    google_refresh_token text,
    google_token_expires_at timestamp without time zone,
    google_root_folder_id character varying(255)
);


ALTER TABLE public.company_storage_configs OWNER TO postgres;

--
-- Name: TABLE company_storage_configs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.company_storage_configs IS 'Document storage provider configuration - SharePoint/Zoho Drive/Azure Blob';


--
-- Name: COLUMN company_storage_configs.google_client_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_storage_configs.google_client_id IS 'Google OAuth2 Client ID for Drive API';


--
-- Name: COLUMN company_storage_configs.google_client_secret; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_storage_configs.google_client_secret IS 'Google OAuth2 Client Secret';


--
-- Name: COLUMN company_storage_configs.google_access_token; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_storage_configs.google_access_token IS 'Google OAuth2 access token';


--
-- Name: COLUMN company_storage_configs.google_refresh_token; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_storage_configs.google_refresh_token IS 'Google OAuth2 refresh token for token renewal';


--
-- Name: COLUMN company_storage_configs.google_token_expires_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_storage_configs.google_token_expires_at IS 'Expiration time for the Google access token';


--
-- Name: COLUMN company_storage_configs.google_root_folder_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.company_storage_configs.google_root_folder_id IS 'Google Drive folder ID where documents will be stored';


--
-- Name: currencies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.currencies (
    id integer NOT NULL,
    code character varying(3) NOT NULL,
    name character varying(100) NOT NULL,
    symbol character varying(10) NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.currencies OWNER TO postgres;

--
-- Name: currencies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.currencies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.currencies_id_seq OWNER TO postgres;

--
-- Name: currencies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.currencies_id_seq OWNED BY public.currencies.id;


--
-- Name: db_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.db_version (
    id integer DEFAULT 1 NOT NULL,
    version integer DEFAULT 0 NOT NULL,
    applied_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT single_row CHECK ((id = 1))
);


ALTER TABLE public.db_version OWNER TO postgres;

--
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documents (
    id character varying(36) NOT NULL,
    original_filename character varying(500) NOT NULL,
    stored_filename character varying(500) NOT NULL,
    file_type character varying(50),
    file_size integer,
    mime_type character varying(100),
    blob_name character varying(1000),
    blob_url character varying(1000),
    storage_type character varying(50),
    uploaded_by_id character varying(36) NOT NULL,
    service_request_id character varying(36),
    document_category character varying(100),
    description text,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    storage_path character varying(1000),
    storage_url character varying(1000),
    external_item_id character varying(255),
    external_web_url character varying(1000),
    company_id character varying(36)
);


ALTER TABLE public.documents OWNER TO postgres;

--
-- Name: COLUMN documents.blob_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.documents.blob_name IS 'Deprecated - use storage_path';


--
-- Name: COLUMN documents.blob_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.documents.blob_url IS 'Deprecated - use storage_url';


--
-- Name: COLUMN documents.storage_path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.documents.storage_path IS 'Path/ID in storage (Google Drive ID, SharePoint path, blob path, local path)';


--
-- Name: COLUMN documents.storage_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.documents.storage_url IS 'URL to access the file';


--
-- Name: COLUMN documents.external_item_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.documents.external_item_id IS 'External ID (Google Drive file ID, SharePoint item ID, Zoho file ID)';


--
-- Name: COLUMN documents.external_web_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.documents.external_web_url IS 'Web URL for browser access';


--
-- Name: COLUMN documents.company_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.documents.company_id IS 'Company that owns this document';


--
-- Name: email_automation_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_automation_logs (
    id integer NOT NULL,
    automation_id integer NOT NULL,
    recipient_user_id character varying(36),
    recipient_email character varying(255) NOT NULL,
    trigger_data json,
    status character varying(20),
    error_message text,
    sent_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.email_automation_logs OWNER TO postgres;

--
-- Name: email_automation_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.email_automation_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.email_automation_logs_id_seq OWNER TO postgres;

--
-- Name: email_automation_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.email_automation_logs_id_seq OWNED BY public.email_automation_logs.id;


--
-- Name: email_automations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_automations (
    id integer NOT NULL,
    company_id character varying(36) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    trigger_type character varying(50) NOT NULL,
    trigger_config json,
    template_id integer,
    custom_subject character varying(500),
    custom_body text,
    delay_minutes integer,
    conditions json,
    is_active boolean,
    last_triggered_at timestamp without time zone,
    trigger_count integer,
    created_by character varying(36),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.email_automations OWNER TO postgres;

--
-- Name: email_automations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.email_automations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.email_automations_id_seq OWNER TO postgres;

--
-- Name: email_automations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.email_automations_id_seq OWNED BY public.email_automations.id;


--
-- Name: email_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_templates (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL,
    subject character varying(500) NOT NULL,
    body_html text NOT NULL,
    variables json,
    company_id character varying(36),
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    service_id integer,
    template_type character varying(50),
    service_category character varying(50)
);


ALTER TABLE public.email_templates OWNER TO postgres;

--
-- Name: email_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.email_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.email_templates_id_seq OWNER TO postgres;

--
-- Name: email_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.email_templates_id_seq OWNED BY public.email_templates.id;


--
-- Name: form_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.form_questions (
    id integer NOT NULL,
    form_id integer NOT NULL,
    question_text character varying(500) NOT NULL,
    question_type character varying(50) NOT NULL,
    is_required boolean,
    allow_attachment boolean,
    options json,
    validation_rules json,
    placeholder character varying(200),
    help_text character varying(500),
    "order" integer,
    created_at timestamp without time zone,
    section_number integer,
    section_title character varying(200),
    section_description text,
    is_section_repeatable boolean,
    section_group character varying(50),
    min_section_repeats integer,
    max_section_repeats integer,
    conditional_on_question_id integer,
    conditional_value character varying(200)
);


ALTER TABLE public.form_questions OWNER TO postgres;

--
-- Name: form_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.form_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.form_questions_id_seq OWNER TO postgres;

--
-- Name: form_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.form_questions_id_seq OWNED BY public.form_questions.id;


--
-- Name: form_responses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.form_responses (
    id integer NOT NULL,
    form_id integer NOT NULL,
    user_id character varying(36) NOT NULL,
    service_request_id character varying(36),
    response_data json NOT NULL,
    responses json,
    submitted_at timestamp without time zone,
    updated_at timestamp without time zone,
    status character varying(20)
);


ALTER TABLE public.form_responses OWNER TO postgres;

--
-- Name: form_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.form_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.form_responses_id_seq OWNER TO postgres;

--
-- Name: form_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.form_responses_id_seq OWNED BY public.form_responses.id;


--
-- Name: forms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forms (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    form_type character varying(50),
    is_active boolean,
    created_by_id character varying(36),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    company_id character varying(36),
    is_default boolean,
    cloned_from_id integer,
    status character varying(20)
);


ALTER TABLE public.forms OWNER TO postgres;

--
-- Name: forms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.forms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.forms_id_seq OWNER TO postgres;

--
-- Name: forms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.forms_id_seq OWNED BY public.forms.id;


--
-- Name: impersonation_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.impersonation_sessions (
    id character varying(36) NOT NULL,
    admin_id character varying(36) NOT NULL,
    impersonated_user_id character varying(36) NOT NULL,
    started_at timestamp without time zone NOT NULL,
    ended_at timestamp without time zone,
    reason text,
    ip_address character varying(50),
    user_agent character varying(500),
    action_count integer
);


ALTER TABLE public.impersonation_sessions OWNER TO postgres;

--
-- Name: import_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.import_logs (
    id integer NOT NULL,
    company_id character varying(36),
    imported_by_id character varying(36),
    import_type character varying(50) NOT NULL,
    filename character varying(255),
    total_rows integer DEFAULT 0,
    imported_count integer DEFAULT 0,
    skipped_count integer DEFAULT 0,
    error_count integer DEFAULT 0,
    errors jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.import_logs OWNER TO postgres;

--
-- Name: import_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.import_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.import_logs_id_seq OWNER TO postgres;

--
-- Name: import_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.import_logs_id_seq OWNED BY public.import_logs.id;


--
-- Name: invoice_line_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invoice_line_items (
    id integer NOT NULL,
    invoice_id character varying(36) NOT NULL,
    description character varying(500) NOT NULL,
    quantity numeric(10,2),
    unit_price numeric(10,2) NOT NULL,
    total numeric(10,2) NOT NULL,
    service_id integer,
    "order" integer,
    is_tax_exempt boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.invoice_line_items OWNER TO postgres;

--
-- Name: invoice_line_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.invoice_line_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invoice_line_items_id_seq OWNER TO postgres;

--
-- Name: invoice_line_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.invoice_line_items_id_seq OWNED BY public.invoice_line_items.id;


--
-- Name: invoice_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invoice_payments (
    id integer NOT NULL,
    invoice_id character varying(36) NOT NULL,
    amount numeric(10,2) NOT NULL,
    payment_method character varying(50),
    reference character varying(100),
    notes text,
    status character varying(20),
    stripe_payment_id character varying(100),
    stripe_payment_intent_id character varying(100),
    stripe_charge_id character varying(100),
    refund_amount numeric(10,2),
    refunded_at timestamp without time zone,
    payment_date timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.invoice_payments OWNER TO postgres;

--
-- Name: invoice_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.invoice_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invoice_payments_id_seq OWNER TO postgres;

--
-- Name: invoice_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.invoice_payments_id_seq OWNED BY public.invoice_payments.id;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invoices (
    id character varying(36) NOT NULL,
    invoice_number character varying(50) NOT NULL,
    reference character varying(100),
    company_id character varying(36) NOT NULL,
    client_id character varying(36) NOT NULL,
    service_request_id character varying(36),
    issue_date date NOT NULL,
    due_date date NOT NULL,
    subtotal numeric(10,2),
    tax_rate numeric(5,2),
    tax_amount numeric(10,2),
    discount_amount numeric(10,2),
    discount_description character varying(200),
    total numeric(10,2),
    amount_paid numeric(10,2),
    balance_due numeric(10,2),
    currency character varying(3),
    status character varying(20),
    notes text,
    internal_notes text,
    payment_terms text,
    payment_link character varying(500),
    stripe_invoice_id character varying(100),
    sent_at timestamp without time zone,
    viewed_at timestamp without time zone,
    paid_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by_id character varying(36)
);


ALTER TABLE public.invoices OWNER TO postgres;

--
-- Name: job_notes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_notes (
    id integer NOT NULL,
    service_request_id character varying(36) NOT NULL,
    created_by_id character varying(36),
    note_type character varying(50),
    content text NOT NULL,
    time_spent_minutes integer,
    created_at timestamp without time zone
);


ALTER TABLE public.job_notes OWNER TO postgres;

--
-- Name: job_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.job_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.job_notes_id_seq OWNER TO postgres;

--
-- Name: job_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.job_notes_id_seq OWNED BY public.job_notes.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id character varying(36) NOT NULL,
    title character varying(200) NOT NULL,
    message text NOT NULL,
    type character varying(50),
    link character varying(500),
    is_read boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notifications_id_seq OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: otps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.otps (
    id integer NOT NULL,
    user_id character varying(36) NOT NULL,
    code character varying(6) NOT NULL,
    purpose character varying(20) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    is_used boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.otps OWNER TO postgres;

--
-- Name: otps_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.otps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.otps_id_seq OWNER TO postgres;

--
-- Name: otps_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.otps_id_seq OWNED BY public.otps.id;


--
-- Name: queries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.queries (
    id integer NOT NULL,
    service_request_id character varying(36) NOT NULL,
    sender_id character varying(36) NOT NULL,
    message text NOT NULL,
    attachment_url character varying(500),
    created_at timestamp without time zone,
    is_internal boolean DEFAULT false
);


ALTER TABLE public.queries OWNER TO postgres;

--
-- Name: queries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.queries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.queries_id_seq OWNER TO postgres;

--
-- Name: queries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.queries_id_seq OWNED BY public.queries.id;


--
-- Name: request_audit_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.request_audit_log (
    id integer NOT NULL,
    service_request_id character varying(36) NOT NULL,
    user_id character varying(36),
    action character varying(100) NOT NULL,
    old_value jsonb,
    new_value jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.request_audit_log OWNER TO postgres;

--
-- Name: request_audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.request_audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.request_audit_log_id_seq OWNER TO postgres;

--
-- Name: request_audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.request_audit_log_id_seq OWNED BY public.request_audit_log.id;


--
-- Name: request_audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.request_audit_logs (
    id integer NOT NULL,
    service_request_id character varying(36) NOT NULL,
    modified_by_id character varying(36),
    field_name character varying(100) NOT NULL,
    old_value text,
    new_value text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.request_audit_logs OWNER TO postgres;

--
-- Name: request_audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.request_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.request_audit_logs_id_seq OWNER TO postgres;

--
-- Name: request_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.request_audit_logs_id_seq OWNED BY public.request_audit_logs.id;


--
-- Name: request_state_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.request_state_history (
    id integer NOT NULL,
    service_request_id character varying(36) NOT NULL,
    from_state character varying(50),
    to_state character varying(50) NOT NULL,
    changed_by_id character varying(36),
    changed_at timestamp without time zone,
    duration_in_previous_state integer,
    notes text
);


ALTER TABLE public.request_state_history OWNER TO postgres;

--
-- Name: request_state_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.request_state_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.request_state_history_id_seq OWNER TO postgres;

--
-- Name: request_state_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.request_state_history_id_seq OWNED BY public.request_state_history.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(200),
    permissions json,
    created_at timestamp without time zone
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: scheduled_emails; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scheduled_emails (
    id integer NOT NULL,
    company_id character varying(36) NOT NULL,
    recipient_type character varying(20) NOT NULL,
    recipient_email character varying(255),
    recipient_user_id character varying(36),
    recipient_filter json,
    subject character varying(500) NOT NULL,
    body_html text NOT NULL,
    template_id integer,
    template_context json,
    scheduled_at timestamp without time zone NOT NULL,
    timezone character varying(50),
    status character varying(20),
    sent_at timestamp without time zone,
    error_message text,
    recipients_count integer,
    sent_count integer,
    failed_count integer,
    created_by character varying(36),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.scheduled_emails OWNER TO postgres;

--
-- Name: scheduled_emails_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scheduled_emails_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.scheduled_emails_id_seq OWNER TO postgres;

--
-- Name: scheduled_emails_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scheduled_emails_id_seq OWNED BY public.scheduled_emails.id;


--
-- Name: service_renewals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_renewals (
    id integer NOT NULL,
    user_id character varying(36) NOT NULL,
    service_id integer NOT NULL,
    company_id character varying(36) NOT NULL,
    last_completed_at timestamp without time zone,
    last_request_id character varying(36),
    next_due_date date NOT NULL,
    reminders_sent jsonb DEFAULT '[]'::jsonb,
    last_reminder_at timestamp without time zone,
    status character varying(20) DEFAULT 'pending'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.service_renewals OWNER TO postgres;

--
-- Name: service_renewals_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_renewals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.service_renewals_id_seq OWNER TO postgres;

--
-- Name: service_renewals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_renewals_id_seq OWNED BY public.service_renewals.id;


--
-- Name: service_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_requests (
    id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    service_id integer NOT NULL,
    assigned_accountant_id character varying(36),
    status character varying(50),
    internal_notes text,
    invoice_raised boolean,
    invoice_paid boolean,
    invoice_amount numeric(10,2),
    payment_link character varying(500),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    completed_at timestamp without time zone,
    xero_reference_job_id character varying(100),
    internal_reference character varying(100),
    request_number character varying(20),
    description text,
    actual_cost numeric(10,2),
    cost_notes text,
    labor_hours numeric(6,2) DEFAULT 0,
    labor_rate numeric(10,2),
    deadline_date date,
    priority character varying(20) DEFAULT 'normal'::character varying,
    current_step_id character varying(36)
);


ALTER TABLE public.service_requests OWNER TO postgres;

--
-- Name: service_workflows; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_workflows (
    id character varying(36) NOT NULL,
    company_id character varying(36),
    name character varying(100) NOT NULL,
    description text,
    is_default boolean DEFAULT false,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by_id character varying(36)
);


ALTER TABLE public.service_workflows OWNER TO postgres;

--
-- Name: services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.services (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    category character varying(100),
    base_price numeric(10,2),
    is_active boolean,
    is_default boolean,
    form_id integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    cost_percentage numeric(5,2) DEFAULT 0,
    cost_category character varying(50),
    workflow_id character varying(36),
    is_recurring boolean DEFAULT false,
    renewal_period_months integer DEFAULT 12,
    renewal_reminder_days jsonb DEFAULT '[30, 14, 7]'::jsonb,
    renewal_due_month integer,
    renewal_due_day integer
);


ALTER TABLE public.services OWNER TO postgres;

--
-- Name: services_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.services_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.services_id_seq OWNER TO postgres;

--
-- Name: services_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.services_id_seq OWNED BY public.services.id;


--
-- Name: system_email_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_email_config (
    id integer NOT NULL,
    provider public.email_provider_type DEFAULT 'GMAIL'::public.email_provider_type,
    is_enabled boolean DEFAULT false,
    smtp_host character varying(255),
    smtp_port integer DEFAULT 587,
    smtp_username character varying(255),
    smtp_password character varying(500),
    smtp_use_tls boolean DEFAULT true,
    smtp_use_ssl boolean DEFAULT false,
    sender_email character varying(255),
    sender_name character varying(255) DEFAULT 'Accountant CRM'::character varying,
    use_as_fallback boolean DEFAULT true,
    last_test_at timestamp without time zone,
    last_test_success boolean,
    last_error text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.system_email_config OWNER TO postgres;

--
-- Name: TABLE system_email_config; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.system_email_config IS 'System-level SMTP configuration managed by super admin';


--
-- Name: system_email_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_email_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_email_config_id_seq OWNER TO postgres;

--
-- Name: system_email_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_email_config_id_seq OWNED BY public.system_email_config.id;


--
-- Name: tax_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tax_types (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    default_rate numeric(5,2) DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.tax_types OWNER TO postgres;

--
-- Name: tax_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tax_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tax_types_id_seq OWNER TO postgres;

--
-- Name: tax_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tax_types_id_seq OWNED BY public.tax_types.id;


--
-- Name: user_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_tags (
    user_id character varying(36) NOT NULL,
    tag_id integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.user_tags OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id character varying(36) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(128) NOT NULL,
    role_id integer NOT NULL,
    first_name character varying(50),
    last_name character varying(50),
    phone character varying(20),
    personal_email character varying(120),
    address text,
    company_name character varying(100),
    visa_status character varying(50),
    tfn character varying(20),
    date_of_birth date,
    occupation character varying(100),
    bsb character varying(10),
    bank_account_number character varying(20),
    bank_account_holder_name character varying(100),
    id_document_url character varying(500),
    passport_url character varying(500),
    bank_statement_url character varying(500),
    driving_licence_url character varying(500),
    terms_accepted boolean,
    terms_accepted_at timestamp without time zone,
    is_active boolean,
    is_verified boolean,
    is_first_login boolean,
    two_fa_enabled boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    last_login timestamp without time zone,
    company_id character varying(36),
    invited_by_id character varying(36),
    is_external_accountant boolean DEFAULT false
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: workflow_automations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_automations (
    id character varying(36) NOT NULL,
    workflow_id character varying(36) NOT NULL,
    step_id character varying(36),
    trigger character varying(20) NOT NULL,
    action_type character varying(50) NOT NULL,
    action_config jsonb,
    conditions jsonb,
    delay_minutes integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.workflow_automations OWNER TO postgres;

--
-- Name: workflow_steps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_steps (
    id character varying(36) NOT NULL,
    workflow_id character varying(36) NOT NULL,
    name character varying(50) NOT NULL,
    display_name character varying(100),
    description text,
    color character varying(20) DEFAULT 'blue'::character varying,
    icon character varying(50),
    step_type public.step_type DEFAULT 'NORMAL'::public.step_type NOT NULL,
    "order" integer DEFAULT 0,
    allowed_roles jsonb,
    required_fields jsonb,
    auto_assign boolean DEFAULT false,
    notify_roles jsonb,
    notify_client boolean DEFAULT false,
    position_x double precision DEFAULT 0,
    position_y double precision DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.workflow_steps OWNER TO postgres;

--
-- Name: workflow_transitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_transitions (
    id character varying(36) NOT NULL,
    workflow_id character varying(36) NOT NULL,
    from_step_id character varying(36) NOT NULL,
    to_step_id character varying(36) NOT NULL,
    name character varying(100),
    description text,
    requires_invoice_raised boolean DEFAULT false,
    requires_invoice_paid boolean DEFAULT false,
    requires_assignment boolean DEFAULT false,
    allowed_roles jsonb,
    send_notification boolean DEFAULT true,
    notification_template text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.workflow_transitions OWNER TO postgres;

--
-- Name: assignment_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assignment_history ALTER COLUMN id SET DEFAULT nextval('public.assignment_history_id_seq'::regclass);


--
-- Name: client_notes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_notes ALTER COLUMN id SET DEFAULT nextval('public.client_notes_id_seq'::regclass);


--
-- Name: client_tags id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_tags ALTER COLUMN id SET DEFAULT nextval('public.client_tags_id_seq'::regclass);


--
-- Name: company_service_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_service_settings ALTER COLUMN id SET DEFAULT nextval('public.company_service_settings_id_seq'::regclass);


--
-- Name: currencies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.currencies ALTER COLUMN id SET DEFAULT nextval('public.currencies_id_seq'::regclass);


--
-- Name: email_automation_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_automation_logs ALTER COLUMN id SET DEFAULT nextval('public.email_automation_logs_id_seq'::regclass);


--
-- Name: email_automations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_automations ALTER COLUMN id SET DEFAULT nextval('public.email_automations_id_seq'::regclass);


--
-- Name: email_templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_templates ALTER COLUMN id SET DEFAULT nextval('public.email_templates_id_seq'::regclass);


--
-- Name: form_questions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_questions ALTER COLUMN id SET DEFAULT nextval('public.form_questions_id_seq'::regclass);


--
-- Name: form_responses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_responses ALTER COLUMN id SET DEFAULT nextval('public.form_responses_id_seq'::regclass);


--
-- Name: forms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms ALTER COLUMN id SET DEFAULT nextval('public.forms_id_seq'::regclass);


--
-- Name: import_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_logs ALTER COLUMN id SET DEFAULT nextval('public.import_logs_id_seq'::regclass);


--
-- Name: invoice_line_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_line_items ALTER COLUMN id SET DEFAULT nextval('public.invoice_line_items_id_seq'::regclass);


--
-- Name: invoice_payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_payments ALTER COLUMN id SET DEFAULT nextval('public.invoice_payments_id_seq'::regclass);


--
-- Name: job_notes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_notes ALTER COLUMN id SET DEFAULT nextval('public.job_notes_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: otps id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otps ALTER COLUMN id SET DEFAULT nextval('public.otps_id_seq'::regclass);


--
-- Name: queries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries ALTER COLUMN id SET DEFAULT nextval('public.queries_id_seq'::regclass);


--
-- Name: request_audit_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_audit_log ALTER COLUMN id SET DEFAULT nextval('public.request_audit_log_id_seq'::regclass);


--
-- Name: request_audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_audit_logs ALTER COLUMN id SET DEFAULT nextval('public.request_audit_logs_id_seq'::regclass);


--
-- Name: request_state_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_state_history ALTER COLUMN id SET DEFAULT nextval('public.request_state_history_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: scheduled_emails id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scheduled_emails ALTER COLUMN id SET DEFAULT nextval('public.scheduled_emails_id_seq'::regclass);


--
-- Name: service_renewals id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_renewals ALTER COLUMN id SET DEFAULT nextval('public.service_renewals_id_seq'::regclass);


--
-- Name: services id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services ALTER COLUMN id SET DEFAULT nextval('public.services_id_seq'::regclass);


--
-- Name: system_email_config id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_email_config ALTER COLUMN id SET DEFAULT nextval('public.system_email_config_id_seq'::regclass);


--
-- Name: tax_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tax_types ALTER COLUMN id SET DEFAULT nextval('public.tax_types_id_seq'::regclass);


--
-- Data for Name: access_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.access_logs (id, user_id, access_type, ip_address, ip_type, country, country_code, region, region_code, city, postal_code, latitude, longitude, timezone, isp, organization, as_number, user_agent, browser, browser_version, operating_system, os_version, device_type, device_brand, device_model, session_id, is_successful, failure_reason, is_vpn, is_proxy, is_tor, is_suspicious, threat_level, company_id, created_at) FROM stdin;
\.


--
-- Data for Name: activity_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.activity_logs (id, entity_type, entity_id, action, details, performed_by_id, company_id, ip_address, user_agent, created_at) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
\.


--
-- Data for Name: assignment_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.assignment_history (id, service_request_id, from_user_id, to_user_id, assigned_by_id, assignment_type, reason, created_at) FROM stdin;
\.


--
-- Data for Name: client_notes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_notes (id, user_id, created_by_id, content, is_pinned, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: client_tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_tags (id, name, color, company_id, created_at) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.companies (id, name, trading_name, abn, acn, email, phone, website, address_line1, address_line2, city, state, postcode, country, owner_id, plan_type, max_users, max_clients, is_active, logo_url, primary_color, created_at, updated_at, invoice_prefix, invoice_footer, invoice_notes, invoice_bank_details, invoice_payment_terms, invoice_email_subject, invoice_email_body, secondary_color, tertiary_color, company_type, currency, currency_symbol, tax_type, tax_label, default_tax_rate, logo_data, logo_mime_type, logo_storage_type, logo_blob_name, theme_primary_color, theme_secondary_color, sidebar_bg_color, sidebar_text_color, sidebar_hover_bg_color, invoice_show_logo, invoice_show_company_details, invoice_show_client_details, invoice_show_bank_details, invoice_show_payment_terms, invoice_show_notes, invoice_show_footer, invoice_show_tax) FROM stdin;
e42c76c5-c662-4160-ae8e-3268f82047a0	Demo Accounting Practice	Demo Tax Services	12 345 678 901	\N	info@demopractice.com	+61 2 1234 5678	\N	123 Main Street	\N	Sydney	NSW	2000	Australia	ec86adcd-8297-4717-b1db-a4b5bc333993	standard	10	100	t	\N	#4F46E5	2026-01-18 05:05:41.549654	2026-01-18 05:05:41.747318	INV	\N	\N	\N	Due within 14 days	Invoice from {company_name}	\N	#10B981	#6366F1	tax_agent	AUD	$	GST	GST	10.00	\N	\N	\N	\N	\N	\N	#0f172a	#ffffff	#334155	t	t	t	t	t	t	t	t
d50d352c-396f-46c5-a336-9b29a89c441b	Aussupersource												Australia	25775935-d117-491b-8ca5-e1f0cbc5ff4b	enterprise	10	100	t	\N	#4F46E5	2026-01-20 04:18:43.095147	2026-01-20 09:42:42.105626	INV	\N	\N	\N	Due within 14 days	Invoice from {company_name}	\N	#10B981	#6366F1	auditor	AED	د.إ	VAT	VAT	20.00	\N	\N	\N	\N	\N	\N	#0f172a	#ffffff	#334155	t	t	t	t	t	t	t	t
92581d3e-52da-454c-93b7-780bd511825a	Pointers Solution	Pointers 			info@pointeraccounting.com.au	+61400000000							Australia	becf0567-7a4d-4c8f-9c8c-408205ef5015	professional	5000	1000	t	/api/companies/92581d3e-52da-454c-93b7-780bd511825a/logo/image	#10B981	2026-01-18 08:26:57.218786	2026-01-26 09:15:52.887284	INV				Due within 14 days	Invoice from {company_name}		#10B981	#10B981	tax_agent	AUD	$	GST	GST	10.00	\\x89504e470d0a1a0a0000000d4948445200000460000001810806000000292ec7290000000970485973000017110000171101ca26f33f0000200049444154789cecdd418824599ee7f79f0da5d5d08388cc56cf8c6e119d0d3a0841462b1b844028bd9095b18c0e192dc83ae8925e425409fc50d17bc9baa5d745645d5451b0b69079294fb4a72ad88a3cac105e06ed21a445b09dea08ed4597aef6d0c04a3b237566ec6ecf080d83e9f09e657a45ba9b99bbdbb367cffcfb01a7bad33ddc9ebb9b3d33fbbffffbbf28cf73010000000000c09d3ff0dd00000000000080be2300030000000000e0180118000000000000c708c0000000000000384600060000000000c03102300000000000008e1180010000000000708c000c0000000000806304600000000000001c2300030000000000e0180118000000000000c708c0000000000000384600060000000000c03102300000000000008e1180010000000000708c000c0000000000806304600000000000001c2300030000000000e0180118000000000000c708c0000000000000384600060000000000c03102300000000000008e1180010000000000708c000c0000000000806304600000000000001c2300030000000000e0180118000000000000c708c0000000000000384600060000000000c0310230003a298aa243df6d0000000080a6108001d03951140d259df86e07000000003485000c804e89a2682ce94bdfed00000000802645799efb6e03004892a2289a487a50fcff3ccf237fad0100000080e6900103a013ae075f00000000a04f08c000f08ee00b00000080be230003c02b822f000000007601011800de107c01000000b02b08c000f0a24ef0258aa21bedb40600000000dc7ac7770300ec161b549948ba57e3e58792662edb03000000603b491a1f4a2a064f071bbcc5b9a457925e4d47d97953edea1a96a106d01a1b7c9949ba5df34fdecdf37ce6ac41000000006a4bd2782033487a60ff7b2869cfc1a6ae64823273fb98493a9f8eb2570eb6d51a02308067b6135b74601f8b66d7feff7c3acae64e1ae4c806c11789000c000000e04592c63764b2598ac73ad7f1ae5cca0466669266a165cb34128089a2e850d2c9f6cd09d66ce17fcfed43dc38429292343e9009a80c64d2f28a88f17e036f5f44865fe94d84f8bc6b1dd186c117c95300a6e37dda799ee7c7be1bb14ac7bfbbc2499ee7a7be1bb18d288a66bedb705d9ee783b6b615c87e8606b5b97fd9347af6af6e994c47d9c4772316b19fbc36b78fc2acf8f7d0060b61d87b9723fbb8ebb735b55cc9ec77a7924ebb9e21d3540d981b0ae3c77165e9678fa2a8f89f67fafe0df29ce04c7fd98c96814ca06520372979853dbdd9ff5ed75449d25832fb5d111d3ef77512dc22f8e2d3aef769db08e1bb3b88a26896e779a74fd015bafe1dbb16c27e8670b17f75cfcc770396603f31ae7f078f8aff61af472f65070865ee8766eac13492beb1992e47928e15d635bb64ee87eed9c797491a5fc8d49b3ced62109022bced78eb06d906672eb470839ce779a7b21650cf429478a07a8565db72d73e3e9624db19cd6452f55a19fd6f20f872d058638037f6652e30c69edb010040dfeddb47713ff4489292342eb2b8672228e38dcde43a56c5caa481b92de973499f27697ca637c1984eec5f0460fcba6d1f0f24298aa2227d6a26e934cff3b9af86a19cedac8632819726a612b5a1d8df3eb627bd224dcf4930a6a1cc9783461a03bced388aa293c0b3600000085591c57d576f8232ad0f16ee2a9bb13f56ffb3b88a7dec2449e3534963df59310460ba65317deaf3288a2e656e922764c7f86753f386f6115a6ade757b3281bf070bc19893a66ac7d8fa0c1385ff3da1bff644160c00005db238582849cf65ae5167be6f9afb6287022fd72ddefb9cc90462663e1a4200a6dbf665a68f7cbc108c392133a65db6a31aaa5fa9798b163ba44b994e79e3343d1b7c99c96ded1ba00964c10000d05dc5c0b492342e82319d994a12125b3261a2dd0bbc2c7357d22f7d0562fea0cd8d612b4530e6b75114cda2281a7a6e4fef25693c4cd27826e997ea6ff0e5ba7d495f4a9a27693cb69d756d045f10983db18205000021b8a737d7a827eb5ea3eeaa248d6f24693c96f45b117cb9ae08c4ccec807b2bc88009d35d4977a3281acb443219c16d5092c643992c1057b55dae57832f56c85af4ba1099ad377363e1b962296bc914fe959aef50f764e6e33e4ad2f8996acc9724f882403d88a2684c6621000041d8939d2150f71a7557d9a0c244e1d4abf465312366e87a7f220013b67d999be4637b03c148ee161c055e8a95aece65822ab375df60455d96b70a93d9918043bd59fefa50cd04438ae9495fc89ce4de0af6390cbe1c56bf04d8da58669a2100000847718d4a206681ad5b39965d0915b5dd95f4db248d3f95a98de924c121caf37cfb3789a281cc340df87529e938cf73aa86afa1e1625445ad9e994cc130af9949367b6620b35a53139fef4aa6431a17ff60573b9acb4de6cb599ee70307ef5baae37d9a97efa4ae8e7f77657e1c52164c1445db9fbc1b96e779d4d6b602decfb0a136f72f7b5dc0fed52d9f2e5e7b7401fb49e7bc758dba8becb5ff442c84b1ad4b996c9859d36f4c064cbfec4bfa268aa2e7328198b9e7f6749a8d0e9f68fbfa2e177ab3befc7ccbf76a94cd9e3997597aed864c20e648b6a0d906f664a6250df5a6536a2ad306f0e944e6d8000000e159768dba53ec673f11d7e54dd8979996b47206c0a608c0f4d33d4983288a8664c32c97a471b1fceca61dd4eb55a9ba167459c5761c1349938560cc509b65c6149dd2f3fdfd83fffdf272de5433afbb6147ba1b97e7f9ccc5fb2258f7a2281ab05f000010b4e21ab57359532e25697c22a61cb9f0b1a44192c6c3156521d64600a6bff664b2619ec964c350a4578d2cc176261374093ab0752d187320e9582618b36e40eadebf7fe7dffbcf1c06606ecb4d7aef33996962c0a2b1de14b6060000e17a64a7891df92e09e05a92c613edce8aad3edc96f4eb248d3f988eb2c9b66fc632d4fdf740d22c8aa203cfedf0cea6e59d6bb3e0cb33493f9d8eb241e8c197eba6a36c3e1d65c7920e24fd4226bba7b67ffc8ffefbd002b9cff23c1ffa6e043ae9aeab8c2b0000d0babb32cb56f7725107bbc4f4b908beb4e5cb248d8b99041b2300b31b6e4b3ab72bd5ec1cdb394d247da9f5333c9e49faf17494359676d655d351f66a3aca4ea6a3ec40d207aa1188f993ab7fcb79bb1a7646f00515c6be1b0000001ab3276996a471afeabcd920c04c14db6ddb0399fd69e3200c0198ddb127930933f4dd9036d988f74ceb47869feb4de065de74bbba6e3aca263610f3a94c55f9a5f2bffc375a6b53032e44915554bbbb6bfd2400003db727e91b9b0ddf17a722f8e2cb6d49e79b66561180d92d7b92bedc959b0bdbc9ceb45ee77421e9dde9283bdac5c0cb75b678d981a42f963dffd7ffcfdfb4d99c6d5c481a500b09358d7d3700000034eecb3e04616c66ffa6f52cd18c7d6d980943006637f53e0893a4f158eb4d39ba92f48be9283bdcc565ebcad8a949c7927e2a13c878ed7ffd1f83989545f005ebdaef7b1f0900c08efad216e70d92bdc7a1e64b379c6c52e09900cceefab2af35616c54f8d11a7f7226e9703aca4edcb4a81fa6a3ec7c3aca0e650af55efde8f73f90c3d58f9a7229822fd8ccd8770300008013a72116e6b5756cd6b9c7813bcf365de69c00cc6e9bf52908b34125f022eb65c074a3fa6ca06a10fd9f7ff8cf7db7a5c295a423822fd8d07e1445c7be1b0100001ab7271384d96a359b3625697c2069e2b919302e246d7c8d18daf2b168d69ea4d3288a0e43bf49dda012f885a4deaf6ce4ca74949d4751f44f25ddf3dd9615ae64325ff87db18d71144593d0fb470000f0967d9942b603cfeda8eb54ebafe68ae65d491a6c32f5a840060cf61578347583e0cb339903879bf3ed74357b8ae00b9ab2a72d4638000040a7dd4dd2b8f3e7795bf785158ffcdb3af822118081712fd454fb0d822f1fd8a5a519d1de4214450732c1bbae21f882a61d4751144c8a32000058cbd84eefe924db36eabe74c3711303f804605018db9bea60ac197cb992595e7ae2b24d3b64e0bb012b1c137c41c3c8820100a0bff6d4edd90013df0d8024e98ba6ee2309c0a0b0a78056fd5833f87229932e3673d9a61d33f0dd80253ec8f37ce2bb11e8a547a105a80100406d77bbb834b55df5e8aeef7640cfa7a3acb1c138023058f4208aa281ef46d474a27ac1970b9925a6c98a68d6c07703ae21f802d7c6be1b0000009c19fb6ec01227be1b00b3704b936f480006d78d7d37a04a92c613d55b6afa420d144ac2f7d97a185daaff42f0056d7840160c0000bdd5a92c98248d87ead6f5f62eba9274d4f4bd24cb50e3babb7659ea4e668cd8ce28f8e04b92c687920e6456123ab00fa93ccdf04252f17966f67f9f7b985a3568797b653e25f882168dd5f028080000e88c63996bec2e18fa6e0034988eb279d36f4a0006cb1cab8307bd0d5a7c59e3a59d0bbed8b61fc9042f369dcbb938e5eaf57b24692c99cf7c2ee954d2ccf1671f387cef753ccbf37cecbb11d8290fa2289ae4793ef3dd100000d0b87b491a1fb8b8e95e87bd6fa0f68b5f1fb82a61410006cb3c88a2e838cff32e05308aa2bb553a137cb185b38ac79ee3cdddb68f0776db173255d34f1d9c44060dbfdf269ee5793ef4dd08eca4b1ba710c000080e61dc97fed953eaebe78b6e4df0ee5fe1e69138dad78b4cc2e0460cef23c1f34f146b6f6c5e1c23f0d2415ffd6d51d685343f9ef7c169daafafbbd9234f4197c49d2f8406f32887cee0fb7257d2ee9f3248d9f4b9a4c47d96983efed13c117f874378aa201593000800e3b9b8eb241936f68af710fecff3db8f6e853b6c650feef818e3c6f7f1bcf65b2f26792e6750682ed40fb62598681fced538dae78b4cc2e04601a633342660bffb4f8bf650b342e4e3509b970d250fe3b1f495292c663551f845732992f5e6ad7d8a25dc792eef9d87e857b3229959732a3f7a79b06a93ab04ad673822fe880b1c882f1ed95968fa675d181ba7b3db0585b0c61b892b9b9d93573df0dd875f6467abeea793b6de650e6fcd846f6b72bb77d4e43b219f4a17d7767924e361decb5f725b3ebff6eefaf0632fb531b03c08daf78b40c019806e5793e97e9984e25298aa243999bf2100fa4db51141dd8cfe48dedcc1fd578e9b18fe08bed18c60a23f2bf2f5343e72449e3f174946d12601b34dba4b5b4d22902359005e3992d143ff0dd8e3aa2281aabde79cc8763f6e3e09c379dd90034c15e879fcb4c815f9c8a5f67f18caef1390d69e069bb9b3893c37b30bbd0c84cd2d866601dc9dc0bb808c63859f1681996a17628cff3733b5a7f20e953991f3624039f1bb7e9687522a94ee7e92d93a4f1815d0efb970a23f8b2684f666ad2dc9e1cd73170d09e2a97929e491a74a92e1176dec477030000e8aae9283b9d8eb2a1a41fcb5cc78564e071db214c3fba922952dbdaec83e9289b4f47d9c974941dcaec535fa8d97b6b272b1e2d43064c0bec4de3388aa213996c898ffdb6a8b623f9bdc9385675daf699eb797ad7d92951c76a36aba948037fa5e5a9c58bf5879a0af8ec4bfa2649e33399da39f31a7fe33cd8b4bf7fa0ffe03f39d40ffef4effcbf7ff57ffd7fffe13ffaefbef9df5c6f13d8c07e1445439641070060357b7d394cd2f844e6bec2772dc13a063e366a079fbb3a65b5e0b5ec83f47a9f3ab6f76443d5bb672ce36cc5a36508c0b4c806628ea3289ac974405d9f9634f0b5e19a538faed46294d8b669a2ed4f1c1732e974e732a9c46b1ff00bc5aa060bffdd747fba2be9bc6a5a521445cebeebf8cfded39ffcbb3714fdf1dfe82ff6fe95feb5fe95feb5f4873ad07fa97e5682473f8c45260c000095ecf5eea1cd20effab4a4bd248d0f3d0419062d6f6f13439fc1974576bad0894c7985a1cc75d9ba8198676dcfa42000e3419ee7a7b698e94cdd0ec2ec79ac035367de656b2b1e25697c2c73506ffa7b3d97994eb57101dc450bc5aa66c5bfd97a34c57cdb753b9f625ad29196cc7fb4f58c261b37f86d973ffad11fff93bffb5fdffd8ffee58ffee5c15fbff3b7fa4bfd6ed9eb3e4ed2f8d4ce0105ba862c180000d6301d65c3248da5ee07610ed57ec1ebc3ea9778f5bcc155551b6583289335efd9ceec34b9565103c6135b4070e8bb1d35b4de11d80866d554972fdae8009234be6123f59f6bfde0cba5a45f48ba391d6547d351367119309a8eb2d974941d4f47d981a477b5d97cdbbb92e636db47d2ebe0cb4cdb050baf6482501f48fa719ee7077ff9977ff15ffc8b7fe7e5cffffa9dbfadfadb4eacc605ac701245d10ddf8d00002020c73219e15d76e0619b5d0fc0743e2bdd66f31fc8d4882973214ff57608c07894e7f9a9aa770edf5aed08ecd49aaa1bee6239e536da32d3fa11fa3349ef4e47d9812d16d57ae1581b8c196ab322557b927e9da4f170cbe0cb994cf1e99fe6797e23cff3a33ccf278b19553685f1d38af7b96d83724017ed29800b120000bac25e1b0f7db7a3c2c0c336bb3ca073e16b69ee754d47d92b5b23f4a732f723d75da9c59914d71180f16f2c1350e8aab623b1758adb1ebb3e606c06c85cebd57bb99009bc0cba3265c6560c3f56bd48f0f7fce8f73ff8f2873ffce1ffa2fac1974bbb8d9f4bba99e7f920cff3b1cdf62a6be358d5c7c0890d88015d744c160c0000f5d941b82eaf8ee4e3bcdee50c9899ef06ac6b3acacea7a36c203323617130fac8671d1b02309e152b24f96e478983b63664d777af1a49763ef7d0065f66aa1f782896623bec4ae0e5ba8548f08fb53c12fc3d3ffafd0ff44ffec13fd3ef7ef7bb7fb3e2a5675a985694e7f9719ee7a71b2c173dac789e2c037419fb270000eb9bf86e40091fab3575b936a8976c9126d8694987b2f72dbeefd708c074c3a99a5dc7bc496d763e6395773c57727c93b341f0e5b9a483b6ab676fca66c40cf47624f8b522f8727939af7abb6736cb65b26da166db11568d821c9305830e230b06008035d8ebbf2ecf04404f14f7405db8672300d301365ba09315a5db62b35faa6aad9cb89c7bb866f0a5c87a796bc5a0102c4482bf57006dcde0cbb0e1668d551e8824cb005db6270a460300b0aecede03d9154681461180e98e99ef06ac620bb1ba5675637d258737376b065f2e24752282ba0d1b093e94ad0de339f8221b5cabfa8dc98241973d88a2e8c0772300000888b75a1c58cb81ef06f4050198ee98f96e4009a737bcf6867a58f1b2b1ab4c13bbfd896aae172f137ce9cdc9623aca8efff49ffff0519de0cbfbffd57faef7fefe7f3a73d89c135567c10c1d6e1fd8d6d87703000008486faea97b6ee0bb017d4100a623b6ada111b8aa958f2eed9419574e55afd6cd333b7730b8294765a2283afc87ffcdd77faf4ef0e5e5e19564562472921565bfdbca2c1817db061a42160c000035f56950b3e7f693343ef2dd883e2000d32d95abd3f4d4b0e27997538fc692eed678e9b3e9281bba6a872f767ad94c15d93f0bc117d9d79e3a9c0a549505b39fa4f1d0d1b6d10f17d52f716ae279fb0000607b4c7bffbe134a016c8f000cea18b87a631b49dd2f79c9951cddccd8c25a8f6abc94e0cbe15bf1907d39fa5d6a66c10c5d6c1bbd7124bf2bcbdd8da268e071fb0000607b6dd4c10cc9be5870606b0460e0dbb0e2f91317537e16eabe5421f8f276f0a570cf6126caa4e2f9bb76e52c609903f95f5561ec79fb000084c2e7a04997f8cee0ade34192c613df8d081901986e99f96e409bec0df4bd8a974d1c6d7eacf2cc1bc97482bdab375237f812ffd97bff7349f0a5e02415d1ae88f4ace265c3a6b78bdeb821ff0110b2600000a8a7ce4218bb20943a930f92343e673074330460ba65d7e6d45515727a666fc41b65a71e7d5cf1b22b99d58e42e9086ba91b7c91f4ecdb7f3cfd8f551d04d993bb2059d5fb0e1d6d17e13bb485cd7dd7d5224d17008070b55d2078def2f6b6715bd27992c6bd1bac768d004cb7ecda3cc361c5f3aea610d4b9293adae1e0cb459ee74349b2d3afaad221efd9a056a3a6a36c26e9b2e425fbae5663426f4c3c6fff76144543cf6d0000009b69fb5e60def2f6b6b527e9f3248de72eee05faea1ddf0d40105cd4603950f9d2cf97d351d67800c6d62ca95a72fa537bf3df0a3b85e750a6d8f1817d2c3393e99867eb6606ad137cd1db45978f644600cafe76a2d5eddec689a4cf4b9e1faa87d3c4b0b58124e5793e89a268aceae9862e8de53f10040040273198f63d33d55b20a46bf625fd3249e34b99eb9ed3be0d643789000cea70917e5735fdc845f0a54e5d888be928ab7a4d536d39920920d459065b8bafb31ddca9a4c9749495fe3eeb065ff23cff5e87391d6573bb5c775920643f49e3e174944d2ab6b1aed38aed1e89000cca4de4f762663f8aa2619ee7138f6d0000a0ab0e7c37a043da9ef2d4b47d495fcad4883c95594c25f4cfd438a620754bdd1bf13ea80ac04c1c6c73a8ea9170a737f3491a1fd8cae173990e6ad3df7c5fa68ecdaf93349ead4afbdb36f852988eb21355d7d318573cbf369be95336058a69485866f1b8ea421d96b1ef060000d05103df0d28d16a1687cd1a299b7e1f8a3d490f64ee53ce93343e76b16847a808c07444144507bedbd0167b0096051e2e1d454bab822bcf5c4d3d4ad2f886cd22f9ad4c87d464b5f7bb32697fb3c5604453c19705e38ae7f71d2d4b3da9787ee0609be809bb5f571593766ddf4e85020000df37f0dd80553c656fcc3c6cd3a5db32d9ec2f93349e502b86004c977479147fdef0fb0d2a9e7755fba52afb65dcf476edb60f65520a5d4f83b82b13691e3b08be144571ab6e645d641055ed0f55d954d841f6182874210be6388a22467f0000b06ad484dc45ae1621e982073283c6f35dce8a2100d31d03df0d58c52ee7daa441c5f3b386b7275507063e75b4e4f550d2afd56211d01ffdfe078ffee44ffef49faac1e0cb8271c5f3b79b9e12647f97b274cc5d9aba87fa5e9fd4f33c3f97ff25a9f744bd2200001675f9bce8e5bac12e4272e563db2ddad79bac98d3248d776a309522bcddd1d51dcf450730287bb2e9d58f6c40a02abadef808b9adf5f2a0e9f72df3a3dfff40ffe41ffc33fdc55ffc8baa637b93e04b5190f799ca3fd7b1aa97185fd7a94ccd9ba592341eb4b97215825064811526f21fac3b8ea2e864dde30e00161cd829cd7d32713108866eb3d90f43dfed28e1f35c7daa96ef213cba27e99e5d6064a21de80f08c07440144503f95d26b58c8bb98f65c11017d1e661c5f3cf9a5e2a6dcbe0cb85deeef42b6f1c8be0cbe5e5bccefbaf1d7c593056f96773114c9ca92400a3b76fb681efa5b5766449ea3d99e3a78911bf33f90f280168dfbec25ca6b6cc4ccd4f7747f78dd56c4dc4a6f95cbd67a2dd09c0148abeed5192c66732df412f97b3660a52370c7d37a0c4bcc937ab517869d6e4f6acaa8040a3d92f76646a9d4ef34ad21792de9d8eb2683aca0ea7a36c70ed1149faa9a45f68c9aa402d065f8a29416581b23d07c5786715cf0f1ade1ec277b0e4df262db761998f77a9e83a0000d7d9ecf4b281b52e98f9dab0cdeaeec36a489bba2bb35aecdc16eeed72add4b59101e399bd10ef728473def0fb551d40b32637660fd8b211ef8b262b9cdb398c7547a62e258da7a36c52e7c5b69de7924e6c206b2ce96e9bc1970513958fbe0fd4e0cdee7494bd4ad2f842abb3a77ad531a311074bfeed44dd18391eabdb817700009cb0538f422834eb33034632d70a5f7a6e836fc572d60fec14a51399ac98b9d7566d890c18ffbab03a479959c3ef5775a3dc746737ac787ed2d486ec09a5eefb7d21e9b06ef0e5bae9289b4d47d9e04ffffcdffe7bffd3dfbfc8ab822ff19fbda7fbffeddffd1f1aac3d515520ccc534a4b27da3ab53f8e0cfc1f57fe8c892d492f4802c1800c0aeb1d7ca3375ffbaedd2f7d4177b8fb0cb5930d715857b7f6b0bf70e3db7676304603c8aa2e848a6f05097351d10392879ce456737a878bec908fc44d57359af247d301d65c7db7ed6288a0effe1675f3dfaf33fff3fa2b2d7c57ff69e7e90447af577fee6a15dee6f6bb6ed65dfdd5e8de966eb2add171d6c0f615b7571376eb31125c65bfe7defe6440300fa6b21f812c2b2d35dc9d0e9f22a513edd93f46592c6af92343e096d8a1201184fa2283a5437ea1194b970b05a47d9b49579931bb21d7d59277fd1540a9bbdf9af0aa65d491a6c9af5b2c8ee3f3355047c8ae0cb5fbff3b7c53f6dbded05b38ae7070d6e4baa0e061e34bc3d042e8aa21bd7ff2dcff3b9fc2f492d992c98c1167fef3b351a00805aec75f2b9c208be481d59d8c1ae0cdb856b96aeda93a925f4eb248dcf93343eb6f77f9d4600c6037b533051b72b7f4bcdd763a93a201add9eaaa73b3519dd1ed778cd5113f566b608be48d2dd063345aabebfa6b65320008375adea03c66d36a2c4d877030000702549e31b491a9f48faa5ba3fed68d1cc7703160c7d372010b765a628bdb4857b5d94436804019896d9e0cb4c614480670dbf5f554064def0f60615cfcf9ad8880d68542d07fb0b5bd17c2b5b065f0a8da433da69486fadc8b4a0d174c01a53b6824a3f442b96067df33c9fa91bf3aaef6e9905030040e7d8c0cb58e6dabeebab1d5df7dc77fd9745365bff53dfed08cc0349df24693cef62560c019816d99be760d2eff23c6f7afe63d5ce3f6f787ba537e44d0444ac61c5f367d351b675b1e5bac1973ffaa33ffaab3fbefb87ab822f9274afa95a302a0f62ed35b89d42591a66a73a577442591f306eab1115c61bfe1d539000009d92a4f16192c613996bfa47ea7eb6ff3213df0db86e3acac62a1ff4c47245e1de7992c6e3ae04625886ba2551148dd58de54feb7aeee03ddbce80392879ae914ecc1ec855cb888fb7dd4edde08ba4abdffffef783fffb8ffeea44e55939476a6605ae3ad382e60d6ca78e8396b68370ac3cd1e6793eb1fdb2ef94e8bb51141d6d10f0eecce81c006037d92cf043fb38529801974557b6ee4a171dc95c7787fe1dfbb027731f7e6ca7c49df8cc722200e358144543991b70df17f9eb9ab4bd41076bba97651a35357a3ca878fe6cdb4c9b75822f9206799e9fdbb4cf5f96bcb6a900ccbce2f9a2ed4d39d7eac05268c718dcab0afa9ec88c8cf876a2eeacb8000008df81bd166cfc7d171e7dbcee6ae2dad889e9289bdba597bff1dd96807d2f1063338b5a4700c681288a0e64a6a50c1566e774e560fa91d46286428d14b379439baa2af0b45547be49f04532d3ab9234bed4eafdafaa664d2d763b652f693ad58f517f3469221320f73d9ab41f45d130cff3c91a7fc3142400c02afb0a2bf3be2b26be1b50663aca4e9334fe54fcb6dbda93f4c806b4860d96a5a8851a300d88a2e8208aa2a3288a4ea2283a97f45b990323c4e08be42efa7b50f25cd3f31adb9aee54b69dadd218370dbe2c28dd7683ab219569b530ae839a33085b69a031cff3572a3d05020000200049444154eace68d7789d17dbb6030080663c73908ddf389bb5f1cc773b7a625fd22f93343e6db33ecc2e64c0dc68689589437d7f34bff8ff87f23f7adab489876db67d33316fe87dcaa639cd367d53bbcf9e6af3e08becdf97559e6f6a7ad09956dfe836dd9975a9e60cfae144666530dffdf87e1445c7799eaf1310ba92ff76030010ba2b75a7387fa5e9281bda0cf4aa3a94a8e79e4ca1de611b3580762100735be5b530f07dcff23c9ffb6e44086a444a379a221045d191eacdef2c0bbed4d97e272a81af89517fac258aa2815d767aa93ccf5f455174a26ea4f38ea3289aac91dd525613090000d4731242f6cb2282308ddb9359bafa8be9283b76b921a620e1bab1ef06346450f17c1337f28d4f73b2d38e26355e5a157c518deade07f55b06f4da89cc31e5db9e4c360e000068c7a5ba331d792dd3513614d3919af67192c6e72ea7241180c1a22f7625fb653acada286039dfe06f4eb4ddb4a3ebca6aeb1cd46d1410b0ca3a441dab05731c4551dd933e85780100d8ced0e792c4dbb241982f7cb7a3676ecb4c497252cb92000c0a41cd7dec237bd355359d609de08bc4941da06e3023c42c188e6f000036f745db2be0b860a7cc7ca06e5cc7f4c59ea4998b200c011814c6bbb4aa464babe5ac9bba56f5fa75832f52794067677e6fecb45a27ce40b360e6ae1b0200404f5db8aef5d1a6e9289bc89460687a65d95de624084300069274b6e6ca1b21a8b35aceb6e615cfaf75b0dae95f672b9ede24f85285e90bd805eb044243cb82993b6e0700007d7425e9c877239a664b2c0cc494a426351e842100835e76406a21bba346b5f4830ddef6486f07612eb541f02549e3c106db07faa67600a66b5930355e3377dd0800007a6810daaa47754d47d92b9bd9f3aecc3d04b6d7681086000c8e7669ead182a62a5b97756c8375df2ccff357799e0f24fd58a6e3fc699ee7071b66be547512b30dde7393ed346950f1fc2eeecb28777bcdd777260b268aa261d90b76a5683a00000dfaa0a5c538bcb2b56d0e45364c53f6249d36b13a120198ddf68b3ccf672d6eafece6b8aaf8ecbae615cf37153428ebc0f7378d94e6793ecff37cb6e594a361c5f34d9d7cca566d9a35b48d5a76e1840ab76c40ba2b73c2c7355ed3856011000021f8c0d64ad9090bd9303fd5ea3207a86f5fd2e9b66f420066773df350f7a5b59be31a69854d65c0541d845e6ee46c91e1b291ff8b2696dc73b53c1bd0a4288ad6adc7345137d276f7abb260442d270000ead8a9e0cba2e9283b9f8eb281a49fab1bd73721bb9ba4f1789b372000b39bcef23c1ffa6ec4754da4745d53d6c134153898553cffa0a51597ae1b573c3f6b683b072d6da73028798e4c00acb249df326eba111baa0ae232ed0e0080723b1b7c59341d65a7d3517620b364358198cd3dda66109a00cceeb990bfa2bbf38ae79bcea628db5e23539e6ca64dd5726fe326b65597ed101e54bc6cd2d0e6aa7eb3366f0ec90440633a9405733b8aa241c9f3ecf700002c7725822f6f998eb2890dc4fc5c4c4ddad464d33f2400b35b2e6456d3f135623aaf78bee90c9859d9930d4e9fa99acaf5a0e515892615cf5f34582b6550f6a4839a2c4c79c22636dd6fba520ba62bed000020145732ab1d4d7c37a4ab6c46cc4066f18f2f4436f93a6e6f3a158900ccee3893dfe08bd47e064cd5cdffa0898dd88ebd6aa4fcb48da948491a4f54bdea4b93b57fca32895c44d43b53f01741d928b89be7f9a9ba3132742f8aa28315cfcdda6b06000041b89074c0e20cf54c47d97c3aca8ea7a3ec86ccf4a4aaec7e18c79b94d02000b31b9ee579ee3bf852a7306e9001186b5cf17c634b97ad62a3b055538f2e9b1a0948d2b86a2a5ba327bd1a5944d4c2800b63df0db0c8820100a0daa7d35176d8c46213bbc84e4f3a945939e999c88a29b3a70daecf08c0f4df2f3a5670b72ca27ad0e4866cc0a72c33e55e5301111bd4a88a16df963473b17290cd7c7954e3a5c306373ba8787ed6e0b6a4eafd83510eacb2f1719ee7f94cddc882194651b4ec73b0df030060aef9df9d8eb2b1ef86f4815d39692873fd4d56cc6a6b67c11080e9af2b49ef7a586abacabce4b9aaa9339b98553cdf6441e2618dd714419846b69ba4f18d248d67aace7c91a4e7d351366b62bb56d56768725b5275861437a25865dba0e7b889466c694f4b8e39df998d000074c0a7920e1bbece85a4e9287bb5242b066fac9d05f38ea386c0af3349471dbd303f97746fd593491a0f1aee3c4f551e9c3852432b024d47d97992c69faa3a13654fd237491a3f97745c636ad65b6ca4f5d83ecaeaa2142ed560f68b0d20ed97bce4b983d4cfb29be82b524de14a9ee7b3288a9eaba4ef6ac958cbfbab4b951f8f00fae3cc16cd04206d7c2d8df5d99a3ac3248d8f65ee2b8ec5f58764be8b71dd179301d32f5732538ebcd77b2931ab78bed1e939d35176aaf2b98bf79a2c8e6bd31e9fd77cf93d49bf4dd2f8b46e464c92c687491a9fc864123d52bde0cb95a4a38603146d67bf48e5057fc97e816b5da8c1b2bf6249ea79cbed0000c0a73399e94647045fda67b3624eec52d6ef8aac98fd7566379001d31fcf241d7738f052a85318b7e9695355593043353bc560281380a83ba5ea9e4c204832279473bd5d507620139caa1370b9eea8c92af036fba66acad3a4a9edd96d0e2a5e326b727bc075799ecfa3287aa67ad3fd5c3ad6dbfb7bd7fb7d00009a7241165877d8990b33b262742473cf59890c98f09dc9d47a1906107c91cdc2282b8c3b70b0d9aa83a1d1916dfb1907daac58d55d491fcb64b72c3eee6afde0cb95a40f1ccc87adfabe5c4c3f1a543c3f6b787be8978386de67dcd0fb6c63d992d46480010076c5ed1a037368d992ac98ba3302faa276060c019870158197815da52324b392e7f69a5e25c84e432a0bfaec25693c6c789b4510c6574ade95a441534b4e17166acf9469749b56ab4b5ea3771a1989c9f37cae6ea4d90e7d370000008f26be1b80d5a6a36c361d6547926e4afa85caefc3fa62af6e6090004c78420ebc146615cf37b932516152f1fcb8a925a90b36123c94e978da74265309de4550a2aae8efa50d7835c6fe2e65d3b92e28c08b161dabbcae545b6d5834f3d10800003cd94fd278ecbb1128772d2ba65841c9f735944b833a2f220013862b495f48fa71e08197c2ace27917019813951ff0fb725464733aca4e643a9d3317efbfe04ad22fa6a36ce0a220992d56dcc5ec9799836d024bd9a99e4dd7a95ad75e144543cf6d0000c0a7e3a6074fe1ce74949ddb81e903491f68b3520d5d37a8f3220230ddf64cd2cff33cbf91e7f9b14d7f0f9e0d0e941d74b79b5c99c86ef3956ad482697abb0bdb3fb705c33e50f369784580eec0067b5c19ab3cfbe54a6e6e4cab02308d66dc0035540574db305cf8df4cc10300ec9a3df91f10c19a6c56cc643aca0ed5bf15946a95d12000d32d57b2411749376d61ddbede5cce2a9e77910533ae78de79476e3b9c0335539cea42667ad3c174941dbb9c8663e73456adfe72d2741becc8c6bd92975c3928320c94ea4816ccdd288a0e17da0300c0ae794041de70d95a3143995a319f2afc5a317b75b2b25886dabf339960c4699ee7bb348a399159ed6795a11abec1998eb27992c69fcaac2ab4cabd248d8f9aae63b2a42d33d920945d37fe50266ded40ab0b869e499adbbf9bb99866b48ced4826152f23fb05bbe644d535915c2b967c94cc45cb2e2efb080078dba59a99167ea8f281b02e18cbcd2aaa68891dc01dcbd4e41cdaff1dea35cda12a120d08c0b4abb8813e9734dbb180cbf74c47d97992c665370cb79334765148b6ce4dd3c46e7bdef0b697b2c19e2e07124e54dd098e1d65e00c2b9eeff2f7861ecbf3fc551445c792bef4d88ca3288a6ed80c98b9c2bd580100346b3e1d65e36ddfc40ec2cde577b0a1cadd248d874daffc093fa6a36c92a4f1a9ccfd9aef81ae4d1c54bd802948cdba9409b29cc9a4517d2a33d5e4c7799e47b680ee30cff3935d0ebe2ca8ba791e36bdc185086b993d71632f49b251e8aaa947172e6acfd87a3c774b5e72e53a53092893e7f9447ed365f7e466ba260000c575b3ef29b7759c5090b73f6c9d98b14c3689eb454c9a7650f5825d08c05cc804419c3c6c60a5781cd820cb20cff3b17dccfa523cd78149c5f343179da90d16541dccb793349e34bded9024697ca87a275d27ab47d5785f822fe882b1e7ed17c7c9cc67230000fd646f84bb5e9b634feeae47e1c97494cded22265ff86e4b93762100f3ca06419c3c7c7fb890d9e94565ab21b91cdd3d56f52a260f9234dec9cedc669fcc549df6f7858b22b836f036ac7859082332e8b90e64c1dc8ea268e071fb0080fe1bfb6e400d8f5cad660abfa6a3ec586625d91054ae84b40b0118745bd54df4d8c5466df0a7ce7b7f6ea7e1ec0c1bfc385575f0e542ee4ec84715dbbf74501f08d894ef40ed50668e3e00008db3f555ca064dbb62e2bb0170c3ee83212c595d397b83000c7c3b557926cabe5d25a871762a529da5a0bfdc95208c0dbecc24ddae78e995a4a1c3a5afc715cf93fd82cec8f3fc547ee7283f102b400000dcf23dd850c75d96a5eeb53a33183a8f000cbcb237f055b53c5c76f843d59b3ed0fb20cc1ac117493a76958162bfe7b2d55caec40807ba67ec79fb55c5b20100d8989d721e4241d489ef06c00d7bdf38f1dd8e6d118041178c2b9e7716cdb607f291ea4553bfec6b4d185b70f75cf5822f5f385eea6f5cf1fcc461e60db0115b132c840b5300003635f6dd801af693341efb6e049c097e110e0230f06e3acae6aa9ed33771b8fd73d55ff2faf3248d277d5aeace4ef19aa93ceba4f0dc16c272d596618d7630fd085d35f6dd0000005cb1593021d4e138dea582bc7dcfd2bf26f81a900460d015938ae7f75d762ed35176aafad5b51f489af5a163b72304dfa8bae0ae648aaf0d1db6e586aa6f609fd9801dd039360ba64e5d2900004235f6dd801af614463bb796a4f144264bbf5703c4abf4210b9e000c3aa1e6bcd2b1cb8ec54eaba91b84b92de93cd42949491a1f24697c2ee951cd3fb9903470dce91dab3afb65ec70fb401382ec130000a8c30e847de1bb1d353ce87b415e7b1f52d4807b20736f52b90c329caaccd02100832e19573cbf2fc737376b0661f664a62405950d63b35eead67b915a08bed8efafeab725fb059d97e7f95c61a4670300b0a9b1c2588da6b7d3d6edcc80cfaffdf3bea45f5303c7abcafb250230e88c9af34a1fb90e76ac198491a4bb927e9ba4b1d30c9d6d25697c94a4f15c26eba5ce9423c96425b9ce7c91cc14b4aa368d1db70168cad87703000070c55e178610dcb8ddc7fa2836cba5ecfb7f94a4f1791f338002f84c0460109c718dd74c1cb7a108c2bcabf5a2fb8f24cdbb168849d27890a4f14ca6d64b9d42bb8567d351e63cf8628b00dfad78d9a764bf201464c1000076c089a44bdf8da8e1a44bd7e5dbb29f65a6ea81cbdb927ed9c3da3003df0da8c0142484c5de647f5af1b2bb6dd45eb119390399293875ede94d2066e26b6a5292c63792341eda8c975faa3ac071dd2fa6a36cd878c3aeb1278449c5cbae14c6280bb0e85861a4670300b0363b4037f6dd8e1a7a5390778de0cba207eae000f11686be1b50615ef5020230e8a23a11f5711b45a6ec12d503adbfb2c99e4c87f75b9b02d8ca7278769ad144e6e0ff52eb65bc48e686f1dde9286b2be03151f549e4b80f15cfb15bf23c0f253d1b00808dd88cf110b2603e0ea95e638989ead7705cb438401c6c20c64e275bf7dea6557532f6df69a11dc05aa6a3ec95cd70f9a6e4657b329d501b419857928e6c9bc65a2fea2c998ef2739982bd173291eb99a4d9b681053b0ff250264834d8a06d8b9e4b1ab615ecb0dfe7bd8a979dd9933b10a213994c986d8e4b0000baacea9abd2b26eafef4959592343e51f57573952210736cdfef2494414e1b34eafac056d58abe9208c0a0a3a6a3ec3449e3e72aef686e27697c321d65ad2cfb3a1d6527491a9fca74e0eb4ee929dcb68f8f252949e34b996c957399a24d732d4f5dbba137c1a6434907da2c02becc954ce0e5b4a1f7ab64b397c6355e3a74db12c09d3ccf5f455174a2facbbd030010147bcd7ea6cdaf8ddb723749e3a336af779b62333f3e6ef02d8b40cca3248d9fc904622a6b97f8b2e1d42b1f66755e4400065d76aceaac8e8f93343e6f2b4bc2a6950d6ce1d8136d9f06b76f1fbe4e5a5f481ab719fd5ea8fb52d5895278177d40160c00a0efc6323507bbee44525001189bedfea5c34d3c90f4c00e0a9f483aedd2f5b79d3a76aae6069e5d9ad579113560d059f6e0af93dd72d2463d9845367a7e28533038c4429b67927e3c1d653eeaab4c54dd895e4c47d9d87d5300b76c2d9856b2f40000f0c12e5cb16ebd441ff693341efb6e445df6fea6ad80d1be4cc984c5fa95adde5f5d67cb159c2b8ce0cb953d0e2a9101834e9b8eb289cd36299b8ab427e93449e3c336830945f5773b87f258618c723f9749339cf9d878cdf9ab57928e5a680ed08a3ccf2751148dd5f1c271008270c38e88ef2c5fd730a854a7b65f171c27693ce95296c7326b648cbb50d4af2cca25ccf4a67ee5dce586ede73e92c9aa0ae9baa976a08c000c423094897e961d84fb9266491a0fdacee85858866f6ce7681eab5b91da2b990efcc4e7c9668df9abc75d3f29021b18cb6d0a3180dd705b614cf57029f2dd00bc6d3acae6b69ec803df6da9502c4b3df4db8c4a3375e37e625f769a92f43a2073bef0986f5b3fe6daa2222104f196210083feb0ab221d49fa75c54b6fcbcc5d1c3a6fd40ab616cdc4a6ec0d6522b8bea2b7cf65e6714e3c6dff35fbfbd5b9f97cd685f6024d230b0600b0038e65ae7dbb9e11fec066c1cc7c376499248d27ea46f06599a27ee5eb404992c692598e7c6effa9585c649581fdefa1babfafd471b54e7167023008c274949d2769fc81aa6fe21f2469ace9281bb6d0ac956c24f85826cdf150e6643490db62bb458ae0a91a58e2ba29f6f34f6abcf442d4ca40bf85b2542700006bb383a6a1acfe77a2372b8c7686ad51d3f52ca2658ac08cd4fd15b19a3659e7c50460100c5b0f66a0ea4ea9134198820dc6bc4ecd5b48b33b58f8efbaa3e2673291e5e2bd3b13705964832f335547b7af241d75f133004dc9f3fc348aa21096ea04006053a1acfe773b49e3619732afed74fd108257f8be93755e4c000641998eb2a1bda9af4acbeb541066914d779c2d7baea2b0de3ca4da286b045f246910d26703b63016f51b00003d65b360c6b2455c3bee2449e3d32e0c00daebe6b56ee4d109cfd6bd87210083100d54af3055678330ab74752eeaba6c20e954f5822f1f6c5bbc0b08459ee733b26000007d361d65277609e1aed73d2b0af27a9d029fa4f181ea0f5aa25bc6ebfec11f386804e0948d520f65a6ad547990a4f1a95dd20c2db0e993bf54fde0cbc4698380ee19fb6e0000008e8d7d37a0a68f6d00c40b7b8f5277d012ddb276f68b44000681b2191303d50bc2dc9359a29a208c6376b4a3ee52bbac78849d94e7f94c66953200007ac95ee39df96e474d13cfdbeeea8a472837dee48f08c020586b06616e4b9adbf99570c02e995777beefb390a686010eb0e21700a0efc6be1b50d3dd248d8fdadea8bd76be57f53a74d2a79bd6af240083a0ad1984d993c98419ba6cd3ae49d2f82049e373d55f328fe00b765e9ee77349cf7cb7030000576c6dc350b2605a2d806bef47425c6e1ad2a5b6d85f08c020781b0461be4cd278c294a4edd9d18273d54f9d24f802bc31f6dd0000001c1bfa6e404dfb76f526e7ec621575a7eca37b86dbac9c450006bdb06610463211e71953923693a4f18d248d4f247da3fa45c33e25f802bc41160c00a0efec348d50ce75c7ae0bf22e14dd4598bed876d55a0230e80d1b8439947451f34f6e4bfa755bd1eebeb041ab99a48fd7f8b30fa6a36ceca44140d88e553f700c004088c6be1b5053b12cb5333673823a7061ba988eb2ad7f3b0230e8151b651f68bdf9a68f92343e271ba6dc42d6cbaf557fcad195a49fb3da11b05c9ee7afd4f2bc730000da64afcf3ff5dd8e9a1ed82942ced8ebe277c5004c48ae243552a899000c7a673aca5e4d47d940eba53b16d93027d48679db42ad9775b25e2e250da6a38c344ba0dc89b8080300f45b48e73ae70323761acb40f533f7e1cf95cc3dcdbc8937230083deb2f5463ed07a9dfdc732cb55931a2853242c49e3994cad97fd35fef4b9a4433b2d0c4009b26000007d67a7de8472aebbddc6aaa90b352c9fbbde16b672dce43d0d0118f49a4df11bc86463d4b527e9f3248de7bbba64b55d5a7a22e99792eeaef9e79f4e47d9d136d5c1811d14d2c82000006bb3f500d7b926f7a995ac789bb97fa470a668ed9a0f9a2ea5400006bdb7509c77dd0aecfb324b56ef4c202649e3431b78f9adcc4a51ebb894f4538aed02ebb3593064de0100fa6eecbb0135392fc8bbc85e3f5317a65b1a0fbe480460b0236c747928e9e75abf632b0231af92341ef7b1464c92c64776aad1afb57ee04592be10538e80ade4793e513823830000accdded08652f7e463d7cb522fb275610ec494a42e70127c91a4775cbc29d055d351766a3bd289a47b6bfef99ea44732ab263d93741a728159fb3d0ced639dfa2e8b2e250ded0903c0f6c692bef4dd0800001c3a9699e61e82894c398356d829fc4776018c89ccfd07da5314dc7536a84c060c76cec25ccb77b5f968f30349dfd8e94927a12c616d6bbb0c93343e979966f4489b075f3e95c97a9935d53e60d791050300e83b7bed78e6bb1d35ddb5c19056d941de03910dd3a60bb590d14f060c765691e697a4f1582612bf4984795f66e5a48f9334be943493742a69d69522b4363874641fb71b78cb3399ac977903ef05e06dc7322b8f0100d057638593057322737ddfaa856c98814c36cca683a6a8f64c66b523e7f76f0460b0f3a6a36c9ca4f1894ce7ba49fd93c2befdfb079294a4f1854c40e65c262033dfaea5d56c7d9a439954c9e2bf4da52e5ec8744cb386de0fc012799e9f465174a6f5572003002008d35136b353fab7b9f66ecb7e92c6635f0b4d3434688ce5ae6406965b0bb0118001f43ac23cb41ddb58cd9c0c6e6b21e3244963c9648fccede35cd22b49afd649755b08b2486fe6a40e64d2145d44c62f258d5d15a202b0d458e18c0c0200b089b1c208c048d27192c6139f19e00d0e1ac3782e33b83c6f73a304608005f6006c3a10b3e8ae968c6adbe0cca20b99e08c64822d3e22dd679226045e80f6e5793e230b0600d067d351364fd2f80b99e9fc5d572c4b3df4d9084783c6bbe65226f0e26531158af0024b4c47d9dc2e5b7d53a6d86cdb45316feb4db0a6ede0cb3349ef4e47d980e00be0d5d877030000706c2c330d24040f6c3d16ef16ee557e2c73ed8e6a577ab38888b7956c09c00025ec8a49e3e9283b90f473f5b712f9a5a45f48faf17494b1ac34d001799ecfd4df3e07008022a3e3c4773bd6d0a9b67660d03814cf64022f63df0ba5300509a8c9464a4f6d0d96a17d34b1aa902f973215dd27ae975b03b0b16349f77c37020000874e64aeab4358e5e77692c6c3ae6589dba0c258d2d82e9b3d14d70f9209bc8cbbb47a2b0118604d0b91fa93248d0f640ae01ea9d915875c29566622e8020420cff3791445a1ac120100c0daa6a3ec95ad69f2a5e7a6d47592a4f1a9ef4c8a5516068d0f64ee51860a7bd0785d9732cb769f74f1372200036cc1465327f6213b2fb478f82a9ebbe84276196cb5b4143680c68d45000600d063d35136b1419810b2608a82bcc79edb51ca5ef72f0e1af73d18f34cd2a9cffa2e751080011a646ba7cc8aff9fa4f1a14c20e640262873436e3abd2b9940cbdcfef79c3a2e403f90050300d811c792bef1dd889a3eb6cb520791517e2d1873436fb2f7070a23e8b5cc954c3985994ce0a573d92ecb44799efb6e03b0736c14fac0fedfc1b5a70f6502358b66d7feffdc3e44a005000000c026164a2a0c64ee43ba9c2173a63799fd33bf4dd90c01180000000000209b2173b8f0389074b7e56614d9fdaf1fa1641b552100030000000000565a08cc486f32f80ff426abbfb02a5873299bc1bf6066fffb4a26d0d2fbec7e02300000000000008efd81ef06000000000000f41d0118000000000000c708c0000000000000384600060000000000c03102300000000000008e1180010000000000708c000c0000000000806304600000000000001c2300030000000000e0180118000000000000c708c0000000000000384600060000000000c03102300000000000008e1180010000000000708c000c0000000000806304600000000000001c2300030000000000e0180118000000000000c708c0000000000000384600060000000000c03102300000000000008e1180010000000000708c000c00000000008063eff86e000000000000bb2249e30f25dd5cf2d48be928cbda6e0fda4300060000000080f6dc97142ff9f74f241180e931023000000000b0a39234be29e98e7d5cf752262be345bbad02fa69ab004c92c6df6a79e46e1bd97494bdd7f07b02402795f4a39f4c47d9676db7a70d0d9c3b5e48facefe37e3a2100050d72e9e7797b141970f65323196055eaebffea5a4af257dcd1419607364c0000042538cd2dd97a4248d5f487a3a1d654fbdb60a00808e5b08bc3cd4f21a24ab147ff76192c6994cc08a0110604dac82040008dd1d494f9234fe3649e35bbe1b03004017d973e4b7921e6bbde0cb75b1a46f6d2159006b20000300e88b58d2af9234ae4ca506006097d8cc975fa9c674a39a6eca0c7e108401d640000600d027376546e5c8840100e08d6fb55dd6cb2a4f18f800ea735503e6a94c91a64dbc6cb221008060d43977142b35dc97b42ac87253d2134914740700ec3c9ba5521624c964cec1d97494bdbe17b38195fb32b55fca82378fc53917a8c55500e63baa630300d654f7dcf1b5a44f92347e2873d1b74c9ca4f18714e60500400f4b9efb68d5b9d216d97d91a4f153495f697510274ed238e6fe0fa8c62a483524691ccb8cb41691df970a28c86453f16fe9fb9de60b492f43ad5edec7cf24f5f77349af8fa39bfa7ed6c277329f2d886309dd321d659fd965319fac78c98732237adef561ffef5bffb4e2f3bc945de27c7114b82b426cf375211f0b217eff21b619cdb2592cab32466bad20381d65df2569fc9e4c0d9955ef755f2693c62bf67948dd3ed7ec5c002649e36f650a355ef7c974947db6f0ba0fedebee97bc97644662b3ae8db2dacee74395a7e9cbdebc7c2de9ebeb3b63c9e872361d65ada719f6f13349bdfe5c37653e53e971645f2b75f45842b74d47d9d3248d8bfdecba3b491adf9a8eb2efda6e575ff6ffbef54f753f8f7ded0b99cff4d4e7057b886d5e14fab110e2f71f629be1d4b2f363a1f671361d652f9334fe4cab073dcab6e394bdd92efa99b4b9c7a20000200049444154aa7dfe3bbdd9e75bbf3e689bfd6ebe5df1f467d351f6c996ef7f472630e7e4fdd7684730e71a8af05e93a4f19d248d7f25d3b994fe78d67d99e253bfb13bb857491adf4cd2f8b1a4dfc8a41b5615a2bc297392fed62ee1dab9225a7dfc4c527f3f97f4fa86eb37aa7f1c496f8ea5dfd9bf07ea2aab1bd3fa71d287fdbf6ffd93fd3c5fa9fee791ccbef358d26f7cfc2621b6f9ba908f8510bfff10db0cbf36c85e2c3bdfb65efc3e49e3d80eae7f2b730eaad3865b32c7c76f9234feaaef45fbeda0c8aa4053132b5895f5ed9bd6845d4b68e79a9dcb802963b35e1e6bb30ae1b7642e3c57cea374cd5ef06e53e1bc58c2f57bd9403e35f899bcfd2ecbf4f1b7925e7fae27daeea6f7a6a4c736abe1fd5d189dc0d6ca2e205bbbb0eacbfedfb77eb781cf53fc2677646a2538cf1208b1cd8b423f1642fcfe436c335ad3d8ca4776bf889a7abf4dd96c87872aaf6d53c77d49f7bb763dedc0532dcf44bd99a4f1fde928db2650b22ae0f1c2f5f4e450cf3564c0bc715fe607dcb6937a620339adb2dbfc959ae9641fdb914faf1afe4c4fba32b2d3c7df4afa5e8a635323df77646ee23a35928eeee942fd91beecff7deb771bb8295d545c273815629b17857e2c84f8fd87d866b46a6530cd06328262dbfcadb60fbe2c7a9ca4719ff7fbb200cbc633386cd062d54097d3ec9790cf350460de68f2cb7ed2e674a485e85f931eaa7e0a57e31c7da6c7f2f899a47efe56d2ebcff5951a1c65b16eca6496f53a3d14dbf1bd7ff465ffef69bfdbc4c0caa2fb2d0495426cb3a4de1c0b217eff21b619ddd0faa0f13616822f2e6e923fec6b10c66675ac2a3cbbcd39ba91fa42eb0afd5c430066b597923e93f4beccbaf63fb1fffd48f576a856b212163aa22a2f247da2379fa5f83c9f6875fabe97cc833e7e2669273e57592798c91c3b3f998eb2a87848fa99cce72a4bf7bb29d3c902ab94edff4ed3e8fbb2fff7b17fb2d93cabb65d9ce37f76ed37f989cc6729db6f9cdd9886d8e6421f8e8510bfff10db8cd6951d570f03cb34ae33dde46b997ee63d493f94e95f8af354d5f4920f7b1c7c5c959172d366b26c62d5df392beadd87730d3560967b2ab32ad2f51de7f58f95982ae05f697527702749e30f5b98ff5e55b3e63b99b9bccba29e4534f4339bb1f3441e0a682dd1c7cf24ede6e77a29732c2d3d0eecd49117329f6bd54a2992399e1ef67c7e2e36573602e37a7a525ff6ff3ef64f65fbc57bcba6aed951c2cf92347eaad5a3ac371d9edf436c73a10fc74288df7f886d468ba6a3ecebc4ac54b7ecf8bc2933ede23399156b3a5bfbc7061bcb020599cc79eafacdf58b85e73fab51f3f37192c62f7c2f55ecc0d75afdb963ad3965c8066d567d872ebfbbe0cf3564c0bcede9749455161fb307f77b2abfb8773a0d2979b3cce02a2f64463d2a0f02fb9a9fc9fdcd4aa93e7e2669673fd74b998bbf5a176fb6937bbfe4250f439cab0cb7ecc8ddaa7df03b97f561fab2fff7b57fd2ea73f0d3aafdc25e0394fd1eae468c436c736f8e0585f9fd87d866b4afea46b25815e8c916d910ced863be6c76c1d3e9287baf4e0155db17fd44e5e7a94ed4576c923dde570559ee6fd0afaeea7bbedbb2a8ef4a7d39d7b80ac0c4491a3f5cf7e1a82debf86e3aca3eaafbe28513d7aa608deb0eacec3b7b21b313d68e64dbd75605955cebe3679276f3737db2eecdafedb03f59f174b1cc2d20e9f589b86cbeb6eb91dbbeecff7ded9f565d38d55ae1c05ec8afba887495e113629ba5fe1c0b217eff21b619ed7baaea3eb938b6be4accd2bc5f2569fca1ef3a6bd6875abdaf7fbdcefd9bf4bdf3d4aa73db9d36eb79b668d575d14dad71df6a03132ba71faddba835f4e25ce32c002313395cf7e1dbda694615272e393e78cb0e948d9610b47fb35627d6b03e7e2669f73e57b669dab28d48afba70ecdca80cda97a4f12d1bb4ff95ca6b1fb80ec0f465ffef6bffb4aaddeb9c979fca5c9c5d7fb84aaf0eb1cd527f8e8510bfff10db8c962df4c97597d82d6eb09fc864c6fcca0e98fb0ac694653dacba812e65bf93b2bfeddda09f0d50acda07d6e933caa61fb95cfda817e71a6ac07cdfa63bccd75a7d903ae9a82ae6dd55a69d96998eb217765e70ab1d4f1f3f93b4b39f6bdbcef7a9960765ef24697cb3cb7394b1950f6b04ad6fa95ebfba51e0a0aebeecff7ded9fac175a7e4119d79ddb6da754b579131a5c9bfb722c58c17dff0ab3cdf0c0f6c93f9309aaac7b6379c73e1e2769fc42e6fcd04a7d203bd578e552c775a61dad321d654fed80ceb2f7efeba0dfaa7ef5fe1afdeaaa6bb56c9bdfa34c9fce35d48079e3c5a65f6ec5bc7857f394cb6e409a3889fa28bad6c7cf24ede0e76ae0a45c76d3c79cf4feba2573522f7bd40dbeb81c8151593b02dbfffbda3f49e5ed7f9ca4f1b71d4c310fb1cd7d3916a430bfff10db0c4fa6a3ece57494152bbc6edac7df91f4c466c5b4714de67aa9e395efd1d363a7ecfaa832e85431fdc8e5b5576fce3564c0bc11da88faca0ea1891b0f1b255f5531dd953e7e2669f73ed7770d9cb0ca6e0aef88913aacf6514ba3727dd9fffbda3f49e6a2fa61c9b663992c81622a71d681552f426c735f8e0529ccef3fc436c3b322eb69a1907ddd018e4577645650727dde2dbbf16ea2d658d9f1d0bb6bcee928fb2e49e3afb53c8812ab3aa8b52af85256e4b709bd39d7b80ac07ca7fa730cbb62dbf66672bcea514d4dee20abd25adbd6c7cf24f5f773dd9259d61268d3aae527dbd697fd3ff8fe693aca5e2669fcbeaa7f8f5b3237b00f6db0a8988ef175dbd31d436c7389e08e8510bfff10db8ceeb0018c8fa4d7537d16334eeb7a92a471135908abacba396ee43c65070a563dddd7d537332d0fa4dc4fd2f856c5b5d4aa2fcb575f12dcb9c65500e6699d39a71de3fba27d5d6da4fcb57d10f5f133497c2ec0956244f7a987c04b5ff6ffbef64f92cc286f92c6ef49fa4af52ea48bd4eafb32371545c6406b53a9026c735f8e0549417eff41b619dd6383312f247d66a799148198b2da1b8527491a3babffe151affab782ad7df358cb7fd7fb5ab1308dc7d58fa41efd16d48009571b11d9b69710ede36792f85c405d99de5e85a3f4843e1d659f78bae0ebcbfedfd7fee9359b6aff136d767158dca0fea6cd5a0081b5b92fc7c26b817dff92c26c33bacbd68a299677fe89eaada0d485156d37d5b7c0511dabfa8ab23a30ab8aea7fd7d074b032bd39d7108009571b1d45db91c63e7e2689cf05d4954d47d967d71e65177dc572d43ef465ffef6bfff43df666a2b891f84ceb67e5dc92f4ad1d316c45406deecbb1f03d017dffaf85d866749fddaf9e4afa99ca037cf76d8644887c2dafedd3aa7a2d774a961bf795fd22f5e85c4300265cab76c2263bbeb63bd13e7e2669f73e17d0b48f4a9e7b5872a1e0525ff6ffbef64f4b4d47d977366bea8792de97b9495d67d4ee61db37a701b4b92fc7c252017cff6f09b1cde8be85005f59ed95be655079cde0746961cad9326f055aecb5d6aa0115d72b4f4a3d3ad7b00a52b8568d6a3439d2d8f6a8651f3f93d4dfcfb54a361d65eff96e04fac3d6375855e8fca64cdaf3fbedb66aa5d0f6ff5deb9f5eb3ab3c7d2dbdbeb05cac7750e6a1ad75d0faca1881b539b463a15260dfbfa430db8ccefb44d2af563ce7624064d58d7723e7968aa5b4fb5ea0fa6b2dff1e97d58159b9f4b4e7da3fc19d6bc88009d7ca886c92c6956bb857b19d51dba3967dfc4c527f3fd7aa8bb2be8d7ea01bcab260ee7ba85bd097fdbfaffdd35a6cc6c0d3e9287b5fd20f555def60d53cf8d674a8cd7d3916d6d2a1efbfb610db8cee69a1d6c7752b33352b82277595f555bdcd80b1564d1dbab3e4bb5d198069b03d657a73ae210013aeb20ea18913a68f936e1f3f93b4839fab891b3760911d5df9a4e4254fda6a8bd597fdbfaffdd3c6aed53b58999edda55a079edbdc97636163ec33e8b2248d1f2769fced8a47273314af29cbc26aa28f59799eea7b06985d367a5500e5f5775b32fde8a5cdb26b436fce354c410a944dc97fa9e5238b7192c6f1a69d86ed8c5bbf68eee3679276f673ddd78611717bb1b7ea82e0a587911774c753490fb57c9fbb95a4f1c3e9285bba7462d3fab2fff7b57fb219512be7aad749979e8eb297491abf2fe9372b5e7247e537066b09b1cd769bbd381642fcfe436c33bc28a69e2d73476b6679b41d949b8eb217491a7fa7e5d39b3e4cd2f8331b48585b92c61fae785fa99dc2b25df0b59607b2eeebcdc0d7aa73796bdf515fce35121930a12bdbe99f6cd241dabf697b2479511f3f93d4dfcfb5326abec594908792be5df1082ecd10cdb117586559306d17e4edcbfedfc7fee9964c6da0658fdadf63cbf3da436c73a10fc74288df7f886d46fbca6e2037c91c28fb1b578364abce531b9f6bec204159b1e9b6323bbcb2192ccbfa805b0b1952bea71f556d2fa4730d0198c0955d34174b09d6be70b6affd567e0b26f6f13349fdfd5c65d9065fad9bda6a4722562d2bfc52bb331a81156ccafcaa0bbca2206f5bfab2fff7b17f2a1bb17f58f7f3b49c9e1f629b0b7d381642fcfe436c33da57ba6a913dde6ab1fbd4ca63d3e1949da75a5d10f77e92c6abdab494dde79f68758db25d2b405d16d8b8a3e559422f3c64a5f7e15c43002664356a22dc91f49b3af3e26cd4d0f705732f3f93d4fbcfb5aa33bc2973e3566b74c576826537cf1ba798a277ca8ea5d60af2f665ffef63ff643fd3aa0bc35b921e57dd9c5665f1347d711e629b17de37f86321c4ef3fc436a37df626b92ccbe971cdfefd964cffbe2ad3d4d914607bcc97bdffe3248dbfaa1374b47d4cd579aaec9cd847ab020df7b53afba5f541d13e9c6b247735606e6d71014c8d87f53c959997b7aa33bc2913117c2113dd7c519c4ced6f744be6c0ead2d48e3e7e26a9bf9feb3399762dfb5cc567ca643e53b698ea6c4f9445e75e5a85beadda1ee83e3b0f78d59c65c99c507fd65273fab2fff7b17ffa4cd2572b9efb5066e4f733bdfdbb14f5121e6af5f7e12aed3ac43617fa702c84f8fd87d866b4ef13adde4f561e9ff6d82c962e2fcb94719ea53c1d659fd99beb558193fb32fbfbd732593f2fa6a3ecbb851a1f455db2aaa9ca9fecdabda8fd9e5ee8edeff696566788f8ea1f823fd7b80ac07ca8cd0bef6592825acbdba785e269dfaa7ca9cfa2e35192d6be3e5e76203ad7c7cf24edfce72a4edeeb7ca6c24b952f418cddf489560760ee242d15e4edcbfedfc7fe693acabeae08d4dd921df9dfe07771b26f85d8e6421f8e8510bfff10db8cf6d9fda408b4afb2cdf1f9514b59caefc9148c5ed5c7dcd4c27de8069fe3e90e0ff83d55fd7a3a4f7d65a5f7e15cc314a41eb051daf7b47a6ee4263e92c7918f3e7e2689cfb5819792dedbb5910854ab316da676fd8306dad28bfdbfa7fdd3476abe28a4ebd1d110db2ca937c74288df7f886d46cba6a3ec23b959d1eaa3b69622b637fdefa97c4ad5a69edaef6857adf31b7a9d9a18fab986004c4f2cec88db76482f653a52efc54efbf899a4de7fae9fa9b98bc01722f882724fb5fa386ab5206f5ff6ffbef54f0b17eb4d5d2c3a1f1d0db1cd8b423f1642fcfe436c33fc988eb2f7d45c6693977e7ea18f696a7f2f3ec72e075f8a7ea4ce6ff95d5b01b732219f6b08c0f4c8c28eb869c79a49fa99ef0be6450d7da6f7baf499a47efe5692c94a988eb29fc964266c1a957e2933f2f633822f2853a328df876d15e4b5ede9c5fedfb77e773aca5eda9b8e6d7e97ef24bddfd6057a886d5e14fab110e2f71f629be1c774947da2ed03765fcbe375e8c2fefe91b61b3078aa0e5e4f7b5427b0d299ef2ad4730d01989eb11dd227927e2273f15cd52915d1cef7a6a3ecbdc542455db1e167fa5a6f3e53276fe2fbf85b15ecc8d94fb45e5af40b990ef4278cbca12e7bd154761159b90a48d3fab0fff7b1df5df85d3ed17abfcb47d351f6131f237e21b67951e8c74288df7f886d46fba6a32cb3018c22d85ee79ab25881e627d351f67e17ae43a7a3ece97494157d4cdd7df785de7c8e8fbaf039ba626a8aeb577d1f9deb23423bd744799eb7b93d78602bdd5f5fc3fda54c0ad9ca1b97248d1f6a790a7fd1697bb3b026fd5a9fa9ebfaf85b1516564ab97e33fc42a6da384b4ca3b7fab0fff7addfbdb632c6a2973217a09dfb5d426cf375211f0b217eff21b6197e2cec2bd29b7ebeb8190f663f09b98f4173babc1f1080c14a491a3fd1f26ae99db9a987c16f0500000000ddc614249459b6be3aba89df0a000000003a8c000cca5c4f572d3057b27bf8ad00000000a0c3def1dd006ccece6d7bb8e2e9f7b799db66df7b55e14a6eead7c46f0500000000bb8d004cd85e4a5ab5c4ea87da7c09516975b040ea60f5eb00f05b01000000c00ea3086fe09234fe9d96673fbc94590e74eda5409334be2fe9ab154fbfb0ebad634dfc5600000000b0bba80113be55190e37257d6b970dadcdbefe49c94b9eaef37ef81e7e2b00000000d85164c0042e49e35b927e53f1b24f243d2dab3392a4f14d99a9308f4bdee7bbe928fbc9faad84c46f0500000000bb8c004c0f2469fc50e537e385cc3ebe9399f62299d573eec8d4275955c8b5f0b34da6c9e00d7e2b00000000d84d04607a2249e327325911ae7c341d654c696900bf1500000000ec1e6ac0f4c474947d2477353fb8a16f10bf1500000000ec1e02303d626fec3fd19b292bdb7a29e97d6ee89bc76f0500000000bb8529483d648bbd3e94745fd5b54296792993a1f1595931586c8fdf0a00000000760301981eb3abe5dcd79bc2adb74a5efe526f0abf7ecdcd7cbbf8ad00000000a0df08c0ec98248de325fffc829bf8eee1b70200000080fe2000030000000000e01845780100000000001c2300030000000000e0180118000000000000c708c0000000000000384600060000000000c03102300000000000008ebdb3e91f26693c6eae190000000000009d349f8eb2c9b66fb2710046d2a36d370e0000000000d071679226dbbe0953900000000000001cdb2603e6acb15600000000000074d379136f12e579dec4fb0000000000006005a620010000000000384600060000000000c03102300000000000008e1180010000000000708c000c0000000000806304600000000000001c2300030000000000e0180118000000000000c708c0000000000000384600060000000000c03102300000000000008e1180010000000000708c000c0000000000806304600000000000001c2300030000000000e0180118000000000000c708c0000000000000384600060000000000c031023000000000804e8aa2e8561445798dc743df6d05aa10800100008d8ba2e86614458faf5d1c7f154551ecbb6d00d025f497ddc56f83a645799efb6e030000e891288a6e49fa95a49b2b5ef2519ee74f5b6c12007412fd6535fb1dfda6c64b3fc9f3fcb386b7cb6f834639cf80b151c387f6b12a5dec2bfbfc7dd7edb9d6b6bae96c8b8fdf35b8fdaf36d8fe874d6d7fcdb6f6ed77dce671abcdcfd796288aee97fcbeadffae3e445114b7bc2fad7a7cebfbbb00b6f495565fb04ad293bef6a5f0a7cbd72a4009facbeee2b741e3de71f5c6f6c4f6a1a43ae959f7ed43511449d227929ee679fed255fbb670338aa23b799ebf68e0bd3a9fbad6e3df1196fd8d1f4b2a3b813cb6affd4e26da9fb5d13600e1894c5af69d1a2ffd50e63c016c856b15848afeb2bbf86de04ae31930361be15b9988e1a60186c7927ee72bdba386ad03275114dd517944d5ab1df91d775e14454f647ee3bad1fb5b92be8d28720660b53a17acebbc0e588a6b15f400fd6577f1dbc0894603307604e2376a2eb3e34914455f35f45e4d6ae240eb6cf6cb0efd8e3bcd065f36bde07c4c1006c09648dbc6c6b856c18ea1bfec2e7e1baca5b1008c1d397071e2badfc17a084d9cec3b192dddb1df7167d9e0c9b6a37d8f99430f7453cd5a434f3c37f33bcfdb47a0b856c10ea2bfecae9dfe6d02b9dee894460230f626cce5171bffffed9ded752abb0e865fad751b6097c02e8194404a202524258412921292124209a184504252c2a104dd1fe3c9260466e4197bc61fefb3163fced9048ce49164599645e429e2e7fbb2704788c6905c054c857aac12d72c2c941e9e4424d9a374849059b0f6880ad14b8d540663155218b497e942dd90288c4ec0b8c5dc1459add43ad60f4ea0a4d8ffa5623dd648c8a3434b8cafa4218414846b526f095c797527f182b10a290ddacb74a16e482c4254c03c62ba64424a3b12632a6092ab7e41bd7aac0a57ad123a61c2040c21e49c07005db7ca3ca86ad565db64108c554889d05ea60b754382332a01e376227c165fcf00feaaaaa8aa00f803bf6bbb960975a91f934449aaff4b457afc6ac73cf295b3a1b5c8fd0bc0add3ed0dfa4b2b97018ee42581aaee7de6021ac76ce1d5738eddc6fc9d84c4c6d9c9bf68fcc5293b34f6853b86c48b8a62155219b497e942dd90188cad80f129cfbc55d5ede9e255558faafa8c6662776517877e674cc6f48149ad02a6663dd68665ce3ea8ea1ef82ebfbc45bf5e539bd384909971be617b965cbc6bed0b219e305621c5427b992ed40d09cd5409986dd724750ed2ba93bc4ea8e9a7f7a233c5fe2fa01e6ba22f017338d7b1aa1ef13bf37f0e7549082124268c5508218464cfd8048cb502a4b73c4b5577b077914e65b77d48054c2a633fa5763dd6c4b2e7dfaf05ad7d3a65804a082124268c5508218464cfe0048cc7f19b83db41b7602de5ea5b444ec510a79c54af0ceab11edcf9f93eaef5b7c9b9ef0d2184908c61ac420821a414fe37e26fad3bde3e77a35bdf9bca6efb424456ae4f8695d47652a847420a4744d66892bf6b5cb6417bf7fa75048d7443d9e6856baabac0f5db74b600e07a85248d883ca2997be747735ed1ccb7929a435619ab38fbb246335f4f39a06902ba4be1628093e7ea1e971356cf68faeebc7a24c8a2e136a43668c67aa9d1722bdf6aed367d5b7a9cccdb4b761ff8376f8f85d9ff41242d2f551df442f330aae1f532e767f67cdfd2f87d5daf478fef5b04f8befb10bfbd523d7e86945d6e2fa39c2ece6734862bc87350d20b4de036d95c1f30be4700ff79da98cfd0766680bcde7b3ec76a63a23df329c9d6431e96d7e867d9c3264f66379cbe7c65f1026039c1d8de0d63590f788e3e01aca6927164199510ab58e6e0bd7bef02c09b717c6f001633e965c873f536c573d5a173cbf376fafa00b08938a6a4ec2512f26d73cb2915dd0c9cb751c685c4e28dd4e575ed35a602c68acfcec1176c5704ce9eed3fc1e7f7a556fde243e97aac01cbaed3b532efbef26fea32215cb9fe0b861d795c027811910d803b0db85ba9aaaf6ed7beafa47f2d224bbdbeb36b6dc619bc8a2155d992cb387dbd61d831927b00f72272a74dcf903959008088bcc13eff97003e44e446fd2a757326f75865e19afebec36e633600566e9e4ea2e791cfd506c046441e74c25d67117981df35e62d2b006f22b253d5bbc0c34a06fab634119127fcae80b3f2e4aad3be6f372d9d5ce4352601637db8d622b2b03c8c2ed84ebeecf70c9fa44a52fd5f1cd46325a8ea51448ee80e507fcd67170cf6052d5518f61c7065c3ef013e6a0de05d446e030753af009e0cefdbe0821d71f3d1b2000d5e529a816cc90901f5f526225b9df758d2c233f972cabb88fccd7caed512abf8265f5a9668f47cd391b80e42c0e7eac5e92aba0e44e41de337413722f2aeaab721c69412f46d69322269784a6b1b52d848884a4ef21a730b92d5c0b767ad73a66b4761e57145619ff19f6387aa263d92fe44c9c2657f4f794177d2664f479b066e072b4410d5d2ee8885e415b6c5d4b585e606b65deea0417d26b2258e800b8a962757bd35178f18967c019ae7c592f44c995a62957b0cdfac6b8f2d45e3a4f225144fae6a221a2e7119aa027ded3eaf18e8dbd2c455728c4d269cf2e6d1cc3c3b7293d7e0048c5b705913068fb10d6c64fa16adbd86dd2569ba1479807d87271895e991d874fd1dbcba6c729fce8bcea8e7c249d97a6836179272837136c7326756579c9fd50605ab7ec945b6a4c135de8bb1487a72899d39187b13cfbdf126bc24a9285619dbf07715cba6383bf886f04d895f62cd4d97340d3d178ab1dbf46d69e2fc4c8c44f29b47d14036e428af31153080dfb183b799778fc6d0b7f362c990f5056d3bcc77d5612d7a24b685ef52441e5dc96e9f03fd9af20c37e9e409f16eeb08fdcc5bab537e04ce2e48b72c8043dfb491936c495c7de5bcb39b6b52a285b18a8d58bffbda0d47638952b5e4164eb16451cadca26f4b93587ee6daad5fb9939dbca64cc000cdeed17b86bb307dd5299605415f9266ce1e1ab5e8b17adcd9708bbe9f609bd7c536a4cb09639f9e312c43eefc7bccc3f305e35cd52fd9c8b6769c2c63261a96192fec6b4ac000f5c62ac16d8ab383318fb1c5a8d06aafc68ec132f70a0ffab63471328b69b372f55f17c9555ea31230ae43b0af435c03f87467b572e188eedf69e903d365848e73de5050911e4943a8de18db8a6ed6481d6b10f585e6860251550170037b597fe840ca9224390fe02c0bc87de07999a36c6bc61a2c1dd1dc74d0eaeb161e475c068d2c0c7b003703c79df5f9ffca6295037eda933ff0f3dda16d8ad50e9e8ffb2fecc7948325083dab5f9edbf1ba315b6ec602f24f68d2b7a5895566af00fe0c98b78b8c8f685e224f7905ba6b7bcc1de04f009653ddbb7d3676ebfdee2b3486bceb3d9b8eef59f4fced9b7b9f652cf7916451831ec7bed673fcbe48327b1f298b97b97f430a2f3401ccecf242732edf64cb2efcadf5f9798f30ee4f8b6d71ef5d19c779d5165726dbd9e6a5c7ef7e9ce97bffc3157f05e063ea7906bb3dbe384fd0c4189667e9e23ccde985bc6395be38b27d7d00588cfc8ccfc063b7ccafcf8e715bece847c0f16ec63cc71e72bef87b3dc73a97bdcccab7cd21a799bed3e2832efa6e8f791b7a2e59be3356bc919dbc5475f4112468b323316647fd11cdee44cadd9917e8df75e91a7b8ab71ffda0123d927f8cd1f5b3aa3e041b090981a5fcf2a0172a43b4390e64ea0de43daa7e2c5530ed2e9d6507e24bc35f1b98ab6c6bc4ba4bb5d5eb57f55a8f554ebd8378c495b169d3efc87aec2eebb95649ac72a7577a58697365b3a50a6819aa79a4939365de3c5f1b376cbbcdab80c7902ccfe7e19abf7072b6dcbc957385077d5b9a586476cdde5b6f992c492f59ca6b7402060054758bf149840d800f117949b143b3334043fbc0a4dcffe59b1af4481a74582937d02c5cac657b643a2ccf5ad7b36d0934632560fa9c5f5bfe6929978ed1103a57d9d68865417dd48ec6e11e0b8ba9175e878ec52d60b7e7d9cfb5d263958ee4608b55d7c1ae5e36bca7f3763bf79b2c3a0b9514b38cb9ef392f3dc140df962616bd5c4bd01e519f5eb294d7ff027ed62d9a32dab1c6f31eb8dc4c4300000fb349444154cdf565dbae2069625ae5ee713dabbe1291c59500a9cb117ca9ea21a1267125eb91fce4157e01daad4bdc90c450d5bf233f22e48d416654f52822afe83fab6fb9a9c1a70ac04caeb2ad148b3db3d8b01dfa77d01722b2bab43b3c139620b2246a8e55a64eb65964bcef491002cdb8fb3e6b057bcf988bb8849a6551d6f7cc14bd90a56fcb9aaef9fddaf3ef407dba4b4e5ec112302e90be4573a6706cd67d01e04544d6aa9ac22d2bad620ee80ecad638731cce1174399cd0e5f2a3285c8fc4e14a8a7dae6db3ee5e11e28b2501632a31352c0048a1389b367647b7c5a7c22009bbe87cb7e5add92e184fa93956719b7647f4cff750953d16f95a92155395fa5be743dfb35b740286248be5d97e429384fe454689e4506429af2047905a54f5a8aab7b07716ee6323221f099587f6254b2e255afab2fd49046fa754a0c7aa710b9577f805674b742c9245e4b1e745dd938b781cf9e8a3b6a083fcc4ba10ea4daeb8449e65b148bb362395c72a93243302569300b63187388264fadd86a35eb55595913430f51e72b62ad53e565392a5bc421e41fa46559f45648f66877dec8f5d01781791dbb9773755f54b440eb8fe9b2e65ddadfd5f92cba297aac79a19987c69791491fd956348f7e89ec33bd457f248ecbc625c53d39d2198266563f5a1563bf4857ebf979cdfae914a63952ff4cfbf1089a490cf95c546a794fc3a225c728f102b96a37a70eff910911d9a06d8c96de84f4496f28a928001be9bd6de88c83d6ce7f7bb688f4bcc551a7a3af62e455fea03d33529fa9aeacd4e617aac1ad767e80de374f822223717e62d17220923226df5d206e19a1c064355f7226259505c63b6ea97d4654b7ee291a863054c465418ab4c353fad9f112a969d2a69d46b075c9c33e6c6adaca16f9b8d1dfa8f659fb24153bdb7437314bbb65e8d59ca2be811a44ba8eaabaafe4193451eb343b9718e756efa3266e746aaeb2c6a360f49217afc525519f1ca465f5778c3f844c9afa348c672eda4138d2522222b77d5aaa259903c21ed206a68a07b98fad9cc50b635103a09ccfe0f195248ac6261aa048c758ebf8b8876bdd054dff692c911b022a16f9b1f974c1e12d36cd03c879f89dbaea0e42aafe8099816557d761db7ef30bcef894f862b167d4afe365486a680a772c822902b488f55e176324239d14711394d2cf6ceddd42bbd4a43445e007c60dcb19ea9197a4c6dd2ea974c654b1a784cad1218ab640d13303340df96140f18be71b94453adfe2922b5e8323b794d96806951d59daade6098535cce94d5fb5e60ba8564d7b84f17b95dd52f47645401734ea67aac1277f4c812486e619f932f27bb547d09182e7a2642441622f281a6274f560c2cf73e4ed5c13e67d912522b8c5508e986be2d3ddc51d9b147209700de44e4bdf4aab21ce5357902a6e5c429fa36b84a219bd7b5483d4dba74551cec4ba80ac85c8fb5b081ed8efb573459640ba7499dbeca1a266026c0398c77d4552e3c890dad54b68414036315427e43df962eee68f52dc6c7396b009f29dd001483dce4355b02a645559f71e56eee2bac13c8e4755d99ba38515a5705ccf94eccdcbf691499eab1162cbb1a3b77a5e717ec016a7b14a96b9e034cc04c45c8636673e1bb03b79ca864b404d912523d8c5508f9017d5bc2b8a4c20dc69f9858a0e97752b4ae7392d7ec0918e05b603ebb127d0bbed0fc3862e11afe7465d8d686fe2fd91e3fba46067aac0e370f2dfd85bee7a30b50ad4913cbb59f4cc044c6e39859b2b852ff21bdb0a2964d97205b42c83f18ab1042df960baafaa5aab7688ed88c89a717688ed8149d50ce455e49246000ef455f0a0d6bbb12282bf4f47f99fbfef15864a8c7d2b1666fcf75663d4be995dc21d1f009a276006e4f6ff8827f597e0c8656b2ac23efea94205bd2409f430030562104f46d59e18e51fec5b81bde96686eb62a9ed4e5f5bf217fe48e1d58025edfeb41ad7779a790bd3be0fa82a16fb7e4924c2677f0d463155865fcc338a9ea41449e317e77e478fed9240ad6e4c5d62d3c92c27894ad8b7bd8fb17f992b56c2b22b49db1d84edab60960ac7211cb98a6ec33f8d71d6126f940df96214e17cfeef8f5902364f722b22da10fa98554e53528018366f0968c90cfad2a80dd594ced0c2f2547ba7ed702dd862d95ea97daf4582326195f312ccf68e6f198e46011cda653c670dcb1659f701035b68f4b140759886cc90922b2342e14535be0d60c6395df4c353f7daa845249c058c6517555137d5bfea8ea0ec06e6062e11efeb74e664d6af21a9a8089e5b4b209665c85c011c31cf324d7a61aa85e8f1530387054d5a3886c01bc8df87e1e3f8a8fd589a462777ee0cea187e8e31223a0c85ab695615dfc596da2658196ca82b37418abfc66aaf959ed312dd7fba1d737659aa0a06f2b8493c4c23d9abe8c168a7b5eada422afd80998d215bc83ffc2e190504500f5583ea6e0e9daaeb0aaee44e415c316c84774df1846c2605d74a45279774ea85b8c62246072976d4d58178a2bf4e8cb2dbc2c7e2f155f5e3a8c557e33c9fc54d52f11b1bc3525d98f8a7b4eb0f47fd823cf4a02fab6c250d557113900f830bc3da5e77516e696d7d026bcd65d6ddf33fd5683904ad03364773fa58a00ea91b474ed866c314c57bb84928d25633d6696ea6ebda50783a5d9dfd2ed68842477d95683e176c2164b2065f57929f9f39261ac728247d3f150e3b62cc253ba29ca9a34e8d37fc94958fab6041111ed7b75fdbdf3839684601109989ce5352801e3165516a3b370cdd3ac4ced54c63224f84a269b4c3d5681d5795ed5af9b2743badde7b82b942329f62730e1122696f1bfc2564d15aa9aa6255bd9568ac5bf5a9274167fc706e313c158e5175327082d9fb372c749bd1091f7217fd7854b1a5874d627c7928f21d2b7658a21019beb9c8c42aaf21a730db5f55ca0e9fa2657f29bd5ae930b0a7c132a498cfd84eaf55838d6f979df1504a9ea2bfcf4f5cc9d93c9b0965bc7bcaa792896c5705b496549c0ac3d17607de42c5b0ba505e1161bb5e8aa94723ecc92c86383f169a92656312424ac89e6503ed81a47785dd72a22ef687460edc3e08345677dfab7266273a474df962b21aacd526d201f23dec8565e6312305687b412118b717d815108ae6428157c1c734afd5f5aa8c782714910ab9cafead7a3637ecbbd0b70493a5c74424eb763af1bf7c6e36ad93df0dd38cd623f4357c158484ab60e4b805d5a706ded39f5d4b1c8b5fa306e204c4b4db14a972fb6dede1132dedcc3687bddf83a119195887ce09fdd5c47383e6a4ac0b81b517ee1febf250153ba1d48d1b7958c653ef5c5d7966729f406e95cf146aef21a9e8051d53dec86e75e443e45e4f15c0822b27159706bd09c5a534f1fc79cdad8a9c73ab0ca7aedca81bf8da488ac5d30fb013fe3b9409c5d2df21bebf3fb741ee4ba60f903c6e45ae052718bd33baf7cb1ec827756737992ab6c01633f94f3c56ace895397703655c100783fd5995b145a7d181b8c4f4c65b1ca5a443e4e930322b2109127d8ab4c828ddba30211686ce1fbb93d041a9b28226fb81c4ffcd2d548ac09fbb7f3a491fb6fcbed8f878c371273f66d2563d1cb12c0c78579bb76b6cd22efd0f376ae7823577901aa3af8852633aa13bfd663c67c36fea5f13b3f3b3e63e131f655c7e7bc183fe33ed4efa71eeb7879c827c62bf87c4de98526896091c34be471fc37913e9713cfc997b3bf5b19ffeeb156d99e8cdbea5382cf550ffd06d3d3c9774fe1cf828e1bc0bbe13bdf0d9f33897ee77a4da4dbf357c858e571c27187b62753c4114f81c73cd4064e6a073c641bdaee64e5dbe690d34cdff939814eaeae47277ed642c41bd9c94b55471d4182363b125336dadcb9ef4c06b5ef0c247be4867a2c1b6d7685ade7e743d355ea4fc231d52e6d285d0eda7d7636d46247439646e726db962a7b3039df12536747cc674fab86b18a99bd06eec1e63e2fb6ec1f03c70bcf88d7eb62ceb82a14b9fab6d289fd9ced23ac47e78c377294d7b8040c00a8ea16d3dcec7304f030c1f70cc1f2fb9376e2d463f16c318f815cc0b3311f19c4548b92d125e2aee4d49220f9bab2f8b1048d9d8d563dc946b667e4be3818c316f1165e0f9a5e2fb76a60ac62228acd9a48f6c1fa44444e1a6d0bb003b9fab6a2d1e6d28b98c9b121b79af6315bbc91a9bcc627601cb7886f946f13367696e44a92d52f67d4aec7627132bf9be9eb4d8df9c8705ca019c5499c112238dec07ef5f425ac8e3648022633d97ee39ef92a93304e6731ecddb336cda0c9bc3056b9ce6be4aa9d3bc4dbccd9867ebe54f519e1176745d8815c7d5b253c20ce73b68d51cd9140bc9195bc80400918553daaea0de264a08e681c61b2090c37b63e479d74050c403d968e93fd6dc08f3cc26ef042971693335ca039d4ce586c1810a694d89a8cbbf85bd4de687515ea4aea8c647b4ecc12fca4718bd09049985757014066a6825865e8ef8abea076f6f716e1173b0fcece064755ef102e062fca0e64ecdb8ac62534423f67db58cf9863b67823477985aa8001f06de44266c7f7006e323983db35c664fbbf5ca2723d168dd3c10dc6eb7607e02fec0b1cde8a3401aa7a0bff60aa0da82d7fb719d3b5de25444c1de77b6ce6a4553040fab2bd845b2ce57a8c62346e973a4450b655d56ae5982a05c72a0ff0aff03960a2aa1d67574225c00e68641e75f7dcd9efb1dff15ca21dc8d1b7d540e0e7ec2e72f265f678233779054dc0004dc0a3aa7f31cc81b4ecd1fcf8dbd08dc422d2f55bb32b03af588fc5a3aa07a7db21bb387b3441de9ddb853c787cce9a4791e2e38229ab136c171c47d89f736b03dd4b58f5dfe740ad578c6e4eaf551f4be2b2bd48c0244496a8ea7e84bddb01f81b3b1023c32931561950e1f3aaaa37538edd8df10ef645f8390734552f37536d50bae4c990f1b6c9ad622a5fcec9d1b7d5c0c973768761f6ed19c09fa98ecccd1d6fe4242fd1e60aa7785fd0643ddb5dc8475c3efb7fc4bf6650af999ebb2d1aeab15c5cb3d2b631ea25bdb641c7689d8ac882f3623a5cc26b85dfc1cf339a2a93eccfb1cf458eb275cffa0a972b835ee16ef628f9193db177f7b85c8df58ca66a9549970c4939567136a3b729bdaacac9dfacd05cbf7dfe770734099a5d0a49a333b95ffb8ded1185d9c7ec8e446fd0d8804bf6b0956f941b50522647df560b27f6e0927e807fb7731d635795f59142bc91b2bca22760082184104208a999210918420821e511fc081221841042082184104208f9091330841042082184104208219161028610420821841042082124324cc0104208218410420821844486091842082184104208218490c8300143082184104208218410121926600821841042082184104222c3040c2184104208218410424864988021841042082184104208890c1330841042082184104208219161028610420821841042082124324cc0104208218410420821844486091842082184104208218490c888aace3d0642082184104208218490a261050c2184104208218410424864988021841042082184104208890c133084104208218410420821916102861042082184104208212432ff07f319e97421ccb9c00000000049454e44ae426082	image/png	\N	\N	\N	\N	#0f172a	#ffffff	#334155	t	t	t	t	t	t	t	t
\.


--
-- Data for Name: company_contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_contacts (id, company_id, first_name, last_name, email, phone, "position", contact_type, is_primary, effective_from, effective_to, is_active, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: company_email_configs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_email_configs (id, company_id, provider, is_enabled, smtp_host, smtp_port, smtp_username, smtp_password, smtp_use_tls, smtp_use_ssl, sender_email, sender_name, reply_to_email, oauth_access_token, oauth_refresh_token, oauth_token_expires_at, last_test_at, last_test_success, last_error, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: company_service_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_service_settings (id, company_id, service_id, is_active, custom_name, custom_description, custom_price, display_order, is_featured, created_at, updated_at, cost_percentage) FROM stdin;
\.


--
-- Data for Name: company_storage_configs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_storage_configs (id, company_id, provider, is_enabled, sharepoint_site_id, sharepoint_drive_id, sharepoint_root_folder, zoho_client_id, zoho_client_secret, zoho_access_token, zoho_refresh_token, zoho_token_expires_at, zoho_root_folder_id, zoho_org_id, azure_connection_string, azure_container_name, last_sync_at, last_error, created_at, updated_at, google_client_id, google_client_secret, google_access_token, google_refresh_token, google_token_expires_at, google_root_folder_id) FROM stdin;
\.


--
-- Data for Name: currencies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.currencies (id, code, name, symbol, is_active, created_at) FROM stdin;
1	AUD	Australian Dollar	$	t	2026-01-20 09:36:36.450576
2	USD	US Dollar	$	t	2026-01-20 09:36:36.450576
3	GBP	British Pound	£	t	2026-01-20 09:36:36.450576
4	EUR	Euro	€	t	2026-01-20 09:36:36.450576
5	AED	UAE Dirham	د.إ	t	2026-01-20 09:36:36.450576
6	SAR	Saudi Riyal	﷼	t	2026-01-20 09:36:36.450576
7	QAR	Qatari Riyal	﷼	t	2026-01-20 09:36:36.450576
8	KWD	Kuwaiti Dinar	د.ك	t	2026-01-20 09:36:36.450576
9	BHD	Bahraini Dinar	.د.ب	t	2026-01-20 09:36:36.450576
10	OMR	Omani Rial	﷼	t	2026-01-20 09:36:36.450576
11	INR	Indian Rupee	₹	t	2026-01-20 09:36:36.450576
12	PKR	Pakistani Rupee	₨	t	2026-01-20 09:36:36.450576
13	NZD	New Zealand Dollar	$	t	2026-01-20 09:36:36.450576
14	CAD	Canadian Dollar	$	t	2026-01-20 09:36:36.450576
15	SGD	Singapore Dollar	$	t	2026-01-20 09:36:36.450576
16	MYR	Malaysian Ringgit	RM	t	2026-01-20 09:36:36.450576
17	ZAR	South African Rand	R	t	2026-01-20 09:36:36.450576
18	CHF	Swiss Franc	CHF	t	2026-01-20 09:36:36.450576
19	JPY	Japanese Yen	¥	t	2026-01-20 09:36:36.450576
20	CNY	Chinese Yuan	¥	t	2026-01-20 09:36:36.450576
21	HKD	Hong Kong Dollar	HK$	t	2026-01-20 09:36:36.450576
\.


--
-- Data for Name: db_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.db_version (id, version, applied_at) FROM stdin;
1	4	2026-01-26 13:31:27.947603
\.


--
-- Data for Name: documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.documents (id, original_filename, stored_filename, file_type, file_size, mime_type, blob_name, blob_url, storage_type, uploaded_by_id, service_request_id, document_category, description, is_active, created_at, updated_at, storage_path, storage_url, external_item_id, external_web_url, company_id) FROM stdin;
\.


--
-- Data for Name: email_automation_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.email_automation_logs (id, automation_id, recipient_user_id, recipient_email, trigger_data, status, error_message, sent_at, created_at) FROM stdin;
\.


--
-- Data for Name: email_automations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.email_automations (id, company_id, name, description, trigger_type, trigger_config, template_id, custom_subject, custom_body, delay_minutes, conditions, is_active, last_triggered_at, trigger_count, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: email_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.email_templates (id, name, slug, subject, body_html, variables, company_id, is_active, created_at, updated_at, service_id, template_type, service_category) FROM stdin;
1	Welcome Email	welcome	Welcome to {company_name}!	<p>Dear {client_name},</p>\n\n<p>Welcome to {company_name}! We're excited to have you as our client.</p>\n\n<p>Your account has been created and you can now access our client portal to:</p>\n<ul>\n    <li>Request services</li>\n    <li>Upload documents securely</li>\n    <li>Track the progress of your requests</li>\n    <li>Communicate with your accountant</li>\n</ul>\n\n<p><strong>Login Details:</strong><br>\nEmail: {client_email}<br>\nPortal: {portal_link}</p>\n\n<p>If you have any questions, please don't hesitate to reach out.</p>\n\n<p>Best regards,<br>\n{company_name}</p>	["client_name", "client_email", "company_name", "portal_link"]	\N	t	2026-01-18 13:43:01.228575	2026-01-18 13:43:01.228577	\N	\N	\N
2	Invoice Email	invoice	Invoice #{invoice_number} from {company_name}	<p>Dear {client_name},</p>\n\n<p>Please find attached your invoice for {service_name}.</p>\n\n<p><strong>Invoice Details:</strong><br>\nInvoice Number: {invoice_number}<br>\nAmount Due: {amount}<br>\nDue Date: {due_date}</p>\n\n<p><strong>Payment Terms:</strong><br>\n{payment_terms}</p>\n\n<p><strong>Bank Details:</strong><br>\n{bank_details}</p>\n\n<p>You can also pay online using this link: <a href="{payment_link}">Pay Now</a></p>\n\n<p>{invoice_notes}</p>\n\n<p>{invoice_footer}</p>\n\n<p>Best regards,<br>\n{company_name}</p>	["client_name", "service_name", "invoice_number", "amount", "due_date", "payment_terms", "bank_details", "payment_link", "invoice_notes", "invoice_footer", "company_name"]	\N	t	2026-01-18 13:43:01.233494	2026-01-18 13:43:01.233496	\N	\N	\N
3	Payment Reminder	payment_reminder	Payment Reminder - Invoice #{invoice_number}	<p>Dear {client_name},</p>\n\n<p>This is a friendly reminder that payment for Invoice #{invoice_number} is due.</p>\n\n<p><strong>Invoice Details:</strong><br>\nService: {service_name}<br>\nAmount Due: {amount}<br>\nDue Date: {due_date}</p>\n\n<p>If you have already made the payment, please disregard this email.</p>\n\n<p>To make a payment, please use one of the following methods:</p>\n\n<p><strong>Online Payment:</strong><br>\n<a href="{payment_link}">Click here to pay securely online</a></p>\n\n<p><strong>Bank Transfer:</strong><br>\n{bank_details}</p>\n\n<p>Please include your invoice number as the payment reference.</p>\n\n<p>If you have any questions about this invoice, please contact us.</p>\n\n<p>Best regards,<br>\n{company_name}</p>	["client_name", "invoice_number", "service_name", "amount", "due_date", "payment_link", "bank_details", "company_name"]	\N	t	2026-01-18 13:43:01.234884	2026-01-18 13:43:01.234886	\N	\N	\N
4	Document Request	document_request	Documents Required for {service_name}	<p>Dear {client_name},</p>\n\n<p>To proceed with your {service_name}, we require the following documents:</p>\n\n<p>{document_list}</p>\n\n<p>Please upload these documents through our secure portal: <a href="{portal_link}">Upload Documents</a></p>\n\n<p>If you have any questions about what's required, please don't hesitate to ask.</p>\n\n<p>Best regards,<br>\n{accountant_name}<br>\n{company_name}</p>	["client_name", "service_name", "document_list", "portal_link", "accountant_name", "company_name"]	\N	t	2026-01-18 13:43:01.236022	2026-01-18 13:43:01.236023	\N	\N	\N
5	Service Completed	service_completed	Your {service_name} is Complete	<p>Dear {client_name},</p>\n\n<p>Great news! Your {service_name} has been completed.</p>\n\n<p>{completion_notes}</p>\n\n<p>You can view the details and download any relevant documents from your client portal: <a href="{portal_link}">View Details</a></p>\n\n<p>If you have any questions, please don't hesitate to reach out.</p>\n\n<p>Thank you for choosing {company_name}.</p>\n\n<p>Best regards,<br>\n{accountant_name}<br>\n{company_name}</p>	["client_name", "service_name", "completion_notes", "portal_link", "accountant_name", "company_name"]	\N	t	2026-01-18 13:43:01.236922	2026-01-18 13:43:01.236923	\N	\N	\N
6	Query Response Required	query_raised	Response Required - {service_name}	<p>Dear {client_name},</p>\n\n<p>We have a question regarding your {service_name} and need your response to proceed.</p>\n\n<p><strong>Query:</strong><br>\n{query_message}</p>\n\n<p>Please log in to your portal to respond: <a href="{portal_link}">Respond Now</a></p>\n\n<p>Best regards,<br>\n{accountant_name}<br>\n{company_name}</p>	["client_name", "service_name", "query_message", "portal_link", "accountant_name", "company_name"]	\N	t	2026-01-18 13:43:01.237916	2026-01-18 13:43:01.237917	\N	\N	\N
7	Annual Tax Reminder	annual_reminder	It's Time to Lodge Your Tax Return - {tax_year}	<p>Dear {client_name},</p>\n\n<p>It's that time of year again! The {tax_year} financial year has ended and it's time to prepare your tax return.</p>\n\n<p><strong>Key Dates:</strong><br>\n- Tax returns for individuals are due by 31 October {due_year}<br>\n- If you're registered with a tax agent (that's us!), you may have an extended deadline</p>\n\n<p><strong>What you need to gather:</strong></p>\n<ul>\n    <li>Income statements from all employers</li>\n    <li>Bank interest statements</li>\n    <li>Dividend statements</li>\n    <li>Private health insurance statement</li>\n    <li>Receipts for work-related expenses</li>\n    <li>Investment property documents (if applicable)</li>\n</ul>\n\n<p>Ready to get started? <a href="{portal_link}">Request your tax return now</a></p>\n\n<p>Best regards,<br>\n{company_name}</p>	["client_name", "tax_year", "due_year", "portal_link", "company_name"]	\N	t	2026-01-18 13:43:01.238951	2026-01-18 13:43:01.238953	\N	\N	\N
8	Password Reset	password_reset	Password Reset Request - {company_name}	<p>Dear {client_name},</p>\n\n<p>We received a request to reset your password for your {company_name} account.</p>\n\n<p>Click the link below to reset your password:</p>\n\n<p><a href="{reset_link}">Reset My Password</a></p>\n\n<p>This link will expire in 24 hours.</p>\n\n<p>If you didn't request a password reset, please ignore this email or contact us if you have concerns.</p>\n\n<p>Best regards,<br>\n{company_name}</p>	["client_name", "reset_link", "company_name"]	\N	t	2026-01-18 13:43:01.239821	2026-01-18 13:43:01.239823	\N	\N	\N
9	Welcome Email	welcome	Welcome to {company_name}!	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #1a365d;">Welcome to {company_name}!</h2>\n<p>Dear {client_name},</p>\n<p>Thank you for choosing {company_name} for your accounting needs. We're excited to have you on board!</p>\n<p>Your account has been created and you can now access our client portal:</p>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Access Your Portal</a>\n</p>\n<p>If you have any questions, please don't hesitate to contact us.</p>\n<p>Best regards,<br>{company_name} Team</p>\n</div>	["client_name", "company_name", "portal_link"]	\N	\N	\N	\N	\N	welcome	\N
17	BAS - Lodged	bas_lodged	Your {period} BAS Has Been Lodged	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #10B981;">BAS Lodged Successfully!</h2>\n<p>Dear {client_name},</p>\n<p>Your <strong>{period} Business Activity Statement</strong> has been lodged with the ATO.</p>\n<div style="background-color: #D1FAE5; padding: 20px; border-radius: 5px; margin: 20px 0;">\n<table style="width: 100%;">\n<tr><td><strong>Period:</strong></td><td>{period}</td></tr>\n<tr><td><strong>GST Collected:</strong></td><td>{gst_collected}</td></tr>\n<tr><td><strong>GST Paid:</strong></td><td>{gst_paid}</td></tr>\n<tr><td><strong>Net Amount:</strong></td><td><strong>{net_amount}</strong></td></tr>\n</table>\n</div>\n<p>{payment_instructions}</p>\n<p>Best regards,<br>{accountant_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "period", "gst_collected", "gst_paid", "net_amount", "payment_instructions", "accountant_name"]	\N	\N	\N	\N	\N	completion	bas_agent
10	Invoice Email	invoice_sent	Invoice #{invoice_number} from {company_name}	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #1a365d;">Invoice #{invoice_number}</h2>\n<p>Dear {client_name},</p>\n<p>Please find attached your invoice for <strong>{service_name}</strong>.</p>\n<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">\n<tr style="background-color: #f7fafc;">\n<td style="padding: 10px; border: 1px solid #e2e8f0;">Service</td>\n<td style="padding: 10px; border: 1px solid #e2e8f0;">{service_name}</td>\n</tr>\n<tr>\n<td style="padding: 10px; border: 1px solid #e2e8f0;">Amount</td>\n<td style="padding: 10px; border: 1px solid #e2e8f0;"><strong>{amount}</strong></td>\n</tr>\n<tr style="background-color: #f7fafc;">\n<td style="padding: 10px; border: 1px solid #e2e8f0;">Due Date</td>\n<td style="padding: 10px; border: 1px solid #e2e8f0;">{due_date}</td>\n</tr>\n</table>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{payment_link}" style="background-color: #10B981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Pay Now</a>\n</p>\n<p>{payment_terms}</p>\n<p>Best regards,<br>{company_name}</p>\n</div>	["client_name", "company_name", "invoice_number", "service_name", "amount", "due_date", "payment_link", "payment_terms"]	\N	\N	\N	\N	\N	invoice	\N
11	Payment Reminder	payment_reminder	Reminder: Invoice #{invoice_number} is Due	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #D97706;">Payment Reminder</h2>\n<p>Dear {client_name},</p>\n<p>This is a friendly reminder that Invoice <strong>#{invoice_number}</strong> for <strong>{service_name}</strong> is due on <strong>{due_date}</strong>.</p>\n<p><strong>Amount Due: {amount}</strong></p>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{payment_link}" style="background-color: #D97706; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Pay Now</a>\n</p>\n<p>If you've already made this payment, please disregard this reminder.</p>\n<p>Best regards,<br>{company_name}</p>\n</div>	["client_name", "company_name", "invoice_number", "service_name", "amount", "due_date", "payment_link"]	\N	\N	\N	\N	\N	payment	\N
12	Query Raised	query_raised	Query Regarding Your {service_name}	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #F59E0B;">We Need Some Information</h2>\n<p>Dear {client_name},</p>\n<p>While processing your <strong>{service_name}</strong>, we need some additional information:</p>\n<div style="background-color: #FEF3C7; padding: 15px; border-radius: 5px; margin: 20px 0;">\n<p style="margin: 0;">{query_message}</p>\n</div>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Respond in Portal</a>\n</p>\n<p>Please respond at your earliest convenience so we can continue processing your request.</p>\n<p>Best regards,<br>{accountant_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "service_name", "query_message", "portal_link", "accountant_name"]	\N	\N	\N	\N	\N	query	\N
13	Document Request	document_request	Documents Required for Your {service_name}	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #7C3AED;">Documents Required</h2>\n<p>Dear {client_name},</p>\n<p>To proceed with your <strong>{service_name}</strong>, we require the following documents:</p>\n<div style="background-color: #F3F4F6; padding: 15px; border-radius: 5px; margin: 20px 0;">\n{document_list}\n</div>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #7C3AED; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Upload Documents</a>\n</p>\n<p>Please upload these documents through our secure portal.</p>\n<p>Best regards,<br>{accountant_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "service_name", "document_list", "portal_link", "accountant_name"]	\N	\N	\N	\N	\N	documents	\N
14	Tax Return - Renewal Reminder	tax_renewal_reminder	Time to Lodge Your {tax_year} Tax Return	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #1a365d;">Your {tax_year} Tax Return is Due Soon</h2>\n<p>Dear {client_name},</p>\n<p>This is a friendly reminder that your <strong>{service_name}</strong> for the {tax_year} financial year is due by <strong>{due_date}</strong>.</p>\n<div style="background-color: #EBF8FF; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #3182CE;">\n<p style="margin: 0; font-size: 18px;"><strong>Due Date: {due_date}</strong></p>\n<p style="margin: 10px 0 0 0;">Days Remaining: {days_remaining}</p>\n</div>\n<p>To get started, please:</p>\n<ol>\n<li>Gather your income statements (payment summaries)</li>\n<li>Collect receipts for work-related expenses</li>\n<li>Upload your documents to our portal</li>\n</ol>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Start Your Tax Return</a>\n</p>\n<p>Need help? Reply to this email or call us.</p>\n<p>Best regards,<br>{company_name} Team</p>\n</div>	["client_name", "company_name", "service_name", "tax_year", "due_date", "days_remaining", "portal_link"]	\N	\N	\N	\N	\N	renewal	tax_agent
15	Tax Return - Lodged	tax_lodged	Your {tax_year} Tax Return Has Been Lodged!	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #10B981;">Tax Return Lodged Successfully!</h2>\n<p>Dear {client_name},</p>\n<p>Great news! Your <strong>{service_name}</strong> for the {tax_year} financial year has been successfully lodged with the ATO.</p>\n<div style="background-color: #D1FAE5; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #10B981;">\n<p style="margin: 0;"><strong>Lodgement Reference:</strong> {lodgement_reference}</p>\n<p style="margin: 10px 0 0 0;"><strong>Lodgement Date:</strong> {lodgement_date}</p>\n</div>\n<p>{completion_notes}</p>\n<p>The ATO will process your return and issue any refund directly to your nominated bank account, usually within 2-4 weeks.</p>\n<p>Best regards,<br>{accountant_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "service_name", "tax_year", "lodgement_reference", "lodgement_date", "completion_notes", "accountant_name"]	\N	\N	\N	\N	\N	completion	tax_agent
16	BAS - Renewal Reminder	bas_renewal_reminder	Your {period} BAS is Due Soon	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #1a365d;">BAS Lodgement Reminder</h2>\n<p>Dear {client_name},</p>\n<p>This is a reminder that your <strong>{period} Business Activity Statement (BAS)</strong> is due by <strong>{due_date}</strong>.</p>\n<div style="background-color: #FEF3C7; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #F59E0B;">\n<p style="margin: 0; font-size: 18px;"><strong>Due Date: {due_date}</strong></p>\n<p style="margin: 10px 0 0 0;">Days Remaining: {days_remaining}</p>\n</div>\n<p>Please ensure your accounting records are up to date so we can prepare your BAS.</p>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Upload Documents</a>\n</p>\n<p>Best regards,<br>{company_name} Team</p>\n</div>	["client_name", "company_name", "period", "due_date", "days_remaining", "portal_link"]	\N	\N	\N	\N	\N	renewal	bas_agent
18	SMSF Audit - Renewal Reminder	smsf_renewal_reminder	Your SMSF Audit for {financial_year} is Due	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #1a365d;">SMSF Audit Reminder</h2>\n<p>Dear {client_name},</p>\n<p>This is a reminder that your <strong>SMSF Audit</strong> for the {financial_year} financial year is due by <strong>{due_date}</strong>.</p>\n<div style="background-color: #E0E7FF; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #4F46E5;">\n<p style="margin: 0;"><strong>Fund Name:</strong> {fund_name}</p>\n<p style="margin: 10px 0 0 0;"><strong>Due Date:</strong> {due_date}</p>\n</div>\n<p>To proceed with the audit, please ensure the following are ready:</p>\n<ul>\n<li>Financial statements for the year</li>\n<li>Bank statements for all accounts</li>\n<li>Investment records and valuations</li>\n<li>Member contribution records</li>\n<li>Trustee meeting minutes</li>\n</ul>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Upload Audit Documents</a>\n</p>\n<p>Best regards,<br>{company_name} Team</p>\n</div>	["client_name", "company_name", "financial_year", "fund_name", "due_date", "portal_link"]	\N	\N	\N	\N	\N	renewal	auditor
19	SMSF Audit - Complete	smsf_audit_complete	Your SMSF Audit is Complete	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #10B981;">SMSF Audit Complete!</h2>\n<p>Dear {client_name},</p>\n<p>We are pleased to advise that the audit of <strong>{fund_name}</strong> for the {financial_year} financial year has been completed.</p>\n<div style="background-color: #D1FAE5; padding: 20px; border-radius: 5px; margin: 20px 0;">\n<p style="margin: 0;"><strong>Audit Opinion:</strong> {audit_opinion}</p>\n<p style="margin: 10px 0 0 0;"><strong>Completion Date:</strong> {completion_date}</p>\n</div>\n<p>The signed audit report has been uploaded to your portal. Please ensure this is provided to your SMSF accountant for lodgement of the annual return.</p>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">View Audit Report</a>\n</p>\n<p>Best regards,<br>{auditor_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "fund_name", "financial_year", "audit_opinion", "completion_date", "portal_link", "auditor_name"]	\N	\N	\N	\N	\N	completion	auditor
20	Bookkeeping - Monthly Reminder	bookkeeping_monthly_reminder	Monthly Bookkeeping for {month} is Due	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #1a365d;">Monthly Bookkeeping Reminder</h2>\n<p>Dear {client_name},</p>\n<p>This is a reminder that your <strong>monthly bookkeeping</strong> for <strong>{month}</strong> needs to be processed.</p>\n<p>Please ensure the following are uploaded to your portal:</p>\n<ul>\n<li>Bank statements for all accounts</li>\n<li>Credit card statements</li>\n<li>Sales invoices issued</li>\n<li>Expense receipts and bills</li>\n<li>Payroll information (if applicable)</li>\n</ul>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Upload Documents</a>\n</p>\n<p>Best regards,<br>{company_name} Team</p>\n</div>	["client_name", "company_name", "month", "portal_link"]	\N	\N	\N	\N	\N	renewal	bookkeeper
21	Bookkeeping - Monthly Report Ready	bookkeeping_report_ready	Your {month} Financial Reports are Ready	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #10B981;">Monthly Reports Ready!</h2>\n<p>Dear {client_name},</p>\n<p>Your financial reports for <strong>{month}</strong> are now ready for review.</p>\n<div style="background-color: #F3F4F6; padding: 20px; border-radius: 5px; margin: 20px 0;">\n<p style="margin: 0;"><strong>Reports Included:</strong></p>\n<ul style="margin: 10px 0 0 0;">\n<li>Profit & Loss Statement</li>\n<li>Balance Sheet</li>\n<li>Bank Reconciliation</li>\n<li>Accounts Receivable Aging</li>\n<li>Accounts Payable Aging</li>\n</ul>\n</div>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">View Reports</a>\n</p>\n<p>{notes}</p>\n<p>Best regards,<br>{bookkeeper_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "month", "portal_link", "notes", "bookkeeper_name"]	\N	\N	\N	\N	\N	completion	bookkeeper
22	Financial Plan - Annual Review Reminder	fp_annual_review_reminder	Time for Your Annual Financial Review	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #1a365d;">Annual Financial Review Due</h2>\n<p>Dear {client_name},</p>\n<p>It's been a year since your last financial review, and it's time to ensure your financial plan is still on track.</p>\n<div style="background-color: #E0E7FF; padding: 20px; border-radius: 5px; margin: 20px 0;">\n<p style="margin: 0;"><strong>Why Review?</strong></p>\n<ul style="margin: 10px 0 0 0;">\n<li>Life circumstances may have changed</li>\n<li>Investment markets have moved</li>\n<li>Tax laws may have updated</li>\n<li>Your goals may have evolved</li>\n</ul>\n</div>\n<p>We recommend scheduling a review meeting to discuss your current situation and any adjustments needed.</p>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{booking_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Book Your Review</a>\n</p>\n<p>Best regards,<br>{planner_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "booking_link", "planner_name"]	\N	\N	\N	\N	\N	renewal	financial_planner
23	Financial Plan - SOA Ready	fp_soa_ready	Your Statement of Advice is Ready	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #10B981;">Your Statement of Advice is Ready!</h2>\n<p>Dear {client_name},</p>\n<p>We have prepared your <strong>Statement of Advice (SOA)</strong> based on our recent discussions.</p>\n<div style="background-color: #D1FAE5; padding: 20px; border-radius: 5px; margin: 20px 0;">\n<p style="margin: 0;"><strong>Document:</strong> Statement of Advice</p>\n<p style="margin: 10px 0 0 0;"><strong>Prepared By:</strong> {planner_name}</p>\n<p style="margin: 10px 0 0 0;"><strong>Date:</strong> {soa_date}</p>\n</div>\n<p>Please review the document carefully. We recommend scheduling a follow-up meeting to discuss the recommendations and answer any questions.</p>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">View Your SOA</a>\n</p>\n<p>Best regards,<br>{planner_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "planner_name", "soa_date", "portal_link"]	\N	\N	\N	\N	\N	completion	financial_planner
24	Mortgage - Application Update	mortgage_application_update	Update on Your Loan Application	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #1a365d;">Loan Application Update</h2>\n<p>Dear {client_name},</p>\n<p>Here's an update on your loan application:</p>\n<div style="background-color: #F3F4F6; padding: 20px; border-radius: 5px; margin: 20px 0;">\n<table style="width: 100%;">\n<tr><td><strong>Application ID:</strong></td><td>{application_id}</td></tr>\n<tr><td><strong>Lender:</strong></td><td>{lender_name}</td></tr>\n<tr><td><strong>Loan Amount:</strong></td><td>{loan_amount}</td></tr>\n<tr><td><strong>Status:</strong></td><td><strong>{status}</strong></td></tr>\n</table>\n</div>\n<p>{update_message}</p>\n<p>If you have any questions, please don't hesitate to contact me.</p>\n<p>Best regards,<br>{broker_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "application_id", "lender_name", "loan_amount", "status", "update_message", "broker_name"]	\N	\N	\N	\N	\N	status_update	mortgage_broker
25	Mortgage - Approval Notice	mortgage_approved	Congratulations! Your Loan is Approved!	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #10B981;">Your Loan is Approved!</h2>\n<p>Dear {client_name},</p>\n<p>Great news! Your loan application has been <strong>approved</strong>!</p>\n<div style="background-color: #D1FAE5; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #10B981;">\n<table style="width: 100%;">\n<tr><td><strong>Lender:</strong></td><td>{lender_name}</td></tr>\n<tr><td><strong>Loan Amount:</strong></td><td>{loan_amount}</td></tr>\n<tr><td><strong>Interest Rate:</strong></td><td>{interest_rate}</td></tr>\n<tr><td><strong>Loan Term:</strong></td><td>{loan_term}</td></tr>\n</table>\n</div>\n<p><strong>Next Steps:</strong></p>\n<ol>\n<li>Review and sign the loan documents</li>\n<li>Arrange building/pest inspection (if applicable)</li>\n<li>Confirm settlement date with your solicitor</li>\n</ol>\n<p>I'll be in touch with the loan documents shortly.</p>\n<p>Congratulations again!<br>{broker_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "lender_name", "loan_amount", "interest_rate", "loan_term", "broker_name"]	\N	\N	\N	\N	\N	completion	mortgage_broker
26	Mortgage - Settlement Complete	mortgage_settled	Congratulations on Your Settlement!	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #10B981;">Settlement Complete!</h2>\n<p>Dear {client_name},</p>\n<p>Congratulations! Your loan has officially settled!</p>\n<div style="background-color: #D1FAE5; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">\n<p style="font-size: 24px; margin: 0;">🎉 🏠 🎉</p>\n<p style="margin: 10px 0 0 0; font-size: 18px;"><strong>Settlement Date: {settlement_date}</strong></p>\n</div>\n<p>The keys to your new property are now yours. Here are some things to remember:</p>\n<ul>\n<li>Your first repayment will be due on {first_repayment_date}</li>\n<li>Set up automatic payments to avoid missing any repayments</li>\n<li>Keep all loan documents in a safe place</li>\n<li>Contact your lender if you need to make any changes</li>\n</ul>\n<p>It's been a pleasure helping you with your home loan journey. Please don't hesitate to reach out if you need any assistance in the future.</p>\n<p>Best wishes,<br>{broker_name}<br>{company_name}</p>\n</div>	["client_name", "company_name", "settlement_date", "first_repayment_date", "broker_name"]	\N	\N	\N	\N	\N	completion	mortgage_broker
27	Service Renewal Reminder	general_renewal_reminder	Reminder: {service_name} is Due Soon	<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">\n<h2 style="color: #1a365d;">Service Reminder</h2>\n<p>Dear {client_name},</p>\n<p>This is a friendly reminder that your <strong>{service_name}</strong> is due by <strong>{due_date}</strong>.</p>\n<div style="background-color: #EBF8FF; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #3182CE;">\n<p style="margin: 0; font-size: 18px;"><strong>Due Date: {due_date}</strong></p>\n<p style="margin: 10px 0 0 0;">Days Remaining: {days_remaining}</p>\n</div>\n<p>Please contact us to get started or login to your portal to submit a new request.</p>\n<p style="text-align: center; margin: 30px 0;">\n<a href="{portal_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Access Portal</a>\n</p>\n<p>Best regards,<br>{company_name} Team</p>\n</div>	["client_name", "company_name", "service_name", "due_date", "days_remaining", "portal_link"]	\N	\N	\N	\N	\N	renewal	\N
\.


--
-- Data for Name: form_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.form_questions (id, form_id, question_text, question_type, is_required, allow_attachment, options, validation_rules, placeholder, help_text, "order", created_at, section_number, section_title, section_description, is_section_repeatable, section_group, min_section_repeats, max_section_repeats, conditional_on_question_id, conditional_value) FROM stdin;
12	2	What is your ABN?	text	t	f	null	\N	XX XXX XXX XXX	\N	0	2026-01-18 05:05:44.472743	1	\N	\N	f	\N	1	10	\N	\N
13	2	What period is this BAS for?	select	t	f	["July-September (Q1)", "October-December (Q2)", "January-March (Q3)", "April-June (Q4)", "Monthly"]	\N	\N	\N	1	2026-01-18 05:05:44.472745	1	\N	\N	f	\N	1	10	\N	\N
14	2	Are you registered for GST?	radio	t	f	["Yes", "No"]	\N	\N	\N	2	2026-01-18 05:05:44.472746	1	\N	\N	f	\N	1	10	\N	\N
15	2	Total sales/income for the period (including GST)	number	t	f	null	\N	0.00	\N	3	2026-01-18 05:05:44.472746	1	\N	\N	f	\N	1	10	\N	\N
16	2	Total purchases/expenses for the period (including GST)	number	t	f	null	\N	0.00	\N	4	2026-01-18 05:05:44.472746	1	\N	\N	f	\N	1	10	\N	\N
17	2	Do you have PAYG withholding obligations?	radio	t	f	["Yes", "No"]	\N	\N	\N	5	2026-01-18 05:05:44.472747	1	\N	\N	f	\N	1	10	\N	\N
18	2	Total wages paid for the period	number	f	f	null	\N	0.00	\N	6	2026-01-18 05:05:44.472747	1	\N	\N	f	\N	1	10	\N	\N
19	2	Total PAYG withheld from wages	number	f	f	null	\N	0.00	\N	7	2026-01-18 05:05:44.472748	1	\N	\N	f	\N	1	10	\N	\N
20	2	Upload your sales report/invoices	file	f	f	null	\N	\N	\N	8	2026-01-18 05:05:44.472748	1	\N	\N	f	\N	1	10	\N	\N
21	2	Upload your purchase invoices/receipts	file	f	f	null	\N	\N	\N	9	2026-01-18 05:05:44.472749	1	\N	\N	f	\N	1	10	\N	\N
22	2	Any additional notes or information	textarea	f	f	null	\N	\N	\N	10	2026-01-18 05:05:44.472749	1	\N	\N	f	\N	1	10	\N	\N
23	3	Property address	textarea	t	f	null	\N	Full address of the rental property	\N	0	2026-01-18 05:05:44.478182	1	\N	\N	f	\N	1	10	\N	\N
24	3	When did you purchase this property?	date	t	f	null	\N	\N	\N	1	2026-01-18 05:05:44.478183	1	\N	\N	f	\N	1	10	\N	\N
25	3	What was the purchase price?	number	t	f	null	\N	0.00	\N	2	2026-01-18 05:05:44.478184	1	\N	\N	f	\N	1	10	\N	\N
26	3	How many weeks was the property rented this year?	number	t	f	null	\N	52	\N	3	2026-01-18 05:05:44.478184	1	\N	\N	f	\N	1	10	\N	\N
27	3	Total rental income received	number	t	f	null	\N	0.00	\N	4	2026-01-18 05:05:44.478185	1	\N	\N	f	\N	1	10	\N	\N
28	3	Is the property managed by an agent?	radio	t	f	["Yes - Full management", "Yes - Letting only", "No - Self managed"]	\N	\N	\N	5	2026-01-18 05:05:44.478185	1	\N	\N	f	\N	1	10	\N	\N
29	3	Property management fees paid	number	f	f	null	\N	0.00	\N	6	2026-01-18 05:05:44.478186	1	\N	\N	f	\N	1	10	\N	\N
30	3	Council rates paid	number	f	f	null	\N	0.00	\N	7	2026-01-18 05:05:44.478186	1	\N	\N	f	\N	1	10	\N	\N
31	3	Water rates paid	number	f	f	null	\N	0.00	\N	8	2026-01-18 05:05:44.478187	1	\N	\N	f	\N	1	10	\N	\N
32	3	Insurance premium paid	number	f	f	null	\N	0.00	\N	9	2026-01-18 05:05:44.478187	1	\N	\N	f	\N	1	10	\N	\N
33	3	Interest on loan paid	number	f	f	null	\N	0.00	\N	10	2026-01-18 05:05:44.478188	1	\N	\N	f	\N	1	10	\N	\N
34	3	Repairs and maintenance costs	number	f	f	null	\N	0.00	\N	11	2026-01-18 05:05:44.478188	1	\N	\N	f	\N	1	10	\N	\N
35	3	Upload rental income statement from agent	file	f	f	null	\N	\N	\N	12	2026-01-18 05:05:44.478188	1	\N	\N	f	\N	1	10	\N	\N
36	3	Upload depreciation schedule (if available)	file	f	f	null	\N	\N	\N	13	2026-01-18 05:05:44.478189	1	\N	\N	f	\N	1	10	\N	\N
37	3	Any capital improvements made this year?	textarea	f	f	null	\N	\N	List any renovations or improvements with costs	14	2026-01-18 05:05:44.478189	1	\N	\N	f	\N	1	10	\N	\N
38	4	Proposed fund name	text	t	f	null	\N	e.g., Smith Family Superannuation Fund	\N	0	2026-01-18 05:05:44.48178	1	\N	\N	f	\N	1	10	\N	\N
39	4	Trustee structure	radio	t	f	["Individual trustees", "Corporate trustee"]	\N	\N	Corporate trustee recommended for better asset protection	1	2026-01-18 05:05:44.481781	1	\N	\N	f	\N	1	10	\N	\N
40	4	Number of members	select	t	f	["1", "2", "3", "4"]	\N	\N	\N	2	2026-01-18 05:05:44.481782	1	\N	\N	f	\N	1	10	\N	\N
41	4	Member 1 - Full name	text	t	f	null	\N	\N	\N	3	2026-01-18 05:05:44.481783	1	\N	\N	f	\N	1	10	\N	\N
42	4	Member 1 - Date of birth	date	t	f	null	\N	\N	\N	4	2026-01-18 05:05:44.481783	1	\N	\N	f	\N	1	10	\N	\N
43	4	Member 1 - TFN	text	t	f	null	\N	\N	\N	5	2026-01-18 05:05:44.481784	1	\N	\N	f	\N	1	10	\N	\N
44	4	Member 1 - Current super fund name	text	f	f	null	\N	\N	Fund you are rolling over from	6	2026-01-18 05:05:44.481784	1	\N	\N	f	\N	1	10	\N	\N
45	4	Member 1 - Approximate rollover amount	number	f	f	null	\N	0.00	\N	7	2026-01-18 05:05:44.481784	1	\N	\N	f	\N	1	10	\N	\N
46	4	Member 2 - Full name (if applicable)	text	f	f	null	\N	\N	\N	8	2026-01-18 05:05:44.481785	1	\N	\N	f	\N	1	10	\N	\N
47	4	Member 2 - Date of birth	date	f	f	null	\N	\N	\N	9	2026-01-18 05:05:44.481785	1	\N	\N	f	\N	1	10	\N	\N
48	4	Member 2 - TFN	text	f	f	null	\N	\N	\N	10	2026-01-18 05:05:44.481786	1	\N	\N	f	\N	1	10	\N	\N
49	4	Investment strategy preferences	multiselect	t	f	["Australian shares", "International shares", "Property", "Cash/Term deposits", "Bonds", "Cryptocurrency"]	\N	\N	\N	11	2026-01-18 05:05:44.481786	1	\N	\N	f	\N	1	10	\N	\N
50	4	Do you plan to borrow to invest (LRBA)?	radio	t	f	["Yes", "No", "Not sure"]	\N	\N	\N	12	2026-01-18 05:05:44.481786	1	\N	\N	f	\N	1	10	\N	\N
51	4	Upload ID documents for all members	file	t	f	null	\N	\N	Passport or Drivers License	13	2026-01-18 05:05:44.481787	1	\N	\N	f	\N	1	10	\N	\N
52	4	Any specific questions or requirements?	textarea	f	f	null	\N	\N	\N	14	2026-01-18 05:05:44.481787	1	\N	\N	f	\N	1	10	\N	\N
53	5	Proposed company name (Option 1)	text	t	f	null	\N	\N	Must end with Pty Ltd	0	2026-01-18 05:05:44.485242	1	\N	\N	f	\N	1	10	\N	\N
54	5	Proposed company name (Option 2)	text	f	f	null	\N	\N	Backup name in case first choice is taken	1	2026-01-18 05:05:44.485244	1	\N	\N	f	\N	1	10	\N	\N
55	5	Company type	radio	t	f	["Proprietary Limited (Pty Ltd)", "Public Company (Ltd)"]	\N	\N	\N	2	2026-01-18 05:05:44.485244	1	\N	\N	f	\N	1	10	\N	\N
56	5	Principal business activity	text	t	f	null	\N	e.g., IT Consulting, Construction, Retail	\N	3	2026-01-18 05:05:44.485245	1	\N	\N	f	\N	1	10	\N	\N
57	5	Registered office address	textarea	t	f	null	\N	\N	Must be a physical address in Australia	4	2026-01-18 05:05:44.485245	1	\N	\N	f	\N	1	10	\N	\N
58	5	Principal place of business	textarea	t	f	null	\N	\N	\N	5	2026-01-18 05:05:44.485246	1	\N	\N	f	\N	1	10	\N	\N
59	5	Number of directors	select	t	f	["1", "2", "3", "4", "5+"]	\N	\N	\N	6	2026-01-18 05:05:44.485246	1	\N	\N	f	\N	1	10	\N	\N
60	5	Director 1 - Full name	text	t	f	null	\N	\N	\N	7	2026-01-18 05:05:44.485246	1	\N	\N	f	\N	1	10	\N	\N
61	5	Director 1 - Date of birth	date	t	f	null	\N	\N	\N	8	2026-01-18 05:05:44.485247	1	\N	\N	f	\N	1	10	\N	\N
62	5	Director 1 - Residential address	textarea	t	f	null	\N	\N	\N	9	2026-01-18 05:05:44.485247	1	\N	\N	f	\N	1	10	\N	\N
63	5	Director 1 - Place of birth (City, Country)	text	t	f	null	\N	\N	\N	10	2026-01-18 05:05:44.485248	1	\N	\N	f	\N	1	10	\N	\N
64	5	Director 2 - Full name (if applicable)	text	f	f	null	\N	\N	\N	11	2026-01-18 05:05:44.485248	1	\N	\N	f	\N	1	10	\N	\N
65	5	Number of shares to be issued	number	t	f	null	\N	100	\N	12	2026-01-18 05:05:44.485249	1	\N	\N	f	\N	1	10	\N	\N
66	5	Share price	number	t	f	null	\N	1.00	\N	13	2026-01-18 05:05:44.485249	1	\N	\N	f	\N	1	10	\N	\N
67	5	Shareholder 1 - Name	text	t	f	null	\N	\N	\N	14	2026-01-18 05:05:44.48525	1	\N	\N	f	\N	1	10	\N	\N
68	5	Shareholder 1 - Number of shares	number	t	f	null	\N	\N	\N	15	2026-01-18 05:05:44.48525	1	\N	\N	f	\N	1	10	\N	\N
69	5	Do you need GST registration?	radio	t	f	["Yes", "No", "Not sure"]	\N	\N	\N	16	2026-01-18 05:05:44.48525	1	\N	\N	f	\N	1	10	\N	\N
70	5	Do you need to register as an employer?	radio	t	f	["Yes", "No", "Not sure"]	\N	\N	\N	17	2026-01-18 05:05:44.485251	1	\N	\N	f	\N	1	10	\N	\N
71	5	Upload ID for all directors	file	t	f	null	\N	\N	\N	18	2026-01-18 05:05:44.485251	1	\N	\N	f	\N	1	10	\N	\N
72	6	Email	email	t	f	null	null	contact@company.com	Primary contact email for this application	0	2026-01-18 05:05:44.52178	1	Company Details	Basic information about the new company	f	\N	1	10	\N	\N
73	6	Proposed Name of the Company	textarea	t	f	null	null	Option 1: ABC Pty Ltd\nOption 2: XYZ Pty Ltd\nOption 3: DEF Pty Ltd	Provide 3 company names of your choice in the order of preference as ASIC will grant names based on availability	1	2026-01-18 05:05:44.522358	1	\N	\N	f	\N	1	10	\N	\N
74	6	Main Business Activity Of the New Company	text	t	f	null	null	e.g., IT Consulting, Construction, Retail	\N	2	2026-01-18 05:05:44.522935	1	\N	\N	f	\N	1	10	\N	\N
75	6	Registered Office Address of the New Company	textarea	t	f	null	null	\N	PO Box address will not work. This can be your home or business address. Note that ASIC charges a fee if you were to change the registered office address later	3	2026-01-18 05:05:44.523402	1	\N	\N	f	\N	1	10	\N	\N
76	6	Principal Place of Business of the New Company	textarea	t	f	null	null	\N	PO Box address will not work. This can be your home or business address. Note that ASIC charges a fee if you were to change the registered office address later	4	2026-01-18 05:05:44.52395	1	\N	\N	f	\N	1	10	\N	\N
77	6	New Company Directors' Information	text	f	f	\N	{"type": "section_header"}	\N	Information about the directors of the new company	5	2026-01-18 05:05:44.524788	2	New Company Directors' Information	Information about the directors of the new company	f	\N	1	10	\N	\N
78	6	Full Name	text	t	f	null	null	\N	Name should ideally be an exact match with a photo identity like passport or Drivers Licence and with ATO Records	6	2026-01-18 05:05:44.525184	3	Director Details	Enter details for Director 1. Click "Add Another Director" to add more directors.	t	director	1	10	\N	\N
79	6	Tax File Number (TFN)	text	t	f	null	null	XXX XXX XXX	\N	7	2026-01-18 05:05:44.525637	3	\N	\N	t	director	1	10	\N	\N
80	6	Director ID	text	t	f	null	null	\N	Director Identification Number is pre-requisite for the incorporation of the company in Australia. If you do not have a Director ID, please apply online on www.abrs.gov.au/director-identification-number/apply-director-identification-number	8	2026-01-18 05:05:44.526075	3	\N	\N	t	director	1	10	\N	\N
81	6	Date of Birth	date	t	f	null	null	\N	\N	9	2026-01-18 05:05:44.526716	3	\N	\N	t	director	1	10	\N	\N
82	6	Country of Birth	text	t	f	null	null	\N	\N	10	2026-01-18 05:05:44.527373	3	\N	\N	t	director	1	10	\N	\N
83	6	City of Birth	text	t	f	null	null	\N	\N	11	2026-01-18 05:05:44.527858	3	\N	\N	t	director	1	10	\N	\N
84	6	Mobile (Phone) Number	phone	t	f	null	null	\N	\N	12	2026-01-18 05:05:44.528688	3	\N	\N	t	director	1	10	\N	\N
85	6	Email ID	email	t	f	null	null	\N	\N	13	2026-01-18 05:05:44.529327	3	\N	\N	t	director	1	10	\N	\N
86	6	Residential Status (Australia)	select	t	f	["PR (Permanent Resident)", "Citizen", "TR (Temporary Resident)", "Non-resident"]	null	\N	Residential Status can be: PR, Citizen, TR, or non-resident	14	2026-01-18 05:05:44.529836	3	\N	\N	t	director	1	10	\N	\N
87	6	Residential Address (Australia)	textarea	t	f	null	null	\N	\N	15	2026-01-18 05:05:44.530416	3	\N	\N	t	director	1	10	\N	\N
88	6	Director will also act as a:	multiselect	f	f	["Public Officer", "Secretary", "None"]	null	\N	\N	16	2026-01-18 05:05:44.530944	3	\N	\N	t	director	1	10	\N	\N
89	6	Passport of Director	file	t	f	null	null	\N	Upload passport copy for this director	17	2026-01-18 05:05:44.531487	3	\N	\N	t	director	1	10	\N	\N
90	6	Drivers Licence of Director	file	f	f	null	null	\N	Upload drivers licence for this director (optional)	18	2026-01-18 05:05:44.531999	3	\N	\N	t	director	1	10	\N	\N
91	6	Company's Shareholders Information	text	f	f	\N	{"type": "section_header"}	\N	Information about the shareholders of the new company	19	2026-01-18 05:05:44.532572	4	Company's Shareholders Information	Information about the shareholders of the new company	f	\N	1	10	\N	\N
92	6	Full Name	text	t	f	null	null	\N	Name should ideally be an exact match with a photo identity like passport or Drivers Licence and with ATO Records	20	2026-01-18 05:05:44.532933	5	Shareholder Details	Enter details for Shareholder 1. Click "Add Another Shareholder" to add more shareholders.	t	shareholder	1	10	\N	\N
93	6	Date of Birth	date	t	f	null	null	\N	\N	21	2026-01-18 05:05:44.533409	5	\N	\N	t	shareholder	1	10	\N	\N
94	6	Country of Birth	text	t	f	null	null	\N	\N	22	2026-01-18 05:05:44.533831	5	\N	\N	t	shareholder	1	10	\N	\N
95	6	City of Birth	text	t	f	null	null	\N	\N	23	2026-01-18 05:05:44.534293	5	\N	\N	t	shareholder	1	10	\N	\N
96	6	Mobile (Phone) Number	phone	t	f	null	null	\N	\N	24	2026-01-18 05:05:44.534693	5	\N	\N	t	shareholder	1	10	\N	\N
97	6	Email ID	email	t	f	null	null	\N	\N	25	2026-01-18 05:05:44.535093	5	\N	\N	t	shareholder	1	10	\N	\N
98	6	Residential Address (Australia)	textarea	t	f	null	null	\N	\N	26	2026-01-18 05:05:44.535608	5	\N	\N	t	shareholder	1	10	\N	\N
99	6	Percentage (%) of shares required in this new company	number	t	f	null	{"min": 0, "max": 100}	\N	% can be mentioned in numeric terms like 50%, 99% etc, but cannot exceed 100% combined for all shareholders	27	2026-01-18 05:05:44.536112	5	\N	\N	t	shareholder	1	10	\N	\N
100	6	Passport of Shareholder	file	t	f	null	null	\N	Upload passport copy for this shareholder	28	2026-01-18 05:05:44.536662	5	\N	\N	t	shareholder	1	10	\N	\N
101	6	Proof of Address	file	f	f	null	null	\N	Upload utility bill or bank statement for this shareholder (optional)	29	2026-01-18 05:05:44.537201	5	\N	\N	t	shareholder	1	10	\N	\N
102	7	Proposed Name of the SMSF Fund	textarea	t	f	null	null	e.g., Smith Family Superannuation Fund	Enter your preferred name for the SMSF	0	2026-01-18 05:05:44.546031	1	SMSF Setup Details	Basic information about your new SMSF	f	\N	1	10	\N	\N
103	7	Registered Address	textarea	t	f	null	null	\N	The official registered address for your SMSF	1	2026-01-18 05:05:44.546541	1	\N	\N	f	\N	1	10	\N	\N
104	7	Principal Business Address	textarea	t	f	null	null	\N	The main business address for your SMSF	2	2026-01-18 05:05:44.546982	1	\N	\N	f	\N	1	10	\N	\N
105	7	Number of Members in SMSF	select	t	f	["1", "2", "3", "4", "5", "6"]	null	\N	In case only 1 member is to be selected, please select "Corporate" as the trustee type in next question	3	2026-01-18 05:05:44.547475	1	\N	\N	f	\N	1	10	\N	\N
106	7	Trustee Type	radio	t	f	["Corporate", "Individual"]	null	\N	Note: If it is a one member fund OR if you want to buy a property on loan through your SMSF, please select Corporate Trustee as an option	4	2026-01-18 05:05:44.54792	1	\N	\N	f	\N	1	10	\N	\N
107	7	Do you have an existing Corporate Trustee Company for your SMSF?	radio	t	f	["Yes", "No"]	null	\N	Select Yes if you already have a company set up as trustee	5	2026-01-18 05:05:44.548453	2	Corporate Trustee (CT) Company Details	Information about your Corporate Trustee Company	f	\N	1	10	\N	\N
108	7	Full Name of Your existing Corporate Trustee Company	text	t	f	null	{"section_conditional": {"type": "section_conditional", "conditional_on_section": 2, "conditional_question": "Do you have an existing Corporate Trustee Company for your SMSF?", "conditional_value": "Yes"}}	e.g., Smith Trustee Pty Ltd	\N	6	2026-01-18 05:05:44.548961	3	Existing Corporate Trustee Company Details	Details of your existing Corporate Trustee Company	f	\N	1	10	\N	\N
109	7	ABN of your existing Corporate Trustee Company	text	t	f	null	null	XX XXX XXX XXX	\N	7	2026-01-18 05:05:44.549505	3	\N	\N	f	\N	1	10	\N	\N
110	7	Proposed Company Name	textarea	t	f	null	{"section_conditional": {"type": "section_conditional", "conditional_on_section": 2, "conditional_question": "Do you have an existing Corporate Trustee Company for your SMSF?", "conditional_value": "No"}}	Option 1: ABC Trustee Pty Ltd\nOption 2: XYZ Trustee Pty Ltd\nOption 3: DEF Trustee Pty Ltd	Give 3 names in the order of preference to check availability with ASIC	8	2026-01-18 05:05:44.549984	4	New Corporate Trustee Company	This section is to be filled when you do not have any existing Corporate Trustee Company for your SMSF and hence needs to be applied for	f	\N	1	10	\N	\N
111	7	Director Name	text	t	f	null	null	\N	Full legal name of the director	9	2026-01-18 05:05:44.550534	5	Directors Details	Details of corporate trustee company directors. Click "Add Another Director" if you have more than one director.	t	director	1	6	\N	\N
112	7	Director Residential Address	textarea	t	f	null	null	\N	Current residential address of the director	10	2026-01-18 05:05:44.551074	5	\N	\N	t	director	1	6	\N	\N
113	7	Director ID	text	t	f	null	null	\N	Director Identification Number. If you do not have one, apply at www.abrs.gov.au	11	2026-01-18 05:05:44.551561	5	\N	\N	t	director	1	6	\N	\N
114	7	Director Passport/ID Document	file	t	f	null	null	\N	Upload passport or government-issued ID for this director	12	2026-01-18 05:05:44.552006	5	\N	\N	t	director	1	6	\N	\N
115	7	Director Proof of Address	file	f	f	null	null	\N	Upload utility bill or bank statement showing address (optional)	13	2026-01-18 05:05:44.552506	5	\N	\N	t	director	1	6	\N	\N
116	7	Full Name	text	t	f	null	null	\N	Full legal name as per identification documents	14	2026-01-18 05:05:44.553001	6	SMSF Members Details	Enter details for Member 1. Click "Add Another Member" to add additional members if applicable.	t	member	1	6	\N	\N
117	7	Residential Address	textarea	t	f	null	null	\N	Current residential address	15	2026-01-18 05:05:44.553463	6	\N	\N	t	member	1	6	\N	\N
118	7	Tax File Number (TFN)	text	t	f	null	null	XXX XXX XXX	\N	16	2026-01-18 05:05:44.553888	6	\N	\N	t	member	1	6	\N	\N
119	7	Date of Birth	date	t	f	null	null	\N	\N	17	2026-01-18 05:05:44.554456	6	\N	\N	t	member	1	6	\N	\N
120	7	Gender	select	f	f	["Male", "Female", "Other", "Prefer not to say"]	null	\N	\N	18	2026-01-18 05:05:44.554906	6	\N	\N	t	member	1	6	\N	\N
121	7	Member Passport/ID Document	file	t	f	null	null	\N	Upload passport or government-issued ID for this member	19	2026-01-18 05:05:44.555424	6	\N	\N	t	member	1	6	\N	\N
122	7	Member Proof of Address	file	f	f	null	null	\N	Upload utility bill or bank statement showing current address (optional)	20	2026-01-18 05:05:44.555908	6	\N	\N	t	member	1	6	\N	\N
123	7	Do you want us to apply for opening Macquarie Bank Account for your SMSF as part of setup (at no additional cost)?	radio	t	f	["Yes", "No"]	null	\N	This is an optional service only and you are free to choose a bank of your choice or preference. If this be the case, please select No while answering this question	21	2026-01-18 05:05:44.556437	7	Other Information	This section requires you to answer some other questions in relation to your SMSF Setup	f	\N	1	10	\N	\N
124	8	What is the name of the SMSF?	text	t	f	null	null	e.g., Smith Family Superannuation Fund	\N	0	2026-01-18 05:05:44.562174	1	Fund Details	Basic information about the SMSF	f	\N	1	10	\N	\N
125	8	What is the ABN of the SMSF?	text	t	f	null	null	XX XXX XXX XXX	\N	1	2026-01-18 05:05:44.562662	1	\N	\N	f	\N	1	10	\N	\N
126	8	Financial year for this compliance?	select	t	f	["2023-24", "2024-25", "2025-26", "2026-27"]	null	\N	\N	2	2026-01-18 05:05:44.563165	1	\N	\N	f	\N	1	10	\N	\N
127	8	Does the fund have:	radio	t	f	["Individual Trustees", "Corporate Trustee"]	null	\N	\N	3	2026-01-18 05:05:44.563699	1	\N	\N	f	\N	1	10	\N	\N
128	8	List all trustees/members of the SMSF	textarea	t	f	null	null	Enter full names of all trustees and members	Include full legal names of all trustees and members	4	2026-01-18 05:05:44.564259	2	Trustee & Member Information	Details about trustees and members of the SMSF	f	\N	1	10	\N	\N
129	8	Have there been any changes to trustees or members during the year?	radio	t	f	["Yes", "No"]	null	\N	\N	5	2026-01-18 05:05:44.564768	2	\N	\N	f	\N	1	10	\N	\N
130	8	If yes, please describe the changes	textarea	f	f	null	null	Describe any trustee or member changes	Only complete if you answered Yes above	6	2026-01-18 05:05:44.565245	2	\N	\N	f	\N	1	10	\N	\N
131	8	How many SMSF bank accounts exist?	number	t	f	null	{"min": 1}	\N	\N	7	2026-01-18 05:05:44.565696	3	Bank Accounts	Information about SMSF bank accounts	f	\N	1	10	\N	\N
132	8	Have you provided full-year bank statements (1 July – 30 June)?	radio	t	f	["Yes", "No"]	null	\N	\N	8	2026-01-18 05:05:44.56614	3	\N	\N	f	\N	1	10	\N	\N
133	8	Did any member receive employer contributions during the year?	radio	t	f	["Yes", "No"]	null	\N	\N	9	2026-01-18 05:05:44.566922	4	Contributions	Details about contributions made during the year	f	\N	1	10	\N	\N
134	8	Did any member make personal (after-tax) contributions?	radio	t	f	["Yes", "No"]	null	\N	\N	10	2026-01-18 05:05:44.567452	4	\N	\N	f	\N	1	10	\N	\N
135	8	Were any contributions received late (after 30 June)?	radio	t	f	["Yes", "No", "Not sure"]	null	\N	\N	11	2026-01-18 05:05:44.567918	4	\N	\N	f	\N	1	10	\N	\N
136	8	Did the SMSF hold any of the following?	multiselect	t	f	["Listed shares / ETFs", "Managed funds", "Property", "Term deposits", "Cryptocurrency", "Private companies / trusts", "None of the above"]	null	\N	\N	12	2026-01-18 05:05:44.568392	5	Investments	Information about SMSF investments	f	\N	1	10	\N	\N
137	8	Were there any investment purchases or sales during the year?	radio	t	f	["Yes", "No"]	null	\N	\N	13	2026-01-18 05:05:44.56883	5	\N	\N	f	\N	1	10	\N	\N
138	8	Have you uploaded all buy/sell contracts and income statements?	radio	t	f	["Yes", "No"]	null	\N	\N	14	2026-01-18 05:05:44.569347	5	\N	\N	f	\N	1	10	\N	\N
139	8	Does the SMSF own property?	radio	t	f	["Yes", "No"]	null	\N	\N	15	2026-01-18 05:05:44.569846	6	Property	Complete this section if the SMSF owns property	f	\N	1	10	\N	\N
140	8	Is the property:	radio	f	f	["Residential", "Commercial"]	null	\N	Only answer if the SMSF owns property	16	2026-01-18 05:05:44.570347	6	\N	\N	f	\N	1	10	\N	\N
141	8	Have you provided the following property documents?	multiselect	f	f	["Rental statements", "Expense invoices", "Market valuation at 30 June"]	null	\N	Select all documents you have provided	17	2026-01-18 05:05:44.570839	6	\N	\N	f	\N	1	10	\N	\N
142	8	Was any member in pension phase during the year?	radio	t	f	["Yes", "No"]	null	\N	\N	18	2026-01-18 05:05:44.57126	7	Pension Phase	Information about pension payments	f	\N	1	10	\N	\N
143	8	Were minimum pension payments met?	radio	f	f	["Yes", "No", "Not sure"]	null	\N	Only answer if a member was in pension phase	19	2026-01-18 05:05:44.571676	7	\N	\N	f	\N	1	10	\N	\N
144	8	Were all investments made at arm's length?	radio	t	f	["Yes", "No", "Not sure"]	null	\N	Arm's length means transactions were conducted as if the parties were unrelated	20	2026-01-18 05:05:44.572131	8	Compliance & Declarations	Compliance questions and final declaration	f	\N	1	10	\N	\N
145	8	Did the SMSF lend money to, or borrow from, related parties?	radio	t	f	["Yes", "No"]	null	\N	\N	21	2026-01-18 05:05:44.572554	8	\N	\N	f	\N	1	10	\N	\N
146	8	Do you confirm that all information provided is true and complete?	radio	t	f	["Yes"]	null	\N	You must confirm this declaration to submit the form	22	2026-01-18 05:05:44.572949	8	\N	\N	f	\N	1	10	\N	\N
147	9	Company legal name	text	t	f	null	null	e.g., ABC Pty Ltd	\N	0	2026-01-18 05:05:44.57881	1	Company Information	Basic company details	f	\N	1	10	\N	\N
148	9	ACN	text	t	f	null	null	XXX XXX XXX	Australian Company Number (9 digits)	1	2026-01-18 05:05:44.579343	1	\N	\N	f	\N	1	10	\N	\N
149	9	Financial year	select	t	f	["2023-24", "2024-25", "2025-26", "2026-27"]	null	\N	\N	2	2026-01-18 05:05:44.579838	1	\N	\N	f	\N	1	10	\N	\N
151	9	List all shareholders and share percentages	textarea	t	f	null	null	e.g., John Smith - 50%, Jane Doe - 50%	Include name and percentage for each shareholder	4	2026-01-18 05:05:44.5808	2	\N	\N	f	\N	1	10	\N	\N
152	9	Were there any changes to directors or shareholders?	radio	t	f	["Yes", "No"]	null	\N	\N	5	2026-01-18 05:05:44.581246	2	\N	\N	f	\N	1	10	\N	\N
153	9	What accounting software do you use?	select	t	f	["Xero", "MYOB", "QuickBooks", "Excel", "Other"]	null	\N	\N	6	2026-01-18 05:05:44.581654	3	Accounting Records	Information about your accounting software and records	f	\N	1	10	\N	\N
154	9	Have you provided all bank statements for the year?	radio	t	f	["Yes", "No"]	null	\N	\N	7	2026-01-18 05:05:44.582044	3	\N	\N	f	\N	1	10	\N	\N
155	9	Primary source of business income	textarea	t	f	null	null	Describe your main business activities and income sources	\N	8	2026-01-18 05:05:44.582425	4	Income	Information about company income	f	\N	1	10	\N	\N
156	9	Did the company receive any other income?	multiselect	t	f	["Interest", "Grants", "Asset sales", "None"]	null	\N	\N	9	2026-01-18 05:05:44.58281	4	\N	\N	f	\N	1	10	\N	\N
157	9	Have all business expenses been recorded?	radio	t	f	["Yes", "No"]	null	\N	\N	10	2026-01-18 05:05:44.583274	5	Expenses	Information about company expenses	f	\N	1	10	\N	\N
158	9	Are there any private or mixed-use expenses?	radio	t	f	["Yes", "No"]	null	\N	e.g., vehicle used for both business and personal purposes	11	2026-01-18 05:05:44.583681	5	\N	\N	f	\N	1	10	\N	\N
159	9	Did the company have employees during the year?	radio	t	f	["Yes", "No"]	null	\N	\N	12	2026-01-18 05:05:44.584121	6	Payroll & Super	Information about employees, payroll and superannuation	f	\N	1	10	\N	\N
160	9	Was Single Touch Payroll (STP) lodged for all pay runs?	radio	f	f	["Yes", "No"]	null	\N	Only answer if the company had employees	13	2026-01-18 05:05:44.584636	6	\N	\N	f	\N	1	10	\N	\N
161	9	Does the company owe money to any director or shareholder?	radio	t	f	["Yes", "No"]	null	\N	\N	14	2026-01-18 05:05:44.585142	7	Loans & Dividends	Information about loans and dividend payments	f	\N	1	10	\N	\N
162	9	Does any director or shareholder owe money to the company?	radio	t	f	["Yes", "No"]	null	\N	Division 7A loans may apply	15	2026-01-18 05:05:44.585643	7	\N	\N	f	\N	1	10	\N	\N
163	9	Were dividends paid or declared during the year?	radio	t	f	["Yes", "No"]	null	\N	\N	16	2026-01-18 05:05:44.586066	7	\N	\N	f	\N	1	10	\N	\N
164	9	Has the ASIC annual review fee been paid?	radio	t	f	["Yes", "No"]	null	\N	\N	17	2026-01-18 05:05:44.586482	8	ASIC & Tax	ASIC and tax compliance questions	f	\N	1	10	\N	\N
165	9	Have all BAS and IAS been lodged for the year?	radio	t	f	["Yes", "No"]	null	\N	Business Activity Statements and Instalment Activity Statements	18	2026-01-18 05:05:44.586868	8	\N	\N	f	\N	1	10	\N	\N
166	9	Do you confirm the information provided is complete and accurate?	radio	t	f	["Yes"]	null	\N	You must confirm this declaration to submit the form	19	2026-01-18 05:05:44.587398	9	Final Declaration	Please confirm the accuracy of the information provided	f	\N	1	10	\N	\N
150	9	List all directors	textarea	t	f	[]	null	Enter full names of all directors	Include full legal names of all current directors	3	2026-01-18 05:05:44.580351	2	Directors & Shareholders	Information about company directors and shareholders	f	\N	1	10	\N	\N
178	1	Type of Client	radio	t	\N	[{"value": "new", "label": "New"}, {"value": "existing", "label": "Existing"}]	\N	\N	\N	0	\N	1	Individual Tax Return (ITR) Form	Please fill in this form carefully to help us assess your tax/refund correctly in line with ATO guidelines.	\N	\N	\N	\N	\N	\N
179	1	Full Name	text	t	\N	\N	\N	\N	\N	1	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
180	1	Date of Birth (DOB)	date	t	\N	\N	\N	\N	Please fill in your DOB correctly	2	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
181	1	Tax File Number (TFN)	text	t	\N	\N	\N	\N	Please fill up your TFN carefully	3	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
182	1	Current Residential Address	textarea	t	\N	\N	\N	\N	PO Box address will not work. Please mention complete address including post code of your suburb.	4	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
183	1	Mobile Number	phone	t	\N	\N	\N	\N	\N	5	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
184	1	Occupation	text	t	\N	\N	\N	\N	\N	6	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
185	1	Residency Status?	radio	t	\N	[{"value": "australian_citizen", "label": "Australian Citizen"}, {"value": "permanent_resident", "label": "Permanent Resident(PR)"}, {"value": "temporary_resident", "label": "Temporary Resident (TR)"}, {"value": "work_sponsored_visa", "label": "Work Sponsored Visa"}, {"value": "holiday_worker", "label": "Holiday Worker"}, {"value": "others", "label": "Others"}]	\N	\N	\N	7	\N	3	Tax related information	This information shall be used to plan your telephonic tax consultation.	\N	\N	\N	\N	\N	\N
186	1	Do u have a Medicare Card?	radio	t	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}, {"value": "exempt", "label": "Medicare Levy Exempt (TR, Work sponsored visa holders etc)"}]	\N	\N	\N	8	\N	3	Tax related information	This information shall be used to plan your telephonic tax consultation.	\N	\N	\N	\N	\N	\N
187	1	Are you self employed/ sub-contractor/ work under your own ABN?	textarea	t	\N	\N	\N	\N	\N	9	\N	3	Tax related information	This information shall be used to plan your telephonic tax consultation.	\N	\N	\N	\N	\N	\N
188	1	Your ABN number?	text	t	\N	\N	\N	\N	If No ABN, then write "Not Applicable" to proceed	10	\N	3	Tax related information	This information shall be used to plan your telephonic tax consultation.	\N	\N	\N	\N	\N	\N
189	1	Do you have a spouse?	radio	t	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]	\N	\N	\N	11	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
190	1	Is your spouse JPATax existing Client?	radio	f	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]	\N	\N	\N	12	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
191	1	Spouse Full Name	text	t	\N	\N	\N	\N	If No spouse selected, then write "Not Applicable" to proceed further.	13	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
192	1	Spouse Date of Birth	date	t	\N	\N	\N	\N	If No spouse selected, then write "Not Applicable" to proceed further.	14	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
193	1	Spouse TFN	text	t	\N	\N	\N	\N	If No spouse selected, then write "Not Applicable" to proceed further.	15	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
194	1	Spouse Gross Taxable Income ($)	text	t	\N	\N	\N	\N	If No spouse selected, then write "Not Applicable" to proceed further.	16	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
195	1	Any dependents?	textarea	t	\N	\N	\N	\N	If Yes, then please provide full names and Date of Birth of all Dependents. If No, then write "Not Applicable" to proceed.	17	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
196	1	Did you SELL any Assets (like units of Shares/Crypto/Land/House during this FY?	radio	t	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]	\N	\N	\N	18	\N	5	Capital Gains Tax Information	Please fill in this section as applicable	\N	\N	\N	\N	\N	\N
197	1	List all such assets sold?	textarea	t	\N	\N	\N	\N	Only mention type of all assets sold during the FY like shares, cryptos, investment property (residential/commercial) etc. If none, then simply write "Not applicable" to proceed.	19	\N	5	Capital Gains Tax Information	Please fill in this section as applicable	\N	\N	\N	\N	\N	\N
198	1	Do you have any Investment Property generating rental income for you during this FY?	radio	t	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]	\N	\N	\N	20	\N	6	Investment Property and Other Income	Any investment property whether in Australia or overseas which has generated rental income during the year	\N	\N	\N	\N	\N	\N
199	1	Please provide full address of each such investment property	textarea	t	\N	\N	\N	\N	If the answer was no to previous question, simply mention "Not Applicable" to proceed further.	21	\N	6	Investment Property and Other Income	Any investment property whether in Australia or overseas which has generated rental income during the year	\N	\N	\N	\N	\N	\N
226	10	Do you have a spouse?	radio	t	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]	\N	\N	\N	11	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
227	10	Is your spouse JPATax existing Client?	radio	f	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]	\N	\N	\N	12	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
228	10	Spouse Full Name	text	t	\N	\N	\N	\N	If No spouse selected, then write "Not Applicable" to proceed further.	13	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
200	1	Do you earn any other income other than salary? E.g. running a side-gig, business etc. (whether as a sole trader or on ABN)	textarea	t	\N	\N	\N	\N	Business can be any sort of commercial or trading activity with the intent of earning income or profit like Uber driving etc. If the answer was no to previous question, simply mention "Not Applicable" to proceed further.	22	\N	6	Investment Property and Other Income	Any investment property whether in Australia or overseas which has generated rental income during the year	\N	\N	\N	\N	\N	\N
201	1	Work from Home Expenses	textarea	t	\N	\N	\N	\N	Mention # of days in a week worked from home in a year of 52 weeks, including hours worked per day from home. Eg. 2 days in a week, 8 hrs a day.	23	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below. This will also be discussed and reconfirmed during your phone tax consultation session. If any expense is not required, just mention "Nil" or "Not Applicable" to proceed further.	\N	\N	\N	\N	\N	\N
202	1	Home Office Set-up	textarea	t	\N	\N	\N	\N	This includes purchase of any desk, chair, stationery, office supplies etc. in relation to your work only.	24	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
203	1	Educational expenses	textarea	t	\N	\N	\N	\N	Any course / training pursued in relation to your present job which was not reimbursed by your employer.	25	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
204	1	Work Related Car Expenses	textarea	t	\N	\N	\N	\N	Any work-related car travel (not including commuting to/from work).	26	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
205	1	Travel Exps (Work Related Only and should be overnight stay related)	textarea	t	\N	\N	\N	\N	Day to day office going and coming expenses are not considered as Travel exps for deduction purpose. But please discuss during your telephonic tax consultation.	27	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
206	1	Uniform/ Laundry Expenses	textarea	t	\N	\N	\N	\N	This includes any Protective clothing laundry as well.	28	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
207	1	Union/ Annual Membership Fees paid	textarea	t	\N	\N	\N	\N	This can be annual membership fee paid to any professional organisation in relation to your work.	29	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
208	1	Donations to approved Charities	textarea	t	\N	\N	\N	\N	\N	30	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
209	1	Tax Agent Fee	textarea	t	\N	\N	\N	\N	Fees paid to your tax agent last year	31	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
210	1	Income Protection Insurance	textarea	t	\N	\N	\N	\N	\N	32	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
211	1	Tools, Equipment, or any asset purchased	textarea	t	\N	\N	\N	\N	\N	33	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
212	1	Any other Deductions	textarea	t	\N	\N	\N	\N	List down any other deduction that you would like to claim	34	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
213	1	Upload all invoices/supportings to claim your deductions in Tax Return	file	t	\N	\N	\N	\N	Note: Supporting such as invoices/receipts are required by ATO in order to claim an expense deduction, specially for any amount over $150, whether individual or in aggregate. If the space is less, you can email all supporting with proper file name for identification purpose.	35	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
214	1	Authorisation	radio	t	\N	[{"value": "agree", "label": "I Agree"}]	\N	\N	\N	36	\N	7	Personal Expense Deductions	I/we hereby authorise the Tax Agent to act on my/our behalf in all matters related to the preparation, lodgement, and processing of my/our tax return.	\N	\N	\N	\N	\N	\N
215	10	Type of Client	radio	t	\N	[{"value": "new", "label": "New"}, {"value": "existing", "label": "Existing"}]	\N	\N	\N	0	\N	1	Individual Tax Return (ITR) Form	Please fill in this form carefully to help us assess your tax/refund correctly in line with ATO guidelines.	\N	\N	\N	\N	\N	\N
216	10	Full Name	text	t	\N	\N	\N	\N	\N	1	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
217	10	Date of Birth (DOB)	date	t	\N	\N	\N	\N	Please fill in your DOB correctly	2	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
218	10	Tax File Number (TFN)	text	t	\N	\N	\N	\N	Please fill up your TFN carefully	3	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
219	10	Current Residential Address	textarea	t	\N	\N	\N	\N	PO Box address will not work. Please mention complete address including post code of your suburb.	4	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
220	10	Mobile Number	phone	t	\N	\N	\N	\N	\N	5	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
221	10	Occupation	text	t	\N	\N	\N	\N	\N	6	\N	2	Client Details	Provide basic details about yourself for verification purpose.	\N	\N	\N	\N	\N	\N
222	10	Residency Status?	radio	t	\N	[{"value": "australian_citizen", "label": "Australian Citizen"}, {"value": "permanent_resident", "label": "Permanent Resident(PR)"}, {"value": "temporary_resident", "label": "Temporary Resident (TR)"}, {"value": "work_sponsored_visa", "label": "Work Sponsored Visa"}, {"value": "holiday_worker", "label": "Holiday Worker"}, {"value": "others", "label": "Others"}]	\N	\N	\N	7	\N	3	Tax related information	This information shall be used to plan your telephonic tax consultation.	\N	\N	\N	\N	\N	\N
223	10	Do u have a Medicare Card?	radio	t	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}, {"value": "exempt", "label": "Medicare Levy Exempt (TR, Work sponsored visa holders etc)"}]	\N	\N	\N	8	\N	3	Tax related information	This information shall be used to plan your telephonic tax consultation.	\N	\N	\N	\N	\N	\N
224	10	Are you self employed/ sub-contractor/ work under your own ABN?	textarea	t	\N	\N	\N	\N	\N	9	\N	3	Tax related information	This information shall be used to plan your telephonic tax consultation.	\N	\N	\N	\N	\N	\N
225	10	Your ABN number?	text	t	\N	\N	\N	\N	If No ABN, then write "Not Applicable" to proceed	10	\N	3	Tax related information	This information shall be used to plan your telephonic tax consultation.	\N	\N	\N	\N	\N	\N
255	11	Trustee Structure	radio	t	f	["Individual Trustees", "Corporate Trustee"]	null	\N	Select the type of trustee structure for your SMSF	3	2026-01-20 06:00:58.594955	1	\N	\N	f	\N	1	10	\N	\N
229	10	Spouse Date of Birth	date	t	\N	\N	\N	\N	If No spouse selected, then write "Not Applicable" to proceed further.	14	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
230	10	Spouse TFN	text	t	\N	\N	\N	\N	If No spouse selected, then write "Not Applicable" to proceed further.	15	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
231	10	Spouse Gross Taxable Income ($)	text	t	\N	\N	\N	\N	If No spouse selected, then write "Not Applicable" to proceed further.	16	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
232	10	Any dependents?	textarea	t	\N	\N	\N	\N	If Yes, then please provide full names and Date of Birth of all Dependents. If No, then write "Not Applicable" to proceed.	17	\N	4	Spouse Section	Spouse details go in your Tax Return. Hence please fill in the required information.	\N	\N	\N	\N	\N	\N
233	10	Did you SELL any Assets (like units of Shares/Crypto/Land/House during this FY?	radio	t	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]	\N	\N	\N	18	\N	5	Capital Gains Tax Information	Please fill in this section as applicable	\N	\N	\N	\N	\N	\N
234	10	List all such assets sold?	textarea	t	\N	\N	\N	\N	Only mention type of all assets sold during the FY like shares, cryptos, investment property (residential/commercial) etc. If none, then simply write "Not applicable" to proceed.	19	\N	5	Capital Gains Tax Information	Please fill in this section as applicable	\N	\N	\N	\N	\N	\N
235	10	Do you have any Investment Property generating rental income for you during this FY?	radio	t	\N	[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]	\N	\N	\N	20	\N	6	Investment Property and Other Income	Any investment property whether in Australia or overseas which has generated rental income during the year	\N	\N	\N	\N	\N	\N
236	10	Please provide full address of each such investment property	textarea	t	\N	\N	\N	\N	If the answer was no to previous question, simply mention "Not Applicable" to proceed further.	21	\N	6	Investment Property and Other Income	Any investment property whether in Australia or overseas which has generated rental income during the year	\N	\N	\N	\N	\N	\N
237	10	Do you earn any other income other than salary? E.g. running a side-gig, business etc. (whether as a sole trader or on ABN)	textarea	t	\N	\N	\N	\N	Business can be any sort of commercial or trading activity with the intent of earning income or profit like Uber driving etc. If the answer was no to previous question, simply mention "Not Applicable" to proceed further.	22	\N	6	Investment Property and Other Income	Any investment property whether in Australia or overseas which has generated rental income during the year	\N	\N	\N	\N	\N	\N
238	10	Work from Home Expenses	textarea	t	\N	\N	\N	\N	Mention # of days in a week worked from home in a year of 52 weeks, including hours worked per day from home. Eg. 2 days in a week, 8 hrs a day.	23	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below. This will also be discussed and reconfirmed during your phone tax consultation session. If any expense is not required, just mention "Nil" or "Not Applicable" to proceed further.	\N	\N	\N	\N	\N	\N
239	10	Home Office Set-up	textarea	t	\N	\N	\N	\N	This includes purchase of any desk, chair, stationery, office supplies etc. in relation to your work only.	24	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
240	10	Educational expenses	textarea	t	\N	\N	\N	\N	Any course / training pursued in relation to your present job which was not reimbursed by your employer.	25	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
241	10	Work Related Car Expenses	textarea	t	\N	\N	\N	\N	Any work-related car travel (not including commuting to/from work).	26	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
242	10	Travel Exps (Work Related Only and should be overnight stay related)	textarea	t	\N	\N	\N	\N	Day to day office going and coming expenses are not considered as Travel exps for deduction purpose. But please discuss during your telephonic tax consultation.	27	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
243	10	Uniform/ Laundry Expenses	textarea	t	\N	\N	\N	\N	This includes any Protective clothing laundry as well.	28	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
244	10	Union/ Annual Membership Fees paid	textarea	t	\N	\N	\N	\N	This can be annual membership fee paid to any professional organisation in relation to your work.	29	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
245	10	Donations to approved Charities	textarea	t	\N	\N	\N	\N	\N	30	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
246	10	Tax Agent Fee	textarea	t	\N	\N	\N	\N	Fees paid to your tax agent last year	31	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
247	10	Income Protection Insurance	textarea	t	\N	\N	\N	\N	\N	32	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
248	10	Tools, Equipment, or any asset purchased	textarea	t	\N	\N	\N	\N	\N	33	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
249	10	Any other Deductions	textarea	t	\N	\N	\N	\N	List down any other deduction that you would like to claim	34	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
250	10	Upload all invoices/supportings to claim your deductions in Tax Return	file	t	\N	\N	\N	\N	Note: Supporting such as invoices/receipts are required by ATO in order to claim an expense deduction, specially for any amount over $150, whether individual or in aggregate. If the space is less, you can email all supporting with proper file name for identification purpose.	35	\N	7	Personal Expense Deductions	Mention all expenses that you wish to claim deduction including the amount in $ in this section below.	\N	\N	\N	\N	\N	\N
251	10	Authorisation	radio	t	\N	[{"value": "agree", "label": "I Agree"}]	\N	\N	\N	36	\N	7	Personal Expense Deductions	I/we hereby authorise the Tax Agent to act on my/our behalf in all matters related to the preparation, lodgement, and processing of my/our tax return.	\N	\N	\N	\N	\N	\N
252	11	Name of the SMSF	text	t	f	null	null	e.g., Smith Family Superannuation Fund	\N	0	2026-01-20 06:00:58.589015	1	Fund Information	Basic details about the SMSF being audited	f	\N	1	10	\N	\N
253	11	ABN of the SMSF	text	t	f	null	null	XX XXX XXX XXX	\N	1	2026-01-20 06:00:58.592417	1	\N	\N	f	\N	1	10	\N	\N
254	11	Financial Year End Date	select	t	f	["30 June 2024", "30 June 2025", "30 June 2026", "30 June 2027"]	null	\N	Select the financial year being audited	2	2026-01-20 06:00:58.593684	1	\N	\N	f	\N	1	10	\N	\N
256	11	Number of Members	select	t	f	["1", "2", "3", "4", "5", "6"]	null	\N	\N	4	2026-01-20 06:00:58.596853	1	\N	\N	f	\N	1	10	\N	\N
257	11	Trust Deed (including all amendments)	file	t	f	null	null	\N	Upload the current Trust Deed and any amendments made since establishment	5	2026-01-20 06:00:58.598836	2	Governing Documents (Permanent Files)	Upload the governing documents of your SMSF. These documents establish and govern the operation of your fund.	f	\N	1	10	\N	\N
258	11	Investment Strategy (current)	file	t	f	null	null	\N	Must be reviewed annually and reflect actual investments held. Should consider risk, return, liquidity, diversification, and insurance needs of members.	6	2026-01-20 06:00:58.600672	2	\N	\N	f	\N	1	10	\N	\N
259	11	Trustee Declarations (all trustees)	file	t	f	null	null	\N	ATO Trustee Declaration forms signed by all trustees within 21 days of appointment	7	2026-01-20 06:00:58.602262	2	\N	\N	f	\N	1	10	\N	\N
260	11	Trustee/Member Consent Forms	file	t	f	null	null	\N	Consent to act as trustee and member of the SMSF	8	2026-01-20 06:00:58.603163	2	\N	\N	f	\N	1	10	\N	\N
261	11	Minutes of Trustee Meetings (for the financial year)	file	t	f	null	null	\N	Include minutes for investment decisions, pension commencement, contributions acceptance, etc.	9	2026-01-20 06:00:58.60413	2	\N	\N	f	\N	1	10	\N	\N
262	11	ASIC Company Extract (for Corporate Trustee only)	file	f	f	null	null	\N	Current ASIC extract showing directors and shareholders of the corporate trustee company	10	2026-01-20 06:00:58.605053	2	\N	\N	f	\N	1	10	\N	\N
263	11	Financial Statements (Balance Sheet & Operating Statement)	file	t	f	null	null	\N	Includes Statement of Financial Position (Balance Sheet) and Operating Statement (Profit & Loss) for the financial year	11	2026-01-20 06:00:58.605985	3	Financial Statements & Tax Records	Provide the financial statements and tax records for the audit year	f	\N	1	10	\N	\N
264	11	Member Statements	file	t	f	null	null	\N	Individual member account balances and movement summaries	12	2026-01-20 06:00:58.606939	3	\N	\N	f	\N	1	10	\N	\N
265	11	General Ledger / Trial Balance	file	t	f	null	null	\N	Detailed transaction listing for the financial year	13	2026-01-20 06:00:58.607897	3	\N	\N	f	\N	1	10	\N	\N
266	11	Prior Year Audit Report	file	f	f	null	null	\N	Previous year's Independent Auditor's Report (if not first year audit)	14	2026-01-20 06:00:58.608759	3	\N	\N	f	\N	1	10	\N	\N
267	11	Prior Year Tax Return	file	f	f	null	null	\N	Previous year's SMSF Annual Return lodged with ATO	15	2026-01-20 06:00:58.610103	3	\N	\N	f	\N	1	10	\N	\N
268	11	ATO Rollover Benefit Statements (if applicable)	file	f	f	null	null	\N	For any rollovers received during the year	16	2026-01-20 06:00:58.610998	3	\N	\N	f	\N	1	10	\N	\N
269	11	How many bank accounts does the SMSF have?	number	t	f	null	{"min": 1}	\N	Include cash management accounts, term deposits held at banks, etc.	17	2026-01-20 06:00:58.612134	4	Bank Account Records	Provide complete bank records for ALL SMSF bank accounts	f	\N	1	10	\N	\N
270	11	Bank Statements (Full Year: 1 July to 30 June)	file	t	t	null	null	\N	Complete bank statements for ALL SMSF accounts covering the entire financial year. Must show opening and closing balances.	18	2026-01-20 06:00:58.613071	4	\N	\N	f	\N	1	10	\N	\N
271	11	Bank Reconciliation at 30 June	file	t	f	null	null	\N	Bank reconciliation showing outstanding items at year end	19	2026-01-20 06:00:58.613967	4	\N	\N	f	\N	1	10	\N	\N
272	11	Term Deposit Statements/Certificates	file	f	f	null	null	\N	Upload if the SMSF holds term deposits	20	2026-01-20 06:00:58.614919	4	\N	\N	f	\N	1	10	\N	\N
273	11	Is the bank account held in the name of the SMSF (not personal names)?	radio	t	f	["Yes", "No"]	null	\N	SMSF funds must not be mixed with personal funds	21	2026-01-20 06:00:58.615925	4	\N	\N	f	\N	1	10	\N	\N
274	11	Does the SMSF hold listed shares, ETFs, or managed funds?	radio	t	f	["Yes", "No"]	null	\N	\N	22	2026-01-20 06:00:58.616947	5	Listed Investments (Shares, ETFs, Managed Funds)	Provide records for all listed investments held by the SMSF	f	\N	1	10	\N	\N
275	11	Share/Investment Portfolio Report at 30 June	file	f	f	null	null	\N	Portfolio valuation showing all holdings and market values at 30 June	23	2026-01-20 06:00:58.617975	5	\N	\N	f	\N	1	10	\N	\N
276	11	Buy/Sell Contract Notes (for transactions during the year)	file	f	t	null	null	\N	Contract notes for all share purchases and sales during the financial year	24	2026-01-20 06:00:58.618954	5	\N	\N	f	\N	1	10	\N	\N
277	11	Dividend Statements	file	f	t	null	null	\N	Dividend statements and Distribution statements received during the year	25	2026-01-20 06:00:58.61991	5	\N	\N	f	\N	1	10	\N	\N
278	11	Corporate Actions Documentation	file	f	f	null	null	\N	Documentation for share splits, buy-backs, mergers, etc. if applicable	26	2026-01-20 06:00:58.620833	5	\N	\N	f	\N	1	10	\N	\N
279	11	CHESS Holding Statements	file	f	f	null	null	\N	CHESS statements showing share ownership registration	27	2026-01-20 06:00:58.621715	5	\N	\N	f	\N	1	10	\N	\N
280	11	Does the SMSF own property?	radio	t	f	["Yes", "No"]	null	\N	\N	28	2026-01-20 06:00:58.622691	6	Property Investments	Complete this section if the SMSF owns real property (residential or commercial)	f	\N	1	10	\N	\N
281	11	Property Type	select	f	f	["Residential", "Commercial", "Both Residential and Commercial"]	null	\N	Note: Residential property cannot be lived in by members or related parties	29	2026-01-20 06:00:58.623648	6	\N	\N	f	\N	1	10	\N	\N
282	11	Certificate of Title / Title Search	file	f	f	null	null	\N	Current title search showing SMSF/trustee as registered owner (required every 3 years minimum)	30	2026-01-20 06:00:58.624639	6	\N	\N	f	\N	1	10	\N	\N
283	11	Purchase Contract and Settlement Statement	file	f	f	null	null	\N	Required if property was purchased during the audit year	31	2026-01-20 06:00:58.625628	6	\N	\N	f	\N	1	10	\N	\N
284	11	Property Valuation at 30 June (Market Value)	file	f	f	null	null	\N	Independent valuation or evidence supporting market value at year end. For 2025 and beyond, valuations are critical due to proposed Div 296 tax on balances over $3M.	32	2026-01-20 06:00:58.62659	6	\N	\N	f	\N	1	10	\N	\N
285	11	Rental/Lease Agreements	file	f	f	null	null	\N	Current lease agreement with tenant	33	2026-01-20 06:00:58.627436	6	\N	\N	f	\N	1	10	\N	\N
286	11	Property Management Statements	file	f	t	null	null	\N	Statements from property manager showing rental income and expenses	34	2026-01-20 06:00:58.628375	6	\N	\N	f	\N	1	10	\N	\N
287	11	Property Expense Invoices (Insurance, Rates, Repairs)	file	f	t	null	null	\N	Council rates, water rates, insurance, repairs, and maintenance invoices	35	2026-01-20 06:00:58.629329	6	\N	\N	f	\N	1	10	\N	\N
288	11	Is the property leased to a related party?	radio	f	f	["Yes - Business Real Property", "No"]	null	\N	Related party leasing is only permitted for business real property at market rent	36	2026-01-20 06:00:58.630165	6	\N	\N	f	\N	1	10	\N	\N
289	11	Does the SMSF have a Limited Recourse Borrowing Arrangement (LRBA)?	radio	t	f	["Yes", "No"]	null	\N	\N	37	2026-01-20 06:00:58.631057	7	Limited Recourse Borrowing Arrangement (LRBA)	Complete if the SMSF has borrowed money to purchase assets	f	\N	1	10	\N	\N
290	11	Loan Agreement	file	f	f	null	null	\N	LRBA loan agreement document	38	2026-01-20 06:00:58.632068	7	\N	\N	f	\N	1	10	\N	\N
291	11	Bare Trust Deed	file	f	f	null	null	\N	Holding trust/bare trust deed for the LRBA asset	39	2026-01-20 06:00:58.632943	7	\N	\N	f	\N	1	10	\N	\N
292	11	Loan Statements (Full Year)	file	f	t	null	null	\N	Loan statements showing principal and interest payments for the year	40	2026-01-20 06:00:58.633801	7	\N	\N	f	\N	1	10	\N	\N
293	11	Is the LRBA from a related party?	radio	f	f	["Yes", "No"]	null	\N	Related party LRBAs must comply with ATO safe harbour terms	41	2026-01-20 06:00:58.63468	7	\N	\N	f	\N	1	10	\N	\N
294	11	Does the SMSF hold investments in private companies or trusts?	radio	t	f	["Yes", "No"]	null	\N	\N	42	2026-01-20 06:00:58.635523	8	Private Company & Trust Investments	Complete if the SMSF holds investments in unlisted/private companies or trusts	f	\N	1	10	\N	\N
295	11	Share/Unit Certificates	file	f	f	null	null	\N	Certificates showing ownership of shares in private companies or units in trusts	43	2026-01-20 06:00:58.636384	8	\N	\N	f	\N	1	10	\N	\N
296	11	Financial Statements of Private Entity	file	f	t	null	null	\N	Audited or reviewed financial statements of the private company/trust	44	2026-01-20 06:00:58.63718	8	\N	\N	f	\N	1	10	\N	\N
297	11	Tax Returns of Private Entity	file	f	f	null	null	\N	Income tax returns of the private company/trust	45	2026-01-20 06:00:58.638058	8	\N	\N	f	\N	1	10	\N	\N
298	11	Valuation of Private Investment at 30 June	file	f	f	null	null	\N	Documentation supporting the market value of private investments	46	2026-01-20 06:00:58.638884	8	\N	\N	f	\N	1	10	\N	\N
299	11	Is the private entity a related party of the SMSF?	radio	f	f	["Yes", "No"]	null	\N	In-house asset rules may apply to related party investments	47	2026-01-20 06:00:58.639743	8	\N	\N	f	\N	1	10	\N	\N
300	11	Does the SMSF hold cryptocurrency?	radio	t	f	["Yes", "No"]	null	\N	\N	48	2026-01-20 06:00:58.640591	9	Cryptocurrency & Other Assets	Complete if the SMSF holds cryptocurrency or other alternative investments	f	\N	1	10	\N	\N
301	11	Cryptocurrency Exchange Statements	file	f	f	null	null	\N	Full year statements from crypto exchanges showing holdings and transactions	49	2026-01-20 06:00:58.641448	9	\N	\N	f	\N	1	10	\N	\N
302	11	Cryptocurrency Wallet Holdings at 30 June	file	f	f	null	null	\N	Screenshot or export of wallet holdings with market values at 30 June	50	2026-01-20 06:00:58.642293	9	\N	\N	f	\N	1	10	\N	\N
303	11	Does the SMSF hold any other alternative investments?	multiselect	t	f	["Collectibles (art, wine, etc.)", "Precious metals (gold, silver)", "Foreign assets", "Options/Derivatives", "None of the above"]	null	\N	Note: Collectibles and personal use assets have strict storage and insurance requirements	51	2026-01-20 06:00:58.643093	9	\N	\N	f	\N	1	10	\N	\N
304	11	Other Asset Documentation	file	f	t	null	null	\N	Provide valuations and ownership documents for any other assets held	52	2026-01-20 06:00:58.643964	9	\N	\N	f	\N	1	10	\N	\N
305	11	Types of contributions received during the year	multiselect	t	f	["Employer (SG) contributions", "Salary sacrifice contributions", "Personal deductible contributions", "Non-concessional (after-tax) contributions", "Spouse contributions", "Downsizer contributions", "Government co-contributions", "Rollovers from other funds", "No contributions received"]	null	\N	\N	53	2026-01-20 06:00:58.644715	10	Contributions	Information about contributions received during the financial year	f	\N	1	10	\N	\N
306	11	Contribution Receipts/Remittance Advices	file	f	t	null	null	\N	Documentation showing contributions received and their classification	54	2026-01-20 06:00:58.645575	10	\N	\N	f	\N	1	10	\N	\N
307	11	Section 290-170 Notices (Notice of Intent to Claim Deduction)	file	f	f	null	null	\N	Required for personal contributions claimed as tax deductions	55	2026-01-20 06:00:58.646435	10	\N	\N	f	\N	1	10	\N	\N
308	11	Were all contributions received within 28 days of the contribution date?	radio	t	f	["Yes", "No", "Not sure"]	null	\N	Contributions must be allocated within 28 days of receipt	56	2026-01-20 06:00:58.647379	10	\N	\N	f	\N	1	10	\N	\N
309	11	Any ATO Notices received (Div 293, Excess Contributions, etc.)?	file	f	t	null	null	\N	Upload any ATO determination notices received	57	2026-01-20 06:00:58.648063	10	\N	\N	f	\N	1	10	\N	\N
310	11	Is any member receiving a pension from the SMSF?	radio	t	f	["Yes", "No"]	null	\N	\N	58	2026-01-20 06:00:58.64888	11	Pension Payments	Complete if any member is receiving a pension from the SMSF	f	\N	1	10	\N	\N
311	11	Pension Type	multiselect	f	f	["Account-based pension", "Transition to retirement pension", "Death benefit pension", "Disability pension"]	null	\N	\N	59	2026-01-20 06:00:58.649749	11	\N	\N	f	\N	1	10	\N	\N
312	11	Pension Commencement Documentation	file	f	f	null	null	\N	Trustee minutes and member election to commence pension	60	2026-01-20 06:00:58.650528	11	\N	\N	f	\N	1	10	\N	\N
313	11	Were minimum pension payments made for the year?	radio	f	f	["Yes", "No"]	null	\N	Minimum pension must be paid by 30 June to retain pension tax exemption	61	2026-01-20 06:00:58.651261	11	\N	\N	f	\N	1	10	\N	\N
314	11	Actuarial Certificate (if required)	file	f	f	null	null	\N	Required if the fund has both accumulation and pension members to determine tax-exempt proportion	62	2026-01-20 06:00:58.652114	11	\N	\N	f	\N	1	10	\N	\N
315	11	Does the SMSF provide insurance for any members?	radio	t	f	["Yes", "No"]	null	\N	\N	63	2026-01-20 06:00:58.652957	12	Insurance	Details of insurance policies held within the SMSF	f	\N	1	10	\N	\N
316	11	Types of insurance held	multiselect	f	f	["Life insurance", "Total & Permanent Disability (TPD)", "Income protection", "None"]	null	\N	\N	64	2026-01-20 06:00:58.653681	12	\N	\N	f	\N	1	10	\N	\N
317	11	Insurance Policy Documents/Certificates	file	f	t	null	null	\N	Current insurance policy certificates	65	2026-01-20 06:00:58.654569	12	\N	\N	f	\N	1	10	\N	\N
318	11	Has the consideration of insurance been documented in minutes?	radio	f	f	["Yes", "No"]	null	\N	Trustees must consider insurance needs when formulating investment strategy	66	2026-01-20 06:00:58.655337	12	\N	\N	f	\N	1	10	\N	\N
319	11	Have all investments been made on an arm's length basis?	radio	t	f	["Yes", "No", "Not sure"]	null	\N	All transactions must be at market value as if dealing with unrelated parties	67	2026-01-20 06:00:58.656196	13	Compliance Questions	Important compliance questions for the SMSF audit	f	\N	1	10	\N	\N
320	11	Has the SMSF acquired any assets from related parties?	radio	t	f	["Yes", "No"]	null	\N	Only business real property and listed securities can generally be acquired from related parties	68	2026-01-20 06:00:58.657046	13	\N	\N	f	\N	1	10	\N	\N
321	11	Has the SMSF provided financial assistance to members or relatives?	radio	t	f	["Yes", "No"]	null	\N	Loans to members or relatives are prohibited	69	2026-01-20 06:00:58.657895	13	\N	\N	f	\N	1	10	\N	\N
322	11	Are all assets held in the name of the SMSF trustees?	radio	t	f	["Yes", "No"]	null	\N	Assets must be held in trustee names and kept separate from personal assets	70	2026-01-20 06:00:58.658734	13	\N	\N	f	\N	1	10	\N	\N
323	11	Have all trustees met their trustee declaration obligations?	radio	t	f	["Yes", "No"]	null	\N	\N	71	2026-01-20 06:00:58.659576	13	\N	\N	f	\N	1	10	\N	\N
324	11	Is the fund's sole purpose to provide retirement benefits to members?	radio	t	f	["Yes", "No"]	null	\N	The sole purpose test is fundamental to SMSF compliance	72	2026-01-20 06:00:58.660445	13	\N	\N	f	\N	1	10	\N	\N
325	11	Are there any matters the auditor should be aware of?	textarea	f	f	null	null	Describe any unusual transactions, changes to the fund, or other relevant information...	Include any significant events, contraventions, or matters requiring attention	73	2026-01-20 06:00:58.661352	14	Additional Information & Declaration	Any additional information and final declaration	f	\N	1	10	\N	\N
326	11	Other Supporting Documents	file	f	t	null	null	\N	Upload any other documents relevant to the audit	74	2026-01-20 06:00:58.662256	14	\N	\N	f	\N	1	10	\N	\N
327	11	I confirm that all information provided is true and complete to the best of my knowledge	radio	t	f	["Yes, I confirm"]	null	\N	This declaration is required to submit the audit documents	75	2026-01-20 06:00:58.663063	14	\N	\N	f	\N	1	10	\N	\N
328	11	I understand that the auditor may request additional information if required	radio	t	f	["Yes, I understand"]	null	\N	The auditor must be provided all requested documents within 14 days	76	2026-01-20 06:00:58.663966	14	\N	\N	f	\N	1	10	\N	\N
\.


--
-- Data for Name: form_responses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.form_responses (id, form_id, user_id, service_request_id, response_data, responses, submitted_at, updated_at, status) FROM stdin;
\.


--
-- Data for Name: forms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forms (id, name, description, form_type, is_active, created_by_id, created_at, updated_at, company_id, is_default, cloned_from_id, status) FROM stdin;
1	Individual Tax Return Information	Please provide the following information for your tax return	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-18 05:05:44.453214	2026-01-18 05:05:44.453215	\N	t	\N	published
2	BAS Information Form	Provide your business activity details for the period	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-18 05:05:44.471581	2026-01-18 05:05:44.471582	\N	t	\N	published
3	Rental Property Information	Details about your investment property for tax purposes	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-18 05:05:44.474911	2026-01-18 05:05:44.474912	\N	t	\N	published
4	SMSF Setup Application	Information required to establish your Self-Managed Super Fund	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-18 05:05:44.480682	2026-01-18 05:05:44.480683	\N	t	\N	published
5	Company Registration Form	Information required to register your new company	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-18 05:05:44.484202	2026-01-18 05:05:44.484203	\N	t	\N	published
6	Company Incorporation Form	Complete this form to register your new company with ASIC	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-18 05:05:44.520772	2026-01-18 05:05:44.520774	\N	t	\N	published
7	SMSF Setup Form	Complete this form to establish your Self-Managed Super Fund	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-18 05:05:44.545466	2026-01-18 05:05:44.545467	\N	t	\N	published
8	SMSF Annual Compliance Questionnaire	Annual compliance questionnaire for Self-Managed Super Fund clients	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-18 05:05:44.56164	2026-01-18 05:05:44.561641	\N	t	\N	published
9	Company Annual Compliance Questionnaire	Annual compliance questionnaire for company clients	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-18 05:05:44.578317	2026-01-18 05:05:44.578318	\N	t	\N	published
10	Individual Tax Return Information (Copy)	Please provide the following information for your tax return	service	t	ec86adcd-8297-4717-b1db-a4b5bc333993	2026-01-18 08:08:51.096287	2026-01-18 08:08:51.096289	e42c76c5-c662-4160-ae8e-3268f82047a0	f	1	draft
11	SMSF Annual Audit Form	Complete this form and upload all required documents for your SMSF Annual Audit. All assets must be valued at market value as at 30 June.	service	t	7c439590-df69-48fd-a1b9-847ae38b94a3	2026-01-20 06:00:58.585643	2026-01-20 06:00:58.670093	\N	t	\N	published
\.


--
-- Data for Name: impersonation_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.impersonation_sessions (id, admin_id, impersonated_user_id, started_at, ended_at, reason, ip_address, user_agent, action_count) FROM stdin;
\.


--
-- Data for Name: import_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.import_logs (id, company_id, imported_by_id, import_type, filename, total_rows, imported_count, skipped_count, error_count, errors, created_at) FROM stdin;
\.


--
-- Data for Name: invoice_line_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.invoice_line_items (id, invoice_id, description, quantity, unit_price, total, service_id, "order", is_tax_exempt, created_at) FROM stdin;
\.


--
-- Data for Name: invoice_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.invoice_payments (id, invoice_id, amount, payment_method, reference, notes, status, stripe_payment_id, stripe_payment_intent_id, stripe_charge_id, refund_amount, refunded_at, payment_date, created_at) FROM stdin;
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.invoices (id, invoice_number, reference, company_id, client_id, service_request_id, issue_date, due_date, subtotal, tax_rate, tax_amount, discount_amount, discount_description, total, amount_paid, balance_due, currency, status, notes, internal_notes, payment_terms, payment_link, stripe_invoice_id, sent_at, viewed_at, paid_at, created_at, updated_at, created_by_id) FROM stdin;
\.


--
-- Data for Name: job_notes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.job_notes (id, service_request_id, created_by_id, note_type, content, time_spent_minutes, created_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, user_id, title, message, type, link, is_read, created_at) FROM stdin;
1	40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	Invoice Ready	Invoice for SMSF Super Setup is ready for payment	info	/requests/898351d7-7220-485c-b240-004f3a6b0047	f	2026-01-18 06:51:57.371402
2	ec86adcd-8297-4717-b1db-a4b5bc333993	New Service Request	Adarsh Aggarwal submitted a request for SMSF Annual Audit	info	/requests/6ebb337c-e964-4b23-b429-7b10ccb5ff4a	f	2026-01-20 05:45:52.815331
4	7c439590-df69-48fd-a1b9-847ae38b94a3	New Service Request	Adarsh Aggarwal submitted a request for SMSF Annual Audit	info	/requests/6ebb337c-e964-4b23-b429-7b10ccb5ff4a	f	2026-01-20 05:45:52.826281
5	25775935-d117-491b-8ca5-e1f0cbc5ff4b	New Service Request	Adarsh Aggarwal submitted a request for SMSF Annual Audit	info	/requests/6ebb337c-e964-4b23-b429-7b10ccb5ff4a	t	2026-01-20 05:45:52.830394
3	becf0567-7a4d-4c8f-9c8c-408205ef5015	New Service Request	Adarsh Aggarwal submitted a request for SMSF Annual Audit	info	/requests/6ebb337c-e964-4b23-b429-7b10ccb5ff4a	t	2026-01-20 05:45:52.821358
\.


--
-- Data for Name: otps; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.otps (id, user_id, code, purpose, expires_at, is_used, created_at) FROM stdin;
7	25775935-d117-491b-8ca5-e1f0cbc5ff4b	901568	password_reset	2026-01-20 04:30:01.842311	t	2026-01-20 04:20:01.843139
8	25775935-d117-491b-8ca5-e1f0cbc5ff4b	987347	login_2fa	2026-01-20 04:30:29.29276	t	2026-01-20 04:20:29.293019
\.


--
-- Data for Name: queries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.queries (id, service_request_id, sender_id, message, attachment_url, created_at, is_internal) FROM stdin;
1	df73d064-d3a7-4af4-af17-ecf575e29c39	314678e1-49e6-41bc-8886-29b242067cab	Hi James, I need clarification on the work from home expenses. Can you provide the calculation method you used?	\N	2025-12-09 05:05:46.302776	f
2	df73d064-d3a7-4af4-af17-ecf575e29c39	40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	Hi, I used the fixed rate method - 67 cents per hour. I worked from home approximately 1200 hours during the year. I have a log if needed.	\N	2025-12-10 05:05:46.302824	f
3	df73d064-d3a7-4af4-af17-ecf575e29c39	314678e1-49e6-41bc-8886-29b242067cab	Thanks for clarifying. That works out to $804. I'll include this in your return.	\N	2025-12-11 05:05:46.302842	f
4	a220a318-4b0e-446a-8b74-182dfab81ce2	314678e1-49e6-41bc-8886-29b242067cab	Hi James, for your rental property at 15 Investment Ave, I noticed you haven't provided the depreciation schedule. Do you have one from a quantity surveyor?	\N	2026-01-16 05:05:46.308263	f
5	7d7301da-0cd3-491e-84a3-8b3a846b374b	314678e1-49e6-41bc-8886-29b242067cab	Hi James, I need clarification on the work from home expenses. Can you provide the calculation method you used?	\N	2025-12-11 05:45:42.58634	f
6	7d7301da-0cd3-491e-84a3-8b3a846b374b	40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	Hi, I used the fixed rate method - 67 cents per hour. I worked from home approximately 1200 hours during the year. I have a log if needed.	\N	2025-12-12 05:45:42.586396	f
7	7d7301da-0cd3-491e-84a3-8b3a846b374b	314678e1-49e6-41bc-8886-29b242067cab	Thanks for clarifying. That works out to $804. I'll include this in your return.	\N	2025-12-13 05:45:42.586417	f
\.


--
-- Data for Name: request_audit_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.request_audit_log (id, service_request_id, user_id, action, old_value, new_value, created_at) FROM stdin;
\.


--
-- Data for Name: request_audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.request_audit_logs (id, service_request_id, modified_by_id, field_name, old_value, new_value, created_at) FROM stdin;
\.


--
-- Data for Name: request_state_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.request_state_history (id, service_request_id, from_state, to_state, changed_by_id, changed_at, duration_in_previous_state, notes) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, description, permissions, created_at) FROM stdin;
1	super_admin	Full system access	{"all": true}	2026-01-18 05:05:41.337857
2	admin	Administrative access	{"manage_users": true, "manage_requests": true, "view_reports": true}	2026-01-18 05:05:41.339556
3	accountant	Accountant access	{"manage_assigned_requests": true, "add_notes": true}	2026-01-18 05:05:41.340888
4	user	Client user access	{"view_own_requests": true, "create_requests": true}	2026-01-18 05:05:41.341943
5	external_accountant	External accountant access	{"manage_assigned_requests": true, "add_notes": true, "external": true}	2026-01-20 04:23:51.677123
\.


--
-- Data for Name: scheduled_emails; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scheduled_emails (id, company_id, recipient_type, recipient_email, recipient_user_id, recipient_filter, subject, body_html, template_id, template_context, scheduled_at, timezone, status, sent_at, error_message, recipients_count, sent_count, failed_count, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: service_renewals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_renewals (id, user_id, service_id, company_id, last_completed_at, last_request_id, next_due_date, reminders_sent, last_reminder_at, status, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: service_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_requests (id, user_id, service_id, assigned_accountant_id, status, internal_notes, invoice_raised, invoice_paid, invoice_amount, payment_link, created_at, updated_at, completed_at, xero_reference_job_id, internal_reference, request_number, description, actual_cost, cost_notes, labor_hours, labor_rate, deadline_date, priority, current_step_id) FROM stdin;
df73d064-d3a7-4af4-af17-ecf575e29c39	40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	1	314678e1-49e6-41bc-8886-29b242067cab	completed	FY2024 tax return completed. Client had good documentation.	t	t	350.00	https://payment.example.com/pay/24094	2025-12-04 05:05:46.301306	2026-01-18 05:05:46.302012	2025-12-09 05:05:46.301345	\N	\N	REQ-000001	\N	\N	\N	0.00	\N	\N	normal	step-completed
7d7301da-0cd3-491e-84a3-8b3a846b374b	40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	40	314678e1-49e6-41bc-8886-29b242067cab	completed	FY2024 tax return completed. Client had good documentation.	t	t	350.00	https://payment.example.com/pay/51281	2025-12-06 05:45:42.581747	2026-01-20 05:45:42.582845	2025-12-11 05:45:42.581794	\N	\N	REQ-000002	\N	\N	\N	0.00	\N	\N	normal	step-completed
687e2d92-8e60-4e54-b334-e518cce2ce99	40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	2	314678e1-49e6-41bc-8886-29b242067cab	processing	Q2 BAS - All documents received. GST calculations in progress.	t	t	150.00	https://payment.example.com/pay/69328	2026-01-08 05:05:46.305956	2026-01-18 05:05:46.306226	\N	\N	\N	REQ-000003	\N	\N	\N	0.00	\N	\N	normal	step-processing
a220a318-4b0e-446a-8b74-182dfab81ce2	40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	3	314678e1-49e6-41bc-8886-29b242067cab	query_raised	Waiting for depreciation schedule from client.	f	f	\N	\N	2026-01-13 05:05:46.30748	2026-01-18 05:05:46.307745	\N	\N	\N	REQ-000004	\N	\N	\N	0.00	\N	\N	normal	step-query-raised
898351d7-7220-485c-b240-004f3a6b0047	40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	4	314678e1-49e6-41bc-8886-29b242067cab	processing	New SMSF setup request. Need to prepare trust deed and corporate trustee setup.	t	f	500.00	\N	2026-01-15 05:05:46.309946	2026-01-18 06:51:57.376923	\N	\N	\N	REQ-000005	\N	\N	\N	0.00	\N	\N	normal	step-processing
81eb7065-b590-463e-a889-61c818a837a2	40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	5	\N	pending		f	f	\N	\N	2026-01-17 05:05:46.311452	2026-01-18 05:05:46.311814	\N	\N	\N	REQ-000006	\N	\N	\N	0.00	\N	\N	normal	step-pending
67441110-3ff6-4070-bf8c-a60fb68760bd	f5522e43-8f01-4872-b439-66fbdc7717d4	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q2  FY-26	t	f	50.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027221	\N	REQ-000009	\N	\N	\N	0.00	\N	\N	normal	step-pending
5b74e999-e03a-4c0c-9e77-61c1873e6f2f	f5522e43-8f01-4872-b439-66fbdc7717d4	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q3  FY-26	t	f	50.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027221	\N	REQ-000010	\N	\N	\N	0.00	\N	\N	normal	step-pending
abd35ec7-52d9-4bb4-af96-e8d0b8534a9a	f5522e43-8f01-4872-b439-66fbdc7717d4	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q4  FY-26	t	f	50.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027221	\N	REQ-000011	\N	\N	\N	0.00	\N	\N	normal	step-pending
10ce0dea-255c-422a-8689-58f2658a65a5	f5522e43-8f01-4872-b439-66fbdc7717d4	9	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY26 CTR	t	f	500.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027170	\N	REQ-000012	\N	\N	\N	0.00	\N	\N	normal	step-pending
f9da41c1-7682-4d34-a9bf-825d9dae354d	12543417-929e-446b-b571-6733c14c3d93	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	300.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000013	\N	\N	\N	0.00	\N	\N	normal	step-pending
bd7595dc-ec8f-4316-a73e-9b5c750a5687	85ebf4e1-7cba-4c78-aeb0-3e2c99864693	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - FY-26	f	f	200.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring job	\N	REQ-000014	\N	\N	\N	0.00	\N	\N	normal	step-pending
3e342a06-7add-4511-8ed3-243c2b3aa6ef	85ebf4e1-7cba-4c78-aeb0-3e2c99864693	8	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	Company Annual Accounts	f	f	500.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027175	\N	REQ-000015	\N	\N	\N	0.00	\N	\N	normal	step-pending
b776b63c-1baa-4749-9e3f-bc0e2fc0cb3f	85ebf4e1-7cba-4c78-aeb0-3e2c99864693	9	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY26 CTR	f	f	500.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027176	\N	REQ-000016	\N	\N	\N	0.00	\N	\N	normal	step-pending
13cca763-bda3-4b0d-8054-0be20c1ad563	1b1a0ea2-a363-4263-a4a7-d6b0733ffe10	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY25	f	f	300.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000017	\N	\N	\N	0.00	\N	\N	normal	step-pending
be22b8cd-489b-4f35-a2db-0d20d10ccb33	e9682053-e70e-4dec-9f68-8a3627b4ad84	8	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	in_progress	FY-26 Accounting	f	f	400.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	QB	\N	REQ-000018	\N	\N	\N	0.00	\N	\N	normal	step-pending
832d000e-0911-46e8-bbf6-7271851ea883	e9682053-e70e-4dec-9f68-8a3627b4ad84	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	in_progress	BAS/GST - FY-26	f	f	400.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring job	\N	REQ-000019	\N	\N	\N	0.00	\N	\N	normal	step-pending
2233e8de-ca2b-4eaf-a05f-acc8327b7fa6	e9682053-e70e-4dec-9f68-8a3627b4ad84	9	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY26 CTR	f	f	500.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000020	\N	\N	\N	0.00	\N	\N	normal	step-pending
9af1f594-2b32-46db-b654-8002e4abfe78	3308a7fe-d5f7-40d5-9221-b5ef38d98dc8	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	completed	IT Return FY25	t	t	220.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	2026-01-18 19:54:51.409051	J026959	\N	REQ-000021	\N	\N	\N	0.00	\N	\N	normal	step-completed
7e709b82-013c-43ec-a3ae-b08b42644cfe	3308a7fe-d5f7-40d5-9221-b5ef38d98dc8	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000022	\N	\N	\N	0.00	\N	\N	normal	step-pending
1e6aede1-fcde-4bb2-8980-b6aed59798be	287b3a83-3af1-414b-a9a3-e057a5a3dd09	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	in_progress	BAS/GST - FY-26	t	t	200.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027224	\N	REQ-000023	\N	\N	\N	0.00	\N	\N	normal	step-pending
4e10c14e-9a04-462c-9e28-1e2d0a6c304d	287b3a83-3af1-414b-a9a3-e057a5a3dd09	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	150.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000024	\N	\N	\N	0.00	\N	\N	normal	step-pending
efb0393b-8328-4182-9192-0686f1f67f5e	1af94636-3a5d-4e4e-9e72-602bcc061572	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	completed	BAS/GST - Q1  FY-26	t	f	150.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	2026-01-18 19:54:51.415314	J026888	\N	REQ-000025	\N	\N	\N	0.00	\N	\N	normal	step-completed
ea9fb14d-0dcb-4afb-be04-6206a8a583f2	e89f5907-94d6-4158-b39c-e7809f4648ee	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	completed	IT Return FY25	t	t	136.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	2026-01-18 19:54:51.416486	J026949	\N	REQ-000026	\N	\N	\N	0.00	\N	\N	normal	step-completed
8124db3a-14b3-4a93-a463-247867cd5b91	36dff369-19b4-4e3e-9035-5a280ad60f28	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	completed	IT Return FY25	t	t	136.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	2026-01-18 19:54:51.417687	J026948	\N	REQ-000027	\N	\N	\N	0.00	\N	\N	normal	step-completed
6ebb337c-e964-4b23-b429-7b10ccb5ff4a	fa8ea5f4-b070-41f1-9c37-2567fe97bf93	10	\N	pending	\N	f	f	\N	\N	2026-01-20 05:45:52.794514	2026-01-20 05:45:52.794516	\N	\N	\N	REQ-000097	\N	\N	\N	0.00	\N	\N	normal	step-pending
38677eca-6f40-44be-a6c6-3b57fe16d626	44b7ca23-104a-40b1-bd43-dc273e7fde92	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	completed	BAS/GST - Q1  FY-26	t	f	50.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	2026-01-18 19:54:51.419722	J027057	\N	REQ-000028	\N	\N	\N	0.00	\N	\N	normal	step-completed
9f6a84ef-cdde-4801-86cc-61d19c6ae04f	44b7ca23-104a-40b1-bd43-dc273e7fde92	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q2  FY-26	f	f	50.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027222	\N	REQ-000029	\N	\N	\N	0.00	\N	\N	normal	step-pending
fb19478e-664f-465e-8ba2-9636b457e333	44b7ca23-104a-40b1-bd43-dc273e7fde92	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q3  FY-26	f	f	50.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027222	\N	REQ-000030	\N	\N	\N	0.00	\N	\N	normal	step-pending
e9f7b1fe-8961-4abe-8598-0fd1edf11808	44b7ca23-104a-40b1-bd43-dc273e7fde92	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q4  FY-26	f	f	50.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027222	\N	REQ-000031	\N	\N	\N	0.00	\N	\N	normal	step-pending
0f87c2b7-7b96-4cd2-a140-07506c136ca9	44b7ca23-104a-40b1-bd43-dc273e7fde92	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY25	t	f	150.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027140	\N	REQ-000032	\N	\N	\N	0.00	\N	\N	normal	step-pending
4b7a0646-7bd8-4598-9496-e0e855fc009d	e59bdabc-0a0f-4645-a029-3f31ab5abcad	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY25	t	f	150.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027142	\N	REQ-000033	\N	\N	\N	0.00	\N	\N	normal	step-pending
61cd6ce2-7cf3-45f8-b4d7-43b55529be5a	6914b989-e132-4e22-8874-6d0fabbe4bcd	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - FY-26	f	f	150.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027261	\N	REQ-000034	\N	\N	\N	0.00	\N	\N	normal	step-pending
6307093b-79a4-4f89-8936-452ab1103d4b	6914b989-e132-4e22-8874-6d0fabbe4bcd	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY-26	f	f	150.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000035	\N	\N	\N	0.00	\N	\N	normal	step-pending
a2320ff2-3aeb-49d2-93a7-382a3f4edb2e	60dbe0d8-03c4-45bc-bc60-e2487401986b	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000036	\N	\N	\N	0.00	\N	\N	normal	step-pending
9903af4c-8958-4f53-a932-1a52faefbcb2	e64a351e-71af-42b3-9586-d708481ed7a9	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000037	\N	\N	\N	0.00	\N	\N	normal	step-pending
e2d122c7-b1b3-4269-9680-b5a6baa6ef37	7640efe5-dd39-4106-bf0c-c352216fa045	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	in_progress	FY-26 SMSF Annual Accounts	t	f	1000.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027153	\N	REQ-000038	\N	\N	\N	0.00	\N	\N	normal	step-pending
f06fa727-1b9b-4cda-8bbf-6500ef421759	7640efe5-dd39-4106-bf0c-c352216fa045	6	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY-26 SMSF Audit	f	f	500.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000039	\N	\N	\N	0.00	\N	\N	normal	step-pending
2ef0b070-9089-4522-acb8-4bbc68e30ff7	82d4deb6-abea-47ad-9994-66a46477d4ec	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q1  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	TNG	\N	REQ-000040	\N	\N	\N	0.00	\N	\N	normal	step-pending
65698108-b748-4b30-af49-80fc5bddd395	82d4deb6-abea-47ad-9994-66a46477d4ec	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q2  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027223	\N	REQ-000041	\N	\N	\N	0.00	\N	\N	normal	step-pending
39e21990-5db8-44bb-87fa-5fd46776bb50	82d4deb6-abea-47ad-9994-66a46477d4ec	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q3  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027223	\N	REQ-000042	\N	\N	\N	0.00	\N	\N	normal	step-pending
239496f4-7345-4b5f-85f6-ebc001bd3d01	82d4deb6-abea-47ad-9994-66a46477d4ec	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q4  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027223	\N	REQ-000043	\N	\N	\N	0.00	\N	\N	normal	step-pending
50ad6976-5b73-43e8-ae8f-b2eea52fe142	82d4deb6-abea-47ad-9994-66a46477d4ec	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000044	\N	\N	\N	0.00	\N	\N	normal	step-pending
509016f0-dedf-42b6-9647-c8ac175a3474	0337cf13-ec50-419f-8318-19ab86469874	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000045	\N	\N	\N	0.00	\N	\N	normal	step-pending
effbaef3-5d9d-4f1f-8ad7-9695107e24a0	fb2838b9-9e21-46c1-8a69-5ecdecf420fe	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q1  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	TNG	\N	REQ-000046	\N	\N	\N	0.00	\N	\N	normal	step-pending
5f39e99c-69d5-43da-80e2-058296ded343	fb2838b9-9e21-46c1-8a69-5ecdecf420fe	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q2  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring job	\N	REQ-000047	\N	\N	\N	0.00	\N	\N	normal	step-pending
dff340e4-fe62-4029-939f-76a19e1d3835	fb2838b9-9e21-46c1-8a69-5ecdecf420fe	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q3  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring job	\N	REQ-000048	\N	\N	\N	0.00	\N	\N	normal	step-pending
986cbdc7-4634-4771-ac9c-ed2009510594	fb2838b9-9e21-46c1-8a69-5ecdecf420fe	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q4  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring job	\N	REQ-000049	\N	\N	\N	0.00	\N	\N	normal	step-pending
f70238d4-e351-44f6-a5d6-6ad97ef9fef6	fb2838b9-9e21-46c1-8a69-5ecdecf420fe	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000050	\N	\N	\N	0.00	\N	\N	normal	step-pending
742cc65c-b902-4f85-bdac-f6a1769815b0	ca00d02b-0bd1-4bc6-8809-3f1a63ddc3a7	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q1  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring job	\N	REQ-000051	\N	\N	\N	0.00	\N	\N	normal	step-pending
a1f9c887-7f50-4538-904a-5c6e8fcbb48a	ca00d02b-0bd1-4bc6-8809-3f1a63ddc3a7	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q2  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring job	\N	REQ-000052	\N	\N	\N	0.00	\N	\N	normal	step-pending
8a7ba7b2-6134-4c6e-8b0c-1517197cfbc5	ca00d02b-0bd1-4bc6-8809-3f1a63ddc3a7	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q3  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring job	\N	REQ-000053	\N	\N	\N	0.00	\N	\N	normal	step-pending
47372f9f-8fe5-4ed0-8d58-056ffbb7299d	ca00d02b-0bd1-4bc6-8809-3f1a63ddc3a7	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q4  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring job	\N	REQ-000054	\N	\N	\N	0.00	\N	\N	normal	step-pending
3ef4c53b-5653-408e-9458-0da15437031b	ca00d02b-0bd1-4bc6-8809-3f1a63ddc3a7	9	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000055	\N	\N	\N	0.00	\N	\N	normal	step-pending
e99b2025-8303-4732-983c-4913091f6257	3de320b2-2f5e-473b-b7db-8238b9f8b90e	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000056	\N	\N	\N	0.00	\N	\N	normal	step-pending
39baf080-76ff-4834-9ab5-d9e95f9dfb15	0e1505e5-2c84-4ec9-8ebc-ffd047216d08	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q1  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	TNG	\N	REQ-000057	\N	\N	\N	0.00	\N	\N	normal	step-pending
95ca4df3-a431-427b-92d5-bd6527cdc2ce	0e1505e5-2c84-4ec9-8ebc-ffd047216d08	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q2  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring Job	\N	REQ-000058	\N	\N	\N	0.00	\N	\N	normal	step-pending
898a9c47-1029-4cf5-a89e-7d767f3f0802	0e1505e5-2c84-4ec9-8ebc-ffd047216d08	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q3  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring Job	\N	REQ-000059	\N	\N	\N	0.00	\N	\N	normal	step-pending
6efcb913-ab2d-408c-8f15-afa1b2c4e84a	0e1505e5-2c84-4ec9-8ebc-ffd047216d08	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q4  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring Job	\N	REQ-000060	\N	\N	\N	0.00	\N	\N	normal	step-pending
01d3ada6-1481-475b-aa9a-442a613ab1f9	0e1505e5-2c84-4ec9-8ebc-ffd047216d08	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000061	\N	\N	\N	0.00	\N	\N	normal	step-pending
9c207a88-a999-4a13-a870-a9166e0768ab	4641887d-612f-4767-b0ac-8885dff9302f	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	SMSF FY 26 Accounts & Tax Return	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000062	\N	\N	\N	0.00	\N	\N	normal	step-pending
8b30d084-0d52-4f61-8cbb-b0ad6bda8549	4641887d-612f-4767-b0ac-8885dff9302f	6	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	SMSF Audit FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000063	\N	\N	\N	0.00	\N	\N	normal	step-pending
58573d3a-c10a-430e-8592-0979fb380ec9	5eb30ffa-0906-4204-a470-cb00d4fc0202	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000064	\N	\N	\N	0.00	\N	\N	normal	step-pending
d98b895e-c71c-47d6-8d63-eae8016b6976	3da36d99-addf-4003-ad1b-f3d943aba3e7	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	in_progress	SMSF FY 26 Accounts & Tax Return	f	f	1500.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000065	\N	\N	\N	0.00	\N	\N	normal	step-pending
caae4e8f-0cb6-4bf0-85c8-c399d7a78b49	da454710-22d8-46df-9d3f-f3a5af4abda3	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q1  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring Job	\N	REQ-000066	\N	\N	\N	0.00	\N	\N	normal	step-pending
c7bc4551-22ca-4cf1-bc20-09e5a3fa0bd3	da454710-22d8-46df-9d3f-f3a5af4abda3	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q2  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring Job	\N	REQ-000067	\N	\N	\N	0.00	\N	\N	normal	step-pending
520c57b4-b60a-42c3-ac05-178f7515e708	da454710-22d8-46df-9d3f-f3a5af4abda3	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q3  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring Job	\N	REQ-000068	\N	\N	\N	0.00	\N	\N	normal	step-pending
e52c6a78-a55d-4b5d-b03d-bfdf77ec636d	da454710-22d8-46df-9d3f-f3a5af4abda3	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q4  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring Job	\N	REQ-000069	\N	\N	\N	0.00	\N	\N	normal	step-pending
b6dee411-60ba-4c45-82ec-9c9f3088c89e	da454710-22d8-46df-9d3f-f3a5af4abda3	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000070	\N	\N	\N	0.00	\N	\N	normal	step-pending
16ee3208-4bb0-4310-9fe3-e3d1a6aa8a4d	66f205ed-06e3-4290-9df1-e5100752e263	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST -  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000071	\N	\N	\N	0.00	\N	\N	normal	step-pending
40d7d5b9-9b03-4d24-a0b7-e79c5b116a62	66f205ed-06e3-4290-9df1-e5100752e263	9	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000072	\N	\N	\N	0.00	\N	\N	normal	step-pending
fba4fdac-2b06-42e1-b72a-50fc0148d4d0	a3476853-c261-4f67-9a5f-9a07ac560ae3	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000073	\N	\N	\N	0.00	\N	\N	normal	step-pending
2ccfc148-a06c-4a59-843e-4fadc64530d3	a3476853-c261-4f67-9a5f-9a07ac560ae3	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST -  FY-26	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	Recurring Job	\N	REQ-000074	\N	\N	\N	0.00	\N	\N	normal	step-pending
eb59af1b-4218-469e-8a94-b5b97e260426	83358bf2-31be-40a7-8922-37157dabe6f8	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	completed	FY 25 SMSF Annual Accounts	t	t	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	2026-01-18 19:54:51.460797	J027081	\N	REQ-000075	\N	\N	\N	0.00	\N	\N	normal	step-completed
0641d9f5-e434-446b-8dd5-6fbc4cf095e1	f3b811f8-c93b-4c50-8dc2-6cc1461d17a0	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY25	f	f	130.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J026957	\N	REQ-000092	\N	\N	\N	0.00	\N	\N	normal	step-pending
f963b7f6-bf24-407c-a88e-74ba2ae9b3ea	13abce87-7f77-4f4a-a7f7-510afb2e2d2c	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	IT Return FY25	f	f	130.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J026958	\N	REQ-000093	\N	\N	\N	0.00	\N	\N	normal	step-pending
9e5843ee-26f8-4da9-97b5-9a03218840a2	ccc05a70-89eb-44af-932e-5aea1a97788e	4	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	SMSF Corporate Trust formation	f	f	3500.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000094	\N	\N	\N	0.00	\N	\N	normal	step-pending
94e6b198-aaf1-4aec-a2d2-409d06e40e05	f5522e43-8f01-4872-b439-66fbdc7717d4	8	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY-26 Accounting	t	f	400.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027169	\N	REQ-000007	\N	\N	\N	0.00	\N	\N	normal	step-pending
4fcc9c91-bdd7-4c01-886c-a7f1da7b061c	f5522e43-8f01-4872-b439-66fbdc7717d4	2	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	BAS/GST - Q1  FY-26	t	f	50.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027221	\N	REQ-000008	\N	\N	\N	0.00	\N	\N	normal	step-pending
b8108c61-d0e7-46d2-82ae-ce4180988911	1b9add8a-7660-48e3-80fe-6f7ac12bbf64	1	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	ITR - FY-25	f	f	250.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000091	\N	\N	\N	0.00	\N	\N	normal	step-pending
1205db9c-5208-4761-a95d-075517593a22	ccc05a70-89eb-44af-932e-5aea1a97788e	6	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	SMSF Audit FY26	f	f	550.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000095	\N	\N	\N	0.00	\N	\N	normal	step-pending
015884d4-6841-405f-b769-48fdf36b9066	ccc05a70-89eb-44af-932e-5aea1a97788e	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 26 SMSF Annual Job - Accounting, Tax Return	f	f	1050.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000096	\N	\N	\N	0.00	\N	\N	normal	step-pending
1944fbd4-09d2-48aa-8b58-087e3d792380	32f4c8ce-e7e6-447c-b351-a4940036aa9f	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 25 SMSF Annual Accounts	f	f	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J024529	\N	REQ-000076	\N	\N	\N	0.00	\N	\N	normal	step-pending
3501d997-18c4-46da-b124-1ffef0d9b6e6	dcb04f00-35af-48a2-8499-38fc84227341	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 25 SMSF Annual Accounts	f	f	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027082	\N	REQ-000077	\N	\N	\N	0.00	\N	\N	normal	step-pending
09fd9967-e1dc-46e6-96a8-aa4a046db569	744388d4-10fe-40fd-8e1c-52e4df7c2f04	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 23 SMSF Annual Accounts	f	f	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027083	\N	REQ-000078	\N	\N	\N	0.00	\N	\N	normal	step-pending
9e7ab4d4-dd01-4e1a-af9f-d2157c91121f	744388d4-10fe-40fd-8e1c-52e4df7c2f04	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 24 SMSF Annual Accounts	f	f	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027083	\N	REQ-000079	\N	\N	\N	0.00	\N	\N	normal	step-pending
30e26cb6-26b7-40b7-9555-789b90cc25c1	744388d4-10fe-40fd-8e1c-52e4df7c2f04	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 25 SMSF Annual Accounts	f	f	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027083	\N	REQ-000080	\N	\N	\N	0.00	\N	\N	normal	step-pending
3116ee3a-c179-4f75-84fa-d72bafbaaf3f	3188095d-072d-44d2-94f3-455af5e939d5	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 25 SMSF Annual Accounts	f	f	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027084	\N	REQ-000081	\N	\N	\N	0.00	\N	\N	normal	step-pending
789746da-5ff4-4da4-b370-cb7b082078e0	5ded99f0-ac1f-4085-974e-2af42f17bfdc	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 26 SMSF Annual Accounts	f	f	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027252	\N	REQ-000082	\N	\N	\N	0.00	\N	\N	normal	step-pending
e4338744-62ed-4b99-a5d3-adf2fe497ce5	50866642-8045-47b9-92c5-38487579c610	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	SMSF Annual Accounts	f	f	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027481	\N	REQ-000083	\N	\N	\N	0.00	\N	\N	normal	step-pending
152f033e-36cb-4c4b-820d-1e86d08b24dd	87f75c5e-5475-463c-ab61-d6a4ba9fef85	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	SMSF Annual Accounts	f	f	1600.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	J027560	\N	REQ-000084	\N	\N	\N	0.00	\N	\N	normal	step-pending
dc00cbc1-563a-4d5b-aa09-02206ac0eee7	2f735592-284c-4b96-9f67-4e7dd4143d5c	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	SMSF Annual Accounts	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000085	\N	\N	\N	0.00	\N	\N	normal	step-pending
a7d35bf6-e46a-43a2-a978-32c25afdb821	b764dc6c-8d5c-459b-9ed9-8af8b04ec226	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 24 SMSF Annual Accounts	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000086	\N	\N	\N	0.00	\N	\N	normal	step-pending
4a4e3070-2b19-4f6e-a248-8921e4f84ac1	bd865dad-f7f9-4f4a-9bd6-081bec7bb9a8	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	completed	FY 24 SMSF Annual Accounts	t	f	700.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	2026-01-18 19:54:51.474883	PC-Completed	\N	REQ-000087	\N	\N	\N	0.00	\N	\N	normal	step-completed
34784ede-6d4b-4cc9-9908-2e826aa3d27e	bd865dad-f7f9-4f4a-9bd6-081bec7bb9a8	7	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 25 SMSF Annual Accounts	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000088	\N	\N	\N	0.00	\N	\N	normal	step-pending
9fbafac7-1f90-4c94-a9fa-620e9098d244	bd865dad-f7f9-4f4a-9bd6-081bec7bb9a8	6	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	completed	FY 24 SMSF Audit	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	2026-01-18 19:54:51.475961	PC-Completed	\N	REQ-000089	\N	\N	\N	0.00	\N	\N	normal	step-completed
665a9a7f-eb8c-49cc-ad43-26f18e381f1e	bd865dad-f7f9-4f4a-9bd6-081bec7bb9a8	6	4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	pending	FY 25 SMSF Audit	f	f	0.00	\N	2026-01-18 08:54:51.384872	2026-01-18 08:54:51.384872	\N	\N	\N	REQ-000090	\N	\N	\N	0.00	\N	\N	normal	step-pending
\.


--
-- Data for Name: service_workflows; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_workflows (id, company_id, name, description, is_default, is_active, created_at, updated_at, created_by_id) FROM stdin;
default-workflow	\N	Default Workflow	Standard service request workflow	t	t	2026-01-23 07:02:19.948635	2026-01-23 07:02:19.948635	\N
4a89df14-fd83-4c8a-976f-b042b652e8e1	92581d3e-52da-454c-93b7-780bd511825a	ITR		f	t	2026-01-23 07:07:22.941988	2026-01-23 07:07:22.941991	becf0567-7a4d-4c8f-9c8c-408205ef5015
workflow-tax-agent	\N	Tax Agent Workflow	Standard workflow for tax returns and tax-related services	f	t	2026-01-23 07:24:06.110521	2026-01-23 07:24:06.110521	\N
workflow-bas-agent	\N	BAS Agent Workflow	Workflow for BAS lodgements, GST, and payroll services	f	t	2026-01-23 07:24:06.15825	2026-01-23 07:24:06.15825	\N
workflow-auditor	\N	SMSF Auditor Workflow	Workflow for SMSF audits and compliance reviews	f	t	2026-01-23 07:24:06.166559	2026-01-23 07:24:06.166559	\N
workflow-bookkeeper	\N	Bookkeeping Workflow	Workflow for bookkeeping, payroll, and reconciliation services	f	t	2026-01-23 07:24:06.175125	2026-01-23 07:24:06.175125	\N
workflow-financial-planner	\N	Financial Planning Workflow	Workflow for financial planning, advice, and strategy services	f	t	2026-01-23 07:24:06.187628	2026-01-23 07:24:06.187628	\N
workflow-mortgage-broker	\N	Mortgage Broker Workflow	Workflow for loan applications and finance services	f	t	2026-01-23 07:24:06.197075	2026-01-23 07:24:06.197075	\N
\.


--
-- Data for Name: services; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.services (id, name, description, category, base_price, is_active, is_default, form_id, created_at, updated_at, cost_percentage, cost_category, workflow_id, is_recurring, renewal_period_months, renewal_reminder_days, renewal_due_month, renewal_due_day) FROM stdin;
40	Individual Tax Return	Preparation and lodgement of individual income tax return	tax_agent	150.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	t	12	[60, 30, 14, 7]	10	31
1	Individual Tax Return	Annual individual tax return preparation and lodgement with ATO	tax_agent	350.00	t	t	1	2026-01-18 05:05:44.469865	2026-01-18 05:05:44.469867	0.00	\N	workflow-tax-agent	t	12	[60, 30, 14, 7]	10	31
9	Company Tax Return	Annual company tax return preparation	tax_agent	500.00	t	t	\N	2026-01-18 08:36:10.922431	2026-01-18 11:01:35.971247	0.00	\N	workflow-tax-agent	t	12	[60, 30, 14]	2	28
10	SMSF Annual Audit	Complete annual audit of Self-Managed Super Fund including compliance review, financial statement audit, and trustee declaration review	auditor	1500.00	t	t	11	2026-01-20 02:00:20.420595	2026-01-20 02:00:20.420595	0.00	\N	workflow-auditor	t	12	[60, 30, 14]	2	28
11	SMSF Compliance Audit	Compliance-focused audit ensuring SMSF meets all regulatory requirements under SIS Act and ATO guidelines	auditor	1200.00	t	t	\N	2026-01-20 02:00:20.420595	2026-01-20 02:00:20.420595	0.00	\N	workflow-auditor	t	12	[60, 30, 14]	2	28
8	Bookkeeping	Monthly/quarterly bookkeeping services	bookkeeper	200.00	t	t	\N	2026-01-18 08:36:10.922431	2026-01-18 11:01:35.971247	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
41	Business Tax Return - Sole Trader	Tax return preparation for sole traders including business schedule	tax_agent	350.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
12	SMSF Establishment Audit	Initial audit for newly established SMSFs including trust deed review and setup compliance check	auditor	800.00	t	t	\N	2026-01-20 02:00:20.420595	2026-01-20 02:00:20.420595	0.00	\N	workflow-auditor	t	12	[60, 30, 14]	2	28
13	SMSF Wind-Up Audit	Final audit for SMSFs being wound up, including distribution compliance and final accounts review	auditor	1000.00	t	t	\N	2026-01-20 02:00:20.420595	2026-01-20 02:00:20.420595	0.00	\N	workflow-auditor	t	12	[60, 30, 14]	2	28
20	Investment Portfolio Review	Review of current investment portfolio with recommendations for optimization	financial_planner	800.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	t	12	[60, 30, 14]	\N	\N
28	Home Loan - New Purchase	Full service for first home buyers or new property purchase including loan comparison, application, and settlement support	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
7	SMSF Annual Accounts	Annual accounting and tax return for SMSF	tax_agent	1050.00	t	t	\N	2026-01-18 08:36:10.922431	2026-01-18 11:01:35.971247	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
2	Business Activity Statement (BAS)	Quarterly or monthly BAS preparation and lodgement	bas_agent	300.00	t	t	2	2026-01-18 05:05:44.473985	2026-01-18 06:57:09.470606	0.00	\N	workflow-bas-agent	f	12	[30, 14, 7]	\N	\N
29	Home Loan Refinance	Review and refinance of existing home loan to secure better rates or features	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
30	Investment Property Loan	Loan arrangement for investment property purchase including tax benefit analysis	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
31	Construction Loan	Specialized loan arrangement for new home construction or major renovations	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
32	Commercial Property Loan	Business and commercial property financing solutions	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
18	Comprehensive Financial Plan	Full financial planning service including retirement planning, investment strategy, insurance review, and estate planning	financial_planner	3500.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	f	12	[30, 14, 7]	\N	\N
19	Retirement Planning	Detailed retirement planning including superannuation strategy, pension planning, and retirement income projections	financial_planner	1800.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	f	12	[30, 14, 7]	\N	\N
21	Superannuation Strategy	Strategic advice on super contributions, consolidation, and optimization for retirement	financial_planner	1200.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	f	12	[30, 14, 7]	\N	\N
22	Insurance Needs Analysis	Comprehensive review of life, TPD, income protection, and trauma insurance needs	financial_planner	600.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	f	12	[30, 14, 7]	\N	\N
23	Estate Planning Advice	Guidance on wills, power of attorney, and estate planning strategies	financial_planner	900.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	f	12	[30, 14, 7]	\N	\N
24	Centrelink/Age Pension Optimization	Strategy to maximize Centrelink benefits and age pension entitlements	financial_planner	750.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	f	12	[30, 14, 7]	\N	\N
42	Company Tax Return	Preparation and lodgement of company tax return	tax_agent	800.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	t	12	[60, 30, 14]	2	28
43	Partnership Tax Return	Tax return preparation for partnerships	tax_agent	600.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	t	12	[60, 30, 14]	2	28
44	Trust Tax Return	Tax return preparation for trusts including distribution statements	tax_agent	750.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	t	12	[60, 30, 14]	2	28
64	BAS Lodgement - Quarterly	Quarterly BAS preparation and lodgement	bas_agent	180.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	t	3	[14, 7, 3]	\N	28
65	BAS Lodgement - Monthly	Monthly BAS preparation and lodgement	bas_agent	150.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	t	1	[7, 3]	\N	21
66	BAS Lodgement - Annual	Annual BAS/IAS preparation and lodgement	bas_agent	250.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	t	12	[30, 14, 7]	\N	28
6	SMSF Audit	Self-Managed Super Fund audit services	auditor	550.00	t	t	\N	2026-01-18 08:36:10.922431	2026-01-18 11:01:35.971244	0.00	\N	workflow-auditor	t	12	[60, 30, 14]	2	28
52	Monthly Bookkeeping	Complete monthly bookkeeping including bank reconciliation, accounts payable/receivable	bookkeeper	400.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	t	1	[7, 3]	\N	5
56	Payroll Processing - Monthly	Monthly payroll processing including STP reporting	bookkeeper	180.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	t	1	[7, 3]	\N	5
53	Quarterly Bookkeeping	Quarterly bookkeeping package for smaller businesses	bookkeeper	350.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	t	3	[14, 7]	\N	15
33	SMSF Property Loan	Specialized lending for property purchase through Self-Managed Super Fund	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
34	Debt Consolidation	Consolidate multiple debts into a single manageable home loan	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
35	Pre-Approval Service	Get pre-approved for a loan before house hunting	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
36	Loan Health Check	Review of current loan to ensure you have the best deal available	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
38	Asset Finance	Finance for vehicles, equipment, and other business assets	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
3	Investment Rental Property	Tax return schedule for rental property income and deductions	tax_agent	200.00	t	t	3	2026-01-18 05:05:44.479619	2026-01-18 05:05:44.47962	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
45	BAS Preparation - Quarterly	Quarterly Business Activity Statement preparation and lodgement	tax_agent	180.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
46	BAS Preparation - Monthly	Monthly Business Activity Statement preparation and lodgement	tax_agent	150.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
47	SMSF Tax Return	Annual tax return preparation for Self-Managed Super Fund	tax_agent	500.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
48	Capital Gains Tax Advice	Advice and calculations for capital gains tax on property or shares	tax_agent	300.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
49	Tax Planning Consultation	Strategic tax planning session to minimize tax liability	tax_agent	250.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
50	ATO Audit Assistance	Representation and support during ATO audit or review	tax_agent	500.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
51	Amendment - Prior Year Return	Amendment of previously lodged tax return	tax_agent	200.00	t	t	\N	2026-01-20 02:00:20.433303	2026-01-20 02:00:20.433303	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
5	Company Incorporation	New company registration with ASIC and initial setup	tax_agent	800.00	t	t	6	2026-01-18 05:05:44.487148	2026-01-18 05:05:44.592492	0.00	\N	workflow-tax-agent	f	12	[30, 14, 7]	\N	\N
67	GST Registration	GST registration with the ATO	bas_agent	100.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	f	12	[30, 14, 7]	\N	\N
68	PAYG Withholding Setup	Setup of PAYG withholding obligations	bas_agent	150.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	f	12	[30, 14, 7]	\N	\N
54	Payroll Processing - Weekly	Weekly payroll processing including STP reporting	bookkeeper	100.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
55	Payroll Processing - Fortnightly	Fortnightly payroll processing including STP reporting	bookkeeper	150.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
57	Bank Reconciliation	Monthly bank account reconciliation	bookkeeper	150.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
58	Accounts Payable Management	Management of supplier invoices and payments	bookkeeper	200.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
59	Accounts Receivable Management	Management of customer invoicing and collections	bookkeeper	200.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
60	Financial Reporting Package	Monthly/quarterly financial reports including P&L and balance sheet	bookkeeper	250.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
61	Xero/MYOB Setup	Initial setup and configuration of accounting software	bookkeeper	500.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
62	Bookkeeping Catch-Up	Catch-up bookkeeping for backlog periods	bookkeeper	75.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
63	Superannuation Processing	Processing of employee superannuation contributions	bookkeeper	100.00	t	t	\N	2026-01-20 02:00:20.436502	2026-01-20 02:00:20.436502	0.00	\N	workflow-bookkeeper	f	12	[30, 14, 7]	\N	\N
4	SMSF Super Setup	Self-Managed Super Fund establishment and registration	financial_planner	1500.00	t	t	7	2026-01-18 05:05:44.483154	2026-01-18 05:05:44.596062	0.00	\N	workflow-financial-planner	f	12	[30, 14, 7]	\N	\N
70	Single Touch Payroll (STP) Setup	Setup and configuration of STP reporting	bas_agent	250.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	f	12	[30, 14, 7]	\N	\N
71	BAS Amendment	Amendment of previously lodged BAS	bas_agent	120.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	f	12	[30, 14, 7]	\N	\N
72	Fuel Tax Credit Claim	Preparation of fuel tax credit claims	bas_agent	150.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	f	12	[30, 14, 7]	\N	\N
73	Instalment Activity Statement (IAS)	Preparation and lodgement of IAS	bas_agent	130.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	f	12	[30, 14, 7]	\N	\N
25	SMSF Setup Advice	Advice on whether an SMSF is suitable and guidance through the setup process	financial_planner	1500.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	f	12	[30, 14, 7]	\N	\N
26	Debt Management Strategy	Planning and advice for managing and reducing debt effectively	financial_planner	500.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	f	12	[30, 14, 7]	\N	\N
69	Taxable Payments Annual Report (TPAR)	Preparation and lodgement of TPAR	bas_agent	200.00	t	t	\N	2026-01-20 02:00:20.438439	2026-01-20 02:00:20.438439	0.00	\N	workflow-bas-agent	t	12	[30, 14, 7]	\N	28
14	SMSF Contravention Review	Review and audit of potential contraventions, including breach assessment and rectification advice	auditor	600.00	t	t	\N	2026-01-20 02:00:20.420595	2026-01-20 02:00:20.420595	0.00	\N	workflow-auditor	t	12	[60, 30, 14]	2	28
15	Limited Recourse Borrowing Arrangement (LRBA) Review	Audit of LRBA arrangements to ensure compliance with super laws	auditor	500.00	t	t	\N	2026-01-20 02:00:20.420595	2026-01-20 02:00:20.420595	0.00	\N	workflow-auditor	t	12	[60, 30, 14]	2	28
16	Related Party Transaction Audit	Review of related party transactions for arm's length compliance	auditor	450.00	t	t	\N	2026-01-20 02:00:20.420595	2026-01-20 02:00:20.420595	0.00	\N	workflow-auditor	t	12	[60, 30, 14]	2	28
17	Investment Strategy Review	Audit of SMSF investment strategy documentation and compliance	auditor	350.00	t	t	\N	2026-01-20 02:00:20.420595	2026-01-20 02:00:20.420595	0.00	\N	workflow-auditor	t	12	[60, 30, 14]	2	28
27	Annual Financial Review	Annual review of financial plan progress and necessary adjustments	financial_planner	650.00	t	t	\N	2026-01-20 02:00:20.430224	2026-01-20 02:00:20.430224	0.00	\N	workflow-financial-planner	t	12	[60, 30, 14]	\N	\N
37	First Home Buyer Package	Complete service for first home buyers including grants assistance and stamp duty advice	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
39	Personal Loan	Unsecured personal loan arrangement for various purposes	mortgage_broker	0.00	t	t	\N	2026-01-20 02:00:20.431762	2026-01-20 02:00:20.431762	0.00	\N	workflow-mortgage-broker	f	12	[30, 14, 7]	\N	\N
\.


--
-- Data for Name: system_email_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_email_config (id, provider, is_enabled, smtp_host, smtp_port, smtp_username, smtp_password, smtp_use_tls, smtp_use_ssl, sender_email, sender_name, use_as_fallback, last_test_at, last_test_success, last_error, created_at, updated_at) FROM stdin;
1	GMAIL	f	\N	587	\N	\N	t	f	\N	Accountant CRM	t	\N	\N	\N	2026-01-27 13:03:42.81892	2026-01-27 13:03:42.818922
\.


--
-- Data for Name: tax_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tax_types (id, code, name, default_rate, is_active, created_at) FROM stdin;
1	GST	Goods and Services Tax	10.00	t	2026-01-20 09:36:36.450576
2	VAT	Value Added Tax	20.00	t	2026-01-20 09:36:36.450576
3	SALES_TAX	Sales Tax	8.00	t	2026-01-20 09:36:36.450576
4	NONE	No Tax	0.00	t	2026-01-20 09:36:36.450576
\.


--
-- Data for Name: user_tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_tags (user_id, tag_id, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, password_hash, role_id, first_name, last_name, phone, personal_email, address, company_name, visa_status, tfn, date_of_birth, occupation, bsb, bank_account_number, bank_account_holder_name, id_document_url, passport_url, bank_statement_url, driving_licence_url, terms_accepted, terms_accepted_at, is_active, is_verified, is_first_login, two_fa_enabled, created_at, updated_at, last_login, company_id, invited_by_id, is_external_accountant) FROM stdin;
314678e1-49e6-41bc-8886-29b242067cab	accountant@example.com	$2b$12$7Ht6BkdC1KfjNaLqQpdeHOGKOC3pw9gLUElucQOuZZJckaYC8zlzC	3	John	Accountant	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	t	f	f	2026-01-18 05:05:41.943223	2026-01-18 05:05:41.943224	\N	e42c76c5-c662-4160-ae8e-3268f82047a0	\N	f
3553e149-8ca9-4ad0-9651-b61961f741ea	client@example.com	$2b$12$58uHKy/s6ZQrIQsJIMlrsepetcam.tU6LzK0pWc/.lMzZe3Yqrmxq	4	Test	Client	+61 412 345 678	\N	456 Test Street, Sydney NSW 2000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	t	f	f	2026-01-18 05:05:42.137469	2026-01-18 05:05:42.137471	\N	e42c76c5-c662-4160-ae8e-3268f82047a0	\N	f
4028052b-e0e3-4732-af16-658450040ff4	aggarwal.adarsh98+8@gmail.com	$2b$12$SoVh/JH0q58tHNMHAo8YLOEmtQ2lEe/DGbsrs3d0mEIUvZ4reGrW2	4	A	A	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	f	t	t	2026-01-28 09:56:07.22397	2026-01-28 09:56:07.223972	\N	92581d3e-52da-454c-93b7-780bd511825a	becf0567-7a4d-4c8f-9c8c-408205ef5015	f
ec86adcd-8297-4717-b1db-a4b5bc333993	practiceadmin@example.com	$2b$12$xbtoGjG2MYISOkJMtkIjRe6WxKYQBzZ1XPHs5X8Zm5errl8dKAZwe	2	Practice	Admin	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	t	f	f	2026-01-18 05:05:41.745372	2026-01-23 07:04:27.297777	2026-01-23 07:04:27.294183	e42c76c5-c662-4160-ae8e-3268f82047a0	\N	f
becf0567-7a4d-4c8f-9c8c-408205ef5015	admin@pointeraccounting.com.au	$2b$12$obaZ5OD6wmJ8XVN4NDGdc.gupBiF/DDdtxcVYTVkw.GhFcg0F1rVG	2	Pointer	Admin	+61400000001	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 08:26:57.218786	2026-01-27 13:03:18.548143	2026-01-27 13:03:18.546407	92581d3e-52da-454c-93b7-780bd511825a	\N	f
916316a8-b799-402c-9bb7-e5c4353c74d3	aggarwal.adarsh98+3@gmail.com	$2b$12$vATw.YGSsvP844wLTo1UIeid/Lx7dL6cGUHkkO3vs.Tv0PL/oduaG	4	Adarsh	Aggarwal	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	f	t	t	2026-01-27 13:03:42.801112	2026-01-27 13:03:42.801114	\N	92581d3e-52da-454c-93b7-780bd511825a	becf0567-7a4d-4c8f-9c8c-408205ef5015	f
1bcb0b68-8175-4fac-9e64-0be2e8c17ec1	charmimodi09@gmail.com	$2b$12$KLzrD/YsGwjbViQ82CsopOWBHi5KZD2OCSFUuQS1McmjTNhG4ty.i	4	CHARMI	MODI	+61412786958	\N	14 PISCES CRESCENT	\N	other	575871142	1997-05-30	Senior Mortgage Broker	063112	10573227	Charmi Modi	\N	https://drive.google.com/open?id=1DlXQjdvzbrLZfG4SlUTjxv0dlO2a_kH4	https://drive.google.com/open?id=1mQnHqPjMfBE7P9g135rMhPdNOi-IbcBg	\N	t	2026-01-28 07:27:11.187123	t	f	t	t	2026-01-28 07:27:11.434096	2026-01-28 07:27:11.434098	\N	\N	\N	f
139f1f48-5ebe-4d03-a649-d3899af67bf8	vasudha0323@gmail.com	$2b$12$rLVRTUdyax24vumD/3MtfuT6/g1GH3xzQ.hCK/WdOdJl200TpZhYq	4	Vasudha	Pati	0469768509	\N	71 playfield drive , Truganina	\N	citizen	897716849	1981-08-03	Full time employee	083004	176827634	Vasudha pati	\N	\N	\N	\N	t	2026-01-28 07:27:11.467209	t	f	t	t	2026-01-28 07:27:11.755099	2026-01-28 07:27:11.755101	\N	\N	\N	f
4c7546a8-95d0-4d18-8c6e-d0a50d7653bd	accountant@pointeraccounting.com.au	$2b$12$obaZ5OD6wmJ8XVN4NDGdc.gupBiF/DDdtxcVYTVkw.GhFcg0F1rVG	3	Pointer	Accountant	+61400000002	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 08:26:57.218786	2026-01-18 08:26:57.218786	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
fb355c08-d3b7-4ee2-b3e1-284de4568e52	dalatorre82@gmail.com	$2b$12$ef4F2QKYxPkuR0m23ZctIOV6tacsMkRDD3PrGTA/8kFwEcVLFbb26	4	Daniel Arturo	Alatorre Flores	0412966796	\N	6 Eaton Road Mount Duneed	\N	permanent_resident	608803295	1982-05-02	Sales	062948	35363180	Daniel Alatorre	\N	\N	https://drive.google.com/open?id=1l7lAm9tMY78PQaatf_zqCPzbHuU2Sr0d	\N	t	2026-01-28 07:27:11.758015	t	f	t	t	2026-01-28 07:27:12.013611	2026-01-28 07:27:12.013613	\N	\N	\N	f
59772f95-3ab7-44dd-ac18-71701473f98a	farrukhnkhan03@gmail.com	$2b$12$e.04T695g2BS3TFA43ft7usyJgN64qlmr4LCJCr.bHOfMjAxWh1mW	4	Farrukh	Khan	0451752034	\N	3 Noah Way, Tarneit VIC 3029	\N	citizen	166810482	1979-06-15	Risk Manager	082135	599680689	Farrukh Naeem Khan and Saima Farrukh	\N	https://drive.google.com/open?id=1b_tV589ihogyHhhTzABAxZnAFl1uqlgj	https://drive.google.com/open?id=1VUX5fgkdC7cBqSWYAAl2-iZeJ9ftXcI-	https://drive.google.com/open?id=1YUXjniIl2T30oSSWEUnCmJq8XCuH1bOf	t	2026-01-28 07:27:12.02567	t	f	t	t	2026-01-28 07:27:12.255505	2026-01-28 07:27:12.255508	\N	\N	\N	f
1fbf9cd7-26c4-4e04-a714-718b977ee778	syma_f@yahoo.com	$2b$12$NX8z9CL8MqTkv/c0e4yiie3q7PvPuRMNreAIMkiLWUY0YckLBynM.	4	Saima	Khan	0452477267	\N	3 Noah Way, Tarneit VIC 3029	\N	citizen	166810892	1979-08-20	HR Professional	082135	599680689	Farrukh Naeem Khan and Saima Farrukh	\N	https://drive.google.com/open?id=1JboV71asspeV_R_5xsS4oPos9aVQbU0W	https://drive.google.com/open?id=1Ey4ffjcLW7LeSo79lMk_iy1OvZH9D1In	https://drive.google.com/open?id=13tFNuihldyODCUkFH-mGMSm6j3NcBKjS	t	2026-01-28 07:27:12.257418	t	f	t	t	2026-01-28 07:27:12.493322	2026-01-28 07:27:12.493324	\N	\N	\N	f
86347343-4226-44e0-9403-6b1eca93ebe5	lblavandbs@gmail.com	$2b$12$TIz4Kpbl3.AjrsLZrQ/Ng.A2H.MtbLCJPcB545nx11IRlexg2jOMa	4	LAVANYA	BALASUNDARAM	0449005110	\N	9 MITCHELL GROVE TAYLORS HILL 3037	\N	citizen	975604675	1989-07-25	ENGINEER	063011	10798243	LAVANYA BALASUNDARAM	\N	https://drive.google.com/open?id=1WZ1QuMWik2t_PZBYyq3EXRA2Pb6qc1rj	https://drive.google.com/open?id=1P6QRP42ngQa4333Jip742udxEslocmmK	https://drive.google.com/open?id=1eKcYV5FcLyMSxDehL3bspleOG5Rvg1lj	t	2026-01-28 07:27:12.495199	t	f	t	t	2026-01-28 07:27:12.741749	2026-01-28 07:27:12.741751	\N	\N	\N	f
ac65b357-891b-4cea-998d-9460c1d3e5e8	dhanaraja21@hotmail.com	$2b$12$tWQfcs6SFhEtuReE1Vemg.nr2tyzyyY5Lm1/TdaDmpBtgox3tFTRW	4	Dhana Raja Pandian	Ramanathan	+61433885110	\N	9 Mitchell Grove, Taylors Hill , Victoria -3037	\N	citizen	405099962	1986-10-21	IT Engineer	013598	419073727	Dhana Raja Pandian	\N	https://drive.google.com/open?id=1Em5b_dnjvfAL-uVupcd8-WYHYPtT8UON	https://drive.google.com/open?id=1ad3GSgoeL78lKiAeR8A3filQDuotQLlR	https://drive.google.com/open?id=1gzWg7YsrV1jLGeQ_obUD_Iz4QQXFT8ek, https://drive.google.com/open?id=1ksyUPPCOqo7k7sF8_2Y61Xjy6hMunX0V	t	2026-01-28 07:27:12.746458	t	f	t	t	2026-01-28 07:27:12.994161	2026-01-28 07:27:12.994163	\N	\N	\N	f
40dc84c3-32a5-4fca-9c8a-c5e24bb33f42	demo@example.com	$2b$12$ooOR8klxE7Gi7M/DaVYIXuLSqUHIhNPMLV8JjAaC5a6ufBAz2NYFa	4	James	Wilson	0412 345 678	\N	42 Demo Street, Sydney NSW 2000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	t	f	f	2026-01-18 05:05:46.295189	2026-01-20 03:14:49.21218	2026-01-20 03:14:49.210739	e42c76c5-c662-4160-ae8e-3268f82047a0	\N	f
0ed5a42b-90b5-41d7-b2fb-e6e8bf4a5b11	muralimanohar23@gmail.com	$2b$12$dJ9MvvwzX1iHUOlWzOMWyOjl/ICEWO0YJOY07gQ5wjbKjITz75Hz6	4	Murali Manohar	SRINIVASAN	0431433668	\N	U2, 77 Lewis Road, WANTIRNA SOUTH 3152	\N	citizen	354077415	1963-07-05	Head of Finance (retired)	062171	10201505	Murali M Srinivasan	\N	https://drive.google.com/open?id=1sDk2PXnHTXidMZWU2gA5R-Sj3eaqNnts	https://drive.google.com/open?id=1s1UmUBUc4DpvJ5RxadKaigZATYDKNDo5	https://drive.google.com/open?id=1KImVssWO_7mLyIPjxAPafJz8a9aNimHG	t	2026-01-28 07:27:12.996031	t	f	t	t	2026-01-28 07:27:13.23222	2026-01-28 07:27:13.232222	\N	\N	\N	f
25775935-d117-491b-8ca5-e1f0cbc5ff4b	addi@aussupersource.com.au	$2b$12$ds4huUG8zURdiU2PEf5oheAJr6xQjrGRsol0ckMKQripLrZjjMBla	2	Adarsh	Aggarwal	+61415969411	aggarwal.adarsh98@gmail.com	3 grimwig cr	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	2026-01-20 04:20:55.127639	t	t	f	t	2026-01-20 04:18:43.295357	2026-01-20 04:20:55.12828	2026-01-20 04:20:39.067045	d50d352c-396f-46c5-a336-9b29a89c441b	7c439590-df69-48fd-a1b9-847ae38b94a3	f
7c439590-df69-48fd-a1b9-847ae38b94a3	admin@example.com	$2b$12$mqsInuNNr74NVIfrve8w.u/hFbXdrkz16bYa4O0z7Kz3WEqxFFWzG	1	Super	Admin	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	t	f	f	2026-01-18 05:05:41.544878	2026-01-23 06:23:12.76063	2026-01-23 06:23:12.759126	\N	\N	f
fa8ea5f4-b070-41f1-9c37-2567fe97bf93	aggarwal.adarsh98@gmail.com	$2b$12$/IEntbjtQt7BFZcb9q9RZ.NJKpHx8mRkyjYNOBI9qZkb31uplL.bG	5	Adarsh	Aggarwal	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	f	t	t	2026-01-20 04:32:32.049536	2026-01-20 04:32:32.049538	\N	d50d352c-396f-46c5-a336-9b29a89c441b	25775935-d117-491b-8ca5-e1f0cbc5ff4b	f
8d303d0f-d1fa-4bc2-99ad-7a60cd454e8a	jaykarthik@gmail.com	$2b$12$VMw9H88pZo4lD1qUgHtRaeGDaMdupgEdMUMmlPRjd05ZQ9rIc0WMO	4	Jay Karthik	Narasimhan	0423181137	\N	17 Eastbourne Avenue Wahroonga NSW 2076	\N	citizen	839590589	1972-08-28	Strategy and Risk Management	670864.0	34454647	Jay Karthik Narasimhan	\N	https://drive.google.com/open?id=19Gu_3ItapjinkAQ6OxOI65g4zgwsNip_	https://drive.google.com/open?id=1iXaRJDNAJzOUQgmeRUsI1c3rCFRzW03V	https://drive.google.com/open?id=11sDq9OsMApF1GeWrRR-m5snxev9vEvgc	t	2026-01-28 07:27:13.234763	t	f	t	t	2026-01-28 07:27:13.463413	2026-01-28 07:27:13.463415	\N	\N	\N	f
476f2065-70af-403d-ba8c-5d5223d70a29	dpak.fernando@gmail.com	$2b$12$zBvn5s9g3TRz4jK4eXZrQeqpew61W9KvFCud/6ue8dzpDmgZcS/gO	4	Deepak	Fernando	0424312165	\N	1/21 stable drive, truganina, vic 3029	\N	citizen	457725777	1994-05-06	IT Consultant	032-115	201773	Deepak Fernando	\N	https://drive.google.com/open?id=1hTBNx3cutNTaUNXhClRKrPPGA9dyuKwy	https://drive.google.com/open?id=1RzRFPv5DQvxW-H2gcPcCbmBuwExouO7h	https://drive.google.com/open?id=1nSxo7IWB_XohAqDyXH1ZPARG1lwXPDH8	t	2026-01-28 07:27:13.474741	t	f	t	t	2026-01-28 07:27:13.703113	2026-01-28 07:27:13.703115	\N	\N	\N	f
d269802f-e9ac-4817-9009-18a44b9499c3	preethi.shanker@gmail.com	$2b$12$.sTFFfsZk0z6ZlKd9pkHe.QFbWa3vCPDBCVfl3OzGUl36gujp/teK	4	Preethi	Shanker	+61413105092	\N	17 Eastbourne Avenue, Wahroonga NSW 2076	\N	citizen	839590980	1979-08-14	Tax Manager	670864.0	34454647	Preethi Shanker	\N	https://drive.google.com/open?id=1lJpfpaxrcn_fAZ6q-VQwpMJxc90CjV1w	https://drive.google.com/open?id=1fswHIaoJ5TKe8QYdpB3GcGHRPzq_eajn	https://drive.google.com/open?id=1mBFiOl0PKedPBw1u_OxqKSHBN2z-gGX9	t	2026-01-28 07:27:13.704732	t	f	t	t	2026-01-28 07:27:13.938795	2026-01-28 07:27:13.938797	\N	\N	\N	f
4637e146-a932-4287-b687-442eea6e0ccf	kumara.sivaraj@hotmail.com	$2b$12$JdzSdfVvcpl9NMJTj04iEuLDC9MhbX2oCWnjfcfVCqsxz97urp2fG	4	Kumara	Sivaraj	+61430348851	\N	1 Calola Court Ringwood East VIC 3135	\N	citizen	884508694	1987-06-20	Self Employed	063608	10572579	Kumara Sivaraj	\N	https://drive.google.com/open?id=1r597yi8tRuQjxs2L4ZSxrOhCrBms8Hl-	https://drive.google.com/open?id=1nZAj8zm0ImfClmuVqBOxD7Eti7K2tUGH, https://drive.google.com/open?id=1TDsD8G2lres4XvBSxz4eTo0CG-5IQseK, https://drive.google.com/open?id=1QpvIXrWw1eivQW-TA7JrzUTCwoJRnqjx	https://drive.google.com/open?id=1Xd688UufKyF4ayKUwCvMsYfqtLYvRVqm	t	2026-01-28 07:27:13.940722	t	f	t	t	2026-01-28 07:27:14.182239	2026-01-28 07:27:14.182242	\N	\N	\N	f
feb8587e-2a39-4c05-861d-93fe0ceabbf0	summesh.dheengra@outlook.com	$2b$12$ph8e3SA40NAi4IVRaD2gYunGWiEFI5V4fvfcDNZvYPsj4n0P4UPtS	4	Sumesh	Dhingra	0479135651	\N	12 Nightmarch Street, Officer VIC 3809	\N	citizen	849293952	1975-02-17	Salaried-Banker	923100.0	35195691	Sumesh Dhingra	\N	https://drive.google.com/open?id=1OQSIKDjc10qfDi2x0p1eUdQJJ0espgPm	https://drive.google.com/open?id=1kLeaIwgZNb3kcic4jn-BwpXinKkREN1J	https://drive.google.com/open?id=18WhhYlf-z4d5qS8wQfV40lZpmAZPoAkN	t	2026-01-28 07:27:14.18428	t	f	t	t	2026-01-28 07:27:14.422312	2026-01-28 07:27:14.422315	\N	\N	\N	f
ce78b52a-81ad-45e3-8f61-3bd68e4fea6e	krieetu.dheengra@hotmail.com	$2b$12$4e5Ojj4o2.ly40j9wG0Z1eqx0p7P4DcH80zFDZPEzocghE8K54CcW	4	Ritu	Dhingra	0435562131	\N	12 Nightmarch Street, Officer VIC 3809	\N	citizen	877618255	1985-05-01	Self employed	923100.0	35195691	Ritu Dhingra	\N	https://drive.google.com/open?id=1PCSkDhTuMMv7Y2iEFm_rxbzglEeZoVuV	https://drive.google.com/open?id=1FGhXsP0EfcYrUx_HQVZyGxS0N90VwWUa	https://drive.google.com/open?id=1ryAZOOkP5wi-9yue7DeT2RcL6PIlEKDF	t	2026-01-28 07:27:14.423953	t	f	t	t	2026-01-28 07:27:14.666638	2026-01-28 07:27:14.66664	\N	\N	\N	f
8b50ea7c-4138-4493-81bb-0cb0ac2ceb6a	katbpositive@gmail.com	$2b$12$07wRX.Wj36zieUxAf2mvZekn2jG.wzb3nyNrQp0tV2rfhQL/AL45q	4	Katherine	Burns	0422639844	\N	102 Horseshoe Bend Road, Charlemont 3217	\N	permanent_resident	609666330	1981-09-07	Compliance Analyst	063097	78031719	Katherine Burns	\N	https://drive.google.com/open?id=1bS-1mMioL0xJefhGjANJ2q00syElMgDT	https://drive.google.com/open?id=1pcRBLnfKNtarB-vjzRl9PkPAkS5GheKF	https://drive.google.com/open?id=1-bKQWxtFkdE7ps9HAGffvk9qv1AhmsRK, https://drive.google.com/open?id=1h3D2PIcIes3RMjWHP5xJ8Z5zYsH3IM0L	t	2026-01-28 07:27:14.668076	t	f	t	t	2026-01-28 07:27:14.897525	2026-01-28 07:27:14.897527	\N	\N	\N	f
caec4eda-afaa-4bf2-b12b-bdef6a43a294	sindhuharsha@yahoo.com	$2b$12$P/tfl8k0atVuIN3ODQi2T.Eqop7mWABmIIek726mXjw5kQPavKPmC	4	Sindhu	Keshavamurthy	0433226634	\N	33 Greenvale Avenue Wallan -3756	\N	citizen	TFN:832134133	1981-07-15	Cleaner	923100.0	310277539	Sindhu Keshavamurthy	\N	https://drive.google.com/open?id=19Sg535gCXvc4zus0QPDapIESYevyNg2z	https://drive.google.com/open?id=1uU80wD2sDjaH5RcCwhNWWbSc6JVS73P_	https://drive.google.com/open?id=1fwt-29CTqS1xCsmKEjo6o_L3wuzjNswd, https://drive.google.com/open?id=1sqpLj9Mni_n6Qu70j2WW8IFUr43WdyRU	t	2026-01-28 07:27:14.899751	t	f	t	t	2026-01-28 07:27:15.130147	2026-01-28 07:27:15.130149	\N	\N	\N	f
987b8458-bf02-4cfd-97e7-9b2bdcb8f5da	tvsharsha@gmail.com	$2b$12$G11ir3kdXoA6eqEpBA3GCegoVmqRbiE/n0XY9vR620pdI7/IlArEO	4	Shree Harsha	Turuvekere Venkataraya	+61423302926	\N	33 Greenvale Avenue, WALLAN VIC 3756\n33 Greenvale Ave	\N	citizen	797721105	1978-08-27	Technician	013347	187928107	Shree Harsha Turuvekere Venkataraya	\N	https://drive.google.com/open?id=1W5YMJYld0iDFNFmVUhJDCGagZu8nGhIP	https://drive.google.com/open?id=1MXGr50J3kfbhi9O89NCAkPhIbxpkCd9o	https://drive.google.com/open?id=1skGkf1MFRLYD5oxSvYKrEsWJENs0B42O, https://drive.google.com/open?id=1qUSL9t179QD5m0yenHGFk9rNgOgxS2ER	t	2026-01-28 07:27:15.131989	t	f	t	t	2026-01-28 07:27:15.374895	2026-01-28 07:27:15.374897	\N	\N	\N	f
e73bb8c5-e9bc-489a-a76d-69cbb3af5be0	veniwalsatveer.15@gmail.com	$2b$12$WpEdGvDAfLsqTAGBN4/qw.09MgojMnjjm5vJtj/jkg/5GMwzYef46	4	Satveer	Singh	0434096842	\N	11 toscana rd, Clyde, 3978, VIC	\N	temporary_resident	498783190	1999-02-28	Warehouse Worker	063788	10125213	Satveer Singh	\N	https://drive.google.com/open?id=13WqkFXiGswAVXBncYhKdUUJPcHHzYeJA	https://drive.google.com/open?id=1PmeISyWidEdtH3q9rRME0xFNeEYqnZDO	https://drive.google.com/open?id=1iBnmgS1nu3EflyHeEA4DaBYzacL7Vo4M, https://drive.google.com/open?id=1uwEs_pmXAL3o63q5gNiEPlC3PQOIxmMI	t	2026-01-28 07:27:15.376606	t	f	t	t	2026-01-28 07:27:15.60494	2026-01-28 07:27:15.604942	\N	\N	\N	f
22ceeb82-1e0f-4b8e-b832-b1b4436d187a	bhotenp@gmail.com	$2b$12$qIj08lgcB1wiTXupVWpo1ekY4m.7SAZjNfz3z.JyeclUyfwlv/yT6	4	Prakash	Maharjan	0432585576	\N	49 Harfield Ave, Mickleham 3064	\N	citizen	868615768	1982-02-28	IT field technician	062028	10494650	Prakash Maharjan	\N	https://drive.google.com/open?id=1tuT9h7OeI2ZVeGt0u-q7TRv7gR3z1Ky2	https://drive.google.com/open?id=1R8m0p7AGgzl-d_w6RlqRSeTHlYO0gzws	https://drive.google.com/open?id=1S40wSNHsdU1sH_QihEaHLDEmrIA7yFnp	t	2026-01-28 07:27:15.606596	t	f	t	t	2026-01-28 07:27:15.843787	2026-01-28 07:27:15.843789	\N	\N	\N	f
5328dd97-03eb-462b-950a-62e925a11cf4	alinasingh.m@gmail.com	$2b$12$sCfuXurXNkVE3dw9frbchuWOx0M7UZHA/GeAWoxr8cjSL1suU21pe	4	Alina Singh	Maharjan	0431253466	\N	49 Harfield Ave, Mickleham 3064	\N	citizen	868990121	1981-11-14	Retail assistant	062005	10695742	Alina Singh Maharjan	\N	https://drive.google.com/open?id=1CYFSVDu98CRiZJoD2-7L9JXOxXny3aCt	https://drive.google.com/open?id=1ZpZdWCP_qi-71UnEFXGDTGqfjZ6bKH-o	https://drive.google.com/open?id=176yP0zCnvbAai1R72q7mjPuydnTcE7Ui	t	2026-01-28 07:27:15.845517	t	f	t	t	2026-01-28 07:27:16.073613	2026-01-28 07:27:16.073615	\N	\N	\N	f
126ad8ba-c385-4341-96e7-ee93432e0535	ritukour0906@gmail.com	$2b$12$szFZ0/vEuQKd2XhChHpAkezwD829K1.rb16eHdibyxyMaMaZq6se6	4	Ritu Kour	Ritu kour	0404470617	\N	11 Toscana road clyde	\N	temporary_resident	101583544	1998-06-09	Food service assistant	013664	650532842	Ritu kour	\N	https://drive.google.com/open?id=1KGDvloufXILfbo8S83ofO7m-Xebew0q8	https://drive.google.com/open?id=1dv1xtAe5LIvHNidF4atvhdAAc9uI8f4w	https://drive.google.com/open?id=1VPFdKgJbsCr91P2Eb8eYGTiDMVuGQImV, https://drive.google.com/open?id=1kHopaQNh7_NGkrvf06F8octJw_OGRq4K	t	2026-01-28 07:27:16.086761	t	f	t	t	2026-01-28 07:27:16.318771	2026-01-28 07:27:16.318773	\N	\N	\N	f
5a3a0bb9-099e-402a-bc4d-0fadc58e2c86	btr.prabhu@gmail.com	$2b$12$lZTATh16b0hEEmUmIgyLA.Y46SmwO35CLU.TSSUAsGI42BCTtmdj.	4	Niranjan	Prabhu	0402892323	\N	28 Barlyn road Mount Waverley VIC 3149	\N	citizen	400023099	1970-05-12	Chief Information Officer	063169	10248321	Niranjan and Yamini Prabhu	\N	https://drive.google.com/open?id=1uxN9Fo0mJUM-ySnCjHNOplv8x0yfq1up	https://drive.google.com/open?id=1PtdjljC0OMIOUnCUGt2qI-MeboDjwLU5	https://drive.google.com/open?id=1awgQvQvJojzyBBkOxiwR9Pc7pCMAcwU9, https://drive.google.com/open?id=1uPNpR7YKRRDuaFgkKNO3aOG45JKuCv6c	t	2026-01-28 07:27:16.322957	t	f	t	t	2026-01-28 07:27:16.552012	2026-01-28 07:27:16.552014	\N	\N	\N	f
9778fdd7-a9ef-467c-88cf-be637aa29a99	yambhu@yahoo.com	$2b$12$5rj9lR54iqdn6Movr8pimeFGgvI8tYbTB.iFjN1yAUybx2lgnpcnG	4	Yamini	Prabhu	0433301346	\N	28 Barlyn Road Mount Waverley VIC 3149	\N	citizen	353806465	1975-06-22	Senior Commercial Analyst	063169	10248321	Niranjan Thimmareddy Prabhu and Yamini Prabhu	\N	https://drive.google.com/open?id=1xdpOo5Wo-DU1f0r3BhNuR1qzzMoh6iFb	https://drive.google.com/open?id=1QNn1DEvjGU4ay96-Ujemv0witIeHuObH	https://drive.google.com/open?id=1kCEG4SLElZvYgoRDkN_c_7KYzP4JnWw9, https://drive.google.com/open?id=1TcT29dWHl1Ouc1Z6ztK79DZOM1i9RdtS	t	2026-01-28 07:27:16.553692	t	f	t	t	2026-01-28 07:27:16.782731	2026-01-28 07:27:16.782733	\N	\N	\N	f
74f2e37e-19ad-434a-9133-c0c65d2d486c	mjbindley@gmail.com	$2b$12$BblJqj6YApuxX3EWAlm9zueU86wvr4vFuQ8oq.Py5jYx30iMN0Qh.	4	Matthew	Bindley	+61401838675	\N	4/140-142 Rupert St, West Footscray, Vic 3012	\N	citizen	850803443	1992-03-16	Banking	182182.0	222943	Matthew Bindley	\N	https://drive.google.com/open?id=1e3Idh_7t97lq6jG25Lt7iIFy59pPbGoJ	https://drive.google.com/open?id=1EXxdwn-egG2vMcqEqZ4wZHdnN0aiLgVc	https://drive.google.com/open?id=1suzBybgFh8hNuqokvdXLx5aJdi41ZQH3, https://drive.google.com/open?id=1F-Gw4_-62ZZ5FC7XoGpjBQ5nk08Pmlqh	t	2026-01-28 07:27:16.784277	t	f	t	t	2026-01-28 07:27:17.013721	2026-01-28 07:27:17.013723	\N	\N	\N	f
f3b811f8-c93b-4c50-8dc2-6cc1461d17a0	hanish.verma@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Hanish	Verma	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
13abce87-7f77-4f4a-a7f7-510afb2e2d2c	vidhu.jain@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Vidhu	Jain	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
ccc05a70-89eb-44af-932e-5aea1a97788e	hanish.and.vidhu.smsf@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Hanish	& Vidhu SMSF	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.389523	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
f5522e43-8f01-4872-b439-66fbdc7717d4	bluerock.financial.services..pty.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Bluerock	Financial Services  Pty Ltd	\N	\N	\N	Company	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.392102	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
12543417-929e-446b-b571-6733c14c3d93	kumara.sivaraj.bala@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Kumara	Sivaraj (Bala)	\N	\N	\N	Director	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.396224	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
85ebf4e1-7cba-4c78-aeb0-3e2c99864693	bas.it.tech.pvt.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	BAS	IT Tech Pvt Ltd	\N	\N	\N	Company	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.397466	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
1b1a0ea2-a363-4263-a4a7-d6b0733ffe10	katherine.burns@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Katherine	Burns	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.399814	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
e9682053-e70e-4dec-9f68-8a3627b4ad84	limitless.leads.pty.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Limitless	Leads Pty Ltd	\N	\N	\N	Company	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.400872	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
3308a7fe-d5f7-40d5-9221-b5ef38d98dc8	rajani.thakkalapally@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Rajani	Thakkalapally	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
287b3a83-3af1-414b-a9a3-e057a5a3dd09	shreyas.thakkalapally.rajini.son@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Shreyas	Thakkalapally (Rajini Son)	\N	\N	\N	BAS ABN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
c5cf53e1-bbb0-4e3e-95ce-97bc1806fb22	nagender@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Nagender		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.412263	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
e7bf01e7-2a8e-47e0-86c9-404b1b890039	spot.on.re@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Spot	On RE	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.412901	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
eeb0fd76-2f17-42e4-ae5d-c7083dd3a868	srikant.sweet.magic@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Srikant	(Sweet Magic)	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.413521	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
85e8d926-1f65-439f-8242-a2151769bca6	vasudha.pati.pizzahut@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Vasudha	Pati (PizzaHut)	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.414147	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
1af94636-3a5d-4e4e-9e72-602bcc061572	srirish.pty.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Srirish	Pty Ltd	\N	\N	\N	Company	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-08-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
e89f5907-94d6-4158-b39c-e7809f4648ee	farrukhkhan@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Farrukh Khan		\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
36dff369-19b4-4e3e-9035-5a280ad60f28	saima.khan@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Saima	Khan	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
d5af09d6-e32f-40dd-af7c-a299ef43906a	daniel.alatorre@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Daniel	Alatorre	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.418288	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
44b7ca23-104a-40b1-bd43-dc273e7fde92	dhana.raja.pandian.ramanathan@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Dhana	Raja Pandian Ramanathan	\N	\N	\N	Individual ABN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
e59bdabc-0a0f-4645-a029-3f31ab5abcad	lavanya.balasundaram@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Lavanya	Balasundaram	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
146d77e1-6d9a-4f81-8ee0-1a3c2fba5424	jay.karthick@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Jay	Karthick	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.424304	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
56ed522e-664d-4ad3-8d58-ca5b54e2aa32	preethi@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Preethi		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.424901	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
a3cca461-32a7-4e06-ada3-6ef6dbb30168	grow.n.glow.super.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Grow	n Glow Super fund	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2024-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
6914b989-e132-4e22-8874-6d0fabbe4bcd	satveer.cab@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Satveer	Cab	\N	\N	\N	Individual ABN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2024-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
60dbe0d8-03c4-45bc-bc60-e2487401986b	ashmita.chatterjee@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Ashmita	Chatterjee	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
e64a351e-71af-42b3-9586-d708481ed7a9	shankar@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Shankar		\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
7640efe5-dd39-4106-bf0c-c352216fa045	karmanidhi.super.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Karmanidhi	Super Fund	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-10-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
82d4deb6-abea-47ad-9994-66a46477d4ec	deepak.fernando@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Deepak	Fernando	\N	\N	\N	Individual ABN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.432187	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
0337cf13-ec50-419f-8318-19ab86469874	alina.singh.maharjan@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Alina	Singh Maharjan	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.435491	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
fb2838b9-9e21-46c1-8a69-5ecdecf420fe	prakash.maharjan@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Prakash	Maharjan	\N	\N	\N	Individual ABN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.43652	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
ca00d02b-0bd1-4bc6-8809-3f1a63ddc3a7	pointers.consulting.pty.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Pointers	Consulting Pty Ltd	\N	\N	\N	Company	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.441092	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
3de320b2-2f5e-473b-b7db-8238b9f8b90e	sumesh.dhingra@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Sumesh	Dhingra	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.444412	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
0e1505e5-2c84-4ec9-8ebc-ffd047216d08	ritu.dhingra@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Ritu	Dhingra	\N	\N	\N	Individual ABN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.445888	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
4641887d-612f-4767-b0ac-8885dff9302f	smsf@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	SMSF…??		\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.449248	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
5eb30ffa-0906-4204-a470-cb00d4fc0202	shiv.rakkar@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Shiv	Rakkar	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.450772	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
3da36d99-addf-4003-ad1b-f3d943aba3e7	shiv.rakkar.smsf@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Shiv	Rakkar SMSF	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.451737	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
da454710-22d8-46df-9d3f-f3a5af4abda3	sindhu.k@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Sindhu	K	\N	\N	\N	Individual ABN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.45297	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
66f205ed-06e3-4290-9df1-e5100752e263	sell.serv.pvt.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Sell	Serv Pvt Ltd	\N	\N	\N	Company	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.456538	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
a3476853-c261-4f67-9a5f-9a07ac560ae3	turuvekere.venkataraya.shree.harsha@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	TURUVEKERE	VENKATARAYA, SHREE HARSHA	\N	\N	\N	Individual Director	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.458096	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
83358bf2-31be-40a7-8922-37157dabe6f8	blanks.and.scars.superannuation.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Blanks	& Scars Superannuation Fund	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
32f4c8ce-e7e6-447c-b351-a4940036aa9f	jacobs.super.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Jacobs	Super Fund	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
dcb04f00-35af-48a2-8499-38fc84227341	sd.investments.smsf@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	SD	Investments SMSF	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
744388d4-10fe-40fd-8e1c-52e4df7c2f04	tassell.and.everitt.superannuation.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Tassell	& Everitt Superannuation Fund	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
3188095d-072d-44d2-94f3-455af5e939d5	the.trustee.for.mack.smsf@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	The	Trustee for MACK SMSF	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
5ded99f0-ac1f-4085-974e-2af42f17bfdc	peters.family.superannuation.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Peters	Family Superannuation Fund	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
50866642-8045-47b9-92c5-38487579c610	j.and.s.mostert.super.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	J	& S Mostert Super fund	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
87f75c5e-5475-463c-ab61-d6a4ba9fef85	harrington.smsf.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Harrington	SMSF Fund	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
2f735592-284c-4b96-9f67-4e7dd4143d5c	ms.garg.super.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	MS	Garg Super fund	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
0c405543-f233-4d56-af25-9b2dc1b39edc	shaw.sf@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Shaw	SF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
b764dc6c-8d5c-459b-9ed9-8af8b04ec226	dorax.super.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Dorax	Super Fund	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
bd865dad-f7f9-4f4a-9bd6-081bec7bb9a8	j.l.cheema@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	J	L Cheema	\N	\N	\N	SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
1489aa68-bc66-4a8f-8fe2-89a8d7a61746	truban@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Truban		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2025-12-01 00:00:00	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
441966cb-5fb8-488b-8e54-f3e4d5ba0e89	kha.luan.nuygen@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Kha	Luan Nuygen	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.478237	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
4450815d-f4dd-42cd-8af5-0a542c86b69b	new.world.tourist.pty.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	New	World Tourist Pty Ltd	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.478838	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
82b35113-2ef0-4458-9653-99b85206644f	kha.luan.nuygen.super.fund@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Kha	Luan Nuygen Super Fund	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.479469	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
1b9add8a-7660-48e3-80fe-6f7ac12bbf64	matthew.bindley@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Matthew	Bindley	\N	\N	\N	Individual TFN	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.482329	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
eca7782d-5a99-475d-97ef-1fbf7e7839cc	niranjan.prabhu@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Niranjan	Prabhu	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.483378	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
3ea796c7-3bb8-4556-890f-52100c3ef165	yamini.prabhu@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Yamini	Prabhu	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.483989	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
5c2fdfdb-ca42-47bc-b7c9-5e4a13d9d909	niranjan.and.yamini.prabhu.smsf@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Niranjan	& Yamini Prabhu SMSF	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.485159	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
97cb9790-75db-4757-944e-d62b34951300	priyankur.sharma@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Priyankur	Sharma	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.48577	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
617c875f-2837-4252-bfde-cce0ce5edc10	shruti.sharma@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Shruti	Sharma	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.486352	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
693b03e3-f22b-43da-a781-a6ef5d070d2c	abhishek.didwania@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Abhishek	Didwania	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.486898	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
78b1a532-09ce-4dc5-9fa9-caae2093b2b0	nisha.didwania@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Nisha	Didwania	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.487579	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
78b3054f-89ef-48f4-9bb7-72038dcf680d	amanda.gideon@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Amanda	(Gideon)	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.48813	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
be626840-5995-4fda-afb9-983f09d36094	amrita.trivedi@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Amrita	Trivedi	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.488678	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
8f248d12-4339-427a-b3a4-0e68351eafa6	anna.shibu@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Anna	Shibu	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.489483	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
2a71a84b-9fe6-422c-a02e-3f817623ed3c	arun.chaudhary@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Arun	Chaudhary	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.490062	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
c396cdf8-fa2f-4d36-8c4b-476a4b02c3ce	minakshi.chaudhary@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Minakshi	Chaudhary	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.490646	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
0255d58b-3d4f-41a6-acbc-9e2263343e14	asmandeep@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Asmandeep		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.491157	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
af8870c0-8896-4839-81e1-6dc44c7bd484	desmond.moletsane@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Desmond	Moletsane	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.491727	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
d27d51dd-23b7-4a77-a72a-ddb34a893e09	luyanda.moletsane@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Luyanda	Moletsane	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.492267	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
f3891cc8-8a69-4d89-83af-325c0ed3c2c5	jack.talbot@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Jack	Talbot	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.492787	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
34a6380d-fba6-4ac2-940b-355c3df5bcb0	michell.talbot@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Michell	Talbot	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.493291	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
1a8d7dfa-1e3a-4e91-93f8-2e4c8d1fd3eb	johan.swanepoel@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Johan	Swanepoel	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.493798	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
d542907c-8dd5-47b2-8760-7a20bd446ab7	sheena.swanepoel@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Sheena	Swanepoel	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.494301	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
4a707a29-8d02-4592-ac85-8468d890f544	vk.tech.pty.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	VK	Tech Pty Ltd	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.494782	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
75b75471-767e-4155-a016-28931166de9b	karthick.ganeshan@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Karthick	Ganeshan	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.495268	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
a33ac215-c702-46d7-b056-5f418a7f8352	sharmila@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Sharmila		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.495758	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
a20e82ae-c2d0-49dc-bc50-c1c652f75841	khamayal@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Khamayal		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.496316	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
310ab27b-9611-4ce6-9660-333e05302bb5	khawater@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Khawater		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.496867	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
32c7005d-3912-4731-b577-b24c37a25b09	loran.hudson@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Loran	Hudson	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.497422	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
b4700604-9bac-445e-a720-22e26051fd65	nadine.hudson@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Nadine	Hudson	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.497888	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
2dc4dfc8-b7c5-4c2b-bd87-3df755d01472	anitha.murali.manohar@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Anitha	Murali Manohar	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.498421	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
9398a649-86e9-4057-bb1e-6ebd7fa50c5e	murali.manohar.srinivasan@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Murali	Manohar Srinivasan	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.498983	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
91b8fe4e-a8ca-4a81-bb7e-9bd2efc065bc	repam.pty.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	REPAM	Pty Ltd	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.499586	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
913c1d8a-513c-43b2-97ee-b8fff6a82672	nicole@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Nicole		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.500512	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
b65a1d58-3839-4d6c-8dbe-d483cf4f0c57	nilesh.indani@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Nilesh	Indani	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.501097	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
dad58362-841f-435b-aa8a-ca8f73b91039	lakshmi.suresh.kodoth@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Lakshmi	Suresh Kodoth	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.501634	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
f0275a92-dcf3-42ec-b605-b5017f509b3c	nithin.krishna.cherippady@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Nithin	Krishna Cherippady	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.502173	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
e751a6f9-47cb-487a-96bc-223c4695da8c	mona@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Mona		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.502695	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
a6d4e671-1598-41f1-81f2-4ed71e167018	pej@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Pej		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.503226	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
e4cddb5b-c753-4be9-8e68-c1d73a70d11a	annai.sathya@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Annai	Sathya	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.503752	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
6c834239-c760-445f-bd58-e170588b174d	philip@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Philip		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.504301	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
c6a825a8-8c5c-43bd-80aa-8f274bfa3f4b	rachna.sharma@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Rachna	Sharma	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.504878	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
9f0c194c-f59f-45d3-825d-a966432c9aaa	reliable.engineers.consulting.pvt.ltd@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Reliable	Engineers Consulting Pvt Ltd	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.505387	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
2e84b078-bec4-42c7-a3b4-af3d4f3b34ce	rohit.srivastava@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Rohit	Srivastava	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.505955	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
ef30e786-8516-4530-a6de-b830bc45cdc3	arpita.khare@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Arpita	Khare	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.506454	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
cc71fcb7-f2be-41a7-a3c5-7eac050d370c	ripneet.kaur@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Ripneet	Kaur	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.507028	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
befefff3-6a7a-4db2-8211-74bac5279a49	manisha.jyoti@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Manisha	Jyoti	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.507564	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
89bb2acd-30ee-45ca-be22-9084651309df	ronel.lal@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Ronel	Lal	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.508111	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
d89f67ad-b63f-4ab8-89e7-61337090589c	ritu.kour@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Ritu	Kour	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.508853	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
35544dbf-1df8-486d-a2ba-60a86bd8034d	saurav.kumar.das@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Saurav	Kumar Das	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.509493	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
7f84bec1-49d7-4f2d-bee4-c42cb0dace99	soma.das@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Soma	Das	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.510084	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
e602ebd4-55a2-47fc-a3f6-54d548f33eaf	angelique.eagar@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Angelique	Eagar	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.510621	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
429634f3-09f8-441b-a4b9-f3e178d0b85f	shane.eagar@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Shane	Eagar	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.511202	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
c2e88517-5ba7-42a3-a606-5c0fb9921780	narayanan.nesamalar@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Narayanan	Nesamalar	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.511749	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
970dc163-b5d0-4ad9-96aa-7d24e0af234d	shanmugan@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Shanmugan		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.51229	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
cb16494a-4db5-4d2d-a2c9-24cc79f50993	rama.k@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Rama	K	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.512783	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
0c0de067-aa41-4a4d-9b74-a3ffa2b79996	vignesh@pointer.client	$2b$12$I7hbIR/Wugb0zUOr70KzRORtX2nqNykpT6bnk0JwE7fPj68hUL5g6	4	Vignesh		\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	\N	2026-01-18 19:54:51.51332	2026-01-18 08:54:51.384872	\N	92581d3e-52da-454c-93b7-780bd511825a	\N	f
d4b2bedc-64f7-4d7b-a97a-b948aac4cf90	aggarwal.adarsh98+5@gmail.com	$2b$12$0ieMgHSeQPeqB3VUice1Eut8dmqGEu3NlzFuEoZIN2iwfN2rjgxHG	4	A	A	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	f	t	t	2026-01-28 09:52:42.27118	2026-01-28 09:52:42.271182	\N	92581d3e-52da-454c-93b7-780bd511825a	becf0567-7a4d-4c8f-9c8c-408205ef5015	f
\.


--
-- Data for Name: workflow_automations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_automations (id, workflow_id, step_id, trigger, action_type, action_config, conditions, delay_minutes, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: workflow_steps; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_steps (id, workflow_id, name, display_name, description, color, icon, step_type, "order", allowed_roles, required_fields, auto_assign, notify_roles, notify_client, position_x, position_y, created_at, updated_at) FROM stdin;
step-pending	default-workflow	pending	Pending	\N	gray	\N	START	1	\N	\N	f	\N	f	100	100	2026-01-23 07:02:19.954786	2026-01-23 07:02:19.954786
step-invoice-raised	default-workflow	invoice_raised	Invoice Raised	\N	blue	\N	NORMAL	2	\N	\N	f	\N	f	300	100	2026-01-23 07:02:19.954786	2026-01-23 07:02:19.954786
step-assigned	default-workflow	assigned	Assigned	\N	indigo	\N	NORMAL	3	\N	\N	f	\N	f	500	100	2026-01-23 07:02:19.954786	2026-01-23 07:02:19.954786
step-processing	default-workflow	processing	Processing	\N	yellow	\N	NORMAL	4	\N	\N	f	\N	f	700	100	2026-01-23 07:02:19.954786	2026-01-23 07:02:19.954786
step-query-raised	default-workflow	query_raised	Query Raised	\N	orange	\N	QUERY	5	\N	\N	f	\N	f	700	250	2026-01-23 07:02:19.954786	2026-01-23 07:02:19.954786
step-review	default-workflow	accountant_review_pending	Under Review	\N	purple	\N	NORMAL	6	\N	\N	f	\N	f	500	250	2026-01-23 07:02:19.954786	2026-01-23 07:02:19.954786
ef6147ef-b0f4-4b1a-bf22-91ab43f83358	4a89df14-fd83-4c8a-976f-b042b652e8e1	new_request	New Request		green	\N	START	1	["super_admin"]	[]	f	["admin"]	f	170	203	2026-01-23 07:08:32.64917	2026-01-23 07:08:32.649172
d6bf859b-b189-412f-a647-0b65a0467d11	4a89df14-fd83-4c8a-976f-b042b652e8e1	invoice_raised	Invoice Raised		blue	\N	NORMAL	2	["admin"]	[]	f	[]	t	377.25	228.75	2026-01-23 07:09:23.761105	2026-01-23 07:09:23.761106
3a366a08-6ae0-4645-b390-9e7fa50c90c8	4a89df14-fd83-4c8a-976f-b042b652e8e1	invoice_paid	Pending Assignment		blue	\N	NORMAL	3	["admin"]	[]	t	["admin"]	f	749.4785844831092	235.1572835086905	2026-01-23 07:10:32.449999	2026-01-23 07:10:32.450001
tax-step-pending	workflow-tax-agent	pending	Pending Review	\N	gray	\N	START	1	["admin", "super_admin"]	\N	f	\N	f	50	150	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
tax-step-docs-requested	workflow-tax-agent	documents_requested	Documents Requested	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	f	\N	t	250	150	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
tax-step-docs-received	workflow-tax-agent	documents_received	Documents Received	\N	indigo	\N	NORMAL	3	["admin", "accountant", "super_admin"]	\N	f	\N	f	450	150	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
tax-step-invoice-raised	workflow-tax-agent	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	4	["admin", "super_admin"]	\N	f	\N	t	650	150	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
tax-step-assigned	workflow-tax-agent	assigned	Assigned to Accountant	\N	blue	\N	NORMAL	5	["admin", "super_admin"]	\N	f	\N	f	850	150	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
tax-step-preparation	workflow-tax-agent	in_preparation	Return Preparation	\N	yellow	\N	NORMAL	6	["accountant", "admin", "super_admin"]	\N	f	\N	f	1050	150	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
tax-step-query	workflow-tax-agent	query_raised	Query Raised	\N	orange	\N	QUERY	7	["accountant", "admin", "super_admin"]	\N	f	\N	t	1050	300	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
tax-step-review	workflow-tax-agent	client_review	Client Review	\N	purple	\N	NORMAL	8	["user"]	\N	f	\N	t	850	300	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
tax-step-lodgement	workflow-tax-agent	ready_for_lodgement	Ready for Lodgement	\N	indigo	\N	NORMAL	9	["accountant", "admin", "super_admin"]	\N	f	\N	f	1250	150	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
tax-step-lodged	workflow-tax-agent	lodged	Lodged with ATO	\N	blue	\N	NORMAL	10	["accountant", "admin", "super_admin"]	\N	f	\N	t	1450	150	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
bas-step-pending	workflow-bas-agent	pending	Pending	\N	gray	\N	START	1	["admin", "super_admin"]	\N	f	\N	f	50	150	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
bas-step-data-collection	workflow-bas-agent	data_collection	Data Collection	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	f	\N	t	250	150	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
bas-step-invoice-raised	workflow-bas-agent	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	3	["admin", "super_admin"]	\N	f	\N	t	450	150	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
bas-step-assigned	workflow-bas-agent	assigned	Assigned	\N	blue	\N	NORMAL	4	["admin", "super_admin"]	\N	f	\N	f	650	150	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
bas-step-reconciliation	workflow-bas-agent	reconciliation	Bank Reconciliation	\N	yellow	\N	NORMAL	5	["accountant", "admin", "super_admin"]	\N	f	\N	f	850	150	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
bas-step-preparation	workflow-bas-agent	bas_preparation	BAS Preparation	\N	yellow	\N	NORMAL	6	["accountant", "admin", "super_admin"]	\N	f	\N	f	1050	150	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
bas-step-query	workflow-bas-agent	query_raised	Query Raised	\N	orange	\N	QUERY	7	["accountant", "admin", "super_admin"]	\N	f	\N	t	1050	300	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
bas-step-review	workflow-bas-agent	review	Review & Approval	\N	purple	\N	NORMAL	8	["admin", "super_admin"]	\N	f	\N	t	1250	150	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
bas-step-lodged	workflow-bas-agent	lodged	Lodged with ATO	\N	blue	\N	NORMAL	9	["accountant", "admin", "super_admin"]	\N	f	\N	t	1450	150	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
aud-step-pending	workflow-auditor	pending	Audit Requested	\N	gray	\N	START	1	["admin", "super_admin"]	\N	f	\N	f	50	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-engagement	workflow-auditor	engagement_letter	Engagement Letter	\N	blue	\N	NORMAL	2	["admin", "super_admin"]	\N	f	\N	t	250	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-docs-requested	workflow-auditor	documents_requested	Documents Requested	\N	blue	\N	NORMAL	3	["admin", "accountant", "super_admin"]	\N	f	\N	t	450	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-docs-received	workflow-auditor	documents_received	Documents Received	\N	indigo	\N	NORMAL	4	["admin", "accountant", "super_admin"]	\N	f	\N	f	650	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-invoice-raised	workflow-auditor	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	5	["admin", "super_admin"]	\N	f	\N	t	850	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-assigned	workflow-auditor	assigned	Assigned to Auditor	\N	blue	\N	NORMAL	6	["admin", "super_admin"]	\N	f	\N	f	1050	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-fieldwork	workflow-auditor	fieldwork	Audit Fieldwork	\N	yellow	\N	NORMAL	7	["accountant", "admin", "super_admin"]	\N	f	\N	f	1250	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-query	workflow-auditor	query_raised	Query Raised	\N	orange	\N	QUERY	8	["accountant", "admin", "super_admin"]	\N	f	\N	t	1250	300	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-draft-report	workflow-auditor	draft_report	Draft Report	\N	purple	\N	NORMAL	9	["accountant", "admin", "super_admin"]	\N	f	\N	f	1450	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-management-review	workflow-auditor	management_review	Management Review	\N	indigo	\N	NORMAL	10	["admin", "super_admin"]	\N	f	\N	t	1650	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-final-report	workflow-auditor	final_report	Final Report Issued	\N	blue	\N	NORMAL	11	["admin", "super_admin"]	\N	f	\N	t	1850	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
aud-step-completed	workflow-auditor	completed	Completed	\N	green	\N	END	12	["admin", "super_admin"]	\N	f	\N	t	2050	150	2026-01-23 07:24:06.168655	2026-01-23 07:24:06.168655
bas-step-completed	workflow-bas-agent	completed	Completed	\N	green	\N	END	11	["accountant", "admin", "super_admin"]	\N	f	\N	t	1650	150	2026-01-23 07:24:06.160475	2026-01-23 07:24:06.160475
step-completed	default-workflow	completed	Completed	\N	green	\N	END	8	\N	\N	f	\N	f	900	100	2026-01-23 07:02:19.954786	2026-01-23 07:02:19.954786
book-step-pending	workflow-bookkeeper	pending	Pending	\N	gray	\N	START	1	["admin", "super_admin"]	\N	f	\N	f	50	150	2026-01-23 07:24:06.177203	2026-01-23 07:24:06.177203
book-step-access-setup	workflow-bookkeeper	access_setup	Access Setup	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	f	\N	t	250	150	2026-01-23 07:24:06.177203	2026-01-23 07:24:06.177203
book-step-invoice-raised	workflow-bookkeeper	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	3	["admin", "super_admin"]	\N	f	\N	t	450	150	2026-01-23 07:24:06.177203	2026-01-23 07:24:06.177203
book-step-assigned	workflow-bookkeeper	assigned	Assigned	\N	blue	\N	NORMAL	4	["admin", "super_admin"]	\N	f	\N	f	650	150	2026-01-23 07:24:06.177203	2026-01-23 07:24:06.177203
book-step-processing	workflow-bookkeeper	processing	Processing	\N	yellow	\N	NORMAL	5	["accountant", "admin", "super_admin"]	\N	f	\N	f	850	150	2026-01-23 07:24:06.177203	2026-01-23 07:24:06.177203
book-step-query	workflow-bookkeeper	query_raised	Query Raised	\N	orange	\N	QUERY	6	["accountant", "admin", "super_admin"]	\N	f	\N	t	850	300	2026-01-23 07:24:06.177203	2026-01-23 07:24:06.177203
book-step-review	workflow-bookkeeper	review	Review	\N	purple	\N	NORMAL	7	["admin", "super_admin"]	\N	f	\N	f	1050	150	2026-01-23 07:24:06.177203	2026-01-23 07:24:06.177203
book-step-client-approval	workflow-bookkeeper	client_approval	Client Approval	\N	indigo	\N	NORMAL	8	["user"]	\N	f	\N	t	1250	150	2026-01-23 07:24:06.177203	2026-01-23 07:24:06.177203
fp-step-pending	workflow-financial-planner	pending	Enquiry Received	\N	gray	\N	START	1	["admin", "super_admin"]	\N	f	\N	f	50	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-discovery	workflow-financial-planner	discovery	Discovery Meeting	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	f	\N	t	250	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-fact-find	workflow-financial-planner	fact_find	Fact Find	\N	indigo	\N	NORMAL	3	["admin", "accountant", "super_admin"]	\N	f	\N	t	450	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-invoice-raised	workflow-financial-planner	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	4	["admin", "super_admin"]	\N	f	\N	t	650	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-assigned	workflow-financial-planner	assigned	Assigned to Planner	\N	blue	\N	NORMAL	5	["admin", "super_admin"]	\N	f	\N	f	850	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-analysis	workflow-financial-planner	analysis	Analysis & Research	\N	yellow	\N	NORMAL	6	["accountant", "admin", "super_admin"]	\N	f	\N	f	1050	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-soa-prep	workflow-financial-planner	soa_preparation	SOA Preparation	\N	yellow	\N	NORMAL	7	["accountant", "admin", "super_admin"]	\N	f	\N	f	1250	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-compliance-review	workflow-financial-planner	compliance_review	Compliance Review	\N	purple	\N	NORMAL	8	["admin", "super_admin"]	\N	f	\N	f	1450	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-presentation	workflow-financial-planner	presentation	Advice Presentation	\N	indigo	\N	NORMAL	9	["admin", "accountant", "super_admin"]	\N	f	\N	t	1650	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-query	workflow-financial-planner	query_raised	Query Raised	\N	orange	\N	QUERY	10	["accountant", "admin", "super_admin"]	\N	f	\N	t	1650	300	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
fp-step-implementation	workflow-financial-planner	implementation	Implementation	\N	blue	\N	NORMAL	11	["accountant", "admin", "super_admin"]	\N	f	\N	f	1850	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
mb-step-pending	workflow-mortgage-broker	pending	Enquiry Received	\N	gray	\N	START	1	["admin", "super_admin"]	\N	f	\N	f	50	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-consultation	workflow-mortgage-broker	consultation	Initial Consultation	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	f	\N	t	250	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-docs-collection	workflow-mortgage-broker	documents_collection	Document Collection	\N	indigo	\N	NORMAL	3	["admin", "accountant", "super_admin"]	\N	f	\N	t	450	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-serviceability	workflow-mortgage-broker	serviceability	Serviceability Assessment	\N	yellow	\N	NORMAL	4	["accountant", "admin", "super_admin"]	\N	f	\N	f	650	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-product-selection	workflow-mortgage-broker	product_selection	Product Selection	\N	purple	\N	NORMAL	5	["accountant", "admin", "super_admin"]	\N	f	\N	t	850	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-invoice-raised	workflow-mortgage-broker	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	6	["admin", "super_admin"]	\N	f	\N	t	1050	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-application	workflow-mortgage-broker	application_submitted	Application Submitted	\N	blue	\N	NORMAL	7	["accountant", "admin", "super_admin"]	\N	f	\N	t	1250	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-assessment	workflow-mortgage-broker	lender_assessment	Lender Assessment	\N	yellow	\N	NORMAL	8	["accountant", "admin", "super_admin"]	\N	f	\N	f	1450	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-query	workflow-mortgage-broker	query_raised	Additional Info Required	\N	orange	\N	QUERY	9	["accountant", "admin", "super_admin"]	\N	f	\N	t	1450	300	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-conditional	workflow-mortgage-broker	conditional_approval	Conditional Approval	\N	indigo	\N	NORMAL	10	["accountant", "admin", "super_admin"]	\N	f	\N	t	1650	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-unconditional	workflow-mortgage-broker	unconditional_approval	Unconditional Approval	\N	blue	\N	NORMAL	11	["accountant", "admin", "super_admin"]	\N	f	\N	t	1850	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-settlement	workflow-mortgage-broker	settlement	Settlement	\N	green	\N	NORMAL	12	["accountant", "admin", "super_admin"]	\N	f	\N	t	2050	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
tax-step-admin-review	workflow-tax-agent	admin_review	Admin Review	\N	purple	\N	NORMAL	10	["admin", "super_admin"]	\N	f	\N	f	1550	150	2026-01-23 07:55:16.489786	2026-01-23 07:55:16.489786
tax-step-completed	workflow-tax-agent	completed	Completed	\N	green	\N	END	12	["accountant", "admin", "super_admin"]	\N	f	\N	t	1650	150	2026-01-23 07:24:06.140498	2026-01-23 07:24:06.140498
bas-step-admin-review	workflow-bas-agent	admin_review	Admin Final Review	\N	purple	\N	NORMAL	10	["admin", "super_admin"]	\N	f	\N	f	1550	150	2026-01-23 07:55:16.513977	2026-01-23 07:55:16.513977
book-step-admin-review	workflow-bookkeeper	admin_review	Admin Final Review	\N	purple	\N	NORMAL	9	["admin", "super_admin"]	\N	f	\N	f	1350	150	2026-01-23 07:55:16.525341	2026-01-23 07:55:16.525341
book-step-completed	workflow-bookkeeper	completed	Completed	\N	green	\N	END	10	["accountant", "admin", "super_admin"]	\N	f	\N	t	1450	150	2026-01-23 07:24:06.177203	2026-01-23 07:24:06.177203
fp-step-admin-review	workflow-financial-planner	admin_review	Admin Final Review	\N	purple	\N	NORMAL	12	["admin", "super_admin"]	\N	f	\N	f	1950	150	2026-01-23 07:55:16.533601	2026-01-23 07:55:16.533601
fp-step-completed	workflow-financial-planner	completed	Completed	\N	green	\N	END	13	["admin", "super_admin"]	\N	f	\N	t	2050	150	2026-01-23 07:24:06.190163	2026-01-23 07:24:06.190163
mb-step-admin-review	workflow-mortgage-broker	admin_review	Admin Final Review	\N	purple	\N	NORMAL	13	["admin", "super_admin"]	\N	f	\N	f	2150	150	2026-01-23 07:55:16.544363	2026-01-23 07:55:16.544363
mb-step-declined	workflow-mortgage-broker	declined	Declined	\N	red	\N	END	15	["admin", "super_admin"]	\N	f	\N	t	1650	300	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
mb-step-completed	workflow-mortgage-broker	completed	Completed	\N	green	\N	END	14	["admin", "super_admin"]	\N	f	\N	t	2250	150	2026-01-23 07:24:06.19996	2026-01-23 07:24:06.19996
step-admin-review	default-workflow	admin_review	Admin Review	\N	purple	\N	NORMAL	7	["admin", "super_admin"]	\N	f	\N	f	1350	150	2026-01-23 07:55:16.554329	2026-01-23 07:55:16.554329
\.


--
-- Data for Name: workflow_transitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, description, requires_invoice_raised, requires_invoice_paid, requires_assignment, allowed_roles, send_notification, notification_template, created_at) FROM stdin;
trans-1	default-workflow	step-pending	step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:02:19.960593
trans-2	default-workflow	step-invoice-raised	step-assigned	Assign	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:02:19.960593
trans-3	default-workflow	step-assigned	step-processing	Start Processing	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:02:19.960593
trans-4	default-workflow	step-processing	step-query-raised	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:02:19.960593
trans-5	default-workflow	step-query-raised	step-review	Client Responded	\N	f	f	f	["user"]	t	\N	2026-01-23 07:02:19.960593
trans-6	default-workflow	step-review	step-processing	Resume Work	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:02:19.960593
trans-7	default-workflow	step-processing	step-completed	Complete	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:02:19.960593
4d1cebe6-d84c-42ad-b6ee-4d4da90b86ea	4a89df14-fd83-4c8a-976f-b042b652e8e1	ef6147ef-b0f4-4b1a-bf22-91ab43f83358	d6bf859b-b189-412f-a647-0b65a0467d11	New Transition	\N	f	f	f	null	t	\N	2026-01-23 07:09:27.593238
31098325-7b88-4025-bab5-0f98b858c33f	4a89df14-fd83-4c8a-976f-b042b652e8e1	d6bf859b-b189-412f-a647-0b65a0467d11	3a366a08-6ae0-4645-b390-9e7fa50c90c8	New Transition	\N	f	f	f	null	t	\N	2026-01-23 07:10:36.172356
tax-t1	workflow-tax-agent	tax-step-pending	tax-step-docs-requested	Request Documents	\N	f	f	f	["admin", "accountant", "super_admin"]	t	\N	2026-01-23 07:24:06.15293
tax-t2	workflow-tax-agent	tax-step-docs-requested	tax-step-docs-received	Documents Received	\N	f	f	f	["admin", "accountant", "super_admin", "user"]	t	\N	2026-01-23 07:24:06.15293
tax-t3	workflow-tax-agent	tax-step-docs-received	tax-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.15293
tax-t4	workflow-tax-agent	tax-step-invoice-raised	tax-step-assigned	Assign Accountant	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.15293
tax-t5	workflow-tax-agent	tax-step-assigned	tax-step-preparation	Start Preparation	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.15293
tax-t6	workflow-tax-agent	tax-step-preparation	tax-step-query	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.15293
tax-t7	workflow-tax-agent	tax-step-query	tax-step-review	Client Responded	\N	f	f	f	["user"]	t	\N	2026-01-23 07:24:06.15293
tax-t8	workflow-tax-agent	tax-step-review	tax-step-preparation	Resume Preparation	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.15293
tax-t9	workflow-tax-agent	tax-step-preparation	tax-step-lodgement	Ready for Lodgement	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.15293
tax-t10	workflow-tax-agent	tax-step-lodgement	tax-step-lodged	Lodge with ATO	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.15293
tax-t11	workflow-tax-agent	tax-step-lodged	tax-step-completed	Complete	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.15293
tax-t12	workflow-tax-agent	tax-step-review	tax-step-lodgement	Client Approved	\N	f	f	f	["user"]	t	\N	2026-01-23 07:24:06.15293
bas-t1	workflow-bas-agent	bas-step-pending	bas-step-data-collection	Request Data	\N	f	f	f	["admin", "accountant", "super_admin"]	t	\N	2026-01-23 07:24:06.163317
bas-t2	workflow-bas-agent	bas-step-data-collection	bas-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.163317
bas-t3	workflow-bas-agent	bas-step-invoice-raised	bas-step-assigned	Assign	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.163317
bas-t4	workflow-bas-agent	bas-step-assigned	bas-step-reconciliation	Start Reconciliation	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.163317
bas-t5	workflow-bas-agent	bas-step-reconciliation	bas-step-preparation	Prepare BAS	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.163317
bas-t6	workflow-bas-agent	bas-step-preparation	bas-step-query	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.163317
bas-t7	workflow-bas-agent	bas-step-query	bas-step-preparation	Query Resolved	\N	f	f	f	["accountant", "admin", "super_admin", "user"]	t	\N	2026-01-23 07:24:06.163317
bas-t8	workflow-bas-agent	bas-step-preparation	bas-step-review	Submit for Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.163317
bas-t9	workflow-bas-agent	bas-step-review	bas-step-lodged	Lodge BAS	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.163317
bas-t10	workflow-bas-agent	bas-step-lodged	bas-step-completed	Complete	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.163317
aud-t1	workflow-auditor	aud-step-pending	aud-step-engagement	Send Engagement Letter	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t2	workflow-auditor	aud-step-engagement	aud-step-docs-requested	Request Documents	\N	f	f	f	["admin", "accountant", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t3	workflow-auditor	aud-step-docs-requested	aud-step-docs-received	Documents Received	\N	f	f	f	["admin", "accountant", "super_admin", "user"]	t	\N	2026-01-23 07:24:06.171449
aud-t4	workflow-auditor	aud-step-docs-received	aud-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t5	workflow-auditor	aud-step-invoice-raised	aud-step-assigned	Assign Auditor	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t6	workflow-auditor	aud-step-assigned	aud-step-fieldwork	Start Fieldwork	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t7	workflow-auditor	aud-step-fieldwork	aud-step-query	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t8	workflow-auditor	aud-step-query	aud-step-fieldwork	Query Resolved	\N	f	f	f	["accountant", "admin", "super_admin", "user"]	t	\N	2026-01-23 07:24:06.171449
aud-t9	workflow-auditor	aud-step-fieldwork	aud-step-draft-report	Prepare Draft Report	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t10	workflow-auditor	aud-step-draft-report	aud-step-management-review	Submit for Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t11	workflow-auditor	aud-step-management-review	aud-step-draft-report	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t12	workflow-auditor	aud-step-management-review	aud-step-final-report	Approve & Issue	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
aud-t13	workflow-auditor	aud-step-final-report	aud-step-completed	Complete	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.171449
book-t1	workflow-bookkeeper	book-step-pending	book-step-access-setup	Setup Access	\N	f	f	f	["admin", "accountant", "super_admin"]	t	\N	2026-01-23 07:24:06.183743
book-t2	workflow-bookkeeper	book-step-access-setup	book-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.183743
book-t3	workflow-bookkeeper	book-step-invoice-raised	book-step-assigned	Assign	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.183743
book-t4	workflow-bookkeeper	book-step-assigned	book-step-processing	Start Processing	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.183743
book-t5	workflow-bookkeeper	book-step-processing	book-step-query	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.183743
book-t6	workflow-bookkeeper	book-step-query	book-step-processing	Query Resolved	\N	f	f	f	["accountant", "admin", "super_admin", "user"]	t	\N	2026-01-23 07:24:06.183743
book-t7	workflow-bookkeeper	book-step-processing	book-step-review	Submit for Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.183743
book-t8	workflow-bookkeeper	book-step-review	book-step-processing	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.183743
book-t9	workflow-bookkeeper	book-step-review	book-step-client-approval	Send for Approval	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.183743
book-t10	workflow-bookkeeper	book-step-client-approval	book-step-completed	Approve	\N	f	f	f	["user"]	t	\N	2026-01-23 07:24:06.183743
book-t11	workflow-bookkeeper	book-step-client-approval	book-step-processing	Request Changes	\N	f	f	f	["user"]	t	\N	2026-01-23 07:24:06.183743
fp-t1	workflow-financial-planner	fp-step-pending	fp-step-discovery	Schedule Discovery	\N	f	f	f	["admin", "accountant", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t2	workflow-financial-planner	fp-step-discovery	fp-step-fact-find	Send Fact Find	\N	f	f	f	["admin", "accountant", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t3	workflow-financial-planner	fp-step-fact-find	fp-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t4	workflow-financial-planner	fp-step-invoice-raised	fp-step-assigned	Assign Planner	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t5	workflow-financial-planner	fp-step-assigned	fp-step-analysis	Start Analysis	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t6	workflow-financial-planner	fp-step-analysis	fp-step-soa-prep	Prepare SOA	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t7	workflow-financial-planner	fp-step-soa-prep	fp-step-compliance-review	Submit for Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t8	workflow-financial-planner	fp-step-compliance-review	fp-step-soa-prep	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t9	workflow-financial-planner	fp-step-compliance-review	fp-step-presentation	Approve & Present	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t10	workflow-financial-planner	fp-step-presentation	fp-step-query	Client Query	\N	f	f	f	["user"]	t	\N	2026-01-23 07:24:06.19318
fp-t11	workflow-financial-planner	fp-step-query	fp-step-presentation	Query Resolved	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t12	workflow-financial-planner	fp-step-presentation	fp-step-implementation	Client Accepted	\N	f	f	f	["user", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
fp-t13	workflow-financial-planner	fp-step-implementation	fp-step-completed	Complete	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.19318
mb-t1	workflow-mortgage-broker	mb-step-pending	mb-step-consultation	Schedule Consultation	\N	f	f	f	["admin", "accountant", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t2	workflow-mortgage-broker	mb-step-consultation	mb-step-docs-collection	Request Documents	\N	f	f	f	["admin", "accountant", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t3	workflow-mortgage-broker	mb-step-docs-collection	mb-step-serviceability	Assess Serviceability	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t4	workflow-mortgage-broker	mb-step-serviceability	mb-step-product-selection	Select Products	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t5	workflow-mortgage-broker	mb-step-product-selection	mb-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t6	workflow-mortgage-broker	mb-step-invoice-raised	mb-step-application	Submit Application	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t7	workflow-mortgage-broker	mb-step-application	mb-step-assessment	Lender Assessing	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t8	workflow-mortgage-broker	mb-step-assessment	mb-step-query	Info Required	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t9	workflow-mortgage-broker	mb-step-query	mb-step-assessment	Info Provided	\N	f	f	f	["accountant", "admin", "super_admin", "user"]	t	\N	2026-01-23 07:24:06.204988
mb-t10	workflow-mortgage-broker	mb-step-assessment	mb-step-conditional	Conditional Approved	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t11	workflow-mortgage-broker	mb-step-assessment	mb-step-declined	Declined	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t12	workflow-mortgage-broker	mb-step-conditional	mb-step-unconditional	Unconditional Approved	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t13	workflow-mortgage-broker	mb-step-unconditional	mb-step-settlement	Proceed to Settlement	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
mb-t14	workflow-mortgage-broker	mb-step-settlement	mb-step-completed	Settlement Complete	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:24:06.204988
tax-t13	workflow-tax-agent	tax-step-lodged	tax-step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.509589
tax-t14	workflow-tax-agent	tax-step-admin-review	tax-step-preparation	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.509589
tax-t15	workflow-tax-agent	tax-step-admin-review	tax-step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.509589
bas-t11	workflow-bas-agent	bas-step-lodged	bas-step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.519376
bas-t12	workflow-bas-agent	bas-step-admin-review	bas-step-preparation	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.519376
bas-t13	workflow-bas-agent	bas-step-admin-review	bas-step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.519376
aud-t14	workflow-auditor	aud-step-management-review	aud-step-fieldwork	Major Rework Required	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.522258
book-t12	workflow-bookkeeper	book-step-client-approval	book-step-admin-review	Send for Admin Review	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.53065
book-t13	workflow-bookkeeper	book-step-admin-review	book-step-processing	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.53065
book-t14	workflow-bookkeeper	book-step-admin-review	book-step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.53065
fp-t14	workflow-financial-planner	fp-step-implementation	fp-step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.540455
fp-t15	workflow-financial-planner	fp-step-admin-review	fp-step-soa-prep	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.540455
fp-t16	workflow-financial-planner	fp-step-admin-review	fp-step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.540455
mb-t15	workflow-mortgage-broker	mb-step-settlement	mb-step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.551803
mb-t16	workflow-mortgage-broker	mb-step-admin-review	mb-step-application	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.551803
mb-t17	workflow-mortgage-broker	mb-step-admin-review	mb-step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.551803
t8	default-workflow	step-processing	step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.559229
t9	default-workflow	step-admin-review	step-processing	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.559229
t10	default-workflow	step-admin-review	step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-23 07:55:16.559229
tax-t16	workflow-tax-agent	tax-step-preparation	tax-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.562122
bas-t14	workflow-bas-agent	bas-step-preparation	bas-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.565099
book-t15	workflow-bookkeeper	book-step-processing	book-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.569391
fp-t17	workflow-financial-planner	fp-step-analysis	fp-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.571801
mb-t18	workflow-mortgage-broker	mb-step-assessment	mb-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-23 07:55:16.574217
trans-8	default-workflow	step-processing	step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin"]	t	\N	2026-01-26 09:12:25.363226
trans-9	default-workflow	step-admin-review	step-processing	Request Changes	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-26 09:12:25.363226
trans-10	default-workflow	step-admin-review	step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin"]	t	\N	2026-01-26 09:12:25.363226
\.


--
-- Name: assignment_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.assignment_history_id_seq', 1, false);


--
-- Name: client_notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.client_notes_id_seq', 1, false);


--
-- Name: client_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.client_tags_id_seq', 1, false);


--
-- Name: company_service_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.company_service_settings_id_seq', 1, false);


--
-- Name: currencies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.currencies_id_seq', 21, true);


--
-- Name: email_automation_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.email_automation_logs_id_seq', 1, false);


--
-- Name: email_automations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.email_automations_id_seq', 1, false);


--
-- Name: email_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.email_templates_id_seq', 27, true);


--
-- Name: form_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.form_questions_id_seq', 328, true);


--
-- Name: form_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.form_responses_id_seq', 1, false);


--
-- Name: forms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.forms_id_seq', 11, true);


--
-- Name: import_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.import_logs_id_seq', 1, false);


--
-- Name: invoice_line_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.invoice_line_items_id_seq', 1, false);


--
-- Name: invoice_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.invoice_payments_id_seq', 1, false);


--
-- Name: job_notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.job_notes_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_id_seq', 5, true);


--
-- Name: otps_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.otps_id_seq', 8, true);


--
-- Name: queries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.queries_id_seq', 7, true);


--
-- Name: request_audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.request_audit_log_id_seq', 1, false);


--
-- Name: request_audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.request_audit_logs_id_seq', 1, false);


--
-- Name: request_state_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.request_state_history_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 4, true);


--
-- Name: scheduled_emails_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.scheduled_emails_id_seq', 1, false);


--
-- Name: service_renewals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_renewals_id_seq', 1, false);


--
-- Name: services_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.services_id_seq', 73, true);


--
-- Name: system_email_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_email_config_id_seq', 1, true);


--
-- Name: tax_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tax_types_id_seq', 4, true);


--
-- Name: access_logs access_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_logs
    ADD CONSTRAINT access_logs_pkey PRIMARY KEY (id);


--
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: assignment_history assignment_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assignment_history
    ADD CONSTRAINT assignment_history_pkey PRIMARY KEY (id);


--
-- Name: client_notes client_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_notes
    ADD CONSTRAINT client_notes_pkey PRIMARY KEY (id);


--
-- Name: client_tags client_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_tags
    ADD CONSTRAINT client_tags_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: company_contacts company_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_contacts
    ADD CONSTRAINT company_contacts_pkey PRIMARY KEY (id);


--
-- Name: company_email_configs company_email_configs_company_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_email_configs
    ADD CONSTRAINT company_email_configs_company_id_key UNIQUE (company_id);


--
-- Name: company_email_configs company_email_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_email_configs
    ADD CONSTRAINT company_email_configs_pkey PRIMARY KEY (id);


--
-- Name: company_service_settings company_service_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_service_settings
    ADD CONSTRAINT company_service_settings_pkey PRIMARY KEY (id);


--
-- Name: company_storage_configs company_storage_configs_company_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_storage_configs
    ADD CONSTRAINT company_storage_configs_company_id_key UNIQUE (company_id);


--
-- Name: company_storage_configs company_storage_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_storage_configs
    ADD CONSTRAINT company_storage_configs_pkey PRIMARY KEY (id);


--
-- Name: currencies currencies_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.currencies
    ADD CONSTRAINT currencies_code_key UNIQUE (code);


--
-- Name: currencies currencies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.currencies
    ADD CONSTRAINT currencies_pkey PRIMARY KEY (id);


--
-- Name: db_version db_version_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.db_version
    ADD CONSTRAINT db_version_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: email_automation_logs email_automation_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_automation_logs
    ADD CONSTRAINT email_automation_logs_pkey PRIMARY KEY (id);


--
-- Name: email_automations email_automations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_automations
    ADD CONSTRAINT email_automations_pkey PRIMARY KEY (id);


--
-- Name: email_templates email_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_templates
    ADD CONSTRAINT email_templates_pkey PRIMARY KEY (id);


--
-- Name: form_questions form_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_questions
    ADD CONSTRAINT form_questions_pkey PRIMARY KEY (id);


--
-- Name: form_responses form_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_responses
    ADD CONSTRAINT form_responses_pkey PRIMARY KEY (id);


--
-- Name: forms forms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_pkey PRIMARY KEY (id);


--
-- Name: impersonation_sessions impersonation_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.impersonation_sessions
    ADD CONSTRAINT impersonation_sessions_pkey PRIMARY KEY (id);


--
-- Name: import_logs import_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_logs
    ADD CONSTRAINT import_logs_pkey PRIMARY KEY (id);


--
-- Name: invoice_line_items invoice_line_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_line_items
    ADD CONSTRAINT invoice_line_items_pkey PRIMARY KEY (id);


--
-- Name: invoice_payments invoice_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_payments
    ADD CONSTRAINT invoice_payments_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_invoice_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_invoice_number_key UNIQUE (invoice_number);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: job_notes job_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_notes
    ADD CONSTRAINT job_notes_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: otps otps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otps
    ADD CONSTRAINT otps_pkey PRIMARY KEY (id);


--
-- Name: queries queries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_pkey PRIMARY KEY (id);


--
-- Name: request_audit_log request_audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_audit_log
    ADD CONSTRAINT request_audit_log_pkey PRIMARY KEY (id);


--
-- Name: request_audit_logs request_audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_audit_logs
    ADD CONSTRAINT request_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: request_state_history request_state_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_state_history
    ADD CONSTRAINT request_state_history_pkey PRIMARY KEY (id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: scheduled_emails scheduled_emails_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scheduled_emails
    ADD CONSTRAINT scheduled_emails_pkey PRIMARY KEY (id);


--
-- Name: service_renewals service_renewals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_renewals
    ADD CONSTRAINT service_renewals_pkey PRIMARY KEY (id);


--
-- Name: service_renewals service_renewals_user_id_service_id_next_due_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_renewals
    ADD CONSTRAINT service_renewals_user_id_service_id_next_due_date_key UNIQUE (user_id, service_id, next_due_date);


--
-- Name: service_requests service_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_pkey PRIMARY KEY (id);


--
-- Name: service_requests service_requests_request_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_request_number_key UNIQUE (request_number);


--
-- Name: service_workflows service_workflows_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_workflows
    ADD CONSTRAINT service_workflows_pkey PRIMARY KEY (id);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: system_email_config system_email_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_email_config
    ADD CONSTRAINT system_email_config_pkey PRIMARY KEY (id);


--
-- Name: tax_types tax_types_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tax_types
    ADD CONSTRAINT tax_types_code_key UNIQUE (code);


--
-- Name: tax_types tax_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tax_types
    ADD CONSTRAINT tax_types_pkey PRIMARY KEY (id);


--
-- Name: company_service_settings unique_company_service; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_service_settings
    ADD CONSTRAINT unique_company_service UNIQUE (company_id, service_id);


--
-- Name: client_tags uq_tag_name_company; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_tags
    ADD CONSTRAINT uq_tag_name_company UNIQUE (name, company_id);


--
-- Name: email_templates uq_template_slug_company; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_templates
    ADD CONSTRAINT uq_template_slug_company UNIQUE (slug, company_id);


--
-- Name: user_tags user_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_tags
    ADD CONSTRAINT user_tags_pkey PRIMARY KEY (user_id, tag_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: workflow_automations workflow_automations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_automations
    ADD CONSTRAINT workflow_automations_pkey PRIMARY KEY (id);


--
-- Name: workflow_steps workflow_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_pkey PRIMARY KEY (id);


--
-- Name: workflow_transitions workflow_transitions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_transitions
    ADD CONSTRAINT workflow_transitions_pkey PRIMARY KEY (id);


--
-- Name: idx_access_logs_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_access_logs_created ON public.access_logs USING btree (created_at);


--
-- Name: idx_access_logs_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_access_logs_user ON public.access_logs USING btree (user_id);


--
-- Name: idx_assignment_history_request; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assignment_history_request ON public.assignment_history USING btree (service_request_id);


--
-- Name: idx_assignment_history_to_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assignment_history_to_user ON public.assignment_history USING btree (to_user_id);


--
-- Name: idx_company_contacts_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_company_contacts_company_id ON public.company_contacts USING btree (company_id);


--
-- Name: idx_company_contacts_contact_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_company_contacts_contact_type ON public.company_contacts USING btree (contact_type);


--
-- Name: idx_company_contacts_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_company_contacts_is_active ON public.company_contacts USING btree (is_active);


--
-- Name: idx_company_contacts_is_primary; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_company_contacts_is_primary ON public.company_contacts USING btree (is_primary);


--
-- Name: idx_company_email_configs_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_company_email_configs_company_id ON public.company_email_configs USING btree (company_id);


--
-- Name: idx_company_storage_configs_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_company_storage_configs_company_id ON public.company_storage_configs USING btree (company_id);


--
-- Name: idx_documents_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_documents_company ON public.documents USING btree (company_id);


--
-- Name: idx_email_templates_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_templates_category ON public.email_templates USING btree (service_category);


--
-- Name: idx_email_templates_service; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_templates_service ON public.email_templates USING btree (service_id);


--
-- Name: idx_email_templates_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_templates_type ON public.email_templates USING btree (template_type);


--
-- Name: idx_import_logs_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_import_logs_company ON public.import_logs USING btree (company_id);


--
-- Name: idx_import_logs_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_import_logs_created ON public.import_logs USING btree (created_at);


--
-- Name: idx_import_logs_imported_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_import_logs_imported_by ON public.import_logs USING btree (imported_by_id);


--
-- Name: idx_import_logs_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_import_logs_type ON public.import_logs USING btree (import_type);


--
-- Name: idx_queries_is_internal; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_queries_is_internal ON public.queries USING btree (is_internal);


--
-- Name: idx_renewals_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_renewals_company ON public.service_renewals USING btree (company_id);


--
-- Name: idx_renewals_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_renewals_due_date ON public.service_renewals USING btree (next_due_date);


--
-- Name: idx_renewals_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_renewals_status ON public.service_renewals USING btree (status);


--
-- Name: idx_renewals_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_renewals_user ON public.service_renewals USING btree (user_id);


--
-- Name: idx_request_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_request_audit_logs_created_at ON public.request_audit_logs USING btree (created_at DESC);


--
-- Name: idx_request_audit_logs_modified_by_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_request_audit_logs_modified_by_id ON public.request_audit_logs USING btree (modified_by_id);


--
-- Name: idx_request_audit_logs_service_request_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_request_audit_logs_service_request_id ON public.request_audit_logs USING btree (service_request_id);


--
-- Name: idx_service_requests_request_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_service_requests_request_number ON public.service_requests USING btree (request_number);


--
-- Name: idx_service_requests_step; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_service_requests_step ON public.service_requests USING btree (current_step_id);


--
-- Name: idx_service_workflows_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_service_workflows_company ON public.service_workflows USING btree (company_id);


--
-- Name: idx_services_workflow; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_services_workflow ON public.services USING btree (workflow_id);


--
-- Name: idx_workflow_automations_step; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workflow_automations_step ON public.workflow_automations USING btree (step_id);


--
-- Name: idx_workflow_automations_workflow; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workflow_automations_workflow ON public.workflow_automations USING btree (workflow_id);


--
-- Name: idx_workflow_steps_workflow; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workflow_steps_workflow ON public.workflow_steps USING btree (workflow_id);


--
-- Name: idx_workflow_transitions_from_step; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workflow_transitions_from_step ON public.workflow_transitions USING btree (from_step_id);


--
-- Name: idx_workflow_transitions_to_step; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workflow_transitions_to_step ON public.workflow_transitions USING btree (to_step_id);


--
-- Name: idx_workflow_transitions_workflow; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workflow_transitions_workflow ON public.workflow_transitions USING btree (workflow_id);


--
-- Name: ix_access_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_access_logs_created_at ON public.access_logs USING btree (created_at);


--
-- Name: ix_activity_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_logs_created_at ON public.activity_logs USING btree (created_at);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: access_logs access_logs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_logs
    ADD CONSTRAINT access_logs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE SET NULL;


--
-- Name: access_logs access_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_logs
    ADD CONSTRAINT access_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: activity_logs activity_logs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: activity_logs activity_logs_performed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_performed_by_id_fkey FOREIGN KEY (performed_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: assignment_history assignment_history_assigned_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assignment_history
    ADD CONSTRAINT assignment_history_assigned_by_id_fkey FOREIGN KEY (assigned_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: assignment_history assignment_history_from_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assignment_history
    ADD CONSTRAINT assignment_history_from_user_id_fkey FOREIGN KEY (from_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: assignment_history assignment_history_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assignment_history
    ADD CONSTRAINT assignment_history_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id) ON DELETE CASCADE;


--
-- Name: assignment_history assignment_history_to_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assignment_history
    ADD CONSTRAINT assignment_history_to_user_id_fkey FOREIGN KEY (to_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: client_notes client_notes_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_notes
    ADD CONSTRAINT client_notes_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: client_notes client_notes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_notes
    ADD CONSTRAINT client_notes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: client_tags client_tags_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_tags
    ADD CONSTRAINT client_tags_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: companies companies_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: company_contacts company_contacts_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_contacts
    ADD CONSTRAINT company_contacts_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: company_email_configs company_email_configs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_email_configs
    ADD CONSTRAINT company_email_configs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: company_service_settings company_service_settings_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_service_settings
    ADD CONSTRAINT company_service_settings_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: company_service_settings company_service_settings_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_service_settings
    ADD CONSTRAINT company_service_settings_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id);


--
-- Name: company_storage_configs company_storage_configs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_storage_configs
    ADD CONSTRAINT company_storage_configs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: documents documents_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE SET NULL;


--
-- Name: documents documents_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id);


--
-- Name: documents documents_uploaded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_uploaded_by_id_fkey FOREIGN KEY (uploaded_by_id) REFERENCES public.users(id);


--
-- Name: email_automation_logs email_automation_logs_automation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_automation_logs
    ADD CONSTRAINT email_automation_logs_automation_id_fkey FOREIGN KEY (automation_id) REFERENCES public.email_automations(id) ON DELETE CASCADE;


--
-- Name: email_automation_logs email_automation_logs_recipient_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_automation_logs
    ADD CONSTRAINT email_automation_logs_recipient_user_id_fkey FOREIGN KEY (recipient_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: email_automations email_automations_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_automations
    ADD CONSTRAINT email_automations_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: email_automations email_automations_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_automations
    ADD CONSTRAINT email_automations_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: email_automations email_automations_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_automations
    ADD CONSTRAINT email_automations_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.email_templates(id) ON DELETE SET NULL;


--
-- Name: email_templates email_templates_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_templates
    ADD CONSTRAINT email_templates_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: email_templates email_templates_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_templates
    ADD CONSTRAINT email_templates_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE SET NULL;


--
-- Name: form_questions form_questions_conditional_on_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_questions
    ADD CONSTRAINT form_questions_conditional_on_question_id_fkey FOREIGN KEY (conditional_on_question_id) REFERENCES public.form_questions(id);


--
-- Name: form_questions form_questions_form_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_questions
    ADD CONSTRAINT form_questions_form_id_fkey FOREIGN KEY (form_id) REFERENCES public.forms(id);


--
-- Name: form_responses form_responses_form_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_responses
    ADD CONSTRAINT form_responses_form_id_fkey FOREIGN KEY (form_id) REFERENCES public.forms(id);


--
-- Name: form_responses form_responses_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_responses
    ADD CONSTRAINT form_responses_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id);


--
-- Name: form_responses form_responses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_responses
    ADD CONSTRAINT form_responses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: forms forms_cloned_from_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_cloned_from_id_fkey FOREIGN KEY (cloned_from_id) REFERENCES public.forms(id);


--
-- Name: forms forms_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: forms forms_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: impersonation_sessions impersonation_sessions_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.impersonation_sessions
    ADD CONSTRAINT impersonation_sessions_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: impersonation_sessions impersonation_sessions_impersonated_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.impersonation_sessions
    ADD CONSTRAINT impersonation_sessions_impersonated_user_id_fkey FOREIGN KEY (impersonated_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: import_logs import_logs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_logs
    ADD CONSTRAINT import_logs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE SET NULL;


--
-- Name: import_logs import_logs_imported_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_logs
    ADD CONSTRAINT import_logs_imported_by_id_fkey FOREIGN KEY (imported_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: invoice_line_items invoice_line_items_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_line_items
    ADD CONSTRAINT invoice_line_items_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id) ON DELETE CASCADE;


--
-- Name: invoice_line_items invoice_line_items_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_line_items
    ADD CONSTRAINT invoice_line_items_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id);


--
-- Name: invoice_payments invoice_payments_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_payments
    ADD CONSTRAINT invoice_payments_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id) ON DELETE CASCADE;


--
-- Name: invoices invoices_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id);


--
-- Name: invoices invoices_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: invoices invoices_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: invoices invoices_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id);


--
-- Name: job_notes job_notes_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_notes
    ADD CONSTRAINT job_notes_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: job_notes job_notes_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_notes
    ADD CONSTRAINT job_notes_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: otps otps_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otps
    ADD CONSTRAINT otps_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: queries queries_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- Name: queries queries_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id);


--
-- Name: request_audit_log request_audit_log_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_audit_log
    ADD CONSTRAINT request_audit_log_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id) ON DELETE CASCADE;


--
-- Name: request_audit_log request_audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_audit_log
    ADD CONSTRAINT request_audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: request_audit_logs request_audit_logs_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_audit_logs
    ADD CONSTRAINT request_audit_logs_modified_by_id_fkey FOREIGN KEY (modified_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: request_audit_logs request_audit_logs_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_audit_logs
    ADD CONSTRAINT request_audit_logs_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id) ON DELETE CASCADE;


--
-- Name: request_state_history request_state_history_changed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_state_history
    ADD CONSTRAINT request_state_history_changed_by_id_fkey FOREIGN KEY (changed_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: request_state_history request_state_history_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_state_history
    ADD CONSTRAINT request_state_history_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id) ON DELETE CASCADE;


--
-- Name: scheduled_emails scheduled_emails_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scheduled_emails
    ADD CONSTRAINT scheduled_emails_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: scheduled_emails scheduled_emails_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scheduled_emails
    ADD CONSTRAINT scheduled_emails_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: scheduled_emails scheduled_emails_recipient_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scheduled_emails
    ADD CONSTRAINT scheduled_emails_recipient_user_id_fkey FOREIGN KEY (recipient_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: scheduled_emails scheduled_emails_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scheduled_emails
    ADD CONSTRAINT scheduled_emails_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.email_templates(id) ON DELETE SET NULL;


--
-- Name: service_renewals service_renewals_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_renewals
    ADD CONSTRAINT service_renewals_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: service_renewals service_renewals_last_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_renewals
    ADD CONSTRAINT service_renewals_last_request_id_fkey FOREIGN KEY (last_request_id) REFERENCES public.service_requests(id) ON DELETE SET NULL;


--
-- Name: service_renewals service_renewals_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_renewals
    ADD CONSTRAINT service_renewals_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;


--
-- Name: service_renewals service_renewals_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_renewals
    ADD CONSTRAINT service_renewals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: service_requests service_requests_assigned_accountant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_assigned_accountant_id_fkey FOREIGN KEY (assigned_accountant_id) REFERENCES public.users(id);


--
-- Name: service_requests service_requests_current_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_current_step_id_fkey FOREIGN KEY (current_step_id) REFERENCES public.workflow_steps(id) ON DELETE SET NULL;


--
-- Name: service_requests service_requests_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id);


--
-- Name: service_requests service_requests_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: service_workflows service_workflows_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_workflows
    ADD CONSTRAINT service_workflows_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: service_workflows service_workflows_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_workflows
    ADD CONSTRAINT service_workflows_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: services services_form_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_form_id_fkey FOREIGN KEY (form_id) REFERENCES public.forms(id);


--
-- Name: services services_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.service_workflows(id) ON DELETE SET NULL;


--
-- Name: user_tags user_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_tags
    ADD CONSTRAINT user_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.client_tags(id) ON DELETE CASCADE;


--
-- Name: user_tags user_tags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_tags
    ADD CONSTRAINT user_tags_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: users users_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: users users_invited_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_invited_by_id_fkey FOREIGN KEY (invited_by_id) REFERENCES public.users(id);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: workflow_automations workflow_automations_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_automations
    ADD CONSTRAINT workflow_automations_step_id_fkey FOREIGN KEY (step_id) REFERENCES public.workflow_steps(id) ON DELETE CASCADE;


--
-- Name: workflow_automations workflow_automations_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_automations
    ADD CONSTRAINT workflow_automations_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.service_workflows(id) ON DELETE CASCADE;


--
-- Name: workflow_steps workflow_steps_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.service_workflows(id) ON DELETE CASCADE;


--
-- Name: workflow_transitions workflow_transitions_from_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_transitions
    ADD CONSTRAINT workflow_transitions_from_step_id_fkey FOREIGN KEY (from_step_id) REFERENCES public.workflow_steps(id) ON DELETE CASCADE;


--
-- Name: workflow_transitions workflow_transitions_to_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_transitions
    ADD CONSTRAINT workflow_transitions_to_step_id_fkey FOREIGN KEY (to_step_id) REFERENCES public.workflow_steps(id) ON DELETE CASCADE;


--
-- Name: workflow_transitions workflow_transitions_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_transitions
    ADD CONSTRAINT workflow_transitions_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.service_workflows(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict NKjvCW5buHtmztcvtCzPheGpkTdYcgsHjKT2KWTMzXNyZ5sAYcc0bjjfeubd5k6

