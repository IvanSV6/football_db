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
            {"column": "championship_id", "label": "ID Чемпионата", "type": "number"},
            {"column": "start_date", "label": "Дата начала", "type": "date"},
            {"column": "end_date", "label": "Дата окончания", "type": "date"},
            {"column": "status", "label": "Статус", "type": "text"}
        ]
    },
    "matches": {
        "title": "Матчи",
        "fields": [
            {"column": "match_id", "label": "ID", "type": "hidden"},
            {"column": "season_id", "label": "ID Сезона", "type": "number"},
            {"column": "home_team_id", "label": "ID Хозяев", "type": "number"},
            {"column": "away_team_id", "label": "ID Гостей", "type": "number"},
            {"column": "match_date", "label": "Дата матча", "type": "date"},
            {"column": "tour", "label": "Тур", "type": "number"},
            {"column": "home_score", "label": "Голы (Хозяева)", "type": "number"},
            {"column": "away_score", "label": "Голы (Гости)", "type": "number"},
            {"column": "status", "label": "Статус", "type": "text"}
        ]
    },
    "contracts": {
        "title": "Контракты",
        "fields": [
            {"column": "contract_id", "label": "ID", "type": "hidden"},
            {"column": "team_id", "label": "ID Команды", "type": "number"},
            {"column": "player_id", "label": "ID Игрока", "type": "number"},
            {"column": "start_date", "label": "Начало", "type": "date"},
            {"column": "end_date", "label": "Окончание", "type": "date"}
        ]
    },
    "match_events": {
        "title": "События матча",
        "fields": [
            {"column": "event_id", "label": "ID", "type": "hidden"},
            {"column": "match_id", "label": "ID Матча", "type": "number"},
            {"column": "player_id", "label": "ID Игрока", "type": "number"},
            {"column": "assist_player_id", "label": "ID Ассистента", "type": "number"},
            {"column": "event_type", "label": "Тип события", "type": "text"},
            {"column": "minute", "label": "Минута", "type": "number"}
        ]
    },
    "team_stats": {
        "title": "Статистика команд",
        "fields": [
            {"column": "stats_id", "label": "ID", "type": "hidden"},
            {"column": "match_id", "label": "ID Матча", "type": "number"},
            {"column": "team_id", "label": "ID Команды", "type": "number"},
            {"column": "possession", "label": "Владение (%)", "type": "number"},
            {"column": "shots", "label": "Удары", "type": "number"},
            {"column": "shots_on_target", "label": "В створ", "type": "number"},
            {"column": "corners", "label": "Угловые", "type": "number"},
            {"column": "fouls", "label": "Фолы", "type": "number"},
            {"column": "offsides", "label": "Офсайды", "type": "number"}
        ]
    },
    "season_teams": {
        "title": "Участники сезонов",
        "fields": [
            {"column": "entry_id", "label": "ID", "type": "hidden"},
            {"column": "season_id", "label": "ID Сезона", "type": "number"},
            {"column": "team_id", "label": "ID Команды", "type": "number"}
        ]
    }
}