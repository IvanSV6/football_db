--
-- PostgreSQL database dump
--

\restrict tSJ0uxgESv8gDrVtkAlAttf00fjoUsaS5MHKwvvH9GPOyfqk51BPEJF36L01JHT

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-04-03 12:09:30

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
-- TOC entry 237 (class 1255 OID 16624)
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
-- TOC entry 238 (class 1255 OID 16628)
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
-- TOC entry 251 (class 1255 OID 16632)
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
-- TOC entry 239 (class 1255 OID 16630)
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
-- TOC entry 220 (class 1259 OID 16407)
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
-- TOC entry 219 (class 1259 OID 16406)
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
-- TOC entry 5122 (class 0 OID 0)
-- Dependencies: 219
-- Name: championships_championships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.championships_championships_id_seq OWNED BY public.championships.championship_id;


--
-- TOC entry 230 (class 1259 OID 16503)
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
-- TOC entry 229 (class 1259 OID 16502)
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
-- TOC entry 5123 (class 0 OID 0)
-- Dependencies: 229
-- Name: contracts_contract_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contracts_contract_id_seq OWNED BY public.contracts.contract_id;


--
-- TOC entry 234 (class 1259 OID 16566)
-- Name: match_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.match_events (
    event_id integer NOT NULL,
    match_id integer NOT NULL,
    player_id integer NOT NULL,
    assist_player_id integer,
    event_type text NOT NULL,
    minute integer NOT NULL,
    CONSTRAINT chk_event_minute CHECK (((minute >= 1) AND (minute <= 120)))
);


ALTER TABLE public.match_events OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16565)
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
-- TOC entry 5124 (class 0 OID 0)
-- Dependencies: 233
-- Name: match_events_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.match_events_event_id_seq OWNED BY public.match_events.event_id;


--
-- TOC entry 232 (class 1259 OID 16524)
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
-- TOC entry 231 (class 1259 OID 16523)
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
-- TOC entry 5125 (class 0 OID 0)
-- Dependencies: 231
-- Name: matches_match_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.matches_match_id_seq OWNED BY public.matches.match_id;


--
-- TOC entry 226 (class 1259 OID 16469)
-- Name: players; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.players (
    player_id integer NOT NULL,
    full_name text NOT NULL,
    birth_date date NOT NULL,
    nationality text NOT NULL,
    "position" text NOT NULL
);


ALTER TABLE public.players OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16468)
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
-- TOC entry 5126 (class 0 OID 0)
-- Dependencies: 225
-- Name: players_player_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.players_player_id_seq OWNED BY public.players.player_id;


--
-- TOC entry 228 (class 1259 OID 16483)
-- Name: season_teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.season_teams (
    entry_id integer CONSTRAINT seasons_team_entry_id_not_null NOT NULL,
    season_id integer CONSTRAINT seasons_team_season_id_not_null NOT NULL,
    team_id integer CONSTRAINT seasons_team_team_id_not_null NOT NULL
);


ALTER TABLE public.season_teams OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16437)
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
-- TOC entry 221 (class 1259 OID 16436)
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
-- TOC entry 5127 (class 0 OID 0)
-- Dependencies: 221
-- Name: seasons_season_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.seasons_season_id_seq OWNED BY public.seasons.season_id;


--
-- TOC entry 227 (class 1259 OID 16482)
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
-- TOC entry 5128 (class 0 OID 0)
-- Dependencies: 227
-- Name: seasons_team_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.seasons_team_entry_id_seq OWNED BY public.season_teams.entry_id;


--
-- TOC entry 236 (class 1259 OID 16595)
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
-- TOC entry 235 (class 1259 OID 16594)
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
-- TOC entry 5129 (class 0 OID 0)
-- Dependencies: 235
-- Name: team_stats_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.team_stats_stats_id_seq OWNED BY public.team_stats.stats_id;


--
-- TOC entry 224 (class 1259 OID 16456)
-- Name: teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teams (
    team_id integer NOT NULL,
    name text NOT NULL,
    city text NOT NULL,
    founded_year integer NOT NULL,
    stadium text
);


