from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta
import csv
import requests
import random

app = Flask(__name__,template_folder='templates')




def yesterday(frmt='%Y-%m-%d', string=True):
    yesterday = datetime.now() - timedelta(1)
    if string:
        return yesterday.strftime(frmt)
    return yesterday
date = yesterday()

def next_day(start_date,frmt='%Y-%m-%d', string=True):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, frmt)
    
    next_day = start_date + timedelta(1)
    if string:
        return next_day.strftime(frmt)
    return next_day

def get_highlight_url(game_id, event_id):
    headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true',
        'Connection': 'keep-alive',
        'Referer': 'https://stats.nba.com/',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    url = 'https://stats.nba.com/stats/videoeventsasset?GameEventID={}&GameID={}'.format(
                event_id, game_id)
    r = requests.get(url, headers=headers)
    json = r.json()
    video_urls = json['resultSets']['Meta']['videoUrls']
    playlist = json['resultSets']['playlist']
    video_event = {'video': video_urls[0]['lurl'], 'desc': playlist[0]['dsc']}
    return (video_event['video'],video_event['desc'])

@app.route('/')
def index():

    return render_template('index.html',date=date,yesterday=yesterday)

@app.route('/makes/')
def return_makes():
    players= request.args.get('players','')
    team_ids = '(1610612737, 1610612751, 1610612738, 1610612766, 1610612739,1610612741, 1610612742, 1610612743, 1610612765, 1610612744,1610612745, 1610612754, 1610612746, 1610612747, 1610612763,1610612748, 1610612749, 1610612750, 1610612752, 1610612740,1610612760, 1610612753, 1610612755, 1610612756, 1610612757,1610612759, 1610612758, 1610612761, 1610612762, 1610612764)'
    if players == 'all':
        players = ' '
    if players == 'heat':
        team_ids = '(1610612748)'
        players = ' '
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    

    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = next_day(start_date)

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    players_list = players.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('data/heat.db')
    cursor = conn.cursor()
    # Execute SQL query
    for p in players_list:
        p = p.strip()
        cursor.execute(f"""
                        SELECT game_id,eventnum
                        FROM heat_pbp
                        Where eventmsgtype = 1 
                       and player1_name LIKE '%{p}%' and date >= '{start_date}' and date <='{end_date}' and player1_team_id in {team_ids}
                        ORDER BY player1_name, date desc
                        """
                        )
        
        plays = cursor.fetchall()
        for i in plays:
            print(f'LOOK HERE!!  {i[0]},{i[1]}')
            highlights.append(get_highlight_url(f'00{i[0]}',str(i[1])))
            
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_makes.html', highlights=highlights, start_date=start_date,end_date=end_date,players=players)

