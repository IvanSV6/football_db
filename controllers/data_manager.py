from database.queries import get_all_table, insert_record

class DataManager:
    def get_all(self, table_name):
        return get_all_table(table_name)

    def add_record(self, table_name, data):
        return insert_record(table_name, data)

data_manager = DataManager()