ALTER TABLE public.teams OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16455)
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
-- TOC entry 5130 (class 0 OID 0)
-- Dependencies: 223
-- Name: teams_team_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teams_team_id_seq OWNED BY public.teams.team_id;


--
-- TOC entry 4900 (class 2604 OID 16410)
-- Name: championships championship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.championships ALTER COLUMN championship_id SET DEFAULT nextval('public.championships_championships_id_seq'::regclass);


--
-- TOC entry 4906 (class 2604 OID 16506)
-- Name: contracts contract_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contracts ALTER COLUMN contract_id SET DEFAULT nextval('public.contracts_contract_id_seq'::regclass);


--
-- TOC entry 4910 (class 2604 OID 16569)
-- Name: match_events event_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events ALTER COLUMN event_id SET DEFAULT nextval('public.match_events_event_id_seq'::regclass);


--
-- TOC entry 4907 (class 2604 OID 16527)
-- Name: matches match_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches ALTER COLUMN match_id SET DEFAULT nextval('public.matches_match_id_seq'::regclass);


--
-- TOC entry 4904 (class 2604 OID 16472)
-- Name: players player_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.players ALTER COLUMN player_id SET DEFAULT nextval('public.players_player_id_seq'::regclass);


--
-- TOC entry 4905 (class 2604 OID 16486)
-- Name: season_teams entry_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.season_teams ALTER COLUMN entry_id SET DEFAULT nextval('public.seasons_team_entry_id_seq'::regclass);


--
-- TOC entry 4902 (class 2604 OID 16440)
-- Name: seasons season_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seasons ALTER COLUMN season_id SET DEFAULT nextval('public.seasons_season_id_seq'::regclass);


--
-- TOC entry 4911 (class 2604 OID 16598)
-- Name: team_stats stats_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_stats ALTER COLUMN stats_id SET DEFAULT nextval('public.team_stats_stats_id_seq'::regclass);


--
-- TOC entry 4903 (class 2604 OID 16459)
-- Name: teams team_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams ALTER COLUMN team_id SET DEFAULT nextval('public.teams_team_id_seq'::regclass);


--
-- TOC entry 5100 (class 0 OID 16407)
-- Dependencies: 220
-- Data for Name: championships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.championships (championship_id, name, country, division_level, team_limit, rank_prefer) FROM stdin;
7	РПЛ	Россия	1	16	t
8	Ла Лига	Испания	1	20	t
9	Серия А	Италия	1	20	f
\.


--
-- TOC entry 5110 (class 0 OID 16503)
-- Dependencies: 230
-- Data for Name: contracts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contracts (contract_id, team_id, player_id, start_date, end_date) FROM stdin;
1	10	7	2020-01-01	2025-06-30
2	13	8	2010-01-01	2024-06-30
3	11	9	2003-01-01	2025-06-30
\.


--
-- TOC entry 5114 (class 0 OID 16566)
-- Dependencies: 234
-- Data for Name: match_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.match_events (event_id, match_id, player_id, assist_player_id, event_type, minute) FROM stdin;
1	7	7	\N	Goal	25
2	7	8	\N	Goal	45
3	7	8	\N	Yellow Card	60
\.


--
-- TOC entry 5112 (class 0 OID 16524)
-- Dependencies: 232
-- Data for Name: matches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.matches (match_id, season_id, home_team_id, away_team_id, match_date, tour, home_score, away_score, status) FROM stdin;
10	13	10	13	2023-08-20 19:30:00	5	1	2	Сыгран
7	15	11	12	2023-10-28 17:15:00	11	2	0	Сыгран
11	15	12	11	2023-09-15 18:00:00	4	4	0	Сыгран
\.


--
-- TOC entry 5106 (class 0 OID 16469)
-- Dependencies: 226
-- Data for Name: players; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.players (player_id, full_name, birth_date, nationality, "position") FROM stdin;
7	Александр Соболев	1997-03-07	Россия	Нападающий
8	Квинси Промес	1992-01-04	Нидерланды	Полузащитник
9	Лука Модрич	1985-09-09	Хорватия	Полузащитник
10	Криштиану Роналду	1985-02-05	Портуналия	Нападающий
11	Лионель Месси	1987-06-24	Аргентина	Нападающий
12	Александр Кокорин	1994-03-07	Россия	Нападающий
\.


