--
-- PostgreSQL database dump
--
ALTER TABLE ONLY public.folha_pagamento
    ADD CONSTRAINT folha_pagamento_uniao UNIQUE (id_funcionario, mes, ano);

CREATE TABLE public.configuracao (
    chave character varying(50) NOT NULL PRIMARY KEY,
    valor text
);

ALTER TABLE public.configuracao OWNER TO postgres;

-- Inicializa o alerta de atraso como desativado por padrão
INSERT INTO public.configuracao (chave, valor) VALUES ('alertas_atraso_ativo', 'false');

\restrict 4FPnHgBJdWfInF2uuQxOIdLNmUBqE5hXd295oxgWx8PphlkJDHKD7CraMabWbRr

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-05-14 20:01:00

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
-- TOC entry 219 (class 1259 OID 24704)
-- Name: banco_horas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.banco_horas (
    id integer NOT NULL,
    id_funcionario integer,
    horas_extras numeric(5,2),
    horas_devidas numeric(5,2)
);


ALTER TABLE public.banco_horas OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 24708)
-- Name: banco_horas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.banco_horas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.banco_horas_id_seq OWNER TO postgres;

--
-- TOC entry 5051 (class 0 OID 0)
-- Dependencies: 220
-- Name: banco_horas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.banco_horas_id_seq OWNED BY public.banco_horas.id;


--
-- TOC entry 221 (class 1259 OID 24709)
-- Name: desconto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.desconto (
    id integer NOT NULL,
    id_funcionario integer,
    tipo character varying(100),
    valor numeric(10,2)
);


ALTER TABLE public.desconto OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 24713)
-- Name: desconto_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.desconto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.desconto_id_seq OWNER TO postgres;

--
-- TOC entry 5052 (class 0 OID 0)
-- Dependencies: 222
-- Name: desconto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.desconto_id_seq OWNED BY public.desconto.id;


--
-- TOC entry 223 (class 1259 OID 24714)
-- Name: folha_pagamento; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.folha_pagamento (
    id integer NOT NULL,
    id_funcionario integer,
    mes integer,
    ano integer,
    salario_bruto numeric(10,2),
    descontos numeric(10,2),
    salario_liquido numeric(10,2)
);


ALTER TABLE public.folha_pagamento OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 24718)
-- Name: folha_pagamento_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.folha_pagamento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.folha_pagamento_id_seq OWNER TO postgres;

--
-- TOC entry 5053 (class 0 OID 0)
-- Dependencies: 224
-- Name: folha_pagamento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.folha_pagamento_id_seq OWNED BY public.folha_pagamento.id;


--
-- TOC entry 225 (class 1259 OID 24719)
-- Name: funcionario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.funcionario (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    cpf character varying(11) NOT NULL,
    cargo character varying(50),
    setor character varying(50),
    salario_base numeric(10,2),
    data_admissao date,
    vale_transporte character varying(3),
    foto TEXT
);


ALTER TABLE public.funcionario OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 24725)
-- Name: funcionario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.funcionario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.funcionario_id_seq OWNER TO postgres;

--
-- TOC entry 5054 (class 0 OID 0)
-- Dependencies: 226
-- Name: funcionario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.funcionario_id_seq OWNED BY public.funcionario.id;


--
-- TOC entry 227 (class 1259 OID 24726)
-- Name: justificativa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.justificativa (
    id integer NOT NULL,
    id_funcionario integer,
    data_justificativa date,
    tipo character varying(50),
    descricao text,
    horas_compensadas boolean,
    quantidade_horas numeric(5,2)
);


ALTER TABLE public.justificativa OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 24732)
-- Name: justificativa_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.justificativa_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.justificativa_id_seq OWNER TO postgres;

--
-- TOC entry 5055 (class 0 OID 0)
-- Dependencies: 228
-- Name: justificativa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.justificativa_id_seq OWNED BY public.justificativa.id;


--
-- TOC entry 229 (class 1259 OID 24733)
-- Name: registro_justificativa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registro_justificativa (
    id integer NOT NULL,
    id_funcionario integer,
    data_falta date,
    motivo text,
    status character varying(20) DEFAULT 'Pendente'::character varying,
    data_envio timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    compensacao character varying(3) DEFAULT 'Não'::character varying
);


