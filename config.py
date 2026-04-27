TABLE_CONFIG = {
    "championships": {
        "title": "Чемпионаты",
        "fields": [
            {"column": "championship_id", "label": "ID", "type": "hidden"},
            {"column": "name", "label": "Название", "type": "text", "required": True},
            {"column": "country", "label": "Страна", "type": "text", "required": True},
            {"column": "division_level", "label": "Уровень дивизиона", "type": "number", "required": True},
            {"column": "team_limit", "label": "Лимит команд", "type": "number", "required": True},
            {"column": "rank_prefer", "label": "Приоритет ранга", "type": "boolean"}
        ]
    },
    "teams": {
        "title": "Команды",
        "fields": [
            {"column": "team_id", "label": "ID", "type": "hidden"},
            {"column": "name", "label": "Название", "type": "text", "required": True},
            {"column": "city", "label": "Город", "type": "text", "required": True},
            {"column": "founded_year", "label": "Год основания", "type": "number", "min": 1850, "max": 2026, "required": True},
            {"column": "stadium", "label": "Стадион", "type": "text"},
            {"column": "logo_path", "label": "Логотип", "type": "file", "folder": "teams"}
        ]
    },
    "players": {
        "title": "Игроки",
        "fields": [
            {"column": "player_id", "label": "ID", "type": "hidden"},
            {"column": "full_name", "label": "ФИО", "type": "text", "required": True},
            {"column": "birth_date", "label": "Дата рождения", "type": "date",},
            {"column": "nationality", "label": "Гражданство", "type": "text", "required": True},
            {"column": "position", "label": "Позиция", "type": "text"},
            {"column": "photo_path", "label": "Фото", "type": "file", "folder": "players"}
        ]
    },
    "seasons": {
        "title": "Сезоны",
        "fields": [
            {"column": "season_id", "label": "ID", "type": "hidden"},
            {"column": "championship_id", "label": "Чемпионат", "type": "combo", "required": True,
             "relation": {"table": "championships", "id_col": "championship_id", "name_col": "name"}},
            {"column": "start_date", "label": "Начало", "type": "date"},
            {"column": "end_date", "label": "Конец", "type": "date"},
            {"column": "status", "label": "Статус", "type": "text", "required": True}
        ]
    },
    "matches": {
        "title": "Матчи",
        "fields": [
            {"column": "match_id", "label": "ID", "type": "hidden"},
            {"column": "season_id", "label": "Сезон", "type": "combo", "relation": {"table": "seasons", "id_col": "season_id", "name_col": "start_date"}},
            {"column": "home_team_id", "label": "Хозяева", "type": "combo", "relation": {"table": "teams", "id_col": "team_id", "name_col": "name"}},
            {"column": "away_team_id", "label": "Гости", "type": "combo", "relation": {"table": "teams", "id_col": "team_id", "name_col": "name"}},
            {"column": "match_date", "label": "Дата и время", "type": "date", "required": True},
            {"column": "tour", "label": "Тур", "type": "number", "min": 1, "required": True},
            {"column": "home_score", "label": "Голы (Дома)", "type": "number", "min": 0, "required": True},
            {"column": "away_score", "label": "Голы (В гостях)", "type": "number", "min": 0, "required": True},
            {"column": "status", "label": "Статус", "type": "text", "required": True}
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
            {"column": "assist_player_id", "label": "Ассистент", "type": "combo", "requireфd": False,
             "relation": {"table": "players", "id_col": "player_id", "name_col": "full_name"}},
            {"column": "event_type", "label": "Тип (Гол/Карточка)", "type": "text", "required": True},
            {"column": "minute", "label": "Минута", "type": "number", "required": True}
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
            {"column": "possession", "label": "Владение (%)", "type": "number", "min": 0, "max": 100, "required": True},
            {"column": "shots", "label": "Удары", "type": "number", "min": 0, "required": True},
            {"column": "shots_on_target", "label": "В створ", "type": "number", "min": 0, "required": True},
            {"column": "corners", "label": "Угловые", "type": "number", "min": 0, "required": True},
            {"column": "fouls", "label": "Фолы", "type": "number", "min": 0, "required": True},
            {"column": "offsides", "label": "Офсайды", "type": "number", "min": 0, "required": True}
        ]
    },
    "season_teams": {
        "title": "Составы лиг",
        "fields": [
            {"column": "entry_id", "label": "ID", "type": "hidden"},
            {"column": "season_id", "label": "Сезон", "type": "combo", "relation": {"table": "seasons","id_col": "season_id","name_col": "season_label"}},
            {"column": "team_id", "label": "Команда", "type": "combo",
             "relation": {"table": "teams", "id_col": "team_id", "name_col": "name"}}
        ]
    },
}