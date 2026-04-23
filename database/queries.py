from database.connection import db
from psycopg2.extras import RealDictCursor
from psycopg2 import sql


def get_one(table_name, id_column, id_value):
    conn = db.get_connection()
    if not conn: return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"SELECT * FROM {table_name} WHERE {id_column} = %s;"
            cursor.execute(query, (id_value,))
            result = cursor.fetchone()
            return result

    except Exception as e:
        print(f"Ошибка при получении данных из таблицы: {e}")
        return []
    finally:
        db.close_connection()


def get_all_table(table):
    conn = db.get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if table == "seasons":
                query = """
                                SELECT s.*, c.name || ' (' || s.start_date || ')' as season_label
                                FROM seasons s
                                JOIN championships c ON s.championship_id = c.championship_id;
                            """
            else:
                query = f"SELECT * FROM {table};"

            cursor.execute(query)
            result = cursor.fetchall()
            return result

    except Exception as e:
        print(f"Ошибка при получении данных из таблицы: {e}")
        return []

    finally:
        db.close_connection()


def insert_record(table, data):
    conn = db.get_connection()
    if not conn: return False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            columns = data.keys()
            values = [data[col] for col in columns]

            query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
                table=sql.Identifier(table),
                fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
                values=sql.SQL(', ').join(sql.Placeholder() * len(values))
            )
            cursor.execute(query, values)
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка INSERT: {e}")
        conn.rollback()
        return False
    finally:
        db.close_connection()

def update_record(table, id_column, record_id, data):
    conn = db.get_connection()
    if not conn: return False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            columns = data.keys()
            values = [data[col] for col in columns]
            values.append(record_id)

            set_clause = sql.SQL(', ').join(
                [sql.SQL("{} = %s").format(sql.Identifier(col)) for col in columns]
            )

            query = sql.SQL("UPDATE {table} SET {clause} WHERE {id_field} = %s").format(
                table=sql.Identifier(table),
                clause=set_clause,
                id_field=sql.Identifier(id_column)
            )
            cursor.execute(query, values)
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка UPDATE: {e}")
        conn.rollback()
        return False
    finally:
        db.close_connection()

def delete_record(table, id_column, record_id):
    conn = db.get_connection()
    if not conn: return False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = sql.SQL("DELETE FROM {table} WHERE {id_field} = %s").format(
                table=sql.Identifier(table),
                id_field=sql.Identifier(id_column)
            )
            cursor.execute(query, (record_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка DELETE: {e}")
        conn.rollback()
        return False
    finally:
        db.close_connection()

def get_tournament_table(season_id):
    conn = db.get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                WITH team_results AS (
                    SELECT 
                        home_team_id AS team_id,
                        home_score AS gs,
                        away_score AS ga,
                        CASE WHEN home_score > away_score THEN 3 
                             WHEN home_score = away_score THEN 1 ELSE 0 END AS pts,
                        CASE WHEN home_score > away_score THEN 1 ELSE 0 END AS win,
                        CASE WHEN home_score = away_score THEN 1 ELSE 0 END AS draw,
                        CASE WHEN home_score < away_score THEN 1 ELSE 0 END AS loss
                    FROM matches 
                    WHERE season_id = %s 

                    UNION ALL
                    
                    SELECT 
                        away_team_id AS team_id,
                        away_score AS gs,
                        home_score AS ga,
                        CASE WHEN away_score > home_score THEN 3 
                             WHEN away_score = home_score THEN 1 ELSE 0 END AS pts,
                        CASE WHEN away_score > home_score THEN 1 ELSE 0 END AS win,
                        CASE WHEN away_score = home_score THEN 1 ELSE 0 END AS draw,
                        CASE WHEN away_score < home_score THEN 1 ELSE 0 END AS loss
                    FROM matches 
                    WHERE season_id = %s 
                )
                SELECT 
                    t.name,
                    COUNT(*) AS played,
                    SUM(tr.win) AS win,
                    SUM(tr.draw) AS draw,
                    SUM(tr.loss) AS loss,
                    SUM(tr.gs) AS gs,
                    SUM(tr.ga) AS ga,
                    SUM(tr.pts) AS pts,
                    t.team_id
                FROM team_results tr
                JOIN teams t ON tr.team_id = t.team_id
                GROUP BY t.team_id, t.name
                ORDER BY pts DESC, (SUM(gs) - SUM(ga)) DESC, SUM(gs) DESC;
            """
            cursor.execute(query, (season_id, season_id))
            result = cursor.fetchall()
            return result

    except Exception as e:
        print(f"Ошибка при формировании турнирной таблицы: {e}")
        return []
    finally:
        db.close_connection()


def get_team_form(team_id, season_id):
    conn = db.get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT res FROM (
                    SELECT 
                        CASE WHEN (home_team_id = %s AND home_score > away_score) OR 
                                  (away_team_id = %s AND away_score > home_score) THEN 'В'
                             WHEN home_score = away_score THEN 'Н'
                             ELSE 'П' END as res,
                        match_date
                    FROM matches 
                    WHERE season_id = %s
                      AND (home_team_id = %s OR away_team_id = %s)
                    ORDER BY match_date DESC
                    LIMIT 5
                ) sub ORDER BY match_date ASC;
            """
            cursor.execute(query, (team_id, team_id, season_id, team_id, team_id))
            result = cursor.fetchall()
            print(result)
            return result

    except Exception as e:
        print(f"Ошибка при получении формы команды: {e}")
        return []
    finally:
        db.close_connection()

def get_matches(season_id, round_number=None, team_id=None):
    conn = db.get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                    SELECT 
                        m.match_id,
                        m.match_date,
                        m.home_score,
                        m.away_score,
                        m.status,
                        m.tour,
                        t1.name as home_team,
                        t2.name as away_team
                    FROM matches m
                    JOIN teams t1 ON m.home_team_id = t1.team_id
                    JOIN teams t2 ON m.away_team_id = t2.team_id
                    
                    WHERE m.season_id = %s
                """
            params = [season_id]
            if round_number and round_number != "Все туры":
                query += " AND m.tour = %s"
                params.append(round_number)

            if team_id and team_id != "Все клубы":
                query += " AND (m.home_team_id = %s OR m.away_team_id = %s)"
                params.extend([team_id, team_id])

            query += " ORDER BY m.match_date ASC;"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    except Exception as e:
        print(f"Ошибка при получении списка матчей: {e}")
        return []
    finally:
        db.close_connection()