ALTER TABLE public.registro_justificativa OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 24742)
-- Name: registro_justificativa_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.registro_justificativa_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.registro_justificativa_id_seq OWNER TO postgres;

--
-- TOC entry 5056 (class 0 OID 0)
-- Dependencies: 230
-- Name: registro_justificativa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.registro_justificativa_id_seq OWNED BY public.registro_justificativa.id;


--
-- TOC entry 231 (class 1259 OID 24743)
-- Name: registro_ponto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registro_ponto (
    id integer NOT NULL,
    id_funcionario integer,
    data_registro date NOT NULL,
    entrada time without time zone,
    saida_intervalo time without time zone,
    volta_intervalo time without time zone,
    saida time without time zone,
    localizacao character varying(100)
);


ALTER TABLE public.registro_ponto OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 24748)
-- Name: registro_ponto_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.registro_ponto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.registro_ponto_id_seq OWNER TO postgres;

--
-- TOC entry 5057 (class 0 OID 0)
-- Dependencies: 232
-- Name: registro_ponto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.registro_ponto_id_seq OWNED BY public.registro_ponto.id;


--
-- TOC entry 234 (class 1259 OID 24818)
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    senha text NOT NULL,
    tipo character varying(20),
    id_funcionario integer
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 24817)
-- Name: usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_id_seq OWNER TO postgres;

--
-- TOC entry 5058 (class 0 OID 0)
-- Dependencies: 233
-- Name: usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_id_seq OWNED BY public.usuario.id;


--
-- TOC entry 4845 (class 2604 OID 24756)
-- Name: banco_horas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.banco_horas ALTER COLUMN id SET DEFAULT nextval('public.banco_horas_id_seq'::regclass);


--
-- TOC entry 4846 (class 2604 OID 24757)
-- Name: desconto id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desconto ALTER COLUMN id SET DEFAULT nextval('public.desconto_id_seq'::regclass);


--
-- TOC entry 4847 (class 2604 OID 24758)
-- Name: folha_pagamento id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folha_pagamento ALTER COLUMN id SET DEFAULT nextval('public.folha_pagamento_id_seq'::regclass);


--
-- TOC entry 4848 (class 2604 OID 24759)
-- Name: funcionario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.funcionario ALTER COLUMN id SET DEFAULT nextval('public.funcionario_id_seq'::regclass);


--
-- TOC entry 4849 (class 2604 OID 24760)
-- Name: justificativa id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.justificativa ALTER COLUMN id SET DEFAULT nextval('public.justificativa_id_seq'::regclass);


--
-- TOC entry 4850 (class 2604 OID 24761)
-- Name: registro_justificativa id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_justificativa ALTER COLUMN id SET DEFAULT nextval('public.registro_justificativa_id_seq'::regclass);


--
-- TOC entry 4854 (class 2604 OID 24762)
-- Name: registro_ponto id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_ponto ALTER COLUMN id SET DEFAULT nextval('public.registro_ponto_id_seq'::regclass);


--
-- TOC entry 4855 (class 2604 OID 24821)
-- Name: usuario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id SET DEFAULT nextval('public.usuario_id_seq'::regclass);


--
-- TOC entry 5030 (class 0 OID 24704)
-- Dependencies: 219
-- Data for Name: banco_horas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.banco_horas (id, id_funcionario, horas_extras, horas_devidas) FROM stdin;
\.


--
-- TOC entry 5032 (class 0 OID 24709)
-- Dependencies: 221
-- Data for Name: desconto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.desconto (id, id_funcionario, tipo, valor) FROM stdin;
\.


--
-- TOC entry 5034 (class 0 OID 24714)
-- Dependencies: 223
-- Data for Name: folha_pagamento; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.folha_pagamento (id, id_funcionario, mes, ano, salario_bruto, descontos, salario_liquido) FROM stdin;
\.


