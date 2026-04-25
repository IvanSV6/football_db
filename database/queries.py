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
                    JOIN championships c ON s.championship_id = c.championship_id
                """
            else:
                query = f"SELECT * FROM {table};"

            cursor.execute(query)
            result = cursor.fetchall()
            return result

    except Exception as e:
        print(f"Ошибка при получении данных из таблицы {table}: {e}")
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
                        t2.name as away_team,
                        t1.city as city,
                        t1.stadium as stadium
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

            query += " ORDER BY m.match_date DESC;"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    except Exception as e:
        print(f"Ошибка при получении списка матчей: {e}")
        return []
    finally:
        db.close_connection()

def get_seasons_by_championship(championship_id):
    conn = db.get_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM seasons WHERE championship_id = %s ORDER BY start_date DESC;"
            cursor.execute(query, (championship_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении списка сезонов: {e}")
        return []
    finally:
        db.close_connection()

def get_teams_by_seasons(season_id):
    conn = db.get_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT DISTINCT t.team_id, t.name, t.city, t.logo_path 
                FROM teams t
                JOIN season_teams ts ON t.team_id = ts.team_id
                JOIN seasons s ON ts.season_id = s.season_id
                WHERE ts.season_id = %s
                ORDER BY t.name;
            """
            cursor.execute(query, (season_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении списка команд: {e}")
        return []
    finally:
        db.close_connection()

def get_existing_rounds(season_id):
    conn = db.get_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT DISTINCT tour FROM matches WHERE season_id = %s ORDER BY tour;"
            cursor.execute(query, (season_id,))
            return [r['tour'] for r in cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении списка туров: {e}")
        return []
    finally:
        db.close_connection()

def get_available_teams_for_season(season_id):
    conn = db.get_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT team_id, name 
                FROM teams 
                WHERE team_id NOT IN (
                    SELECT team_id 
                    FROM season_teams 
                    WHERE season_id = %s
                )
                ORDER BY name;
            """
            cursor.execute(query, (season_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при поиске свободных команд: {e}")
        return []
    finally:
        db.close_connection()


def get_players(championship_id=None, season_id=None, club_id=None, position=None, nationality=None, search_text=None):
    conn = db.get_connection()
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            conditions = []
            params = []

            # 1. Базовая выборка: используем LEFT JOIN, чтобы сохранить ВСЕХ игроков,
            # COALESCE заменит NULL в названии клуба на 'Свободный агент'
            query = """
                SELECT DISTINCT
                    p.player_id, p.full_name, p.birth_date, p.nationality, p.position, p.photo_path,
                    t.team_id,
                    COALESCE(t.name, 'Свободный агент') AS team_name,
                    t.logo_path
                FROM players p
            """

            # 2. Подтягиваем ТОЛЬКО актуальный контракт
            if season_id:
                # Если передан сезон, контракт должен действовать в рамках дат этого сезона
                query += """
                    LEFT JOIN contracts c ON p.player_id = c.player_id
                        AND c.start_date <= (SELECT end_date FROM seasons WHERE season_id = %s)
                        AND c.end_date >= (SELECT start_date FROM seasons WHERE season_id = %s)
                """
                params.extend([season_id, season_id])
            else:
                # Если сезон не передан, берем контракт, действующий на СЕГОДНЯШНИЙ день
                query += """
                    LEFT JOIN contracts c ON p.player_id = c.player_id
                        AND CURRENT_DATE BETWEEN c.start_date AND c.end_date
                """

            # 3. Подтягиваем клуб (если контракта нет, t.team_id будет NULL)
            query += " LEFT JOIN teams t ON c.team_id = t.team_id"

            # 4. Жесткая фильтрация по чемпионату (только если он запрошен)
            if championship_id:
                if season_id:
                    # Конкретный сезон (оставляем твою логику)
                    query += """
                        INNER JOIN season_teams st ON t.team_id = st.team_id
                        INNER JOIN seasons s ON st.season_id = s.season_id
                    """
                    conditions.append("s.championship_id = %s")
                    params.append(championship_id)

                    conditions.append("s.season_id = %s")
                    params.append(season_id)

                else:
                    # 🔥 ВСЯ ИСТОРИЯ чемпионата
                    conditions.append("""
                        EXISTS (
                            SELECT 1
                            FROM contracts c2
                            JOIN season_teams st2 ON c2.team_id = st2.team_id
                            JOIN seasons s2 ON st2.season_id = s2.season_id
                            WHERE c2.player_id = p.player_id
                              AND s2.championship_id = %s
                        )
                    """)
                    params.append(championship_id)

            # 5. Обычные фильтры
            if search_text:
                conditions.append("p.full_name ILIKE %s")
                params.append(f"%{search_text}%")

            if club_id:
                conditions.append("t.team_id = %s")
                params.append(club_id)

            if position and position not in ("", "Все амплуа"):
                conditions.append("p.position = %s")
                params.append(position)

            if nationality and nationality not in ("", "Все страны"):
                conditions.append("p.nationality = %s")
                params.append(nationality)

            # 6. Финальная сборка WHERE
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY p.full_name;"

            cursor.execute(query, tuple(params))
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при поиске игроков: {e}")
        return []
    finally:
        db.close_connection()

def get_nationalities():
    """Получает список стран, которые реально есть у игроков в базе"""
    conn = db.get_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT DISTINCT nationality FROM players WHERE nationality IS NOT NULL ORDER BY nationality;"
            cursor.execute(query)
            return [row['nationality'] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении списка стран: {e}")
        return []
    finally:
        db.close_connection()