@app.route('/search_makes/')
def search_makes():
    players = request.args.get('players', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_makes.html', players=players, end_date=end_date, start_date=start_date)


@app.route('/dunks/')
def return_dunks():
    players= request.args.get('players','')
    team_ids = '(1610612737, 1610612751, 1610612738, 1610612766, 1610612739,1610612741, 1610612742, 1610612743, 1610612765, 1610612744,1610612745, 1610612754, 1610612746, 1610612747, 1610612763,1610612748, 1610612749, 1610612750, 1610612752, 1610612740,1610612760, 1610612753, 1610612755, 1610612756, 1610612757,1610612759, 1610612758, 1610612761, 1610612762, 1610612764)'
    if players == 'all':
        players = ' '
    if players == 'heat':
        team_ids = '(1610612748)'
        players = ' '
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    

    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = next_day(start_date)

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    players_list = players.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('data/heat.db')
    cursor = conn.cursor()
    # Execute SQL query
    for p in players_list:
        p = p.strip()
        cursor.execute(f"""
                        SELECT game_id,eventnum
                        FROM heat_pbp
                        Where eventmsgtype = 1 
                       and player1_name LIKE '%{p}%' and date >= '{start_date}' and date <='{end_date}' and player1_team_id in {team_ids} 
                       and (HOMEDESCRIPTION LIKE '%dunk%' or VISITORDESCRIPTION LIKE '%dunk%')
                        ORDER BY player1_name, date desc
                        """
                        )
        
        plays = cursor.fetchall()
        for i in plays:
            highlights.append(get_highlight_url(f'00{i[0]}',str(i[1])))
            
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_dunks.html', highlights=highlights, start_date=start_date,end_date=end_date,players=players)

@app.route('/search_dunks/')
def search_dunks():
    players = request.args.get('players', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_dunks.html', players=players, end_date=end_date, start_date=start_date)

@app.route('/threes/')
def return_threes():
    players= request.args.get('players','')
    team_ids = '(1610612737, 1610612751, 1610612738, 1610612766, 1610612739,1610612741, 1610612742, 1610612743, 1610612765, 1610612744,1610612745, 1610612754, 1610612746, 1610612747, 1610612763,1610612748, 1610612749, 1610612750, 1610612752, 1610612740,1610612760, 1610612753, 1610612755, 1610612756, 1610612757,1610612759, 1610612758, 1610612761, 1610612762, 1610612764)'
    if players == 'all':
        players = ' '
    if players == 'heat':
        team_ids = '(1610612748)'
        players = ' '
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    

    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = next_day(start_date)

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    players_list = players.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('data/heat.db')
    cursor = conn.cursor()
    # Execute SQL query
    for p in players_list:
        p = p.strip()
        cursor.execute(f"""
                        SELECT game_id,eventnum
                        FROM heat_pbp
                        Where eventmsgtype = 1 
                       and player1_name LIKE '%{p}%' and date >= '{start_date}' and date <='{end_date}' and player1_team_id in {team_ids}
                           and (HOMEDESCRIPTION LIKE '%3PT%' or VISITORDESCRIPTION LIKE '%3PT%')
                        ORDER BY player1_name, date desc
                        """
                        )
        
        plays = cursor.fetchall()
        for i in plays:
            highlights.append(get_highlight_url(f'00{i[0]}',str(i[1])))
            
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_threes.html', highlights=highlights, start_date=start_date,end_date=end_date,players=players)

@app.route('/search_threes/')
def search_threes():
    players = request.args.get('players', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_threes.html', players=players, end_date=end_date, start_date=start_date)

@app.route('/oops/')
def return_oops():
    players= request.args.get('players','')
    team_ids = '(1610612737, 1610612751, 1610612738, 1610612766, 1610612739,1610612741, 1610612742, 1610612743, 1610612765, 1610612744,1610612745, 1610612754, 1610612746, 1610612747, 1610612763,1610612748, 1610612749, 1610612750, 1610612752, 1610612740,1610612760, 1610612753, 1610612755, 1610612756, 1610612757,1610612759, 1610612758, 1610612761, 1610612762, 1610612764)'
    if players == 'all':
        players = ' '
    if players == 'heat':
        team_ids = '(1610612748)'
        players = ' '
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    

    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = next_day(start_date)

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    players_list = players.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('data/heat.db')
    cursor = conn.cursor()
    # Execute SQL query
    for p in players_list:
        p = p.strip()
        cursor.execute(f"""
                        SELECT game_id,eventnum
                        FROM heat_pbp
                        Where eventmsgtype = 1 
                       and (player1_name LIKE '%{p}%' or player2_name LIKE '%{p}%') and date >= '{start_date}' and date <='{end_date}' and player1_team_id in {team_ids}
                        and (HOMEDESCRIPTION LIKE '%alley oop%' or VISITORDESCRIPTION LIKE '%alley oop%')
                        ORDER BY player1_name, date desc
                        """
                        )
        
        plays = cursor.fetchall()
        for i in plays:
            highlights.append(get_highlight_url(f'00{i[0]}',str(i[1])))
            
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_oops.html', highlights=highlights, start_date=start_date,end_date=end_date,players=players)

@app.route('/search_oops/')
def search_oops():
    players = request.args.get('players', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_oops.html', players=players, end_date=end_date, start_date=start_date)

@app.route('/assists/')
def return_assists():
    players= request.args.get('players','')
    team_ids = '(1610612737, 1610612751, 1610612738, 1610612766, 1610612739,1610612741, 1610612742, 1610612743, 1610612765, 1610612744,1610612745, 1610612754, 1610612746, 1610612747, 1610612763,1610612748, 1610612749, 1610612750, 1610612752, 1610612740,1610612760, 1610612753, 1610612755, 1610612756, 1610612757,1610612759, 1610612758, 1610612761, 1610612762, 1610612764)'
    if players == 'all':
        players = ' '
    if players == 'heat':
        team_ids = '(1610612748)'
        players = ' '
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    

    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = next_day(start_date)

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    players_list = players.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('data/heat.db')
    cursor = conn.cursor()
    # Execute SQL query
    for p in players_list:
        p = p.strip()
        cursor.execute(f"""
                        SELECT game_id,eventnum
                        FROM heat_pbp
                        Where eventmsgtype = 1 
                       and player2_name LIKE '%{p}%' and date >= '{start_date}' and date <='{end_date}' and player1_team_id in {team_ids}
                        and (HOMEDESCRIPTION LIKE '%AST%' or VISITORDESCRIPTION LIKE '%AST%')
                        ORDER BY player2_name, date desc
                        """
                        )
        
        plays = cursor.fetchall()
        for i in plays:
            highlights.append(get_highlight_url(f'00{i[0]}',str(i[1])))
            
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_assists.html', highlights=highlights, start_date=start_date,end_date=end_date,players=players)

@app.route('/search_assists/')
def search_assists():
    players = request.args.get('players', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_assists.html', players=players, end_date=end_date, start_date=start_date)

@app.route('/blocks/')
def return_blocks():
    players= request.args.get('players','')
    team_ids = '(1610612737, 1610612751, 1610612738, 1610612766, 1610612739,1610612741, 1610612742, 1610612743, 1610612765, 1610612744,1610612745, 1610612754, 1610612746, 1610612747, 1610612763,1610612748, 1610612749, 1610612750, 1610612752, 1610612740,1610612760, 1610612753, 1610612755, 1610612756, 1610612757,1610612759, 1610612758, 1610612761, 1610612762, 1610612764)'
    if players == 'all':
        players = ' '
    if players == 'heat':
        team_ids = '(1610612748)'
        players = ' '
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    

    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = next_day(start_date)

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    players_list = players.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('data/heat.db')
    cursor = conn.cursor()
    # Execute SQL query
    for p in players_list:
        p = p.strip()
        cursor.execute(f"""
                        SELECT game_id,eventnum
                        FROM heat_pbp
                        Where eventmsgtype = 2 
                       and player3_name LIKE '%{p}%' and date >= '{start_date}' and date <='{end_date}' and player3_team_id in {team_ids}
                        and (HOMEDESCRIPTION LIKE '%BLOCK%' or VISITORDESCRIPTION LIKE '%BLOCK%')
                        ORDER BY player3_name, date desc
                        """
                        )
        
        plays = cursor.fetchall()
        for i in plays:
            highlights.append(get_highlight_url(f'00{i[0]}',str(i[1])))
            
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_blocks.html', highlights=highlights, start_date=start_date,end_date=end_date,players=players)

@app.route('/search_blocks/')
def search_blocks():
    players = request.args.get('players', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_blocks.html', players=players, end_date=end_date, start_date=start_date)

@app.route('/steals/')
def return_steals():
    players= request.args.get('players','')
    team_ids = '(1610612737, 1610612751, 1610612738, 1610612766, 1610612739,1610612741, 1610612742, 1610612743, 1610612765, 1610612744,1610612745, 1610612754, 1610612746, 1610612747, 1610612763,1610612748, 1610612749, 1610612750, 1610612752, 1610612740,1610612760, 1610612753, 1610612755, 1610612756, 1610612757,1610612759, 1610612758, 1610612761, 1610612762, 1610612764)'
    if players == 'all':
        players = ' '
    if players == 'heat':
        team_ids = '(1610612748)'
        players = ' '
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    

    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = next_day(start_date)

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    players_list = players.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('data/heat.db')
    cursor = conn.cursor()
    # Execute SQL query
    for p in players_list:
        p = p.strip()
        cursor.execute(f"""
                        SELECT game_id,eventnum
                        FROM heat_pbp
                        Where eventmsgtype = 5 
                       and player2_name LIKE '%{p}%' and date >= '{start_date}' and date <='{end_date}' and player2_team_id in {team_ids}
                       and (HOMEDESCRIPTION LIKE '%STEAL%' or VISITORDESCRIPTION LIKE '%STEAL%')
                         ORDER BY player2_name, date desc
                        """
                        )
        
        plays = cursor.fetchall()
        for i in plays:
            highlights.append(get_highlight_url(f'00{i[0]}',str(i[1])))
            
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_steals.html', highlights=highlights, start_date=start_date,end_date=end_date,players=players)

@app.route('/search_steals/')
def search_steals():
    players = request.args.get('players', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_steals.html', players=players, end_date=end_date, start_date=start_date)

@app.route('/keyword/')
def return_keyword():
    keywords= request.args.get('keywords','')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    
    
    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = next_day(start_date)

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    keywords_list = keywords.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('MLB_Highlights.db')
    cursor = conn.cursor()
    # Execute SQL query
    for k in keywords_list:
        k = k.strip()
        cursor.execute(f"""
                        SELECT player_name,date,headline,description,mp4_url,yahoo_team_name,mlb_team_name
                        FROM yahoo_highlights_{season_id}
                        Where description LIKE '%{k}%' and date >= '{start_date}' and date <='{end_date}'
                        ORDER BY date desc, player_name
                        """
                        )
        
        keyword = cursor.fetchall()
        for i in keyword:
            highlights.append(i)
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_keyword.html', highlights=highlights, start_date=start_date,end_date=end_date,keywords=keywords)

@app.route('/search_keyword/')
def search_keyword():
    keywords = request.args.get('keywords', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_keyword.html', keywords=keywords, end_date=end_date, start_date=start_date)


if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0')
