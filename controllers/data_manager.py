from database import queries
from config import TABLE_CONFIG
import os
import shutil

class DataManager:
    def get_all(self, table_name):
        return queries.get_all_table(table_name)

    def _get_id_column(self, table_name):
        for field in TABLE_CONFIG[table_name]["fields"]:
            if field["type"] == "hidden":
                return field["column"]
        return None

    def _get_one(self, table, id_col, id_val):
        return queries.get_one(table, id_col, id_val)

    def up_record(self, table_name, record_id, data):
        id_col = self._get_id_column(table_name)
        return queries.update_record(table_name, id_col, record_id, data)

    def del_record(self, table_name, record_id):
        id_col = self._get_id_column(table_name)
        return queries.delete_record(table_name, id_col, record_id)

    def add_record(self, table_name, data):
        return queries.insert_record(table_name, data)

    def get_team_dynamics(self, team_id, season_id):
        return queries.get_team_form(team_id, season_id)

    def get_tournament_data(self, season_id):
        data = queries.get_tournament_table(season_id)
        for row in data:
            row['full_logo_path'] = self._get_valid_asset_path("teams", row.get('logo_path'))
            row['goals_stat'] = f"{row['gs']}-{row['ga']}"

            form_data = data_manager.get_team_dynamics(row['team_id'], season_id)
            row['form_list'] = [m['res'] for m in form_data]

        return data

    def get_filtered_matches(self, season_id, round_num, team_id):
        return queries.get_matches(season_id, round_num, team_id)

    def get_seasons(self,championship_id):
        seasons = queries.get_seasons_by_championship(championship_id)
        for s in seasons:
            start = str(s['start_date'])[:4]
            end = str(s['end_date'])[:4]
            s['display_name'] = f"{start} - {end}"
        return seasons

    def get_teams(self, season_id):
        teams = queries.get_teams_by_seasons(season_id)
        for t in teams:
            t['full_logo_path'] = self._get_valid_asset_path("teams", t.get('logo_path'))
        return teams

    def get_tours(self, season_id):
        return queries.get_existing_rounds(season_id)

    def get_teams_for_season(self, season_id):
        return queries.get_available_teams_for_season(season_id)

    def get_filtered_players(self, championship_id=None, season_id=None, club_id=None, position=None, nationality=None, search_text=None):
        players = queries.get_players(championship_id, season_id, club_id, position, nationality, search_text)
        for p in players:
            p['full_photo_path'] = self._get_valid_asset_path("players", p.get('photo_path'))
            p['full_logo_path'] = self._get_valid_asset_path("teams", p.get('logo_path'))
        return players

    def get_national(self):
        return queries.get_nationalities()

    def get_match_stats(self, match_id):
        return queries.get_stats(match_id)

    def get_player_rankings(self, championship_id, season_id, event_type, is_assist):
        rankings = queries.get_rankings(championship_id, season_id, event_type, is_assist)
        for r in rankings:
            r['full_photo_path'] = self._get_valid_asset_path("players", r.get('photo_path'))
        return rankings

    def get_events(self, match_id):
        return queries.get_match_events(match_id)

    def save_logo(self, source_path, subfolder="teams"):
        if not source_path or not os.path.exists(source_path):
            return None
        target_dir = os.path.join("assets", subfolder)
        os.makedirs(target_dir, exist_ok=True)
        file_name = os.path.basename(source_path)
        destination = os.path.join(target_dir, file_name)
        try:
            shutil.copy2(source_path, destination)
            return file_name
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")
            return None

    def get_players_for_match_team(self, match_id, team_id):
        return queries.get_players_for_match_team(match_id, team_id)

    def update_team_stats(self, stats_id, data):
        return queries.update_record("team_stats", "stats_id", stats_id, data)

    def insert_team_stats(self, data):
        return queries.insert_record("team_stats", data)

    def add_match_event(self, data):
        return queries.insert_record("match_events", data)

    def validate_universal_data(self, title, data, config_fields):
        """Перенесенная логика валидации из UniversalDialog"""
        for field in config_fields:
            col_name = field["column"]
            f_type = field["type"]
            label = field["label"]

            if f_type == "hidden":
                continue

            val = data.get(col_name)
            if field.get("required") and (val is None or str(val).strip() == ""):
                return False, "Ошибка целостности", f"Поле '{label}' обязательно для заполнения!"

            if f_type == "number" and val != "":
                try:
                    num_val = int(val)
                    if "min" in field and num_val < field["min"]:
                        return False, "Ошибка целостности", f"Поле '{label}' не может быть меньше {field['min']}!"
                    if "max" in field and num_val > field["max"]:
                        return False, "Ошибка целостности", f"Поле '{label}' не может быть больше {field['max']}!"
                except ValueError:
                    return False, "Ошибка типа данных", f"Поле '{label}' должно быть числом!"

        if title == "Матчи":
            if data.get("home_team_id") == data.get("away_team_id"):
                return False, "Логическая аномалия", "Команда 'Хозяева' и команда 'Гости' не могут совпадать!"

            season_id = data.get("season_id")
            match_date = data.get("match_date")
            if season_id and match_date:
                season_data = self._get_one("seasons", "season_id", season_id)
                if season_data:
                    s_start = str(season_data["start_date"])
                    s_end = str(season_data["end_date"])
                    if not (s_start <= match_date <= s_end):
                        return False, "Ошибка целостности", f"Дата матча ({match_date}) выходит за рамки сезона!\nСезон длится с {s_start} по {s_end}"

        if title in ["Контракты", "Сезоны"]:
            if data.get("start_date") > data.get("end_date"):
                return False, "Временная аномалия", "Дата начала не может быть позже даты окончания!"

        return True, "", ""

    def update_match_and_stats(self, match_id, home_team, match_update, stats_home, stats_away):
        # 1. Проверки
        if stats_home["possession"] + stats_away["possession"] != 100:
            return False, "Ошибка ввода", "Сумма владения мячом (Хозяева + Гости) должна быть ровно 100%."

        if stats_home["shots_on_target"] > stats_home["shots"]:
            return False, "Ошибка ввода", "Удары в створ хозяев не могут превышать их общее количество ударов."

        if stats_away["shots_on_target"] > stats_away["shots"]:
            return False, "Ошибка ввода", "Удары в створ гостей не могут превышать их общее количество ударов."

        self.up_record("matches", match_id, match_update)

        stats = self.get_match_stats(match_id)
        if stats and len(stats) == 2:
            for s in stats:
                is_home = s["team_name"] == home_team
                stat_data = stats_home if is_home else stats_away
                self.update_team_stats(s["stats_id"], stat_data)
        else:
            self.insert_team_stats(stats_home)
            self.insert_team_stats(stats_away)

        return True, "Успех", "Сохранено!"

    def _get_valid_asset_path(self, folder, filename):
        if not filename:
            return None
        path = os.path.join("assets", folder, str(filename))
        return path if os.path.exists(path) else None

data_manager = DataManager()