--
-- TOC entry 5108 (class 0 OID 16483)
-- Dependencies: 228
-- Data for Name: season_teams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.season_teams (entry_id, season_id, team_id) FROM stdin;
1	13	10
2	13	13
3	14	10
4	15	11
5	15	12
\.


--
-- TOC entry 5102 (class 0 OID 16437)
-- Dependencies: 222
-- Data for Name: seasons; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.seasons (season_id, championship_id, start_date, end_date, status) FROM stdin;
13	7	2023-07-01	2024-05-30	Завершен
14	7	2025-07-01	2026-05-30	В процессе
15	8	2023-08-15	2024-05-25	Завершен
\.


--
-- TOC entry 5116 (class 0 OID 16595)
-- Dependencies: 236
-- Data for Name: team_stats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.team_stats (stats_id, match_id, team_id, possession, shots, shots_on_target, corners, fouls, offsides) FROM stdin;
2	7	11	45	10	4	5	3	6
3	7	12	55	12	7	3	4	5
4	10	10	50	8	2	4	4	6
\.


--
-- TOC entry 5104 (class 0 OID 16456)
-- Dependencies: 224
-- Data for Name: teams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teams (team_id, name, city, founded_year, stadium) FROM stdin;
10	Зенит	Санкт-Петербург	1925	Газпром Арена
11	Реал Мадрид	Мадрид	1902	Сантьяго Бернабеу
12	Барселона	Барселона	1899	Камп Ноу
13	Спартак	Москва	1922	Открытие Арена
14	ЦСКА	Москва	1911	ВЭБ Арена
15	Динамо	Москва	1923	ВТБ Арена
\.


--
-- TOC entry 5131 (class 0 OID 0)
-- Dependencies: 219
-- Name: championships_championships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.championships_championships_id_seq', 9, true);


--
-- TOC entry 5132 (class 0 OID 0)
-- Dependencies: 229
-- Name: contracts_contract_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contracts_contract_id_seq', 3, true);


--
-- TOC entry 5133 (class 0 OID 0)
-- Dependencies: 233
-- Name: match_events_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.match_events_event_id_seq', 3, true);


--
-- TOC entry 5134 (class 0 OID 0)
-- Dependencies: 231
-- Name: matches_match_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.matches_match_id_seq', 11, true);


--
-- TOC entry 5135 (class 0 OID 0)
-- Dependencies: 225
-- Name: players_player_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.players_player_id_seq', 12, true);


--
-- TOC entry 5136 (class 0 OID 0)
-- Dependencies: 221
-- Name: seasons_season_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.seasons_season_id_seq', 15, true);


--
-- TOC entry 5137 (class 0 OID 0)
-- Dependencies: 227
-- Name: seasons_team_entry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.seasons_team_entry_id_seq', 5, true);


--
-- TOC entry 5138 (class 0 OID 0)
-- Dependencies: 235
-- Name: team_stats_stats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.team_stats_stats_id_seq', 4, true);


--
-- TOC entry 5139 (class 0 OID 0)
-- Dependencies: 223
-- Name: teams_team_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teams_team_id_seq', 15, true);


--
-- TOC entry 4918 (class 2606 OID 16421)
-- Name: championships championships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.championships
    ADD CONSTRAINT championships_pkey PRIMARY KEY (championship_id);


--
-- TOC entry 4928 (class 2606 OID 16512)
-- Name: contracts contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_pkey PRIMARY KEY (contract_id);


--
-- TOC entry 4932 (class 2606 OID 16578)
-- Name: match_events match_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_pkey PRIMARY KEY (event_id);


--
-- TOC entry 4930 (class 2606 OID 16544)
-- Name: matches matches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_pkey PRIMARY KEY (match_id);


--
-- TOC entry 4924 (class 2606 OID 16481)
-- Name: players players_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.players
    ADD CONSTRAINT players_pkey PRIMARY KEY (player_id);


--
-- TOC entry 4920 (class 2606 OID 16449)
-- Name: seasons seasons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT seasons_pkey PRIMARY KEY (season_id);


