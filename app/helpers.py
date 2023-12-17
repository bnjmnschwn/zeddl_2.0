import html
import datetime
import os
from app import db
from app.rankings import bp
from app.main import bp
from flask_sqlalchemy import Pagination
from config import Config
from sqlalchemy import text
import logging

@bp.app_context_processor
def utility_processor():
    '''
    this class inherits other classes.
    classes defined in the context processor are available in jinja2
    '''
    def points_diff(points):
        '''
        styles the difference in points for rankings
        '''
        if points != None and points < 0:
            return html.unescape(
                "<small class='text-danger fw-light'>- " \
                + str(abs(points)) +"</small>")
        elif points != None and points > 0:
            return html.unescape(
                "<small class='fw-light' style='color: #198754'>+ " \
                + str(abs(points)) +"</small>")
        else:
            return "&nbsp;";

    def rank_diff(rank):
        '''
        styles the difference in ranks for rankings
        '''
        if rank != None and rank < 0:
            return html.unescape(
                "<small class='text-danger fw-light'>\
                <i class='fas fa-caret-down'></i> "+ str(abs(rank)) +"</small>")
        elif rank != None and rank > 0:
            return html.unescape(
                "<small class='fw-light' style='color: #198754'>\
                <i class='fas fa-caret-up'></i> "+ str(abs(rank)) +"</small>")
        else:
            return "&nbsp;";

    def calculate_age(birthdate):
        '''
        calculate age from birthday
        '''
        if birthdate == None:
            return "-" 
        else:
            today = datetime.date.today()
        return today.year - birthdate.year - ((today.month, today.day) <
             (birthdate.month, birthdate.day)) 

    def results_time_format(result_in_seconds):
        if result_in_seconds/3600 < 1:
            minutes = result_in_seconds/60%60
            seconds = result_in_seconds%60
            return "%02d:%02d" % (minutes, seconds) 
        else:
            hours = result_in_seconds/3600
            minutes = result_in_seconds/60%60
            seconds = result_in_seconds%60
            return "%1d:%02d:%02d" % (hours, minutes, seconds)

    def display_rank(rank):
        if rank == 1:
            bg_color = "#ffd700"
        elif rank == 2:
            bg_color = "#c0c0c0"
        elif rank == 3:
            bg_color = "#cd7f32"
        else: 
            return rank
        return '<div class="circle" style="background-color: {}; \
            display: inline-block;">{}</div>'.format(bg_color, rank)

    def add_ordinal_number_suffix(num):
        if num % 100 not in [11, 12, 13]:
            if num % 10 == 1:
                return str(num) + 'st'
            elif num % 10 == 2:
                return str(num) + 'nd'
            elif num % 10 == 3:
                return str(num) + 'rd'
        return str(num) + 'th'

    def format_date(date_start, date_end):
        if date_start == date_end:
            return date_start.strftime("%d %b %Y")
        elif date_start.month == date_end.month:
            return date_start.strftime("%d")+" - "+date_end.strftime("%d %b %Y")
        else:
            return date_start.strftime("%d %b")+" - "+date_end.strftime("%d %b %Y")

    return dict(points_diff=points_diff, rank_diff=rank_diff, \
        calculate_age=calculate_age, results_time_format=results_time_format, \
        display_rank=display_rank, \
        ordinal_number_suffix=add_ordinal_number_suffix, format_date=format_date)

def path_exists(path):
    print(path)
    if os.path.exists(path):
        print("yes")
    else:
        print("no")
    return os.path.exists(path)

def remove_empty_keys(dictionary):
    '''
    removes keys with no value from dictionaries
    '''
    if isinstance(dictionary, dict):
        for key, value in dictionary.copy().items():
            if isinstance(value, dict):
                remove_empty_keys(value)
            if not value:
                del(dictionary[key])

def paginate(query, page):
    rows = db.session.execute(query).fetchall()[0][0]
    if page == None:
        page = 1
    else:
        page = page
    total_pages = round_up(rows, Config.ITEMS_PER_PAGE)
    current_page = page
    offset = (int(page) - 1) * int(Config.ITEMS_PER_PAGE)
    return rows, total_pages, current_page, offset

def round_up(number, denominator):
    return (number // denominator) + (number % denominator > 0)

def get_race_results(races):
    '''
    gets list of 5 latest races with results
    creates a dictionary with all information regarding a race incl. results
    --> future API?
    '''
    races = races
    race_results_dict = {"races": []}

    for race in races:
        # get results for these races
        sql = text('SELECT events.*, race_results.*, riders.seo_url, \
            race_results.nationality_ioc \
            FROM events \
            JOIN race_results ON events.eventcode = race_results.eventcode \
            LEFT JOIN riders ON race_results.uci_id = riders.uci_id \
            WHERE events.competition_id = "'+ str(race.competition_id) +'" \
            AND race_results.rank BETWEEN 1 AND 3 \
            ORDER BY events.category ASC, race_results.rank ASC')
        results = [item for item in db.session.execute(sql)]
        xco_me = []
        xco_we = []
        xco_mj = []
        xco_wj = []
        xcc_me = []
        xcc_we = []
        for result in results:
            if (result.racetype == "XCO" and result.category == "ME"):
                xco_me.append({
                    "rank": result.rank,
                    "last_name": result.last_name,
                    "first_name": result.first_name,
                    "seo_url": result.seo_url,
                    "nationality": result.nationality_ioc
                    })
            if (result.racetype == "XCO" and result.category == "WE"):
                xco_we.append({
                    "rank": result.rank,
                    "last_name": result.last_name,
                    "first_name": result.first_name,
                    "seo_url": result.seo_url,
                    "nationality": result.nationality_ioc
                    })
            if (result.racetype == "XCO" and result.category == "MJ"):
                xco_mj.append({
                    "rank": result.rank,
                    "last_name": result.last_name,
                    "first_name": result.first_name,
                    "seo_url": result.seo_url,
                    "nationality": result.nationality_ioc
                    })
            if (result.racetype == "XCO" and result.category == "WJ"):
                xco_wj.append({
                    "rank": result.rank,
                    "last_name": result.last_name,
                    "first_name": result.first_name,
                    "seo_url": result.seo_url,
                    "nationality": result.nationality_ioc
                    })
            if (result.racetype == "XCC" and result.category == "ME"):
                xcc_me.append({
                    "rank": result.rank,
                    "last_name": result.last_name,
                    "first_name": result.first_name,
                    "seo_url": result.seo_url,
                    "nationality": result.nationality_ioc
                    })
            if (result.racetype == "XCC" and result.category == "WE"):
                xcc_we.append({
                    "rank": result.rank,
                    "last_name": result.last_name,
                    "first_name": result.first_name,
                    "seo_url": result.seo_url,
                    "nationality": result.nationality_ioc
                    })
        # create latest_results dict
        race_results_dict["races"].append(
            {
            "race_id": race.id,
            "race_details": {
                "name": race.name,
                "venue": race.venue,
                "country": race.country,
                "race_class": race.race_class,
                "date_start": race.date_start,
                "date_end": race.date_end
                },
            "results": {
                "XCO_ME": xco_me,
                "XCO_WE": xco_we,
                "XCO_MJ": xco_mj,
                "XCO_WJ": xco_wj,
                "XCC_ME": xcc_me,
                "XCC_WE": xcc_we
                }
            })
    # remove empty result dicts
    for i in range(0, len(race_results_dict["races"])):
        remove_empty_keys(race_results_dict["races"][i]["results"])
    return race_results_dict