--
-- PostgreSQL database dump
--

\restrict NSlJTARm8xlR1bedM0JbHCRfaIWGJ6sHcsmzDXRioaUkz4T7tTo070K5MuHkVBc

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-04-28 09:07:37 UTC

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
-- TOC entry 239 (class 1255 OID 16385)
-- Name: check_match_date_in_season(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_match_date_in_season() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    season_start DATE;
    season_end DATE;
BEGIN
    SELECT start_date, end_date INTO season_start, season_end FROM seasons WHERE season_id = NEW.season_id;
    IF NEW.match_date::date < season_start OR NEW.match_date::date > season_end THEN
        RAISE EXCEPTION 'Ошибка: Дата матча выходит за рамки установленного сезона!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_match_date_in_season() OWNER TO postgres;

--
-- TOC entry 240 (class 1255 OID 16386)
-- Name: check_team_limit(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_team_limit() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    current_count INTEGER;
    max_limit INTEGER;
BEGIN
    -- Считаем, сколько команд уже в сезоне
    SELECT COUNT(*) INTO current_count FROM season_teams WHERE season_id = NEW.season_id;
    -- Узнаем лимит из таблицы чемпионатов
    SELECT c.team_limit INTO max_limit 
    FROM seasons s JOIN championships c ON s.championship_id = c.championship_id 
    WHERE s.season_id = NEW.season_id;

    IF current_count >= max_limit THEN
        RAISE EXCEPTION 'Ошибка: Превышен лимит количества команд в данном чемпионате!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_team_limit() OWNER TO postgres;

--
-- TOC entry 252 (class 1255 OID 16387)
-- Name: fn_check_player_status_after_card(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_check_player_status_after_card() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    dismissal_minute INTEGER;
BEGIN
    -- 1. Проверяем, была ли у игрока прямая красная карточка в этом матче
    SELECT minute INTO dismissal_minute 
    FROM match_events 
    WHERE match_id = NEW.match_id 
      AND player_id = NEW.player_id 
      AND event_type = 'Red Card'
    LIMIT 1;

    -- 2. Если прямой красной нет, проверяем, была ли ВТОРАЯ желтая (что равно удалению)
    IF dismissal_minute IS NULL THEN
        SELECT minute INTO dismissal_minute
        FROM (
            SELECT minute, ROW_NUMBER() OVER (ORDER BY minute ASC) as card_count
            FROM match_events
            WHERE match_id = NEW.match_id 
              AND player_id = NEW.player_id 
              AND event_type = 'Yellow Card'
        ) sub
        WHERE card_count = 2;
    END IF;

    -- 3. Если минута удаления найдена и текущее событие происходит позже
    IF dismissal_minute IS NOT NULL AND NEW.minute > dismissal_minute THEN
        RAISE EXCEPTION 'Ошибка: Игрок был удален на % минуте и не может совершать действия на % минуте!', 
                        dismissal_minute, NEW.minute;
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_check_player_status_after_card() OWNER TO postgres;

--
-- TOC entry 253 (class 1255 OID 16388)
-- Name: fn_check_team_tour_limit(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_check_team_tour_limit() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Ищем матчи в том же сезоне и туре, где участвует либо домашняя, либо гостевая команда
    IF EXISTS (
        SELECT 1 FROM matches 
        WHERE season_id = NEW.season_id 
        AND tour = NEW.tour 
        AND (
            home_team_id IN (NEW.home_team_id, NEW.away_team_id) 
            OR 
            away_team_id IN (NEW.home_team_id, NEW.away_team_id)
        )
        AND match_id != NEW.match_id -- игнорируем саму себя при обновлении
    ) THEN
        RAISE EXCEPTION 'Ошибка: Одна из команд уже имеет назначенный матч в этом туре сезона!';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_check_team_tour_limit() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 219 (class 1259 OID 16389)
-- Name: championships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.championships (
    championship_id integer CONSTRAINT championships_championships_id_not_null NOT NULL,
    name text NOT NULL,
    country text NOT NULL,
    division_level integer NOT NULL,
    team_limit integer NOT NULL,
    rank_prefer boolean DEFAULT false NOT NULL
);


ALTER TABLE public.championships OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16401)
-- Name: championships_championships_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.championships_championships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.championships_championships_id_seq OWNER TO postgres;

--
-- TOC entry 3565 (class 0 OID 0)
-- Dependencies: 220
-- Name: championships_championships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.championships_championships_id_seq OWNED BY public.championships.championship_id;


--
-- TOC entry 221 (class 1259 OID 16402)
-- Name: contracts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contracts (
    contract_id integer NOT NULL,
    team_id integer NOT NULL,
    player_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date
);


ALTER TABLE public.contracts OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16409)
-- Name: contracts_contract_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contracts_contract_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contracts_contract_id_seq OWNER TO postgres;

--
-- TOC entry 3566 (class 0 OID 0)
-- Dependencies: 222
-- Name: contracts_contract_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contracts_contract_id_seq OWNED BY public.contracts.contract_id;


--
-- TOC entry 223 (class 1259 OID 16410)
-- Name: match_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.match_events (
    event_id integer NOT NULL,
    match_id integer NOT NULL,
    player_id integer NOT NULL,
    assist_player_id integer,
    event_type text NOT NULL,
    minute integer NOT NULL,
    team_id integer,
    CONSTRAINT chk_event_minute CHECK (((minute >= 1) AND (minute <= 120)))
);


ALTER TABLE public.match_events OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16421)
-- Name: match_events_event_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.match_events_event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.match_events_event_id_seq OWNER TO postgres;

--
-- TOC entry 3567 (class 0 OID 0)
-- Dependencies: 224
-- Name: match_events_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.match_events_event_id_seq OWNED BY public.match_events.event_id;


--
-- TOC entry 225 (class 1259 OID 16422)
-- Name: matches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.matches (
    match_id integer NOT NULL,
    season_id integer NOT NULL,
    home_team_id integer NOT NULL,
    away_team_id integer NOT NULL,
    match_date timestamp without time zone NOT NULL,
    tour integer NOT NULL,
    home_score integer DEFAULT 0 NOT NULL,
    away_score integer DEFAULT 0 NOT NULL,
    status text NOT NULL,
    CONSTRAINT chk_positive_scores CHECK (((home_score >= 0) AND (away_score >= 0))),
    CONSTRAINT chk_teams_different CHECK ((home_team_id <> away_team_id))
);


ALTER TABLE public.matches OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16440)
-- Name: matches_match_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.matches_match_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.matches_match_id_seq OWNER TO postgres;

