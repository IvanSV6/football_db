from database.utils import db_op
from psycopg2.extras import RealDictCursor
from psycopg2 import sql


@db_op()
def get_one(cursor, table_name, id_column, id_value):
    query = sql.SQL("SELECT * FROM {table} WHERE {id_field} = %s").format(
        table=sql.Identifier(table_name),
        id_field=sql.Identifier(id_column)
    )
    cursor.execute(query, (id_value,))
    return cursor.fetchone()


@db_op()
def get_all_table(cursor, table):
    if table == "seasons":
        query = """
            SELECT s.*, c.name || ' (' || s.start_date || ')' as season_label
            FROM seasons s
            JOIN championships c ON s.championship_id = c.championship_id
        """
        cursor.execute(query)
    else:
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))
        cursor.execute(query)

    return cursor.fetchall()


@db_op(commit=True)
def insert_record(cursor, table, data):
    columns = list(data.keys())
    values = [data[col] for col in columns]

    query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
        table=sql.Identifier(table),
        fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
        values=sql.SQL(', ').join(sql.Placeholder() * len(values))
    )

    cursor.execute(query, values)
    return True


@db_op(commit=True)
def update_record(cursor, table, id_column, record_id, data):
    columns = list(data.keys())
    values = [data[col] for col in columns]
    values.append(record_id)

    set_clause = sql.SQL(', ').join(
        sql.SQL("{} = %s").format(sql.Identifier(col)) for col in columns
    )

    query = sql.SQL("UPDATE {table} SET {clause} WHERE {id_field} = %s").format(
        table=sql.Identifier(table),
        clause=set_clause,
        id_field=sql.Identifier(id_column)
    )

    cursor.execute(query, values)
    return True


@db_op(commit=True)
def delete_record(cursor, table, id_column, record_id):
    query = sql.SQL("DELETE FROM {table} WHERE {id_field} = %s").format(
        table=sql.Identifier(table),
        id_field=sql.Identifier(id_column)
    )

    cursor.execute(query, (record_id,))
    return True


@db_op()
def get_tournament_table(cursor, season_id):
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
    return cursor.fetchall()


@db_op()
def get_team_form(cursor, team_id, season_id):
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
    return cursor.fetchall()