--
-- TOC entry 4926 (class 2606 OID 16491)
-- Name: season_teams seasons_team_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.season_teams
    ADD CONSTRAINT seasons_team_pkey PRIMARY KEY (entry_id);


--
-- TOC entry 4934 (class 2606 OID 16609)
-- Name: team_stats team_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_stats
    ADD CONSTRAINT team_stats_pkey PRIMARY KEY (stats_id);


--
-- TOC entry 4922 (class 2606 OID 16467)
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (team_id);


--
-- TOC entry 4949 (class 2620 OID 16625)
-- Name: matches trg_check_match_date; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_check_match_date BEFORE INSERT OR UPDATE ON public.matches FOR EACH ROW EXECUTE FUNCTION public.check_match_date_in_season();


--
-- TOC entry 4948 (class 2620 OID 16629)
-- Name: season_teams trg_check_team_limit; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_check_team_limit BEFORE INSERT ON public.season_teams FOR EACH ROW EXECUTE FUNCTION public.check_team_limit();


--
-- TOC entry 4951 (class 2620 OID 16633)
-- Name: match_events trg_player_event_after_dismissal; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_player_event_after_dismissal BEFORE INSERT OR UPDATE ON public.match_events FOR EACH ROW EXECUTE FUNCTION public.fn_check_player_status_after_card();


--
-- TOC entry 4950 (class 2620 OID 16631)
-- Name: matches trg_team_tour_limit; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_team_tour_limit BEFORE INSERT OR UPDATE ON public.matches FOR EACH ROW EXECUTE FUNCTION public.fn_check_team_tour_limit();


--
-- TOC entry 4938 (class 2606 OID 16518)
-- Name: contracts contracts_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(player_id) ON DELETE CASCADE;


--
-- TOC entry 4939 (class 2606 OID 16513)
-- Name: contracts contracts_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 4943 (class 2606 OID 16589)
-- Name: match_events match_events_assist_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_assist_player_id_fkey FOREIGN KEY (assist_player_id) REFERENCES public.players(player_id) ON DELETE SET NULL;


--
-- TOC entry 4944 (class 2606 OID 16579)
-- Name: match_events match_events_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(match_id) ON DELETE CASCADE;


--
-- TOC entry 4945 (class 2606 OID 16584)
-- Name: match_events match_events_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(player_id) ON DELETE CASCADE;


--
-- TOC entry 4940 (class 2606 OID 16555)
-- Name: matches matches_away_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_away_team_id_fkey FOREIGN KEY (away_team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 4941 (class 2606 OID 16550)
-- Name: matches matches_home_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_home_team_id_fkey FOREIGN KEY (home_team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 4942 (class 2606 OID 16545)
-- Name: matches matches_season_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_season_id_fkey FOREIGN KEY (season_id) REFERENCES public.seasons(season_id) ON DELETE CASCADE;


--
-- TOC entry 4935 (class 2606 OID 16450)
-- Name: seasons seasons_championship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT seasons_championship_id_fkey FOREIGN KEY (championship_id) REFERENCES public.championships(championship_id) ON DELETE CASCADE;


--
-- TOC entry 4936 (class 2606 OID 16492)
-- Name: season_teams seasons_team_season_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.season_teams
    ADD CONSTRAINT seasons_team_season_id_fkey FOREIGN KEY (season_id) REFERENCES public.seasons(season_id) ON DELETE CASCADE;


--
-- TOC entry 4937 (class 2606 OID 16497)
-- Name: season_teams seasons_team_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.season_teams
    ADD CONSTRAINT seasons_team_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- TOC entry 4946 (class 2606 OID 16610)
-- Name: team_stats team_stats_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_stats
    ADD CONSTRAINT team_stats_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(match_id) ON DELETE CASCADE;


--
-- TOC entry 4947 (class 2606 OID 16615)
-- Name: team_stats team_stats_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_stats
    ADD CONSTRAINT team_stats_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


-- Completed on 2026-04-03 12:09:30

--
-- PostgreSQL database dump complete
--

\unrestrict tSJ0uxgESv8gDrVtkAlAttf00fjoUsaS5MHKwvvH9GPOyfqk51BPEJF36L01JHT