--
-- TOC entry 3568 (class 0 OID 0)
-- Dependencies: 226
-- Name: matches_match_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.matches_match_id_seq OWNED BY public.matches.match_id;


--
-- TOC entry 227 (class 1259 OID 16441)
-- Name: players; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.players (
    player_id integer NOT NULL,
    full_name text NOT NULL,
    birth_date date NOT NULL,
    nationality text NOT NULL,
    "position" text NOT NULL,
    photo_path text
);


ALTER TABLE public.players OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16451)
-- Name: players_player_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.players_player_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.players_player_id_seq OWNER TO postgres;

--
-- TOC entry 3569 (class 0 OID 0)
-- Dependencies: 228
-- Name: players_player_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.players_player_id_seq OWNED BY public.players.player_id;


--
-- TOC entry 229 (class 1259 OID 16452)
-- Name: season_teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.season_teams (
    entry_id integer CONSTRAINT seasons_team_entry_id_not_null NOT NULL,
    season_id integer CONSTRAINT seasons_team_season_id_not_null NOT NULL,
    team_id integer CONSTRAINT seasons_team_team_id_not_null NOT NULL
);


ALTER TABLE public.season_teams OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16458)
-- Name: seasons; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.seasons (
    season_id integer NOT NULL,
    championship_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    status text NOT NULL,
    CONSTRAINT chk_season_dates CHECK ((end_date >= start_date))
);


ALTER TABLE public.seasons OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16469)
-- Name: seasons_season_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.seasons_season_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.seasons_season_id_seq OWNER TO postgres;

--
-- TOC entry 3570 (class 0 OID 0)
-- Dependencies: 231
-- Name: seasons_season_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.seasons_season_id_seq OWNED BY public.seasons.season_id;


--
-- TOC entry 232 (class 1259 OID 16470)
-- Name: seasons_team_entry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.seasons_team_entry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.seasons_team_entry_id_seq OWNER TO postgres;

--
-- TOC entry 3571 (class 0 OID 0)
-- Dependencies: 232
-- Name: seasons_team_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.seasons_team_entry_id_seq OWNED BY public.season_teams.entry_id;


--
-- TOC entry 233 (class 1259 OID 16471)
-- Name: team_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.team_stats (
    stats_id integer NOT NULL,
    match_id integer NOT NULL,
    team_id integer NOT NULL,
    possession integer CONSTRAINT team_stats_possession_pct_not_null NOT NULL,
    shots integer NOT NULL,
    shots_on_target integer NOT NULL,
    corners integer NOT NULL,
    fouls integer NOT NULL,
    offsides integer NOT NULL,
    CONSTRAINT chk_shots CHECK ((shots_on_target <= shots))
);


