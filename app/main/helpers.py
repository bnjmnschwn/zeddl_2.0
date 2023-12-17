import html
import app.helpers
from sqlalchemy.sql import text
from app import db
from app.main import bp
from datetime import date

def get_races():
    # get races with latest results
    sql = text('SELECT DISTINCT(races.id), races.date_start, races.date_end, \
        races.name, races.venue, races.country, races.class as race_class, \
        races.competition_id \
     FROM races \
        JOIN events ON races.competition_id = events.competition_id \
        WHERE eventcode IN (SELECT DISTINCT(eventcode) FROM race_results) \
        ORDER BY races.date_end DESC, \
        FIELD(races.class, "JO", "WCh", "WC", "HC", "NC", "C1", "C2", "C3"), \
        races.date_start DESC \
        LIMIT 5')
    results = db.session.execute(sql)
    return results.mappings().all()

def get_uci_rankings_top10():
    '''
    gets UCI rankings top10 for latest date for every category 
    '''
    sql = text('SELECT rankings.rank, rankings.rank_diff, rankings.category, \
        rankings.nationality_iso, rankings.rider, rankings.points, \
        rankings.points_diff, riders.seo_url as slug FROM rankings \
        LEFT JOIN riders ON rankings.uci_id = riders.uci_id \
        WHERE ranking_date = (SELECT MAX(ranking_date) FROM rankings) \
        AND rankings.rank BETWEEN 1 AND 10 \
        ORDER BY rankings.category ASC, rankings.rank ASC')
    results = db.session.execute(sql)
    return results.mappings().all()

def get_todays_birthdays():
    '''
    gets riders who have a birthday today
    '''
    sql = text('SELECT last_name, first_name, birthday, nationality, \
        nationality_iso, seo_url FROM riders \
        WHERE DAY(birthday) = DAY(DATE(NOW())) \
        AND MONTH(birthday) = MONTH(DATE(NOW()))')
    results = db.session.execute(sql)
    return results.mappings().all()

def get_upcoming_races():
    '''
    gets upcoming races for next 7 days from database
    '''
    sql = text('SELECT * FROM races \
        WHERE date_start BETWEEN DATE(NOW()) AND ADDDATE(NOW(),+7) \
        ORDER BY date_start')
    results = db.session.execute(sql)
    return results.mappings().all()

def get_todays_races(races):
    '''
    gets todays races from database
    '''
    todays_races = []
    for race in races:
        if race["date_start"] == date.today():
            todays_races.append(race)
    return todays_races