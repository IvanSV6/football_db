from database.queries import get_all_table, insert_record, delete_record, update_record, get_one
from config import TABLE_CONFIG

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

data_manager = DataManager()