ALTER TABLE public.team_stats OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 16484)
-- Name: team_stats_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.team_stats_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.team_stats_stats_id_seq OWNER TO postgres;

--
-- TOC entry 3572 (class 0 OID 0)
-- Dependencies: 234
-- Name: team_stats_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.team_stats_stats_id_seq OWNED BY public.team_stats.stats_id;


--
-- TOC entry 235 (class 1259 OID 16485)
-- Name: teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teams (
    team_id integer NOT NULL,
    name text NOT NULL,
    city text NOT NULL,
    founded_year integer NOT NULL,
    stadium text,
    logo_path text
);


ALTER TABLE public.teams OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 16494)
-- Name: teams_team_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teams_team_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teams_team_id_seq OWNER TO postgres;

--
-- TOC entry 3573 (class 0 OID 0)
-- Dependencies: 236
-- Name: teams_team_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teams_team_id_seq OWNED BY public.teams.team_id;


--
-- TOC entry 238 (class 1259 OID 16596)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    login text NOT NULL,
    password text NOT NULL,
    access_level integer NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 16595)
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- TOC entry 3574 (class 0 OID 0)
-- Dependencies: 237
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- TOC entry 3335 (class 2604 OID 16495)
-- Name: championships championship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.championships ALTER COLUMN championship_id SET DEFAULT nextval('public.championships_championships_id_seq'::regclass);


--
-- TOC entry 3337 (class 2604 OID 16496)
-- Name: contracts contract_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contracts ALTER COLUMN contract_id SET DEFAULT nextval('public.contracts_contract_id_seq'::regclass);


--
-- TOC entry 3338 (class 2604 OID 16497)
-- Name: match_events event_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events ALTER COLUMN event_id SET DEFAULT nextval('public.match_events_event_id_seq'::regclass);


--
-- TOC entry 3339 (class 2604 OID 16498)
-- Name: matches match_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches ALTER COLUMN match_id SET DEFAULT nextval('public.matches_match_id_seq'::regclass);


--
-- TOC entry 3342 (class 2604 OID 16499)
-- Name: players player_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.players ALTER COLUMN player_id SET DEFAULT nextval('public.players_player_id_seq'::regclass);


--
-- TOC entry 3343 (class 2604 OID 16500)
-- Name: season_teams entry_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.season_teams ALTER COLUMN entry_id SET DEFAULT nextval('public.seasons_team_entry_id_seq'::regclass);


--
-- TOC entry 3344 (class 2604 OID 16501)
-- Name: seasons season_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seasons ALTER COLUMN season_id SET DEFAULT nextval('public.seasons_season_id_seq'::regclass);


--
-- TOC entry 3345 (class 2604 OID 16502)
-- Name: team_stats stats_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_stats ALTER COLUMN stats_id SET DEFAULT nextval('public.team_stats_stats_id_seq'::regclass);


--
-- TOC entry 3346 (class 2604 OID 16503)
-- Name: teams team_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams ALTER COLUMN team_id SET DEFAULT nextval('public.teams_team_id_seq'::regclass);


--
-- TOC entry 3347 (class 2604 OID 16599)
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- TOC entry 3540 (class 0 OID 16389)
-- Dependencies: 219
-- Data for Name: championships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.championships (championship_id, name, country, division_level, team_limit, rank_prefer) FROM stdin;
7	РПЛ	Россия	1	16	t
8	Ла Лига	Испания	1	20	t
9	Серия А	Италия	1	20	f
\.


