--
-- PostgreSQL database dump
--

\restrict PpHAC5U5sHicVxroikuPwxYQ7pIpkiQJaGs42bIH1iRfH0x1KpggdboNl9KbLVv

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

DROP DATABASE IF EXISTS accountant_crm;
--
-- Name: accountant_crm; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE accountant_crm WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE accountant_crm OWNER TO postgres;

\unrestrict PpHAC5U5sHicVxroikuPwxYQ7pIpkiQJaGs42bIH1iRfH0x1KpggdboNl9KbLVv
\connect accountant_crm
\restrict PpHAC5U5sHicVxroikuPwxYQ7pIpkiQJaGs42bIH1iRfH0x1KpggdboNl9KbLVv

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
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


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
-- Name: emailprovidertype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.emailprovidertype AS ENUM (
    'GMAIL',
    'OUTLOOK',
    'ZOHO',
    'CUSTOM'
);


ALTER TYPE public.emailprovidertype OWNER TO postgres;

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
-- Name: storageprovidertype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.storageprovidertype AS ENUM (
    'AZURE_BLOB',
    'GOOGLE_DRIVE',
    'SHAREPOINT',
    'ZOHO_DRIVE'
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
-- Name: assignment_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assignment_history (
    id integer NOT NULL,
    service_request_id character varying(36) NOT NULL,
    from_user_id character varying(36),
    to_user_id character varying(36),
    assigned_by_id character varying(36),
    assignment_type character varying(50),
    reason text,
    created_at timestamp without time zone
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
-- Name: client_entities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_entities (
    id character varying(36) NOT NULL,
    company_id character varying(36) NOT NULL,
    name character varying(200) NOT NULL,
    trading_name character varying(200),
    entity_type character varying(50) NOT NULL,
    abn character varying(20),
    acn character varying(20),
    tfn character varying(20),
    trust_type character varying(50),
    trustee_name character varying(200),
    trust_deed_date date,
    email character varying(120),
    phone character varying(20),
    address_line1 character varying(200),
    address_line2 character varying(200),
    city character varying(100),
    state character varying(50),
    postcode character varying(10),
    country character varying(100),
    financial_year_end_month integer,
    financial_year_end_day integer,
    xero_contact_id character varying(100),
    is_active boolean,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by_id character varying(36)
);


ALTER TABLE public.client_entities OWNER TO postgres;

--
-- Name: client_entity_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_entity_contacts (
    id integer NOT NULL,
    client_entity_id character varying(36) NOT NULL,
    user_id character varying(36),
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(120),
    phone character varying(20),
    "position" character varying(100),
    contact_type character varying(20),
    is_primary boolean,
    effective_from date NOT NULL,
    effective_to date,
    is_active boolean,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.client_entity_contacts OWNER TO postgres;

--
-- Name: client_entity_contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.client_entity_contacts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.client_entity_contacts_id_seq OWNER TO postgres;

--
-- Name: client_entity_contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.client_entity_contacts_id_seq OWNED BY public.client_entity_contacts.id;


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
-- Name: client_service_pricing; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_service_pricing (
    id character varying(36) NOT NULL,
    company_id character varying(36) NOT NULL,
    user_id character varying(36),
    client_entity_id character varying(36),
    service_id integer NOT NULL,
    custom_price numeric(10,2),
    discount_percentage numeric(5,2),
    notes text,
    valid_from date,
    valid_until date,
    is_active boolean,
    created_by_id character varying(36),
    updated_by_id character varying(36),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.client_service_pricing OWNER TO postgres;

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
    company_type character varying(50),
    logo_url character varying(500),
    logo_data bytea,
    logo_mime_type character varying(50),
    primary_color character varying(20),
    secondary_color character varying(20),
    tertiary_color character varying(20),
    sidebar_bg_color character varying(20),
    sidebar_text_color character varying(20),
    sidebar_hover_bg_color character varying(20),
    currency character varying(3),
    currency_symbol character varying(5),
    tax_type character varying(20),
    tax_label character varying(20),
    default_tax_rate numeric(5,2),
    invoice_prefix character varying(20),
    invoice_footer text,
    invoice_notes text,
    invoice_bank_details text,
    invoice_payment_terms character varying(100),
    invoice_show_logo boolean,
    invoice_show_company_details boolean,
    invoice_show_client_details boolean,
    invoice_show_bank_details boolean,
    invoice_show_payment_terms boolean,
    invoice_show_notes boolean,
    invoice_show_footer boolean,
    invoice_show_tax boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.companies OWNER TO postgres;

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
    contact_type public.contacttype,
    is_primary boolean,
    effective_from date,
    effective_to date,
    is_active boolean,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.company_contacts OWNER TO postgres;

--
-- Name: company_email_configs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_email_configs (
    id character varying(36) NOT NULL,
    company_id character varying(36) NOT NULL,
    provider public.emailprovidertype,
    is_enabled boolean,
    smtp_host character varying(255),
    smtp_port integer,
    smtp_username character varying(255),
    smtp_password character varying(500),
    smtp_use_tls boolean,
    smtp_use_ssl boolean,
    sender_email character varying(255),
    sender_name character varying(255),
    reply_to_email character varying(255),
    oauth_access_token text,
    oauth_refresh_token text,
    oauth_token_expires_at timestamp without time zone,
    last_test_at timestamp without time zone,
    last_test_success boolean,
    last_error text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.company_email_configs OWNER TO postgres;

--
-- Name: company_request_statuses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_request_statuses (
    id integer NOT NULL,
    company_id character varying(36) NOT NULL,
    status_key character varying(50) NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    "position" integer NOT NULL,
    wip_limit integer,
    is_final boolean,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.company_request_statuses OWNER TO postgres;

--
-- Name: company_request_statuses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_request_statuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.company_request_statuses_id_seq OWNER TO postgres;

--
-- Name: company_request_statuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_request_statuses_id_seq OWNED BY public.company_request_statuses.id;


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
    cost_percentage numeric(5,2),
    display_order integer,
    is_featured boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
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
    provider public.storageprovidertype,
    is_enabled boolean,
    sharepoint_site_id character varying(255),
    sharepoint_drive_id character varying(255),
    sharepoint_root_folder character varying(255),
    zoho_client_id character varying(255),
    zoho_client_secret character varying(500),
    zoho_access_token text,
    zoho_refresh_token text,
    zoho_token_expires_at timestamp without time zone,
    zoho_root_folder_id character varying(255),
    zoho_org_id character varying(255),
    google_client_id character varying(255),
    google_client_secret character varying(500),
    google_access_token text,
    google_refresh_token text,
    google_token_expires_at timestamp without time zone,
    google_root_folder_id character varying(255),
    azure_connection_string text,
    azure_container_name character varying(255),
    last_sync_at timestamp without time zone,
    last_error text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.company_storage_configs OWNER TO postgres;

--
-- Name: currencies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.currencies (
    id integer NOT NULL,
    code character varying(3) NOT NULL,
    name character varying(100) NOT NULL,
    symbol character varying(10) NOT NULL,
    is_active boolean,
    created_at timestamp without time zone
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
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documents (
    id character varying(36) NOT NULL,
    original_filename character varying(500) NOT NULL,
    stored_filename character varying(500) NOT NULL,
    file_type character varying(50),
    file_size integer,
    mime_type character varying(100),
    storage_path character varying(1000),
    storage_url character varying(1000),
    storage_type character varying(50),
    blob_name character varying(1000),
    blob_url character varying(1000),
    external_item_id character varying(255),
    external_web_url character varying(1000),
    client_folder_name character varying(255),
    company_id character varying(36),
    uploaded_by_id character varying(36) NOT NULL,
    service_request_id character varying(36),
    document_category character varying(100),
    description text,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.documents OWNER TO postgres;

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
    service_id integer,
    template_type character varying(50),
    service_category character varying(50),
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
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
    is_internal boolean,
    created_at timestamp without time zone
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
-- Name: request_audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.request_audit_logs (
    id integer NOT NULL,
    service_request_id character varying(36) NOT NULL,
    modified_by_id character varying(36),
    field_name character varying(100) NOT NULL,
    old_value text,
    new_value text,
    created_at timestamp without time zone
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
    reminders_sent json,
    last_reminder_at timestamp without time zone,
    status character varying(20),
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
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
    client_entity_id character varying(36),
    request_number character varying(20),
    description text,
    status character varying(50),
    current_step_id character varying(36),
    internal_notes text,
    invoice_raised boolean,
    invoice_paid boolean,
    invoice_amount numeric(10,2),
    payment_link character varying(500),
    xero_reference_job_id character varying(100),
    internal_reference character varying(100),
    deadline_date date,
    priority character varying(20),
    actual_cost numeric(10,2),
    cost_notes text,
    labor_hours numeric(6,2),
    labor_rate numeric(10,2),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    completed_at timestamp without time zone
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
    is_default boolean,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
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
    workflow_id character varying(36),
    cost_percentage numeric(5,2),
    cost_category character varying(50),
    is_recurring boolean,
    renewal_period_months integer,
    renewal_reminder_days json,
    renewal_due_month integer,
    renewal_due_day integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
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
-- Name: smsf_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.smsf_questions (
    id integer NOT NULL,
    text text NOT NULL,
    category character varying(50) NOT NULL,
    type character varying(50) NOT NULL,
    weight double precision,
    "order" integer,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    options json
);


ALTER TABLE public.smsf_questions OWNER TO postgres;

--
-- Name: smsf_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.smsf_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.smsf_questions_id_seq OWNER TO postgres;

--
-- Name: smsf_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.smsf_questions_id_seq OWNED BY public.smsf_questions.id;


--
-- Name: smsf_submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.smsf_submissions (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    email character varying(200) NOT NULL,
    phone character varying(50) NOT NULL,
    answers json,
    scores json,
    overall_score double precision,
    ip_address character varying(50),
    user_agent text,
    submitted_at timestamp without time zone,
    client_entity_id character varying(36)
);


ALTER TABLE public.smsf_submissions OWNER TO postgres;

--
-- Name: smsf_submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.smsf_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.smsf_submissions_id_seq OWNER TO postgres;

--
-- Name: smsf_submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.smsf_submissions_id_seq OWNED BY public.smsf_submissions.id;


--
-- Name: system_email_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_email_config (
    id integer NOT NULL,
    provider public.emailprovidertype,
    is_enabled boolean,
    smtp_host character varying(255),
    smtp_port integer,
    smtp_username character varying(255),
    smtp_password character varying(500),
    smtp_use_tls boolean,
    smtp_use_ssl boolean,
    sender_email character varying(255),
    sender_name character varying(255),
    use_as_fallback boolean,
    last_test_at timestamp without time zone,
    last_test_success boolean,
    last_error text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.system_email_config OWNER TO postgres;

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
-- Name: system_request_statuses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_request_statuses (
    id integer NOT NULL,
    status_key character varying(50) NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    "position" integer NOT NULL,
    is_final boolean,
    is_active boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.system_request_statuses OWNER TO postgres;

--
-- Name: system_request_statuses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_request_statuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_request_statuses_id_seq OWNER TO postgres;

--
-- Name: system_request_statuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_request_statuses_id_seq OWNED BY public.system_request_statuses.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    id character varying(36) NOT NULL,
    company_id character varying(36) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    created_by_id character varying(36) NOT NULL,
    assigned_to_id character varying(36),
    service_request_id character varying(36),
    status character varying(50),
    priority character varying(20),
    due_date date,
    completed_at timestamp without time zone,
    estimated_minutes integer,
    actual_minutes integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- Name: tax_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tax_types (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    default_rate numeric(5,2),
    is_active boolean,
    created_at timestamp without time zone
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
    is_external_accountant boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    last_login timestamp without time zone,
    company_id character varying(36),
    invited_by_id character varying(36),
    supervisor_id character varying(36)
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
    action_config json,
    conditions json,
    delay_minutes integer,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
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
    color character varying(20),
    icon character varying(50),
    step_type public.steptype,
    "order" integer,
    allowed_roles json,
    required_fields json,
    auto_assign boolean,
    notify_roles json,
    notify_client boolean,
    position_x double precision,
    position_y double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
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
    requires_invoice_raised boolean,
    requires_invoice_paid boolean,
    requires_assignment boolean,
    allowed_roles json,
    send_notification boolean,
    notification_template text,
    created_at timestamp without time zone
);


ALTER TABLE public.workflow_transitions OWNER TO postgres;

--
-- Name: assignment_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assignment_history ALTER COLUMN id SET DEFAULT nextval('public.assignment_history_id_seq'::regclass);


--
-- Name: client_entity_contacts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_entity_contacts ALTER COLUMN id SET DEFAULT nextval('public.client_entity_contacts_id_seq'::regclass);


--
-- Name: client_notes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_notes ALTER COLUMN id SET DEFAULT nextval('public.client_notes_id_seq'::regclass);


--
-- Name: client_tags id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_tags ALTER COLUMN id SET DEFAULT nextval('public.client_tags_id_seq'::regclass);


--
-- Name: company_request_statuses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_request_statuses ALTER COLUMN id SET DEFAULT nextval('public.company_request_statuses_id_seq'::regclass);


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
-- Name: smsf_questions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.smsf_questions ALTER COLUMN id SET DEFAULT nextval('public.smsf_questions_id_seq'::regclass);


--
-- Name: smsf_submissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.smsf_submissions ALTER COLUMN id SET DEFAULT nextval('public.smsf_submissions_id_seq'::regclass);


--
-- Name: system_email_config id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_email_config ALTER COLUMN id SET DEFAULT nextval('public.system_email_config_id_seq'::regclass);


--
-- Name: system_request_statuses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_request_statuses ALTER COLUMN id SET DEFAULT nextval('public.system_request_statuses_id_seq'::regclass);


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
-- Data for Name: assignment_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.assignment_history (id, service_request_id, from_user_id, to_user_id, assigned_by_id, assignment_type, reason, created_at) FROM stdin;
\.


--
-- Data for Name: client_entities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_entities (id, company_id, name, trading_name, entity_type, abn, acn, tfn, trust_type, trustee_name, trust_deed_date, email, phone, address_line1, address_line2, city, state, postcode, country, financial_year_end_month, financial_year_end_day, xero_contact_id, is_active, notes, created_at, updated_at, created_by_id) FROM stdin;
\.


--
-- Data for Name: client_entity_contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_entity_contacts (id, client_entity_id, user_id, first_name, last_name, email, phone, "position", contact_type, is_primary, effective_from, effective_to, is_active, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: client_notes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_notes (id, user_id, created_by_id, content, is_pinned, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: client_service_pricing; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_service_pricing (id, company_id, user_id, client_entity_id, service_id, custom_price, discount_percentage, notes, valid_from, valid_until, is_active, created_by_id, updated_by_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: client_tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_tags (id, name, color, company_id, created_at) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.companies (id, name, trading_name, abn, acn, email, phone, website, address_line1, address_line2, city, state, postcode, country, owner_id, plan_type, max_users, max_clients, is_active, company_type, logo_url, logo_data, logo_mime_type, primary_color, secondary_color, tertiary_color, sidebar_bg_color, sidebar_text_color, sidebar_hover_bg_color, currency, currency_symbol, tax_type, tax_label, default_tax_rate, invoice_prefix, invoice_footer, invoice_notes, invoice_bank_details, invoice_payment_terms, invoice_show_logo, invoice_show_company_details, invoice_show_client_details, invoice_show_bank_details, invoice_show_payment_terms, invoice_show_notes, invoice_show_footer, invoice_show_tax, created_at, updated_at) FROM stdin;
0950fc1f-cddf-4fb3-b926-54a573059dc8	Pointers Consulting	Pointers Consulting Pty Ltd	\N	\N	sam@pointersconsulting.com.au	+61 426 784 982	\N	Sydney	\N	Sydney	NSW	2000	Australia	\N	enterprise	100	10000	t	tax_agent	/assets/pointers-logo.png	\N	\N	#2D8C3C	#1F7A2E	#3BA34D	#0f172a	#ffffff	#334155	AUD	$	GST	GST	10.00	INV	\N	\N	\N	Due within 14 days	t	t	t	t	t	t	t	t	2026-02-04 06:57:12.383614	2026-02-04 06:57:12.383615
pointers-consulting-001	Pointers Consulting	Pointers Consulting Pty Ltd	\N	\N	sam@pointersconsulting.com.au	+61 426 784 982	\N	Sydney	\N	Sydney	NSW	2000	Australia	\N	enterprise	100	10000	t	\N	/assets/pointers-logo.png	\N	\N	#2D8C3C	#ffffff	#3BA34D	#0f172a	#ffffff	#334155	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
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
-- Data for Name: company_request_statuses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_request_statuses (id, company_id, status_key, display_name, description, color, "position", wip_limit, is_final, is_active, created_at, updated_at) FROM stdin;
1	pointers-consulting-001	pending	Pending	Request received, waiting to be assigned	#F59E0B	1	\N	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
2	pointers-consulting-001	collecting_docs	Collecting Documents	Gathering required documents from client	#8B5CF6	2	\N	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
3	pointers-consulting-001	in_progress	In Progress	Accountant actively working on the request	#3B82F6	3	\N	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
4	pointers-consulting-001	review	Under Review	Senior accountant reviewing the work	#F97316	4	\N	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
5	pointers-consulting-001	awaiting_client	Awaiting Client	Sent to client for approval/signature	#6B7280	5	\N	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
6	pointers-consulting-001	lodgement	Ready for Lodgement	Ready to submit to ATO/authority	#14B8A6	6	\N	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
7	pointers-consulting-001	invoicing	Invoicing	Generating and sending invoice	#EC4899	7	\N	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
8	pointers-consulting-001	completed	Completed	Request successfully completed	#10B981	8	\N	t	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
9	pointers-consulting-001	on_hold	On Hold	Request temporarily paused	#9CA3AF	9	\N	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
10	pointers-consulting-001	cancelled	Cancelled	Request was cancelled	#EF4444	10	\N	t	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
\.


--
-- Data for Name: company_service_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_service_settings (id, company_id, service_id, is_active, custom_name, custom_description, custom_price, cost_percentage, display_order, is_featured, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: company_storage_configs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_storage_configs (id, company_id, provider, is_enabled, sharepoint_site_id, sharepoint_drive_id, sharepoint_root_folder, zoho_client_id, zoho_client_secret, zoho_access_token, zoho_refresh_token, zoho_token_expires_at, zoho_root_folder_id, zoho_org_id, google_client_id, google_client_secret, google_access_token, google_refresh_token, google_token_expires_at, google_root_folder_id, azure_connection_string, azure_container_name, last_sync_at, last_error, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: currencies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.currencies (id, code, name, symbol, is_active, created_at) FROM stdin;
1	AUD	Australian Dollar	$	t	2026-02-04 07:01:46.65691
2	USD	US Dollar	$	t	2026-02-04 07:01:46.65691
3	GBP	British Pound	£	t	2026-02-04 07:01:46.65691
4	EUR	Euro	€	t	2026-02-04 07:01:46.65691
5	AED	UAE Dirham	د.إ	t	2026-02-04 07:01:46.65691
6	SAR	Saudi Riyal	﷼	t	2026-02-04 07:01:46.65691
7	QAR	Qatari Riyal	﷼	t	2026-02-04 07:01:46.65691
8	KWD	Kuwaiti Dinar	د.ك	t	2026-02-04 07:01:46.65691
9	BHD	Bahraini Dinar	.د.ب	t	2026-02-04 07:01:46.65691
10	OMR	Omani Rial	﷼	t	2026-02-04 07:01:46.65691
11	INR	Indian Rupee	₹	t	2026-02-04 07:01:46.65691
12	PKR	Pakistani Rupee	₨	t	2026-02-04 07:01:46.65691
13	NZD	New Zealand Dollar	$	t	2026-02-04 07:01:46.65691
14	CAD	Canadian Dollar	$	t	2026-02-04 07:01:46.65691
15	SGD	Singapore Dollar	$	t	2026-02-04 07:01:46.65691
16	MYR	Malaysian Ringgit	RM	t	2026-02-04 07:01:46.65691
17	ZAR	South African Rand	R	t	2026-02-04 07:01:46.65691
18	CHF	Swiss Franc	CHF	t	2026-02-04 07:01:46.65691
19	JPY	Japanese Yen	¥	t	2026-02-04 07:01:46.65691
20	CNY	Chinese Yuan	¥	t	2026-02-04 07:01:46.65691
21	HKD	Hong Kong Dollar	HK$	t	2026-02-04 07:01:46.65691
\.


--
-- Data for Name: documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.documents (id, original_filename, stored_filename, file_type, file_size, mime_type, storage_path, storage_url, storage_type, blob_name, blob_url, external_item_id, external_web_url, client_folder_name, company_id, uploaded_by_id, service_request_id, document_category, description, is_active, created_at, updated_at) FROM stdin;
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

COPY public.email_templates (id, name, slug, subject, body_html, variables, company_id, service_id, template_type, service_category, is_active, created_at, updated_at) FROM stdin;
1	Welcome Email	welcome	Welcome to {company_name}!	<p>Dear {client_name},</p>\n<p>Welcome to {company_name}! We're excited to have you as our client.</p>\n<p>Your account has been created. Please login at: {portal_link}</p>\n<p>Best regards,<br>{company_name}</p>	["client_name", "client_email", "company_name", "portal_link"]	\N	\N	\N	\N	t	2026-02-04 07:01:46.65691	\N
2	Invoice Email	invoice	Invoice #{invoice_number} from {company_name}	<p>Dear {client_name},</p>\n<p>Please find attached your invoice for {service_name}.</p>\n<p><strong>Invoice Details:</strong><br>\nInvoice Number: {invoice_number}<br>\nAmount Due: {amount}<br>\nDue Date: {due_date}</p>\n<p>Pay online: <a href="{payment_link}">Pay Now</a></p>\n<p>Best regards,<br>{company_name}</p>	["client_name", "service_name", "invoice_number", "amount", "due_date", "payment_link", "company_name"]	\N	\N	\N	\N	t	2026-02-04 07:01:46.65691	\N
3	Payment Reminder	payment_reminder	Payment Reminder - Invoice #{invoice_number}	<p>Dear {client_name},</p>\n<p>This is a friendly reminder that payment for Invoice #{invoice_number} is due.</p>\n<p>Amount Due: {amount}<br>Due Date: {due_date}</p>\n<p><a href="{payment_link}">Pay Now</a></p>\n<p>Best regards,<br>{company_name}</p>	["client_name", "invoice_number", "amount", "due_date", "payment_link", "company_name"]	\N	\N	\N	\N	t	2026-02-04 07:01:46.65691	\N
4	Document Request	document_request	Documents Required for {service_name}	<p>Dear {client_name},</p>\n<p>To proceed with your {service_name}, we require the following documents:</p>\n<p>{document_list}</p>\n<p>Please upload via: <a href="{portal_link}">Upload Documents</a></p>\n<p>Best regards,<br>{accountant_name}<br>{company_name}</p>	["client_name", "service_name", "document_list", "portal_link", "accountant_name", "company_name"]	\N	\N	\N	\N	t	2026-02-04 07:01:46.65691	\N
5	Service Completed	service_completed	Your {service_name} is Complete	<p>Dear {client_name},</p>\n<p>Great news! Your {service_name} has been completed.</p>\n<p>{completion_notes}</p>\n<p>View details: <a href="{portal_link}">View Details</a></p>\n<p>Thank you for choosing {company_name}.</p>\n<p>Best regards,<br>{accountant_name}<br>{company_name}</p>	["client_name", "service_name", "completion_notes", "portal_link", "accountant_name", "company_name"]	\N	\N	\N	\N	t	2026-02-04 07:01:46.65691	\N
6	Query Raised	query_raised	Response Required - {service_name}	<p>Dear {client_name},</p>\n<p>We have a question regarding your {service_name}:</p>\n<p><strong>Query:</strong><br>{query_message}</p>\n<p>Please respond: <a href="{portal_link}">Respond Now</a></p>\n<p>Best regards,<br>{accountant_name}<br>{company_name}</p>	["client_name", "service_name", "query_message", "portal_link", "accountant_name", "company_name"]	\N	\N	\N	\N	t	2026-02-04 07:01:46.65691	\N
7	Password Reset	password_reset	Password Reset Request - {company_name}	<p>Dear {client_name},</p>\n<p>We received a request to reset your password.</p>\n<p>Reset code: <strong>{otp}</strong></p>\n<p>This code expires in 10 minutes.</p>\n<p>If you didn't request this, please ignore this email.</p>\n<p>Best regards,<br>{company_name}</p>	["client_name", "otp", "company_name"]	\N	\N	\N	\N	t	2026-02-04 07:01:46.65691	\N
8	User Invitation	user_invitation	You've Been Invited to {company_name}	<p>Hello {user_name},</p>\n<p>You have been invited to join {company_name}.</p>\n<p><strong>Login Details:</strong><br>\nEmail: {email}<br>\nTemporary Password: {password}</p>\n<p><a href="{login_url}">Login Now</a></p>\n<p>Please change your password after first login.</p>\n<p>Best regards,<br>{company_name}</p>	["user_name", "company_name", "email", "password", "login_url"]	\N	\N	\N	\N	t	2026-02-04 07:01:46.65691	\N
\.


--
-- Data for Name: form_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.form_questions (id, form_id, question_text, question_type, is_required, allow_attachment, options, validation_rules, placeholder, help_text, "order", created_at, section_number, section_title, section_description, is_section_repeatable, section_group, min_section_repeats, max_section_repeats, conditional_on_question_id, conditional_value) FROM stdin;
1	1	What is your Tax File Number (TFN)?	text	t	\N	\N	\N	XXX XXX XXX	\N	0	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
2	1	What is your date of birth?	date	t	\N	\N	\N	\N	\N	1	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
3	1	What is your occupation?	text	t	\N	\N	\N	\N	\N	2	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
4	1	Did you have any income from employment?	radio	t	\N	["Yes", "No"]	\N	\N	\N	3	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
5	1	Upload your PAYG Payment Summary / Income Statement	file	f	\N	\N	\N	\N	You can find this in your myGov account	4	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
6	1	Did you have any bank interest income?	radio	t	\N	["Yes", "No"]	\N	\N	\N	5	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
7	1	Did you have any dividend income?	radio	t	\N	["Yes", "No"]	\N	\N	\N	6	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
8	1	Do you have private health insurance?	radio	t	\N	["Yes", "No"]	\N	\N	\N	7	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
9	1	Upload your Private Health Insurance Statement	file	f	\N	\N	\N	\N	\N	8	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
10	1	What work-related expenses do you want to claim?	multiselect	f	\N	["Work from home expenses", "Vehicle/Travel expenses", "Uniform/Clothing", "Tools and equipment", "Self-education", "Other"]	\N	\N	\N	9	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
11	1	Please provide details of any other deductions	textarea	f	\N	\N	\N	List any additional deductions	\N	10	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
12	2	What is your ABN?	text	t	\N	\N	\N	XX XXX XXX XXX	\N	0	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
13	2	What period is this BAS for?	select	t	\N	["July-September (Q1)", "October-December (Q2)", "January-March (Q3)", "April-June (Q4)", "Monthly"]	\N	\N	\N	1	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
14	2	Are you registered for GST?	radio	t	\N	["Yes", "No"]	\N	\N	\N	2	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
15	2	Total sales/income for the period (including GST)	number	t	\N	\N	\N	0.00	\N	3	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
16	2	Total purchases/expenses for the period (including GST)	number	t	\N	\N	\N	0.00	\N	4	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
17	2	Do you have PAYG withholding obligations?	radio	t	\N	["Yes", "No"]	\N	\N	\N	5	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
18	2	Total wages paid for the period	number	f	\N	\N	\N	0.00	\N	6	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
19	2	Total PAYG withheld from wages	number	f	\N	\N	\N	0.00	\N	7	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
20	2	Upload your sales report/invoices	file	f	\N	\N	\N	\N	\N	8	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
21	2	Upload your purchase invoices/receipts	file	f	\N	\N	\N	\N	\N	9	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
22	2	Any additional notes or information	textarea	f	\N	\N	\N	\N	\N	10	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
23	3	Property address	textarea	t	\N	\N	\N	Full address of the rental property	\N	0	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
24	3	When did you purchase this property?	date	t	\N	\N	\N	\N	\N	1	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
25	3	What was the purchase price?	number	t	\N	\N	\N	0.00	\N	2	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
26	3	How many weeks was the property rented this year?	number	t	\N	\N	\N	52	\N	3	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
27	3	Total rental income received	number	t	\N	\N	\N	0.00	\N	4	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
28	3	Is the property managed by an agent?	radio	t	\N	["Yes - Full management", "Yes - Letting only", "No - Self managed"]	\N	\N	\N	5	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
29	3	Property management fees paid	number	f	\N	\N	\N	0.00	\N	6	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
30	3	Council rates paid	number	f	\N	\N	\N	0.00	\N	7	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
31	3	Water rates paid	number	f	\N	\N	\N	0.00	\N	8	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
32	3	Insurance premium paid	number	f	\N	\N	\N	0.00	\N	9	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
33	3	Interest on loan paid	number	f	\N	\N	\N	0.00	\N	10	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
34	3	Repairs and maintenance costs	number	f	\N	\N	\N	0.00	\N	11	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
35	3	Upload rental income statement from agent	file	f	\N	\N	\N	\N	\N	12	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
36	3	Upload depreciation schedule (if available)	file	f	\N	\N	\N	\N	\N	13	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
37	3	Any capital improvements made this year?	textarea	f	\N	\N	\N	\N	List any renovations or improvements with costs	14	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
38	4	Proposed fund name	text	t	\N	\N	\N	e.g., Smith Family Superannuation Fund	\N	0	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
39	4	Trustee structure	radio	t	\N	["Individual trustees", "Corporate trustee"]	\N	\N	Corporate trustee recommended for better asset protection	1	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
40	4	Number of members	select	t	\N	["1", "2", "3", "4"]	\N	\N	\N	2	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
41	4	Member 1 - Full name	text	t	\N	\N	\N	\N	\N	3	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
42	4	Member 1 - Date of birth	date	t	\N	\N	\N	\N	\N	4	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
43	4	Member 1 - TFN	text	t	\N	\N	\N	\N	\N	5	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
44	4	Member 1 - Current super fund name	text	f	\N	\N	\N	\N	Fund you are rolling over from	6	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
45	4	Member 1 - Approximate rollover amount	number	f	\N	\N	\N	0.00	\N	7	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
46	4	Member 2 - Full name (if applicable)	text	f	\N	\N	\N	\N	\N	8	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
47	4	Member 2 - Date of birth	date	f	\N	\N	\N	\N	\N	9	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
48	4	Member 2 - TFN	text	f	\N	\N	\N	\N	\N	10	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
49	4	Investment strategy preferences	multiselect	t	\N	["Australian shares", "International shares", "Property", "Cash/Term deposits", "Bonds", "Cryptocurrency"]	\N	\N	\N	11	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
50	4	Do you plan to borrow to invest (LRBA)?	radio	t	\N	["Yes", "No", "Not sure"]	\N	\N	\N	12	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
51	4	Upload ID documents for all members	file	t	\N	\N	\N	\N	Passport or Drivers License	13	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
52	4	Any specific questions or requirements?	textarea	f	\N	\N	\N	\N	\N	14	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
53	5	Proposed company name (Option 1)	text	t	\N	\N	\N	\N	Must end with Pty Ltd	0	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
54	5	Proposed company name (Option 2)	text	f	\N	\N	\N	\N	Backup name in case first choice is taken	1	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
55	5	Company type	radio	t	\N	["Proprietary Limited (Pty Ltd)", "Public Company (Ltd)"]	\N	\N	\N	2	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
56	5	Principal business activity	text	t	\N	\N	\N	e.g., IT Consulting, Construction, Retail	\N	3	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
57	5	Registered office address	textarea	t	\N	\N	\N	\N	Must be a physical address in Australia	4	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
58	5	Principal place of business	textarea	t	\N	\N	\N	\N	\N	5	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
59	5	Number of directors	select	t	\N	["1", "2", "3", "4", "5+"]	\N	\N	\N	6	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
60	5	Director 1 - Full name	text	t	\N	\N	\N	\N	\N	7	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
61	5	Director 1 - Date of birth	date	t	\N	\N	\N	\N	\N	8	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
62	5	Director 1 - Residential address	textarea	t	\N	\N	\N	\N	\N	9	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
63	5	Director 1 - Place of birth (City, Country)	text	t	\N	\N	\N	\N	\N	10	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
64	5	Director 2 - Full name (if applicable)	text	f	\N	\N	\N	\N	\N	11	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
65	5	Number of shares to be issued	number	t	\N	\N	\N	100	\N	12	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
66	5	Share price	number	t	\N	\N	\N	1.00	\N	13	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
67	5	Shareholder 1 - Name	text	t	\N	\N	\N	\N	\N	14	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
68	5	Shareholder 1 - Number of shares	number	t	\N	\N	\N	\N	\N	15	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
69	5	Do you need GST registration?	radio	t	\N	["Yes", "No", "Not sure"]	\N	\N	\N	16	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
70	5	Do you need to register as an employer?	radio	t	\N	["Yes", "No", "Not sure"]	\N	\N	\N	17	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
71	5	Upload ID for all directors	file	t	\N	\N	\N	\N	\N	18	2026-02-04 07:01:46.65691	\N	\N	\N	\N	\N	\N	\N	\N	\N
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
1	Individual Tax Return Information	Please provide the following information for your tax return	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
2	BAS Information Form	Provide your business activity details for the period	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
3	Rental Property Information	Details about your investment property for tax purposes	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
4	SMSF Setup Application	Information required to establish your Self-Managed Super Fund	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
5	Company Registration Form	Information required to register your new company	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
6	Company Incorporation Form	Complete this form to register your new company with ASIC	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
7	SMSF Setup Form	Complete this form to establish your Self-Managed Super Fund	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
8	SMSF Annual Compliance Questionnaire	Annual compliance questionnaire for Self-Managed Super Fund clients	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
9	Company Annual Compliance Questionnaire	Annual compliance questionnaire for company clients	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
11	SMSF Annual Audit Form	Complete this form and upload all required documents for your SMSF Annual Audit	service	t	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N	t	\N	published
\.


--
-- Data for Name: impersonation_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.impersonation_sessions (id, admin_id, impersonated_user_id, started_at, ended_at, reason, ip_address, user_agent, action_count) FROM stdin;
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
\.


--
-- Data for Name: otps; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.otps (id, user_id, code, purpose, expires_at, is_used, created_at) FROM stdin;
1	bff5b70e-a917-4a73-8e3c-a9114122d9d3	823575	password_reset	2026-02-06 01:19:29.80884	f	2026-02-06 01:09:29.81701
\.


--
-- Data for Name: queries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.queries (id, service_request_id, sender_id, message, attachment_url, is_internal, created_at) FROM stdin;
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
1	super_admin	Full system access	{"all": true}	2026-02-04 07:01:46.65691
2	admin	Administrative access	{"manage_users": true, "manage_requests": true, "view_reports": true, "manage_invoices": true}	2026-02-04 07:01:46.65691
3	senior_accountant	Senior accountant with admin privileges	{"manage_users": true, "manage_requests": true, "view_reports": true, "manage_team": true}	2026-02-04 07:01:46.65691
4	accountant	Accountant access	{"manage_assigned_requests": true, "add_notes": true}	2026-02-04 07:01:46.65691
5	external_accountant	External accountant access	{"manage_assigned_requests": true, "add_notes": true, "external": true}	2026-02-04 07:01:46.65691
6	user	Client user access	{"view_own_requests": true, "create_requests": true}	2026-02-04 07:01:46.65691
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

COPY public.service_requests (id, user_id, service_id, assigned_accountant_id, client_entity_id, request_number, description, status, current_step_id, internal_notes, invoice_raised, invoice_paid, invoice_amount, payment_link, xero_reference_job_id, internal_reference, deadline_date, priority, actual_cost, cost_notes, labor_hours, labor_rate, created_at, updated_at, completed_at) FROM stdin;
\.


--
-- Data for Name: service_workflows; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_workflows (id, company_id, name, description, is_default, is_active, created_at, updated_at, created_by_id) FROM stdin;
default-workflow	\N	Default Workflow	Standard service request workflow	t	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N
workflow-tax-agent	\N	Tax Agent Workflow	Standard workflow for tax returns and tax-related services	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N
workflow-bas-agent	\N	BAS Agent Workflow	Workflow for BAS lodgements, GST, and payroll services	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N
workflow-auditor	\N	SMSF Auditor Workflow	Workflow for SMSF audits and compliance reviews	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N
workflow-bookkeeper	\N	Bookkeeping Workflow	Workflow for bookkeeping, payroll, and reconciliation services	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N
workflow-financial-planner	\N	Financial Planning Workflow	Workflow for financial planning, advice, and strategy services	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N
workflow-mortgage-broker	\N	Mortgage Broker Workflow	Workflow for loan applications and finance services	f	t	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691	\N
\.


--
-- Data for Name: services; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.services (id, name, description, category, base_price, is_active, is_default, form_id, workflow_id, cost_percentage, cost_category, is_recurring, renewal_period_months, renewal_reminder_days, renewal_due_month, renewal_due_day, created_at, updated_at) FROM stdin;
1	Individual Tax Return	Annual individual tax return preparation and lodgement with ATO	tax_agent	350.00	t	t	\N	workflow-tax-agent	\N	\N	t	12	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
2	Business Activity Statement (BAS)	Quarterly or monthly BAS preparation and lodgement	bas_agent	300.00	t	t	\N	workflow-bas-agent	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
3	Investment Rental Property	Tax return schedule for rental property income and deductions	tax_agent	200.00	t	t	\N	workflow-tax-agent	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
4	Company Tax Return	Annual company tax return preparation	tax_agent	800.00	t	t	\N	workflow-tax-agent	\N	\N	t	12	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
5	Partnership Tax Return	Tax return preparation for partnerships	tax_agent	600.00	t	t	\N	workflow-tax-agent	\N	\N	t	12	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
6	Trust Tax Return	Tax return preparation for trusts including distribution statements	tax_agent	750.00	t	t	\N	workflow-tax-agent	\N	\N	t	12	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
7	SMSF Tax Return	Annual tax return preparation for Self-Managed Super Fund	tax_agent	500.00	t	t	\N	workflow-tax-agent	\N	\N	t	12	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
8	Business Tax Return - Sole Trader	Tax return preparation for sole traders	tax_agent	350.00	t	t	\N	workflow-tax-agent	\N	\N	t	12	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
10	SMSF Annual Audit	Complete annual audit of Self-Managed Super Fund	auditor	1500.00	t	t	\N	workflow-auditor	\N	\N	t	12	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
11	SMSF Compliance Audit	Compliance-focused audit ensuring SMSF meets all regulatory requirements	auditor	1200.00	t	t	\N	workflow-auditor	\N	\N	t	12	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
12	SMSF Establishment Audit	Initial audit for newly established SMSFs	auditor	800.00	t	t	\N	workflow-auditor	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
13	SMSF Wind-Up Audit	Final audit for SMSFs being wound up	auditor	1000.00	t	t	\N	workflow-auditor	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
20	Comprehensive Financial Plan	Full financial planning including retirement, investment, insurance	financial_planner	3500.00	t	t	\N	workflow-financial-planner	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
21	Retirement Planning	Detailed retirement planning including super strategy	financial_planner	1800.00	t	t	\N	workflow-financial-planner	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
22	Investment Portfolio Review	Review of investment portfolio with recommendations	financial_planner	800.00	t	t	\N	workflow-financial-planner	\N	\N	t	12	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
23	Superannuation Strategy	Strategic advice on super contributions and optimization	financial_planner	1200.00	t	t	\N	workflow-financial-planner	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
24	Insurance Needs Analysis	Comprehensive review of insurance needs	financial_planner	600.00	t	t	\N	workflow-financial-planner	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
30	Home Loan - New Purchase	Full service for home purchase including loan comparison	mortgage_broker	0.00	t	t	\N	workflow-mortgage-broker	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
31	Home Loan Refinance	Refinance existing home loan for better rates	mortgage_broker	0.00	t	t	\N	workflow-mortgage-broker	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
32	Investment Property Loan	Loan arrangement for investment property	mortgage_broker	0.00	t	t	\N	workflow-mortgage-broker	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
33	Construction Loan	Specialized loan for new home construction	mortgage_broker	0.00	t	t	\N	workflow-mortgage-broker	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
34	Commercial Property Loan	Business and commercial property financing	mortgage_broker	0.00	t	t	\N	workflow-mortgage-broker	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
40	Monthly Bookkeeping	Complete monthly bookkeeping including reconciliation	bookkeeper	400.00	t	t	\N	workflow-bookkeeper	\N	\N	t	1	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
41	Quarterly Bookkeeping	Quarterly bookkeeping package for smaller businesses	bookkeeper	350.00	t	t	\N	workflow-bookkeeper	\N	\N	t	3	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
42	Payroll Processing - Monthly	Monthly payroll processing including STP reporting	bookkeeper	180.00	t	t	\N	workflow-bookkeeper	\N	\N	t	1	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
50	BAS Lodgement - Quarterly	Quarterly BAS preparation and lodgement	bas_agent	180.00	t	t	\N	workflow-bas-agent	\N	\N	t	3	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
51	BAS Lodgement - Monthly	Monthly BAS preparation and lodgement	bas_agent	150.00	t	t	\N	workflow-bas-agent	\N	\N	t	1	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
52	GST Registration	GST registration with the ATO	bas_agent	100.00	t	t	\N	workflow-bas-agent	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
53	PAYG Withholding Setup	Setup of PAYG withholding obligations	bas_agent	150.00	t	t	\N	workflow-bas-agent	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
60	Company Incorporation	New company registration with ASIC	tax_agent	800.00	t	t	\N	workflow-tax-agent	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
61	Trust Establishment	Setup of new trust including trust deed	tax_agent	1200.00	t	t	\N	workflow-tax-agent	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
62	SMSF Establishment	Setup of new Self-Managed Super Fund	tax_agent	1500.00	t	t	\N	workflow-tax-agent	\N	\N	f	\N	\N	\N	\N	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
\.


--
-- Data for Name: smsf_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.smsf_questions (id, text, category, type, weight, "order", is_active, created_at, updated_at, options) FROM stdin;
1	Do you understand that only properly licensed professionals can provide personal advice recommending an SMSF, and that you should receive written advice (e.g. SOA) if personal advice is given?	Am I Right for SMSF?	Compliance	0.05	1	t	2026-02-04 07:01:46.65691	2026-02-06 01:26:16.876165	\N
2	Do you understand that SMSF investments must comply with the sole purpose test, arm’s‑length rules and other restrictions (e.g. on in‑house assets and related‑party transactions)?	Am I Right for SMSF?	Compliance	0.05	2	t	2026-02-04 07:01:46.65691	2026-02-06 01:26:51.292361	\N
3	Are you aware the ATO is the regulator and that it takes a strong stance on illegal early access, related‑party dealings and non‑arm’s‑length arrangements?	Am I Right for SMSF?	Compliance	0.05	3	t	2026-02-04 07:01:46.65691	2026-02-06 01:27:10.004105	\N
4	Do any member/s of your proposed SMSF have a history of bankruptcy, serious credit issues or legal disputes that might affect their eligibility or trustee suitability?	Am I Right for SMSF?	Compliance	0.05	4	t	2026-02-04 07:01:46.65691	2026-02-06 01:27:33.730758	\N
5	Do you stay updated on superannuation regulations and compliance requirements for SMSFs?	Am I Right for SMSF?	Compliance	0.03	5	t	2026-02-04 07:01:46.65691	2026-02-06 01:27:55.6918	\N
6	Have you set clear financial goals for your retirement and actively monitor your progress?	Am I Right for SMSF?	Financial	0.03	6	t	2026-02-04 07:01:46.65691	2026-02-06 01:28:21.431636	\N
7	Do you currently have a will, powers of attorney and any binding or non-binding death benefit nominations in place in your existing funds?	Am I Right for SMSF?	Governance	0.05	7	t	2026-02-04 07:01:46.65691	2026-02-06 01:29:06.802487	\N
8	What experience do you (and other proposed trustees) have with investing, tax, trusts, or running a small business or entity in Australia?	Am I Right for SMSF?	Governance	0.04	8	t	2026-02-04 07:01:46.65691	2026-02-06 01:29:26.582607	\N
9	How would you rate your overall understanding of SMSF rules, including the regulatory obligations and ongoing compliance responsibilities involved in running an SMSF?	Am I Right for SMSF?	Governance	0.03	9	t	2026-02-04 07:01:46.65691	2026-02-06 01:29:52.96079	\N
10	Are you able to realistically commit time each month to actively manage an SMSF (including reviewing investments, paperwork, record-keeping and working with advisers)?	Am I Right for SMSF?	Governance	0.02	10	t	2026-02-04 07:01:46.65691	2026-02-06 01:32:38.34044	\N
11	In general, do you tend to seek professional advice before making significant investment decisions?	Am I Right for SMSF?	Risk Appetite	0.05	11	t	2026-02-04 07:01:46.65691	2026-02-06 01:33:19.140594	\N
12	Are you comfortable with the idea of taking risk to achieve better returns for your retirement by investing your Super money?	Am I Right for SMSF?	Risk Appetite	0.05	12	t	2026-02-04 07:01:46.65691	2026-02-06 01:33:34.619467	\N
13	How important do you think it is for an SMSF to hold a diversified mix of assets (rather than just one or two major investments such as a single property)	Am I Right for SMSF?	Risk Appetite	0.05	13	t	2026-02-04 07:01:46.65691	2026-02-06 01:33:56.465486	\N
14	If you are well guided on SMSF setup and its ongoing compliance by a subject matter expert (like an SMSF Accountant or a SMSF Specialist, how comfortable will you be to move ahead forming your own SMSF​?	Am I Right for SMSF?	Risk Appetite	0.02	14	t	2026-02-04 07:01:46.65691	2026-02-06 01:34:16.80203	\N
15	Have you considered whether to use individual trustees or a corporate trustee, and do you understand some of the pros and cons of each?	Is SMSF Right for me?	Compliance	0.04	15	t	2026-02-04 07:01:46.65691	2026-02-06 01:35:06.147319	\N
24	How many members will be there in your SMSF, presuming you have decided to go ahead with the idea of setting up an SMSF?	Is SMSF Right for me?	Governance	0	24	t	2026-02-04 07:01:46.65691	2026-02-06 01:45:29.487718	\N
25	How did you hear or come to know about SMSF?	Is SMSF Right for me?	Governance	0.03	25	t	2026-02-04 07:01:46.65691	2026-02-06 01:46:03.131618	\N
16	Are there any specific assets you want the SMSF to hold or invest in?	Is SMSF Right for me?	Financial	0	16	t	2026-02-04 07:01:46.65691	2026-02-06 01:39:36.64831	\N
17	Do all potential members of your SMSF (including you) have basic insurances (like life, TPD, income protection insurance) in place?	Is SMSF Right for me?	Financial	0.07	17	t	2026-02-04 07:01:46.65691	2026-02-06 01:41:12.690188	\N
18	What is the combined super balance (in AUD$) of all potential SMSF members if your SMSF was to be established today?	Is SMSF Right for me?	Financial	0.07	18	t	2026-02-04 07:01:46.65691	2026-02-06 01:41:41.92925	\N
19	What is the approximate annual super contributions (in AUD $) of all potential SMSF members combined to come into your SMSF?	Is SMSF Right for me?	Financial	0.07	19	t	2026-02-04 07:01:46.65691	2026-02-06 01:42:26.485886	\N
20	What is the gross annual taxable income of your household combined? (Note: You can check your last tax return filed to provide a specific number in AUD $)	Is SMSF Right for me?	Financial	0.07	20	t	2026-02-04 07:01:46.65691	2026-02-06 01:42:46.385655	\N
21	What is the average age (in years) for each individual planning to be an SMSF member as of 30th June of previous year?	Is SMSF Right for me?	Financial	0.07	21	t	2026-02-04 07:01:46.65691	2026-02-06 01:43:01.089762	\N
22	Have you sought a written professional financial advice (SOA) for forming an SMSF in last 6 months from today?	Is SMSF Right for me?	Financial	0.03	22	t	2026-02-04 07:01:46.65691	2026-02-06 01:43:19.705309	\N
23	What type of support relationship are you looking for with Pointers Consulting in relation to your SMSF plan?	Is SMSF Right for me?	Governance	0	23	t	2026-02-04 07:01:46.65691	2026-02-06 01:43:32.018972	\N
\.


--
-- Data for Name: smsf_submissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.smsf_submissions (id, name, email, phone, answers, scores, overall_score, ip_address, user_agent, submitted_at, client_entity_id) FROM stdin;
1	SS TEST	reachsharat11@gmail.com	+61426784982	{"0": 3, "1": 2, "2": 2, "3": 2, "4": 2, "5": 2, "6": 2, "7": 2, "8": 2, "9": 2, "10": 2, "11": 2, "12": 2, "13": 2, "14": 2, "15": 2, "16": 2, "17": 2, "18": 2, "19": 2, "20": 2, "21": 2, "22": 2, "23": 2, "24": 2}	{"typePercentages": {"Compliance": 73, "Financial": 67, "Governance": 67, "Risk Appetite": 67}, "categoryPercentages": {"Am I Right for SMSF?": 70, "Is SMSF Right for me?": 67}, "overall": 68}	68	58.179.159.64	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36	2026-02-04 07:33:27.923241	\N
2	adarsh	aggarwal.adarsh@gmail.com	+61415969411	{"0": 1, "1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "6": 1, "7": 1, "8": 1, "9": 1, "10": 1, "11": 1, "12": 1, "13": 1, "14": 1, "15": 1, "16": 1, "17": 1, "18": 1, "19": 1, "20": 1, "21": 1, "22": 1, "23": 1, "24": 1}	{"typePercentages": {"Compliance": 33, "Financial": 33, "Governance": 33, "Risk Appetite": 33}, "categoryPercentages": {"Am I Right for SMSF?": 33, "Is SMSF Right for me?": 33}, "overall": 33}	33	60.242.61.202	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36	2026-02-04 08:05:35.156478	\N
3	ss test	reachsharat11@gmail.com	+61426784982	{"0": 2, "1": 2, "2": 2, "3": 2, "4": 2, "5": 2, "6": 2, "7": 2, "8": 2, "9": 2, "10": 2, "11": 2, "12": 2, "13": 2, "14": 2, "15": 2, "16": 2, "17": 2, "18": 2, "19": 2, "20": 2, "21": 2, "22": 2, "23": 2, "24": 2}	{"typePercentages": {"Compliance": 67, "Financial": 67, "Governance": 67, "Risk Appetite": 67}, "categoryPercentages": {"Am I Right for SMSF?": 67, "Is SMSF Right for me?": 67}, "overall": 67}	67	58.179.159.64	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36	2026-02-04 08:07:57.832294	\N
4	TT Test	reachsharat11@gmail.com	+61426784982	{"0": 3, "1": 2, "2": 2, "3": 3, "4": 2, "5": 3, "6": 2, "7": 3, "8": 2, "9": 3, "10": 2, "11": 3, "12": 2, "13": 3, "14": 2, "15": 3, "16": 2, "17": 3, "18": 2, "19": 3, "20": 2, "21": 3, "22": 2, "23": 3, "24": 2}	{"typePercentages": {"Compliance": 79, "Financial": 83, "Governance": 78, "Risk Appetite": 80}, "categoryPercentages": {"Am I Right for SMSF?": 82, "Is SMSF Right for me?": 79}, "overall": 81}	81	58.179.159.64	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36	2026-02-04 10:32:52.139079	\N
\.


--
-- Data for Name: system_email_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_email_config (id, provider, is_enabled, smtp_host, smtp_port, smtp_username, smtp_password, smtp_use_tls, smtp_use_ssl, sender_email, sender_name, use_as_fallback, last_test_at, last_test_success, last_error, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: system_request_statuses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_request_statuses (id, status_key, display_name, description, color, "position", is_final, is_active, created_at) FROM stdin;
1	pending	Pending	Request is waiting to be assigned	#f59e0b	1	f	t	2026-02-04 07:01:46.65691
2	assigned	Assigned	Request has been assigned to an accountant	#3b82f6	2	f	t	2026-02-04 07:01:46.65691
3	in_progress	In Progress	Work is in progress	#8b5cf6	3	f	t	2026-02-04 07:01:46.65691
4	query_raised	Query Raised	Waiting for client response	#ef4444	4	f	t	2026-02-04 07:01:46.65691
5	review	Under Review	Work is being reviewed	#06b6d4	5	f	t	2026-02-04 07:01:46.65691
6	completed	Completed	Request has been completed	#10b981	6	t	t	2026-02-04 07:01:46.65691
7	cancelled	Cancelled	Request has been cancelled	#6b7280	7	t	t	2026-02-04 07:01:46.65691
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, company_id, title, description, created_by_id, assigned_to_id, service_request_id, status, priority, due_date, completed_at, estimated_minutes, actual_minutes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: tax_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tax_types (id, code, name, default_rate, is_active, created_at) FROM stdin;
1	GST	Goods and Services Tax	10.00	t	2026-02-04 07:01:46.65691
2	VAT	Value Added Tax	20.00	t	2026-02-04 07:01:46.65691
3	SALES_TAX	Sales Tax	8.00	t	2026-02-04 07:01:46.65691
4	NONE	No Tax	0.00	t	2026-02-04 07:01:46.65691
\.


--
-- Data for Name: user_tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_tags (user_id, tag_id, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, password_hash, role_id, first_name, last_name, phone, personal_email, address, company_name, visa_status, tfn, date_of_birth, occupation, bsb, bank_account_number, bank_account_holder_name, id_document_url, passport_url, bank_statement_url, driving_licence_url, terms_accepted, terms_accepted_at, is_active, is_verified, is_first_login, two_fa_enabled, is_external_accountant, created_at, updated_at, last_login, company_id, invited_by_id, supervisor_id) FROM stdin;
bff5b70e-a917-4a73-8e3c-a9114122d9d3	sam@pointersconsulting.com.au	$2b$12$SVem.qnw5eqwHd70ry6UKuu2THSd9dAc83TBKtgO8XwnP0JhK7yga	2	sam	sharma	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	t	f	t	t	f	2026-02-04 07:23:07.305684	2026-02-04 07:23:07.305686	\N	0950fc1f-cddf-4fb3-b926-54a573059dc8	admin-user-001	\N
admin-user-001	aggarwal.adarsh98@gmail.com	$2b$12$TpB5nMKoAxJmpMkfPcSAmOz472rc88G.DHmvDc2pffPkl4nIqrS9u	1	Adarsh	Aggarwal	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	t	f	f	\N	2026-02-04 07:01:46.65691	2026-02-06 01:17:44.862494	2026-02-06 01:17:44.850968	pointers-consulting-001	\N	\N
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
step-pending	default-workflow	pending	Pending	\N	gray	\N	START	1	\N	\N	\N	\N	\N	100	100	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
step-invoice-raised	default-workflow	invoice_raised	Invoice Raised	\N	blue	\N	NORMAL	2	\N	\N	\N	\N	\N	300	100	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
step-assigned	default-workflow	assigned	Assigned	\N	indigo	\N	NORMAL	3	\N	\N	\N	\N	\N	500	100	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
step-processing	default-workflow	processing	Processing	\N	yellow	\N	NORMAL	4	\N	\N	\N	\N	\N	700	100	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
step-query-raised	default-workflow	query_raised	Query Raised	\N	orange	\N	QUERY	5	\N	\N	\N	\N	\N	700	250	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
step-review	default-workflow	accountant_review_pending	Under Review	\N	purple	\N	NORMAL	6	\N	\N	\N	\N	\N	500	250	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
step-completed	default-workflow	completed	Completed	\N	green	\N	END	8	\N	\N	\N	\N	\N	900	100	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-pending	workflow-tax-agent	pending	Pending Review	\N	gray	\N	START	1	["admin", "super_admin"]	\N	\N	\N	\N	50	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-docs-requested	workflow-tax-agent	documents_requested	Documents Requested	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-docs-received	workflow-tax-agent	documents_received	Documents Received	\N	indigo	\N	NORMAL	3	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-invoice-raised	workflow-tax-agent	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	4	["admin", "super_admin"]	\N	\N	\N	\N	650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-assigned	workflow-tax-agent	assigned	Assigned to Accountant	\N	blue	\N	NORMAL	5	["admin", "super_admin"]	\N	\N	\N	\N	850	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-preparation	workflow-tax-agent	in_preparation	Return Preparation	\N	yellow	\N	NORMAL	6	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1050	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-query	workflow-tax-agent	query_raised	Query Raised	\N	orange	\N	QUERY	7	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1050	300	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-review	workflow-tax-agent	client_review	Client Review	\N	purple	\N	NORMAL	8	["user"]	\N	\N	\N	\N	850	300	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-lodgement	workflow-tax-agent	ready_for_lodgement	Ready for Lodgement	\N	indigo	\N	NORMAL	9	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-lodged	workflow-tax-agent	lodged	Lodged with ATO	\N	blue	\N	NORMAL	10	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-admin-review	workflow-tax-agent	admin_review	Admin Review	\N	purple	\N	NORMAL	11	["admin", "super_admin"]	\N	\N	\N	\N	1550	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
tax-step-completed	workflow-tax-agent	completed	Completed	\N	green	\N	END	12	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-pending	workflow-bas-agent	pending	Pending	\N	gray	\N	START	1	["admin", "super_admin"]	\N	\N	\N	\N	50	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-data-collection	workflow-bas-agent	data_collection	Data Collection	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-invoice-raised	workflow-bas-agent	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	3	["admin", "super_admin"]	\N	\N	\N	\N	450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-assigned	workflow-bas-agent	assigned	Assigned	\N	blue	\N	NORMAL	4	["admin", "super_admin"]	\N	\N	\N	\N	650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-reconciliation	workflow-bas-agent	reconciliation	Bank Reconciliation	\N	yellow	\N	NORMAL	5	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	850	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-preparation	workflow-bas-agent	bas_preparation	BAS Preparation	\N	yellow	\N	NORMAL	6	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1050	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-query	workflow-bas-agent	query_raised	Query Raised	\N	orange	\N	QUERY	7	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1050	300	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-review	workflow-bas-agent	review	Review & Approval	\N	purple	\N	NORMAL	8	["admin", "super_admin"]	\N	\N	\N	\N	1250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-lodged	workflow-bas-agent	lodged	Lodged with ATO	\N	blue	\N	NORMAL	9	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-admin-review	workflow-bas-agent	admin_review	Admin Final Review	\N	purple	\N	NORMAL	10	["admin", "super_admin"]	\N	\N	\N	\N	1550	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
bas-step-completed	workflow-bas-agent	completed	Completed	\N	green	\N	END	11	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-pending	workflow-auditor	pending	Audit Requested	\N	gray	\N	START	1	["admin", "super_admin"]	\N	\N	\N	\N	50	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-engagement	workflow-auditor	engagement_letter	Engagement Letter	\N	blue	\N	NORMAL	2	["admin", "super_admin"]	\N	\N	\N	\N	250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-docs-requested	workflow-auditor	documents_requested	Documents Requested	\N	blue	\N	NORMAL	3	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-docs-received	workflow-auditor	documents_received	Documents Received	\N	indigo	\N	NORMAL	4	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-invoice-raised	workflow-auditor	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	5	["admin", "super_admin"]	\N	\N	\N	\N	850	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-assigned	workflow-auditor	assigned	Assigned to Auditor	\N	blue	\N	NORMAL	6	["admin", "super_admin"]	\N	\N	\N	\N	1050	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-fieldwork	workflow-auditor	fieldwork	Audit Fieldwork	\N	yellow	\N	NORMAL	7	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-query	workflow-auditor	query_raised	Query Raised	\N	orange	\N	QUERY	8	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1250	300	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-draft-report	workflow-auditor	draft_report	Draft Report	\N	purple	\N	NORMAL	9	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-management-review	workflow-auditor	management_review	Management Review	\N	indigo	\N	NORMAL	10	["admin", "super_admin"]	\N	\N	\N	\N	1650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-final-report	workflow-auditor	final_report	Final Report Issued	\N	blue	\N	NORMAL	11	["admin", "super_admin"]	\N	\N	\N	\N	1850	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
aud-step-completed	workflow-auditor	completed	Completed	\N	green	\N	END	12	["admin", "super_admin"]	\N	\N	\N	\N	2050	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-pending	workflow-bookkeeper	pending	Pending	\N	gray	\N	START	1	["admin", "super_admin"]	\N	\N	\N	\N	50	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-access-setup	workflow-bookkeeper	access_setup	Access Setup	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-invoice-raised	workflow-bookkeeper	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	3	["admin", "super_admin"]	\N	\N	\N	\N	450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-assigned	workflow-bookkeeper	assigned	Assigned	\N	blue	\N	NORMAL	4	["admin", "super_admin"]	\N	\N	\N	\N	650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-processing	workflow-bookkeeper	processing	Processing	\N	yellow	\N	NORMAL	5	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	850	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-query	workflow-bookkeeper	query_raised	Query Raised	\N	orange	\N	QUERY	6	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	850	300	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-review	workflow-bookkeeper	review	Review	\N	purple	\N	NORMAL	7	["admin", "super_admin"]	\N	\N	\N	\N	1050	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-client-approval	workflow-bookkeeper	client_approval	Client Approval	\N	indigo	\N	NORMAL	8	["user"]	\N	\N	\N	\N	1250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-admin-review	workflow-bookkeeper	admin_review	Admin Final Review	\N	purple	\N	NORMAL	9	["admin", "super_admin"]	\N	\N	\N	\N	1350	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
book-step-completed	workflow-bookkeeper	completed	Completed	\N	green	\N	END	10	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-pending	workflow-financial-planner	pending	Enquiry Received	\N	gray	\N	START	1	["admin", "super_admin"]	\N	\N	\N	\N	50	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-discovery	workflow-financial-planner	discovery	Discovery Meeting	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-fact-find	workflow-financial-planner	fact_find	Fact Find	\N	indigo	\N	NORMAL	3	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-invoice-raised	workflow-financial-planner	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	4	["admin", "super_admin"]	\N	\N	\N	\N	650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-assigned	workflow-financial-planner	assigned	Assigned to Planner	\N	blue	\N	NORMAL	5	["admin", "super_admin"]	\N	\N	\N	\N	850	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-analysis	workflow-financial-planner	analysis	Analysis & Research	\N	yellow	\N	NORMAL	6	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1050	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-soa-prep	workflow-financial-planner	soa_preparation	SOA Preparation	\N	yellow	\N	NORMAL	7	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-compliance-review	workflow-financial-planner	compliance_review	Compliance Review	\N	purple	\N	NORMAL	8	["admin", "super_admin"]	\N	\N	\N	\N	1450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-presentation	workflow-financial-planner	presentation	Advice Presentation	\N	indigo	\N	NORMAL	9	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	1650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-query	workflow-financial-planner	query_raised	Query Raised	\N	orange	\N	QUERY	10	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1650	300	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-implementation	workflow-financial-planner	implementation	Implementation	\N	blue	\N	NORMAL	11	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1850	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-admin-review	workflow-financial-planner	admin_review	Admin Final Review	\N	purple	\N	NORMAL	12	["admin", "super_admin"]	\N	\N	\N	\N	1950	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
fp-step-completed	workflow-financial-planner	completed	Completed	\N	green	\N	END	13	["admin", "super_admin"]	\N	\N	\N	\N	2050	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-pending	workflow-mortgage-broker	pending	Enquiry Received	\N	gray	\N	START	1	["admin", "super_admin"]	\N	\N	\N	\N	50	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-consultation	workflow-mortgage-broker	consultation	Initial Consultation	\N	blue	\N	NORMAL	2	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-docs-collection	workflow-mortgage-broker	documents_collection	Document Collection	\N	indigo	\N	NORMAL	3	["admin", "accountant", "super_admin"]	\N	\N	\N	\N	450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-serviceability	workflow-mortgage-broker	serviceability	Serviceability Assessment	\N	yellow	\N	NORMAL	4	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-product-selection	workflow-mortgage-broker	product_selection	Product Selection	\N	purple	\N	NORMAL	5	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	850	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-invoice-raised	workflow-mortgage-broker	invoice_raised	Invoice Raised	\N	purple	\N	NORMAL	6	["admin", "super_admin"]	\N	\N	\N	\N	1050	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-application	workflow-mortgage-broker	application_submitted	Application Submitted	\N	blue	\N	NORMAL	7	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-assessment	workflow-mortgage-broker	lender_assessment	Lender Assessment	\N	yellow	\N	NORMAL	8	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1450	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-query	workflow-mortgage-broker	query_raised	Additional Info Required	\N	orange	\N	QUERY	9	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1450	300	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-conditional	workflow-mortgage-broker	conditional_approval	Conditional Approval	\N	indigo	\N	NORMAL	10	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1650	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-unconditional	workflow-mortgage-broker	unconditional_approval	Unconditional Approval	\N	blue	\N	NORMAL	11	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1850	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-settlement	workflow-mortgage-broker	settlement	Settlement	\N	green	\N	NORMAL	12	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	2050	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-declined	workflow-mortgage-broker	declined	Declined	\N	red	\N	END	13	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	1650	300	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-admin-review	workflow-mortgage-broker	admin_review	Admin Review	\N	purple	\N	NORMAL	14	["admin", "super_admin"]	\N	\N	\N	\N	2150	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
mb-step-completed	workflow-mortgage-broker	completed	Completed	\N	green	\N	END	15	["accountant", "admin", "super_admin"]	\N	\N	\N	\N	2250	150	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
step-admin-review	default-workflow	admin_review	Admin Review	\N	purple	\N	NORMAL	7	["admin", "super_admin"]	\N	\N	\N	\N	800	250	2026-02-04 07:01:46.65691	2026-02-04 07:01:46.65691
\.


--
-- Data for Name: workflow_transitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, description, requires_invoice_raised, requires_invoice_paid, requires_assignment, allowed_roles, send_notification, notification_template, created_at) FROM stdin;
trans-1	default-workflow	step-pending	step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
trans-2	default-workflow	step-invoice-raised	step-assigned	Assign	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
trans-3	default-workflow	step-assigned	step-processing	Start Processing	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
trans-4	default-workflow	step-processing	step-query-raised	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
trans-5	default-workflow	step-query-raised	step-review	Client Responded	\N	f	f	f	["user"]	t	\N	2026-02-04 07:01:46.65691
trans-6	default-workflow	step-review	step-processing	Resume Work	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
trans-7	default-workflow	step-processing	step-completed	Complete	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
trans-8	default-workflow	step-processing	step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
trans-9	default-workflow	step-admin-review	step-processing	Request Changes	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
trans-10	default-workflow	step-admin-review	step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t1	workflow-tax-agent	tax-step-pending	tax-step-docs-requested	Request Documents	\N	f	f	f	["admin", "accountant", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t2	workflow-tax-agent	tax-step-docs-requested	tax-step-docs-received	Documents Received	\N	f	f	f	["admin", "accountant", "super_admin", "user", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t3	workflow-tax-agent	tax-step-docs-received	tax-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t4	workflow-tax-agent	tax-step-invoice-raised	tax-step-assigned	Assign Accountant	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t5	workflow-tax-agent	tax-step-assigned	tax-step-preparation	Start Preparation	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t6	workflow-tax-agent	tax-step-preparation	tax-step-query	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t7	workflow-tax-agent	tax-step-query	tax-step-review	Client Responded	\N	f	f	f	["user"]	t	\N	2026-02-04 07:01:46.65691
tax-t8	workflow-tax-agent	tax-step-review	tax-step-preparation	Resume Preparation	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t9	workflow-tax-agent	tax-step-preparation	tax-step-lodgement	Ready for Lodgement	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t10	workflow-tax-agent	tax-step-lodgement	tax-step-lodged	Lodge with ATO	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t11	workflow-tax-agent	tax-step-lodged	tax-step-completed	Complete	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t12	workflow-tax-agent	tax-step-review	tax-step-lodgement	Client Approved	\N	f	f	f	["user"]	t	\N	2026-02-04 07:01:46.65691
tax-t13	workflow-tax-agent	tax-step-lodged	tax-step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
tax-t16	workflow-tax-agent	tax-step-preparation	tax-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t1	workflow-bas-agent	bas-step-pending	bas-step-data-collection	Request Data	\N	f	f	f	["admin", "accountant", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t2	workflow-bas-agent	bas-step-data-collection	bas-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t3	workflow-bas-agent	bas-step-invoice-raised	bas-step-assigned	Assign	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t4	workflow-bas-agent	bas-step-assigned	bas-step-reconciliation	Start Reconciliation	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t5	workflow-bas-agent	bas-step-reconciliation	bas-step-preparation	Prepare BAS	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t6	workflow-bas-agent	bas-step-preparation	bas-step-query	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t7	workflow-bas-agent	bas-step-query	bas-step-preparation	Query Resolved	\N	f	f	f	["accountant", "admin", "super_admin", "user", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t8	workflow-bas-agent	bas-step-preparation	bas-step-review	Submit for Review	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t9	workflow-bas-agent	bas-step-review	bas-step-lodged	Lodge BAS	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t10	workflow-bas-agent	bas-step-lodged	bas-step-completed	Complete	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
bas-t14	workflow-bas-agent	bas-step-preparation	bas-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t1	workflow-auditor	aud-step-pending	aud-step-engagement	Send Engagement Letter	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t2	workflow-auditor	aud-step-engagement	aud-step-docs-requested	Request Documents	\N	f	f	f	["admin", "accountant", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t3	workflow-auditor	aud-step-docs-requested	aud-step-docs-received	Documents Received	\N	f	f	f	["admin", "accountant", "super_admin", "user", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t4	workflow-auditor	aud-step-docs-received	aud-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t5	workflow-auditor	aud-step-invoice-raised	aud-step-assigned	Assign Auditor	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t6	workflow-auditor	aud-step-assigned	aud-step-fieldwork	Start Fieldwork	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t7	workflow-auditor	aud-step-fieldwork	aud-step-query	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t8	workflow-auditor	aud-step-query	aud-step-fieldwork	Query Resolved	\N	f	f	f	["accountant", "admin", "super_admin", "user", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t9	workflow-auditor	aud-step-fieldwork	aud-step-draft-report	Prepare Draft Report	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t10	workflow-auditor	aud-step-draft-report	aud-step-management-review	Submit for Review	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t11	workflow-auditor	aud-step-management-review	aud-step-draft-report	Request Changes	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t12	workflow-auditor	aud-step-management-review	aud-step-final-report	Approve & Issue	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
aud-t13	workflow-auditor	aud-step-final-report	aud-step-completed	Complete	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t1	workflow-bookkeeper	book-step-pending	book-step-access-setup	Setup Access	\N	f	f	f	["admin", "accountant", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t2	workflow-bookkeeper	book-step-access-setup	book-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t3	workflow-bookkeeper	book-step-invoice-raised	book-step-assigned	Assign	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t4	workflow-bookkeeper	book-step-assigned	book-step-processing	Start Processing	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t5	workflow-bookkeeper	book-step-processing	book-step-query	Raise Query	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t6	workflow-bookkeeper	book-step-query	book-step-processing	Query Resolved	\N	f	f	f	["accountant", "admin", "super_admin", "user", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t7	workflow-bookkeeper	book-step-processing	book-step-review	Submit for Review	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t8	workflow-bookkeeper	book-step-review	book-step-processing	Request Changes	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t9	workflow-bookkeeper	book-step-review	book-step-client-approval	Send for Approval	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t10	workflow-bookkeeper	book-step-client-approval	book-step-completed	Approve	\N	f	f	f	["user"]	t	\N	2026-02-04 07:01:46.65691
book-t11	workflow-bookkeeper	book-step-client-approval	book-step-processing	Request Changes	\N	f	f	f	["user"]	t	\N	2026-02-04 07:01:46.65691
book-t14	workflow-bookkeeper	book-step-admin-review	book-step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
book-t15	workflow-bookkeeper	book-step-processing	book-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t1	workflow-financial-planner	fp-step-pending	fp-step-discovery	Schedule Discovery	\N	f	f	f	["admin", "accountant", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t2	workflow-financial-planner	fp-step-discovery	fp-step-fact-find	Send Fact Find	\N	f	f	f	["admin", "accountant", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t3	workflow-financial-planner	fp-step-fact-find	fp-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t4	workflow-financial-planner	fp-step-invoice-raised	fp-step-assigned	Assign Planner	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t5	workflow-financial-planner	fp-step-assigned	fp-step-analysis	Start Analysis	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t6	workflow-financial-planner	fp-step-analysis	fp-step-soa-prep	Prepare SOA	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t7	workflow-financial-planner	fp-step-soa-prep	fp-step-compliance-review	Submit for Review	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t8	workflow-financial-planner	fp-step-compliance-review	fp-step-soa-prep	Request Changes	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t9	workflow-financial-planner	fp-step-compliance-review	fp-step-presentation	Approve & Present	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t10	workflow-financial-planner	fp-step-presentation	fp-step-query	Client Query	\N	f	f	f	["user"]	t	\N	2026-02-04 07:01:46.65691
fp-t11	workflow-financial-planner	fp-step-query	fp-step-presentation	Query Resolved	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t12	workflow-financial-planner	fp-step-presentation	fp-step-implementation	Client Accepted	\N	f	f	f	["user", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t13	workflow-financial-planner	fp-step-implementation	fp-step-completed	Complete	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t14	workflow-financial-planner	fp-step-implementation	fp-step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t16	workflow-financial-planner	fp-step-admin-review	fp-step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
fp-t17	workflow-financial-planner	fp-step-analysis	fp-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t1	workflow-mortgage-broker	mb-step-pending	mb-step-consultation	Schedule Consultation	\N	f	f	f	["admin", "accountant", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t2	workflow-mortgage-broker	mb-step-consultation	mb-step-docs-collection	Request Documents	\N	f	f	f	["admin", "accountant", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t3	workflow-mortgage-broker	mb-step-docs-collection	mb-step-serviceability	Assess Serviceability	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t4	workflow-mortgage-broker	mb-step-serviceability	mb-step-product-selection	Select Products	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t5	workflow-mortgage-broker	mb-step-product-selection	mb-step-invoice-raised	Raise Invoice	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t6	workflow-mortgage-broker	mb-step-invoice-raised	mb-step-application	Submit Application	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t7	workflow-mortgage-broker	mb-step-application	mb-step-assessment	Lender Assessing	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t8	workflow-mortgage-broker	mb-step-assessment	mb-step-query	Info Required	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t9	workflow-mortgage-broker	mb-step-query	mb-step-assessment	Info Provided	\N	f	f	f	["accountant", "admin", "super_admin", "user", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t10	workflow-mortgage-broker	mb-step-assessment	mb-step-conditional	Conditional Approved	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t11	workflow-mortgage-broker	mb-step-assessment	mb-step-declined	Declined	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t12	workflow-mortgage-broker	mb-step-conditional	mb-step-unconditional	Unconditional Approved	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t13	workflow-mortgage-broker	mb-step-unconditional	mb-step-settlement	Proceed to Settlement	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t14	workflow-mortgage-broker	mb-step-settlement	mb-step-completed	Settlement Complete	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t15	workflow-mortgage-broker	mb-step-settlement	mb-step-admin-review	Submit for Admin Review	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t16	workflow-mortgage-broker	mb-step-admin-review	mb-step-application	Request Changes	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t17	workflow-mortgage-broker	mb-step-admin-review	mb-step-completed	Approve & Complete	\N	f	f	f	["admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
mb-t18	workflow-mortgage-broker	mb-step-assessment	mb-step-admin-review	Escalate to Admin	\N	f	f	f	["accountant", "admin", "super_admin", "senior_accountant"]	t	\N	2026-02-04 07:01:46.65691
\.


--
-- Name: assignment_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.assignment_history_id_seq', 1, false);


--
-- Name: client_entity_contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.client_entity_contacts_id_seq', 1, false);


--
-- Name: client_notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.client_notes_id_seq', 1, false);


--
-- Name: client_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.client_tags_id_seq', 1, false);


--
-- Name: company_request_statuses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.company_request_statuses_id_seq', 10, true);


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

SELECT pg_catalog.setval('public.email_templates_id_seq', 8, true);


--
-- Name: form_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.form_questions_id_seq', 71, true);


--
-- Name: form_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.form_responses_id_seq', 1, false);


--
-- Name: forms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.forms_id_seq', 11, true);


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

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: otps_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.otps_id_seq', 1, true);


--
-- Name: queries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.queries_id_seq', 1, false);


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

SELECT pg_catalog.setval('public.roles_id_seq', 6, true);


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

SELECT pg_catalog.setval('public.services_id_seq', 62, true);


--
-- Name: smsf_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.smsf_questions_id_seq', 25, true);


--
-- Name: smsf_submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.smsf_submissions_id_seq', 4, true);


--
-- Name: system_email_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_email_config_id_seq', 1, false);


--
-- Name: system_request_statuses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_request_statuses_id_seq', 7, true);


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
-- Name: assignment_history assignment_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assignment_history
    ADD CONSTRAINT assignment_history_pkey PRIMARY KEY (id);


--
-- Name: client_entities client_entities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_entities
    ADD CONSTRAINT client_entities_pkey PRIMARY KEY (id);


--
-- Name: client_entity_contacts client_entity_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_entity_contacts
    ADD CONSTRAINT client_entity_contacts_pkey PRIMARY KEY (id);


--
-- Name: client_notes client_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_notes
    ADD CONSTRAINT client_notes_pkey PRIMARY KEY (id);


--
-- Name: client_service_pricing client_service_pricing_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_service_pricing
    ADD CONSTRAINT client_service_pricing_pkey PRIMARY KEY (id);


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
-- Name: company_request_statuses company_request_statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_request_statuses
    ADD CONSTRAINT company_request_statuses_pkey PRIMARY KEY (id);


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
-- Name: service_requests service_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_pkey PRIMARY KEY (id);


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
-- Name: smsf_questions smsf_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.smsf_questions
    ADD CONSTRAINT smsf_questions_pkey PRIMARY KEY (id);


--
-- Name: smsf_submissions smsf_submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.smsf_submissions
    ADD CONSTRAINT smsf_submissions_pkey PRIMARY KEY (id);


--
-- Name: system_email_config system_email_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_email_config
    ADD CONSTRAINT system_email_config_pkey PRIMARY KEY (id);


--
-- Name: system_request_statuses system_request_statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_request_statuses
    ADD CONSTRAINT system_request_statuses_pkey PRIMARY KEY (id);


--
-- Name: system_request_statuses system_request_statuses_status_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_request_statuses
    ADD CONSTRAINT system_request_statuses_status_key_key UNIQUE (status_key);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


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
-- Name: company_request_statuses unique_company_status_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_request_statuses
    ADD CONSTRAINT unique_company_status_key UNIQUE (company_id, status_key);


--
-- Name: service_renewals unique_user_service_due_date; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_renewals
    ADD CONSTRAINT unique_user_service_due_date UNIQUE (user_id, service_id, next_due_date);


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
-- Name: ix_access_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_access_logs_created_at ON public.access_logs USING btree (created_at);


--
-- Name: ix_activity_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_logs_created_at ON public.activity_logs USING btree (created_at);


--
-- Name: ix_service_requests_request_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_service_requests_request_number ON public.service_requests USING btree (request_number);


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
-- Name: client_entities client_entities_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_entities
    ADD CONSTRAINT client_entities_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: client_entities client_entities_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_entities
    ADD CONSTRAINT client_entities_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: client_entity_contacts client_entity_contacts_client_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_entity_contacts
    ADD CONSTRAINT client_entity_contacts_client_entity_id_fkey FOREIGN KEY (client_entity_id) REFERENCES public.client_entities(id) ON DELETE CASCADE;


--
-- Name: client_entity_contacts client_entity_contacts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_entity_contacts
    ADD CONSTRAINT client_entity_contacts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


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
-- Name: client_service_pricing client_service_pricing_client_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_service_pricing
    ADD CONSTRAINT client_service_pricing_client_entity_id_fkey FOREIGN KEY (client_entity_id) REFERENCES public.client_entities(id) ON DELETE CASCADE;


--
-- Name: client_service_pricing client_service_pricing_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_service_pricing
    ADD CONSTRAINT client_service_pricing_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: client_service_pricing client_service_pricing_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_service_pricing
    ADD CONSTRAINT client_service_pricing_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: client_service_pricing client_service_pricing_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_service_pricing
    ADD CONSTRAINT client_service_pricing_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;


--
-- Name: client_service_pricing client_service_pricing_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_service_pricing
    ADD CONSTRAINT client_service_pricing_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES public.users(id);


--
-- Name: client_service_pricing client_service_pricing_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_service_pricing
    ADD CONSTRAINT client_service_pricing_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


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
-- Name: company_request_statuses company_request_statuses_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_request_statuses
    ADD CONSTRAINT company_request_statuses_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


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
    ADD CONSTRAINT documents_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


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
-- Name: service_requests service_requests_client_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_client_entity_id_fkey FOREIGN KEY (client_entity_id) REFERENCES public.client_entities(id) ON DELETE SET NULL;


--
-- Name: service_requests service_requests_current_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_current_step_id_fkey FOREIGN KEY (current_step_id) REFERENCES public.workflow_steps(id);


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
    ADD CONSTRAINT service_workflows_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: service_workflows service_workflows_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_workflows
    ADD CONSTRAINT service_workflows_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: services services_form_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_form_id_fkey FOREIGN KEY (form_id) REFERENCES public.forms(id);


--
-- Name: services services_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.service_workflows(id);


--
-- Name: smsf_submissions smsf_submissions_client_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.smsf_submissions
    ADD CONSTRAINT smsf_submissions_client_entity_id_fkey FOREIGN KEY (client_entity_id) REFERENCES public.client_entities(id);


--
-- Name: tasks tasks_assigned_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assigned_to_id_fkey FOREIGN KEY (assigned_to_id) REFERENCES public.users(id);


--
-- Name: tasks tasks_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: tasks tasks_service_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_service_request_id_fkey FOREIGN KEY (service_request_id) REFERENCES public.service_requests(id) ON DELETE SET NULL;


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
-- Name: users users_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.users(id);


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

\unrestrict PpHAC5U5sHicVxroikuPwxYQ7pIpkiQJaGs42bIH1iRfH0x1KpggdboNl9KbLVv

