TABLE_CONFIG = {
    "championships": {
        "title": "Чемпионаты",
        "fields": [
            {"column": "championship_id", "label": "ID", "type": "hidden"},
            {"column": "name", "label": "Название", "type": "text"},
            {"column": "country", "label": "Страна", "type": "text"},
            {"column": "division_level", "label": "Уровень дивизиона", "type": "number"},
            {"column": "team_limit", "label": "Лимит команд", "type": "number"},
            {"column": "rank_prefer", "label": "Приоритет ранга", "type": "boolean"}
        ]
    },
    "teams": {
        "title": "Команды",
        "fields": [
            {"column": "team_id", "label": "ID", "type": "hidden"},
            {"column": "name", "label": "Название", "type": "text"},
            {"column": "city", "label": "Город", "type": "text"},
            {"column": "founded_year", "label": "Год основания", "type": "number"},
            {"column": "stadium", "label": "Стадион", "type": "text"}
        ]
    },
    "players": {
        "title": "Игроки",
        "fields": [
            {"column": "player_id", "label": "ID", "type": "hidden"},
            {"column": "full_name", "label": "ФИО", "type": "text"},
            {"column": "birth_date", "label": "Дата рождения", "type": "date"},
            {"column": "nationality", "label": "Гражданство", "type": "text"},
            {"column": "position", "label": "Позиция", "type": "text"}
        ]
    },
    "seasons": {
        "title": "Сезоны",
        "fields": [
            {"column": "season_id", "label": "ID", "type": "hidden"},
            {"column": "championship_id", "label": "Чемпионат", "type": "combo",
             "relation": {"table": "championships", "id_col": "championship_id", "name_col": "name"}},
            {"column": "start_date", "label": "Начало", "type": "date"},
            {"column": "end_date", "label": "Конец", "type": "date"},
            {"column": "status", "label": "Статус", "type": "text"}
        ]
    },
    "matches": {
        "title": "Матчи",
        "fields": [
            {"column": "match_id", "label": "ID", "type": "hidden"},
            {"column": "season_id", "label": "Сезон", "type": "combo",
             "relation": {"table": "seasons", "id_col": "season_id", "name_col": "start_date"}},
            {"column": "home_team_id", "label": "Хозяева", "type": "combo",
             "relation": {"table": "teams", "id_col": "team_id", "name_col": "name"}},
            {"column": "away_team_id", "label": "Гости", "type": "combo",
             "relation": {"table": "teams", "id_col": "team_id", "name_col": "name"}},
            {"column": "match_date", "label": "Дата и время", "type": "date"},
            {"column": "tour", "label": "Тур", "type": "number"},
            {"column": "home_score", "label": "Голы (Дома)", "type": "number"},
            {"column": "away_score", "label": "Голы (В гостях)", "type": "number"},
            {"column": "status", "label": "Статус", "type": "text"}
        ]
    },
    "contracts": {
        "title": "Контракты",
        "fields": [
            {"column": "contract_id", "label": "ID", "type": "hidden"},
            {"column": "team_id", "label": "Команда", "type": "combo",
             "relation": {"table": "teams", "id_col": "team_id", "name_col": "name"}},
            {"column": "player_id", "label": "Игрок", "type": "combo",
             "relation": {"table": "players", "id_col": "player_id", "name_col": "full_name"}},
            {"column": "start_date", "label": "Начало", "type": "date"},
            {"column": "end_date", "label": "Конец", "type": "date"}
        ]
    },
    "match_events": {
        "title": "События матча",
        "fields": [
            {"column": "event_id", "label": "ID", "type": "hidden"},
            {"column": "match_id", "label": "ID Матча (Дата)", "type": "combo",
             "relation": {"table": "matches", "id_col": "match_id", "name_col": "match_date"}},
            {"column": "player_id", "label": "Автор", "type": "combo",
             "relation": {"table": "players", "id_col": "player_id", "name_col": "full_name"}},
            {"column": "assist_player_id", "label": "Ассистент", "type": "combo",
             "relation": {"table": "players", "id_col": "player_id", "name_col": "full_name"}},
            {"column": "event_type", "label": "Тип (Гол/Карточка)", "type": "text"},
            {"column": "minute", "label": "Минута", "type": "number"}
        ]
    },
    "team_stats": {
        "title": "Статистика",
        "fields": [
            {"column": "stats_id", "label": "ID", "type": "hidden"},
            {"column": "match_id", "label": "Матч", "type": "combo",
             "relation": {"table": "matches", "id_col": "match_id", "name_col": "match_date"}},
            {"column": "team_id", "label": "Команда", "type": "combo",
             "relation": {"table": "teams", "id_col": "team_id", "name_col": "name"}},
            {"column": "possession", "label": "Владение (%)", "type": "number"},
            {"column": "shots", "label": "Удары", "type": "number"},
            {"column": "shots_on_target", "label": "В створ", "type": "number"},
            {"column": "corners", "label": "Угловые", "type": "number"},
            {"column": "fouls", "label": "Фолы", "type": "number"},
            {"column": "offsides", "label": "Офсайды", "type": "number"}
        ]
    },
    "season_teams": {
        "title": "Составы лиг",
        "fields": [
            {"column": "entry_id", "label": "ID", "type": "hidden"},
            {"column": "season_id", "label": "Сезон", "type": "combo",
             "relation": {
                 "table": "seasons",
                 "id_col": "season_id",
                 "name_col": "season_label"
             }},
            {"column": "team_id", "label": "Команда", "type": "combo",
             "relation": {"table": "teams", "id_col": "team_id", "name_col": "name"}}
        ]
    },
}