--
-- TOC entry 3542 (class 0 OID 16402)
-- Dependencies: 221
-- Data for Name: contracts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contracts (contract_id, team_id, player_id, start_date, end_date) FROM stdin;
1	10	7	2020-01-01	2025-06-30
2	13	8	2010-01-01	2024-06-30
3	11	9	2003-01-01	2025-06-30
5	13	12	2021-07-01	2023-06-30
6	10	12	2023-07-01	2026-06-30
7	10	14	2020-07-01	2025-06-30
8	10	15	2022-07-01	2026-06-30
9	10	16	2021-07-01	2024-06-30
10	14	13	2020-07-01	2022-06-30
11	13	13	2022-07-01	2025-06-30
12	13	17	2021-07-01	2024-06-30
13	13	21	2022-01-01	2026-06-30
14	13	41	2023-07-01	2026-06-30
15	14	22	2021-07-01	2025-06-30
16	14	23	2022-07-01	2026-06-30
17	14	25	2020-07-01	2024-06-30
18	14	33	2021-07-01	2025-06-30
19	15	19	2023-07-01	2026-06-30
20	15	20	2022-07-01	2025-06-30
21	15	36	2021-07-01	2024-06-30
22	15	46	2023-01-01	2026-06-30
23	18	29	2020-07-01	2023-06-30
24	18	29	2023-07-01	2026-06-30
25	18	35	2022-07-01	2026-06-30
26	18	30	2021-07-01	2025-06-30
27	19	42	2021-07-01	2024-06-30
28	19	43	2022-07-01	2025-06-30
29	19	44	2020-07-01	2024-06-30
30	20	49	2022-07-01	2026-06-30
31	20	50	2023-07-01	2027-06-30
32	20	51	2021-07-01	2025-06-30
33	21	52	2023-07-01	2028-06-30
34	21	53	2022-07-01	2026-06-30
35	21	54	2021-07-01	2025-06-30
36	22	55	2022-07-01	2026-06-30
37	22	56	2023-07-01	2027-06-30
38	22	57	2021-07-01	2025-06-30
39	23	58	2022-07-01	2026-06-30
40	23	59	2023-07-01	2027-06-30
41	23	60	2021-07-01	2024-06-30
42	24	61	2020-07-01	2022-06-30
43	23	61	2022-07-01	2024-06-30
44	24	61	2024-07-01	2027-06-30
45	25	24	2021-07-01	2024-06-30
46	26	18	2022-07-01	2025-06-30
47	27	27	2023-07-01	2027-06-30
48	28	28	2023-07-01	2027-06-30
49	29	31	2022-07-01	2025-06-30
\.


--
-- TOC entry 3544 (class 0 OID 16410)
-- Dependencies: 223
-- Data for Name: match_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.match_events (event_id, match_id, player_id, assist_player_id, event_type, minute, team_id) FROM stdin;
3	7	8	\N	ЖК	60	\N
1	7	7	\N	Гол	25	\N
2	7	8	\N	Гол	45	\N
74	40	12	14	Гол	15	\N
75	40	14	\N	Гол	60	\N
76	40	8	\N	Гол	75	\N
77	41	22	23	Гол	22	\N
78	41	19	\N	Гол	68	\N
79	42	29	35	Гол	10	\N
80	42	35	\N	Гол	40	\N
81	42	30	\N	Гол	79	\N
82	43	52	53	Гол	33	\N
83	43	54	\N	Гол	70	\N
84	44	55	\N	Гол	55	\N
85	45	61	\N	Гол	18	\N
86	45	24	\N	Гол	30	\N
87	45	61	\N	Гол	66	\N
88	45	24	\N	Гол	80	\N
89	46	27	\N	Гол	72	\N
90	47	28	\N	Гол	11	\N
91	47	28	\N	Гол	48	\N
92	47	28	\N	Гол	77	\N
93	47	31	\N	Гол	83	\N
94	48	22	\N	Гол	25	\N
95	48	23	\N	Гол	67	\N
96	49	19	\N	Гол	12	\N
97	49	12	14	Гол	39	\N
98	49	14	\N	Гол	58	\N
99	49	15	\N	Гол	76	\N
100	50	42	\N	Гол	14	\N
101	50	43	\N	Гол	61	\N
102	51	52	\N	Гол	36	\N
103	51	29	\N	Гол	72	\N
104	52	58	\N	ЖК	40	\N
105	52	61	\N	ЖК	75	\N
106	53	24	\N	Гол	33	\N
107	53	55	\N	Гол	59	\N
108	53	56	\N	Гол	82	\N
109	56	12	14	Гол	17	\N
110	56	14	\N	Гол	43	\N
111	56	22	\N	Гол	66	\N
112	56	23	\N	Гол	88	\N
\.