--
-- TOC entry 5036 (class 0 OID 24719)
-- Dependencies: 225
-- Data for Name: funcionario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.funcionario (id, nome, cpf, cargo, setor, salario_base, data_admissao, vale_transporte) FROM stdin;
30	Lana 	71023213419	Dev	TI	3000.00	2026-05-13	S
31	Tiago Ferreira Garcia	22334254678	Servente de Pedreiro	Manutenção	1500.00	2026-05-14	S
32	ju	47839808730	ti	dev	80.00	2026-05-14	S
33	ho	89873295490	ti	dev	890.00	2026-05-14	S
\.


--
-- TOC entry 5038 (class 0 OID 24726)
-- Dependencies: 227
-- Data for Name: justificativa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.justificativa (id, id_funcionario, data_justificativa, tipo, descricao, horas_compensadas, quantidade_horas) FROM stdin;
\.


--
-- TOC entry 5040 (class 0 OID 24733)
-- Dependencies: 229
-- Data for Name: registro_justificativa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registro_justificativa (id, id_funcionario, data_falta, motivo, status, data_envio, compensacao) FROM stdin;
\.


--
-- TOC entry 5042 (class 0 OID 24743)
-- Dependencies: 231
-- Data for Name: registro_ponto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registro_ponto (id, id_funcionario, data_registro, entrada, saida_intervalo, volta_intervalo, saida, localizacao) FROM stdin;
13	31	2026-05-14	14:18:58.231305	\N	\N	\N	\N
14	32	2026-05-14	15:59:46.230602	\N	\N	\N	\N
15	30	2026-05-14	16:53:22.852882	19:46:39.408637	19:47:37.663678	\N	\N
\.


--
-- TOC entry 5045 (class 0 OID 24818)
-- Dependencies: 234
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (id, email, senha, tipo, id_funcionario) FROM stdin;
1	admin@empresa.com	$2b$12$X7ct.pvohvem4T9K5O61ceJ6jKKYKmbrQU4ehFKBa2Q7b/10c81sy	admin	\N
2	ju@gmail.com	$2b$12$/Ppnuuq9UepCadUcytuTXeF4EkKFPjI.qw3ctszgsG6KCNTiK0IH2	funcionario	\N
\.


--
-- TOC entry 5059 (class 0 OID 0)
-- Dependencies: 220
-- Name: banco_horas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.banco_horas_id_seq', 1, false);


--
-- TOC entry 5060 (class 0 OID 0)
-- Dependencies: 222
-- Name: desconto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.desconto_id_seq', 1, false);


--
-- TOC entry 5061 (class 0 OID 0)
-- Dependencies: 224
-- Name: folha_pagamento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.folha_pagamento_id_seq', 1, false);


--
-- TOC entry 5062 (class 0 OID 0)
-- Dependencies: 226
-- Name: funcionario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.funcionario_id_seq', 33, true);


--
-- TOC entry 5063 (class 0 OID 0)
-- Dependencies: 228
-- Name: justificativa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.justificativa_id_seq', 1, false);


--
-- TOC entry 5064 (class 0 OID 0)
-- Dependencies: 230
-- Name: registro_justificativa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.registro_justificativa_id_seq', 3, true);


--
-- TOC entry 5065 (class 0 OID 0)
-- Dependencies: 232
-- Name: registro_ponto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.registro_ponto_id_seq', 15, true);


--
-- TOC entry 5066 (class 0 OID 0)
-- Dependencies: 233
-- Name: usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_seq', 2, true);


--
-- TOC entry 4857 (class 2606 OID 24765)
-- Name: banco_horas banco_horas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.banco_horas
    ADD CONSTRAINT banco_horas_pkey PRIMARY KEY (id);


--
-- TOC entry 4863 (class 2606 OID 24837)
-- Name: funcionario cpf_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.funcionario
    ADD CONSTRAINT cpf_unico UNIQUE (cpf);


--
-- TOC entry 4859 (class 2606 OID 24767)
-- Name: desconto desconto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desconto
    ADD CONSTRAINT desconto_pkey PRIMARY KEY (id);


