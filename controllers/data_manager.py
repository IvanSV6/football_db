from database.queries import (get_all_table, insert_record, delete_record, update_record,
                              get_one, get_tournament_table, get_team_form, get_matches, get_teams_by_seasons,
                              get_seasons_by_championship, get_existing_rounds, get_available_teams_for_season,
                              get_players, get_nationalities, get_stats)
from config import TABLE_CONFIG
import os
import shutil

class DataManager:
    def get_all(self, table_name):
        return get_all_table(table_name)

    def _get_id_column(self, table_name):
        for field in TABLE_CONFIG[table_name]["fields"]:
            if field["type"] == "hidden":
                return field["column"]
        return None

    def _get_one(self, table, id_col, id_val):
        return get_one(table, id_col, id_val)

    def up_record(self, table_name, record_id, data):
        id_col = self._get_id_column(table_name)
        return update_record(table_name, id_col, record_id, data)

    def del_record(self, table_name, record_id):
        id_col = self._get_id_column(table_name)
        return delete_record(table_name, id_col, record_id)

    def add_record(self, table_name, data):
        return insert_record(table_name, data)

    def get_tournament_data(self, season_id):
        return get_tournament_table(season_id)

    def get_team_dynamics(self, team_id, season_id):
        return get_team_form(team_id, season_id)

    def get_filtered_matches(self, season_id, round_num, team_id):
        return get_matches(season_id, round_num, team_id)

    def get_seasons(self,championship_id):
        return get_seasons_by_championship(championship_id)

    def get_teams(self,championship_id):
        return get_teams_by_seasons(championship_id)

    def get_tours(self, season_id):
        return get_existing_rounds(season_id)

    def get_teams_for_season(self, season_id):
        return get_available_teams_for_season(season_id)

    def save_logo(self, source_path):
        if not source_path or not os.path.exists(source_path):
            return None
        target_dir = os.path.join("assets", "teams")
        os.makedirs(target_dir, exist_ok=True)
        file_name = os.path.basename(source_path)
        destination = os.path.join(target_dir, file_name)
        try:
            shutil.copy2(source_path, destination)
            return file_name
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")
            return None
    def get_filtered_players(self,championship_id=None, season_id=None, club_id=None, position=None, nationality=None, search_text=None):
        return get_players(championship_id, season_id, club_id, position, nationality, search_text)

    def get_national(self):
        return get_nationalities()
    def get_match_stats(self, match_id):
        return get_stats(match_id)
data_manager = DataManager()