--
-- TOC entry 3546 (class 0 OID 16422)
-- Dependencies: 225
-- Data for Name: matches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.matches (match_id, season_id, home_team_id, away_team_id, match_date, tour, home_score, away_score, status) FROM stdin;
7	15	11	12	2023-10-28 17:15:00	11	2	0	Сыгран
11	15	12	11	2023-09-15 18:00:00	4	4	0	Сыгран
40	13	10	13	2023-08-01 18:00:00	1	2	1	Сыгран
41	13	14	15	2023-08-01 20:00:00	1	1	1	Сыгран
42	13	18	19	2023-08-02 18:00:00	1	3	0	Сыгран
43	13	20	21	2023-08-02 20:00:00	1	0	2	Сыгран
44	13	22	23	2023-08-03 18:00:00	1	1	0	Сыгран
45	13	24	25	2023-08-03 20:00:00	1	2	2	Сыгран
46	13	26	27	2023-08-04 18:00:00	1	0	1	Сыгран
47	13	28	29	2023-08-04 20:00:00	1	3	1	Сыгран
48	13	13	14	2023-08-08 18:00:00	2	0	2	Сыгран
49	13	15	10	2023-08-08 20:00:00	2	1	3	Сыгран
50	13	19	20	2023-08-09 18:00:00	2	2	0	Сыгран
51	13	21	18	2023-08-09 20:00:00	2	1	1	Сыгран
52	13	23	24	2023-08-10 18:00:00	2	0	0	Сыгран
53	13	25	22	2023-08-10 20:00:00	2	1	2	Сыгран
54	13	27	28	2023-08-11 18:00:00	2	2	2	Сыгран
55	13	29	26	2023-08-11 20:00:00	2	1	0	Сыгран
56	13	10	14	2023-08-15 18:00:00	3	2	2	Сыгран
57	13	13	15	2023-08-15 20:00:00	3	3	1	Сыгран
58	13	18	20	2023-08-16 18:00:00	3	0	1	Сыгран
59	13	19	21	2023-08-16 20:00:00	3	2	3	Сыгран
60	13	22	24	2023-08-17 18:00:00	3	1	1	Сыгран
61	13	23	25	2023-08-17 20:00:00	3	2	0	Сыгран
62	13	26	28	2023-08-18 18:00:00	3	1	3	Сыгран
63	13	27	29	2023-08-18 20:00:00	3	0	2	Сыгран
64	13	10	15	2023-08-22 18:00:00	4	1	0	Сыгран
65	13	13	18	2023-08-22 20:00:00	4	2	2	Сыгран
66	13	14	19	2023-08-23 18:00:00	4	3	1	Сыгран
67	13	20	22	2023-08-23 20:00:00	4	0	1	Сыгран
68	13	21	23	2023-08-24 18:00:00	4	2	0	Сыгран
69	13	24	26	2023-08-24 20:00:00	4	1	1	Сыгран
70	13	25	27	2023-08-25 18:00:00	4	0	2	Сыгран
71	13	28	29	2023-08-25 20:00:00	4	3	2	Сыгран
75	14	10	13	2025-08-01 18:00:00	1	2	1	Сыгран
76	14	14	15	2025-08-01 20:00:00	1	1	1	Сыгран
77	14	18	19	2025-08-02 18:00:00	1	3	0	Сыгран
78	14	20	21	2025-08-02 20:00:00	1	0	2	Сыгран
79	14	22	23	2025-08-03 18:00:00	1	1	0	Сыгран
80	14	24	25	2025-08-03 20:00:00	1	2	2	Сыгран
81	14	26	27	2025-08-04 18:00:00	1	0	1	Сыгран
82	14	28	29	2025-08-04 20:00:00	1	3	1	Сыгран
83	14	13	14	2025-08-08 18:00:00	2	0	2	Сыгран
84	14	15	10	2025-08-08 20:00:00	2	1	3	Сыгран
85	14	19	20	2025-08-09 18:00:00	2	2	0	Сыгран
86	14	21	18	2025-08-09 20:00:00	2	1	1	Сыгран
87	14	23	24	2025-08-10 18:00:00	2	0	0	Сыгран
88	14	25	22	2025-08-10 20:00:00	2	1	2	Сыгран
89	14	27	28	2025-08-11 18:00:00	2	2	2	Сыгран
90	14	29	26	2025-08-11 20:00:00	2	1	0	Сыгран
\.


