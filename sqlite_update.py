import sqlite3
import pandas as pd
import shutil

database_filepath = r'D:\Documents\GFA\SportsPython\Basketball\dadbirthday2024\data\heat.db'

def update_sqlite():
    game_info_df = pd.read_csv(r'D:\Documents\GFA\SportsPython\Basketball\dadbirthday2024\data\heat_game_info_2023.csv')
    play_by_play_df = pd.read_csv(r'D:\Documents\GFA\SportsPython\Basketball\dadbirthday2024\data\heat_play_by_play_2023.csv')
    teams_df = pd.read_csv(r'D:\Documents\GFA\SportsPython\Basketball\dadbirthday2024\data\team_ids.csv')

    conn = sqlite3.connect(database_filepath)
    game_info_df.to_sql(f'game_info', conn, if_exists='replace')
    play_by_play_df.to_sql(f'play_by_play', conn, if_exists='replace')
    teams_df.to_sql(f'teams', conn, if_exists='replace')
    conn.close()
    print(f"{database_filepath} was updated")

def update_final_table():
    conn = sqlite3.connect(database_filepath)
    cur = conn.cursor()
    res = cur.execute(f"""
                    with source as 
                        (select p.*,g.date,g.home_id,g.visitor_id
                        from play_by_play as p
                        LEFT join game_info as g on g.game_id = p.game_id)

                    select s.*, th.team_name as home_name, ta.team_name as visitor_name
                    from source as s
                    left join teams as th on s.home_id = th.team_id
                    left join teams as ta on s.visitor_id = ta.team_id
                    """)
    data = res.fetchall()
    data = [row[1:]for row in data]
    print(f'DATA TYPE IS {type(data[0][1])}')


    cur.close()

    cur=conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS heat_pbp")
    cur.execute(f"""
                CREATE TABLE IF NOT EXISTS heat_pbp (
                game_id STRING,
                eventnum INTEGER,
                eventmsgtype INTEGER,
                eventmsgactiontype INTEGER,
                period INTEGER,
                wctimestring STRING,
                pctimestring STRING,
                homedescription STRING,
                neutraldescription STRING,
                visitordescription STRING,
                score STRING,
                scoremargin INTEGER,
                person1type INTEGER,
                player1_id INTEGER,
                player1_name STRING,
                player1_team_id INTEGER,
                player1_team_city STRING,
                player1_team_nickname STRING,
                player1_team_abbreviation STRING,
                person2type INTEGER,
                player2_id INTEGER,
                player2_name STRING,
                player2_team_id INTEGER,
                player2_team_city STRING,
                player2_team_nickname STRING,
                player2_team_abbreviation STRING,
                person3type INTEGER,
                player3_id INTEGER,
                player3_name STRING,
                player3_team_id INTEGER,
                player3_team_city STRING,
                player3_team_nickname STRING,
                player3_team_abbreviation STRING,
                video_available_flag INTEGER,
                date DATETIME,
                home_id INTEGER,
                visitor_id INTEGER,
                home_name STRING,
                visitor_name STRING
            )
    """)

    cur.executemany(f"INSERT INTO heat_pbp VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",data)
    print(f"heat_pbp was updated")
    conn.commit()
    conn.close()


update_sqlite()
update_final_table()