@db_op()
def get_matches(cursor, season_id, round_number=None, team_id=None):
    query = """
        SELECT 
            m.match_id,
            m.home_team_id,
            m.away_team_id,
            m.match_date,
            m.home_score,
            m.away_score,
            m.status,
            m.tour,
            t1.name as home_team,
            t2.name as away_team,
            t1.logo_path as home_logo,
            t2.logo_path as away_logo,
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


@db_op()
def get_seasons_by_championship(cursor, championship_id):
    query = """
        SELECT * FROM seasons 
        WHERE championship_id = %s 
        ORDER BY start_date DESC;
    """
    cursor.execute(query, (championship_id,))
    return cursor.fetchall()


@db_op()
def get_teams_by_seasons(cursor, season_id):
    query = """
        SELECT DISTINCT t.team_id, t.name, t.city, t.logo_path 
        FROM teams t
        JOIN season_teams ts ON t.team_id = ts.team_id
        WHERE ts.season_id = %s
        ORDER BY t.name;
    """
    cursor.execute(query, (season_id,))
    return cursor.fetchall()


@db_op()
def get_existing_rounds(cursor, season_id):
    query = """
        SELECT DISTINCT tour 
        FROM matches 
        WHERE season_id = %s 
        ORDER BY tour;
    """
    cursor.execute(query, (season_id,))
    return [r['tour'] for r in cursor.fetchall()]


@db_op()
def get_available_teams_for_season(cursor, season_id):
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


@db_op()
def get_players(cursor, championship_id=None, season_id=None, club_id=None,
                position=None, nationality=None, search_text=None):
    conditions = []
    params = []

    query = """
        SELECT DISTINCT
            p.player_id, p.full_name, p.birth_date, p.nationality,
            p.position, p.photo_path,
            t.team_id,
            COALESCE(t.name, 'Свободный агент') AS team_name,
            t.logo_path
        FROM players p
    """

    if season_id:
        query += """
            LEFT JOIN contracts c ON p.player_id = c.player_id
                AND c.start_date <= (SELECT end_date FROM seasons WHERE season_id = %s)
                AND c.end_date >= (SELECT start_date FROM seasons WHERE season_id = %s)
        """
        params.extend([season_id, season_id])
    else:
        query += """
            LEFT JOIN contracts c ON p.player_id = c.player_id
                AND CURRENT_DATE BETWEEN c.start_date AND c.end_date
        """

    query += " LEFT JOIN teams t ON c.team_id = t.team_id"

    if championship_id:
        if season_id:
            query += """
                INNER JOIN season_teams st ON t.team_id = st.team_id
                INNER JOIN seasons s ON st.season_id = s.season_id
            """
            conditions.append("s.championship_id = %s")
            params.append(championship_id)

            conditions.append("s.season_id = %s")
            params.append(season_id)
        else:
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

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY p.full_name;"

    cursor.execute(query, tuple(params))
    return cursor.fetchall()


@db_op()
def get_nationalities(cursor):
    query = """
        SELECT DISTINCT nationality 
        FROM players 
        WHERE nationality IS NOT NULL 
        ORDER BY nationality;
    """
    cursor.execute(query)
    return [row['nationality'] for row in cursor.fetchall()]


@db_op()
def get_stats(cursor, match_id):
    query = """
        SELECT ms.*, t.name as team_name 
        FROM team_stats ms
        JOIN teams t ON ms.team_id = t.team_id
        WHERE ms.match_id = %s;
    """
    cursor.execute(query, (match_id,))
    return cursor.fetchall()

@db_op()
def get_rankings(cursor, championship_id=None, season_id=None, event_type='Гол', is_assist=False):
    join_col = "me.assist_player_id" if is_assist else "me.player_id"

    query = f"""
                    SELECT 
                        p.full_name, 
                        p.photo_path, 
                        t.name as team_name,
                        COUNT(me.event_id) as total
                    FROM players p
                    JOIN match_events me ON {join_col} = p.player_id
                    JOIN matches m ON me.match_id = m.match_id
                    LEFT JOIN contracts c ON p.player_id = c.player_id 
                         AND m.match_date::date BETWEEN c.start_date AND COALESCE(c.end_date, '9999-12-31')
                    LEFT JOIN teams t ON c.team_id = t.team_id
                    WHERE me.event_type = %s
                """

    params = [event_type]
    if is_assist:
        query += " AND me.assist_player_id IS NOT NULL"

    if season_id:
        query += " AND m.season_id = %s"
        params.append(season_id)
    elif championship_id:
        query += " AND m.season_id IN (SELECT season_id FROM seasons WHERE championship_id = %s)"
        params.append(championship_id)

    query += """
                    GROUP BY p.player_id, p.full_name, p.photo_path, t.name
                    ORDER BY total DESC, p.full_name ASC
                    LIMIT 10
                """
    cursor.execute(query, tuple(params))
    return cursor.fetchall()

@db_op(commit=True)
def add_match_event(cursor, data):
    query = """
        INSERT INTO match_events (match_id, player_id, assist_player_id, event_type, minute)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        data["match_id"],
        data["player_id"],
        data.get("assist_player_id"),
        data["event_type"],
        data["minute"]
    ))
    return True

@db_op()
def get_players_for_match_team(cursor, match_id, team_id):
    query = """
        SELECT p.player_id, p.full_name
        FROM players p
        JOIN contracts c ON p.player_id = c.player_id
        JOIN matches m ON m.match_id = %s
        WHERE c.team_id = %s
          AND m.match_date::date BETWEEN c.start_date AND COALESCE(c.end_date, '9999-12-31')
        ORDER BY p.full_name;
    """
    cursor.execute(query, (match_id, team_id))
    return cursor.fetchall()

@db_op()
def get_match_events(cursor, match_id):
    query = """
        SELECT me.*, p.full_name as player_name, t.name as team_name
        FROM match_events me
        JOIN players p ON me.player_id = p.player_id
        JOIN teams t ON me.team_id = t.team_id
        WHERE me.match_id = %s
        ORDER BY me.minute;
    """
    cursor.execute(query, (match_id,))
    return cursor.fetchall()