--
-- TOC entry 3548 (class 0 OID 16441)
-- Dependencies: 227
-- Data for Name: players; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.players (player_id, full_name, birth_date, nationality, "position", photo_path) FROM stdin;
7	Александр Соболев	1997-03-07	Россия	Нападающий	\N
8	Квинси Промес	1992-01-04	Нидерланды	Полузащитник	\N
9	Лука Модрич	1985-09-09	Хорватия	Полузащитник	\N
10	Криштиану Роналду	1985-02-05	Портуналия	Нападающий	\N
13	Савенков Иван	2006-11-01	Россия	Полузащитник	\N
12	Kylian Mbappe	1998-12-20	Франция	Нападающий	\N
1	Erling Haaland	2000-07-21	Норвегия	Нападающий	\N
14	Kevin De Bruyne	1991-06-28	Бельгия	Полузащитник	\N
15	Virgil van Dijk	1991-07-08	Нидерланды	Защитник	\N
16	Alisson Becker	1992-10-02	Бразилия	Вратарь	\N
17	Mohamed Salah	1992-06-15	Египет	Нападающий	\N
18	Sadio Mane	1992-04-10	Сенегал	Нападающий	\N
19	Harry Kane	1993-07-28	Англия	Нападающий	\N
20	Son Heung-min	1992-07-08	Южная Корея	Нападающий	\N
21	Bruno Fernandes	1994-09-08	Португалия	Полузащитник	\N
22	Joshua Kimmich	1995-02-08	Германия	Полузащитник	\N
23	Leon Goretzka	1995-02-06	Германия	Полузащитник	\N
24	Thomas Muller	1989-09-13	Германия	Нападающий	\N
25	Manuel Neuer	1986-03-27	Германия	Вратарь	\N
26	Jamal Musiala	2003-02-26	Германия	Полузащитник	\N
27	Pedri	2002-11-25	Испания	Полузащитник	\N
28	Gavi	2004-08-05	Испания	Полузащитник	\N
29	Frenkie de Jong	1997-05-12	Нидерланды	Полузащитник	\N
30	Marc-Andre ter Stegen	1992-04-30	Германия	Вратарь	\N
31	Robert Lewandowski	1988-08-21	Польша	Нападающий	\N
32	Luka Modric	1985-09-09	Хорватия	Полузащитник	\N
33	Toni Kroos	1990-01-04	Германия	Полузащитник	\N
34	Karim Benzema	1987-12-19	Франция	Нападающий	\N
35	Vinicius Junior	2000-07-12	Бразилия	Нападающий	\N
36	Thibaut Courtois	1992-05-11	Бельгия	Вратарь	\N
37	Antoine Griezmann	1991-03-21	Франция	Нападающий	\N
38	Olivier Giroud	1986-09-30	Франция	Нападающий	\N
39	N Golo Kante	1991-03-29	Франция	Полузащитник	\N
40	Paul Pogba	1993-03-15	Франция	Полузащитник	\N
41	Raphael Varane	1993-04-25	Франция	Защитник	\N
42	Romelu Lukaku	1993-05-13	Бельгия	Нападающий	\N
43	Eden Hazard	1991-01-07	Бельгия	Полузащитник	\N
44	Jan Oblak	1993-01-07	Словения	Вратарь	\N
45	Joao Felix	1999-11-10	Португалия	Нападающий	\N
46	Bernardo Silva	1994-08-10	Португалия	Полузащитник	\N
47	Ruben Dias	1997-05-14	Португалия	Защитник	\N
48	Joao Cancelo	1994-05-27	Португалия	Защитник	\N
49	Declan Rice	1999-01-14	Англия	Полузащитник	\N
50	Bukayo Saka	2001-09-05	Англия	Нападающий	\N
51	Phil Foden	2000-05-28	Англия	Полузащитник	\N
52	Jude Bellingham	2003-06-29	Англия	Полузащитник	\N
53	Mason Mount	1999-01-10	Англия	Полузащитник	\N
54	Raheem Sterling	1994-12-08	Англия	Нападающий	\N
55	Gianluigi Donnarumma	1999-02-25	Италия	Вратарь	\N
56	Federico Chiesa	1997-10-25	Италия	Нападающий	\N
57	Marco Verratti	1992-11-05	Италия	Полузащитник	\N
58	Nicolo Barella	1997-02-07	Италия	Полузащитник	\N
59	Lautaro Martinez	1997-08-22	Аргентина	Нападающий	\N
60	Angel Di Maria	1988-02-14	Аргентина	Полузащитник	\N
61	Rodrigo De Paul	1994-05-24	Аргентина	Полузащитник	\N
62	Савенков Иван	2026-04-26	Россия	Вратарь	\N
63	Петров Петр	2026-04-26	Россия	Вратарь	\N
11	Леонель Месси	1987-06-24	Аргентина	Нападающий	messi.png
\.


--
-- TOC entry 3550 (class 0 OID 16452)
-- Dependencies: 229
-- Data for Name: season_teams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.season_teams (entry_id, season_id, team_id) FROM stdin;
1	13	10
2	13	13
3	14	10
4	15	11
5	15	12
8	13	14
9	13	15
10	13	18
11	13	19
12	13	20
13	13	21
15	13	22
16	13	23
17	13	24
18	13	25
19	13	26
20	13	28
21	13	29
22	13	27
24	14	15
26	14	18
27	14	19
28	14	20
29	14	21
30	14	22
31	14	23
32	14	24
33	14	25
34	14	26
35	14	27
36	14	28
37	14	29
38	14	13
39	14	14
\.


--
-- TOC entry 3551 (class 0 OID 16458)
-- Dependencies: 230
-- Data for Name: seasons; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.seasons (season_id, championship_id, start_date, end_date, status) FROM stdin;
13	7	2023-07-01	2024-05-30	Завершен
14	7	2025-07-01	2026-05-30	В процессе
15	8	2023-08-15	2024-05-25	Завершен
\.