--
-- TOC entry 4861 (class 2606 OID 24769)
-- Name: folha_pagamento folha_pagamento_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folha_pagamento
    ADD CONSTRAINT folha_pagamento_pkey PRIMARY KEY (id);

-- Adiciona restrição para permitir o funcionamento do ON CONFLICT no Python
ALTER TABLE ONLY public.folha_pagamento
    ADD CONSTRAINT folha_pagamento_uniao UNIQUE (id_funcionario, mes, ano);

--
-- TOC entry 4865 (class 2606 OID 24771)
-- Name: funcionario funcionario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.funcionario
    ADD CONSTRAINT funcionario_pkey PRIMARY KEY (id);


--
-- TOC entry 4867 (class 2606 OID 24773)
-- Name: justificativa justificativa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.justificativa
    ADD CONSTRAINT justificativa_pkey PRIMARY KEY (id);


--
-- TOC entry 4869 (class 2606 OID 24775)
-- Name: registro_justificativa registro_justificativa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_justificativa
    ADD CONSTRAINT registro_justificativa_pkey PRIMARY KEY (id);


--
-- TOC entry 4871 (class 2606 OID 24777)
-- Name: registro_ponto registro_ponto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_ponto
    ADD CONSTRAINT registro_ponto_pkey PRIMARY KEY (id);


--
-- TOC entry 4873 (class 2606 OID 24830)
-- Name: usuario usuario_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_email_key UNIQUE (email);


--
-- TOC entry 4875 (class 2606 OID 24828)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- TOC entry 4876 (class 2606 OID 24780)
-- Name: banco_horas banco_horas_id_funcionario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.banco_horas
    ADD CONSTRAINT banco_horas_id_funcionario_fkey FOREIGN KEY (id_funcionario) REFERENCES public.funcionario(id);


--
-- TOC entry 4877 (class 2606 OID 24785)
-- Name: desconto desconto_id_funcionario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desconto
    ADD CONSTRAINT desconto_id_funcionario_fkey FOREIGN KEY (id_funcionario) REFERENCES public.funcionario(id);


--
-- TOC entry 4878 (class 2606 OID 24790)
-- Name: folha_pagamento folha_pagamento_id_funcionario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folha_pagamento
    ADD CONSTRAINT folha_pagamento_id_funcionario_fkey FOREIGN KEY (id_funcionario) REFERENCES public.funcionario(id);


--
-- TOC entry 4879 (class 2606 OID 24795)
-- Name: justificativa justificativa_id_funcionario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.justificativa
    ADD CONSTRAINT justificativa_id_funcionario_fkey FOREIGN KEY (id_funcionario) REFERENCES public.funcionario(id);


--
-- TOC entry 4880 (class 2606 OID 24800)
-- Name: registro_justificativa registro_justificativa_id_funcionario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_justificativa
    ADD CONSTRAINT registro_justificativa_id_funcionario_fkey FOREIGN KEY (id_funcionario) REFERENCES public.funcionario(id);


--
-- TOC entry 4881 (class 2606 OID 24805)
-- Name: registro_ponto registro_ponto_id_funcionario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro_ponto
    ADD CONSTRAINT registro_ponto_id_funcionario_fkey FOREIGN KEY (id_funcionario) REFERENCES public.funcionario(id);


--
-- TOC entry 4882 (class 2606 OID 24831)
-- Name: usuario usuario_id_funcionario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_id_funcionario_fkey FOREIGN KEY (id_funcionario) REFERENCES public.funcionario(id);


-- Completed on 2026-05-14 20:01:01

--
-- PostgreSQL database dump complete
--
--
-- TOC entry 235 (class 1259 OID 24850)
-- Name: configuracao; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.configuracao (
    chave character varying(50) NOT NULL PRIMARY KEY,
    valor text
);

ALTER TABLE public.configuracao OWNER TO postgres;

-- Inicializa o alerta de atraso como desativado por padrão
INSERT INTO public.configuracao (chave, valor) VALUES ('alertas_atraso_ativo', 'false');

\unrestrict 4FPnHgBJdWfInF2uuQxOIdLNmUBqE5hXd295oxgWx8PphlkJDHKD7CraMabWbRr