--
-- TOC entry 3554 (class 0 OID 16471)
-- Dependencies: 233
-- Data for Name: team_stats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.team_stats (stats_id, match_id, team_id, possession, shots, shots_on_target, corners, fouls, offsides) FROM stdin;
2	7	11	45	10	4	5	3	6
3	7	12	55	12	7	3	4	5
5	7	11	58	14	6	7	10	2
6	7	12	42	8	2	3	14	1
7	11	12	65	18	9	10	8	3
8	11	11	35	5	1	2	12	0
11	40	10	52	13	5	5	13	1
12	40	13	48	10	4	4	15	2
13	41	14	50	11	4	5	12	1
14	41	15	50	12	4	6	11	2
\.


--
-- TOC entry 3556 (class 0 OID 16485)
-- Dependencies: 235
-- Data for Name: teams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teams (team_id, name, city, founded_year, stadium, logo_path) FROM stdin;
15	Динамо	Москва	1923	ВТБ Арена	\N
18	Краснодар	Краснодар	2008		\N
19	Локомотив	Москва	1922		\N
20	Балтика	Калининград	2000		\N
21	Рубин	Казань	2000		\N
22	Ахмат	Грозный	1990		\N
23	Ростов	Ростов-на-Дону	1980		\N
24	Крылья Советов	Самара	1930		\N
25	Акрон	Тольятти	1980		\N
26	Оренбург	Оренбург	1950		\N
27	Урал	Екатеринбург	1930	Екатеринбург Арена	\N
28	Сочи	Сочи	2018	Фишт	\N
29	Факел	Воронеж	1947	Центральный стадион профсоюзов	\N
13	Спартак	Москва	1922	Открытие Арена	spartak.png
14	ЦСКА	Москва	1911	ВЭБ Арена	cska.png
11	Реал Мадрид	Мадрид	1902	Сантьяго Бернабеу	real-madrid.png
12	Барселона	Барселона	1899	Камп Ноу	barcelona.png
10	Зенит	Санкт-Петербург	1925	Газпром Арена	zenit.png
\.


--
-- TOC entry 3559 (class 0 OID 16596)
-- Dependencies: 238
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, login, password, access_level) FROM stdin;
1	admin	admin	1
\.


--
-- TOC entry 3575 (class 0 OID 0)
-- Dependencies: 220
-- Name: championships_championships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.championships_championships_id_seq', 9, true);


--
-- TOC entry 3576 (class 0 OID 0)
-- Dependencies: 222
-- Name: contracts_contract_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contracts_contract_id_seq', 49, true);


--
-- TOC entry 3577 (class 0 OID 0)
-- Dependencies: 224
-- Name: match_events_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.match_events_event_id_seq', 114, true);


--
-- TOC entry 3578 (class 0 OID 0)
-- Dependencies: 226
-- Name: matches_match_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.matches_match_id_seq', 90, true);


--
-- TOC entry 3579 (class 0 OID 0)
-- Dependencies: 228
-- Name: players_player_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.players_player_id_seq', 65, true);


--
-- TOC entry 3580 (class 0 OID 0)
-- Dependencies: 231
-- Name: seasons_season_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.seasons_season_id_seq', 17, true);


--
-- TOC entry 3581 (class 0 OID 0)
-- Dependencies: 232
-- Name: seasons_team_entry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.seasons_team_entry_id_seq', 40, true);


--
-- TOC entry 3582 (class 0 OID 0)
-- Dependencies: 234
-- Name: team_stats_stats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.team_stats_stats_id_seq', 26, true);


--
-- TOC entry 3583 (class 0 OID 0)
-- Dependencies: 236
-- Name: teams_team_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teams_team_id_seq', 29, true);


--
-- TOC entry 3584 (class 0 OID 0)
-- Dependencies: 237
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, true);


--
-- TOC entry 3354 (class 2606 OID 16505)
-- Name: championships championships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.championships
    ADD CONSTRAINT championships_pkey PRIMARY KEY (championship_id);


--
-- TOC entry 3356 (class 2606 OID 16507)
-- Name: contracts contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_pkey PRIMARY KEY (contract_id);


--
-- TOC entry 3358 (class 2606 OID 16509)
-- Name: match_events match_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_pkey PRIMARY KEY (event_id);


--
-- TOC entry 3360 (class 2606 OID 16511)
-- Name: matches matches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_pkey PRIMARY KEY (match_id);


--
-- TOC entry 3362 (class 2606 OID 16513)
-- Name: players players_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.players
    ADD CONSTRAINT players_pkey PRIMARY KEY (player_id);


--
-- TOC entry 3366 (class 2606 OID 16515)
-- Name: seasons seasons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT seasons_pkey PRIMARY KEY (season_id);


--
-- TOC entry 3364 (class 2606 OID 16517)
-- Name: season_teams seasons_team_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.season_teams
    ADD CONSTRAINT seasons_team_pkey PRIMARY KEY (entry_id);


--
-- TOC entry 3368 (class 2606 OID 16519)
-- Name: team_stats team_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_stats
    ADD CONSTRAINT team_stats_pkey PRIMARY KEY (stats_id);


--
-- TOC entry 3370 (class 2606 OID 16521)
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (team_id);


--
-- TOC entry 3372 (class 2606 OID 16609)
-- Name: users unique_login; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT unique_login UNIQUE (login);


--
-- TOC entry 3374 (class 2606 OID 16607)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 3390 (class 2620 OID 16522)
-- Name: matches trg_check_match_date; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_check_match_date BEFORE INSERT OR UPDATE ON public.matches FOR EACH ROW EXECUTE FUNCTION public.check_match_date_in_season();


--
-- TOC entry 3392 (class 2620 OID 16523)
-- Name: season_teams trg_check_team_limit; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_check_team_limit BEFORE INSERT ON public.season_teams FOR EACH ROW EXECUTE FUNCTION public.check_team_limit();


--
-- TOC entry 3389 (class 2620 OID 16524)
-- Name: match_events trg_player_event_after_dismissal; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_player_event_after_dismissal BEFORE INSERT OR UPDATE ON public.match_events FOR EACH ROW EXECUTE FUNCTION public.fn_check_player_status_after_card();


--
-- TOC entry 3391 (class 2620 OID 16525)
-- Name: matches trg_team_tour_limit; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_team_tour_limit BEFORE INSERT OR UPDATE ON public.matches FOR EACH ROW EXECUTE FUNCTION public.fn_check_team_tour_limit();


--
-- TOC entry 3375 (class 2606 OID 16526)
-- Name: contracts contracts_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(player_id) ON DELETE CASCADE;


--
-- TOC entry 3376 (class 2606 OID 16531)
-- Name: contracts contracts_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 3377 (class 2606 OID 16536)
-- Name: match_events match_events_assist_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_assist_player_id_fkey FOREIGN KEY (assist_player_id) REFERENCES public.players(player_id) ON DELETE SET NULL;


--
-- TOC entry 3378 (class 2606 OID 16541)
-- Name: match_events match_events_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(match_id) ON DELETE CASCADE;


--
-- TOC entry 3379 (class 2606 OID 16546)
-- Name: match_events match_events_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(player_id) ON DELETE CASCADE;


--
-- TOC entry 3380 (class 2606 OID 16610)
-- Name: match_events match_events_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 3381 (class 2606 OID 16551)
-- Name: matches matches_away_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_away_team_id_fkey FOREIGN KEY (away_team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 3382 (class 2606 OID 16556)
-- Name: matches matches_home_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_home_team_id_fkey FOREIGN KEY (home_team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 3383 (class 2606 OID 16561)
-- Name: matches matches_season_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_season_id_fkey FOREIGN KEY (season_id) REFERENCES public.seasons(season_id) ON DELETE CASCADE;


--
-- TOC entry 3386 (class 2606 OID 16566)
-- Name: seasons seasons_championship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT seasons_championship_id_fkey FOREIGN KEY (championship_id) REFERENCES public.championships(championship_id) ON DELETE CASCADE;


--
-- TOC entry 3384 (class 2606 OID 16571)
-- Name: season_teams seasons_team_season_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.season_teams
    ADD CONSTRAINT seasons_team_season_id_fkey FOREIGN KEY (season_id) REFERENCES public.seasons(season_id) ON DELETE CASCADE;


--
-- TOC entry 3385 (class 2606 OID 16576)
-- Name: season_teams seasons_team_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.season_teams
    ADD CONSTRAINT seasons_team_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 3387 (class 2606 OID 16581)
-- Name: team_stats team_stats_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_stats
    ADD CONSTRAINT team_stats_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(match_id) ON DELETE CASCADE;


--
-- TOC entry 3388 (class 2606 OID 16586)
-- Name: team_stats team_stats_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_stats
    ADD CONSTRAINT team_stats_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


-- Completed on 2026-04-28 09:07:37 UTC

--
-- PostgreSQL database dump complete
--

\unrestrict NSlJTARm8xlR1bedM0JbHCRfaIWGJ6sHcsmzDXRioaUkz4T7tTo070K5MuHkVBc

