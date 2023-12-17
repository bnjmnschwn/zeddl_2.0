import time
import datetime
import html
import app.helpers
import app.main.helpers
from flask import render_template, flash, redirect, url_for, jsonify, \
    current_app, g, request, session
from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from app import db, login
from config import Config
from sqlalchemy.sql import text
from app.main.forms import contact_form, login_form
from app.main.emails import send_email
from app.main import bp
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

class User(UserMixin):
    pass

@login.user_loader
def user_loader(username):
    sql = text('SELECT name FROM users')
    users = [item for item in db.session.execute(sql)]
    if username not in users:
        return

    user = User()
    user.id = username
    return user

@login.request_loader
def request_loader(request):
    sql = text('SELECT name FROM users')
    users = [item for item in db.session.execute(sql)]
    form = login_form()
    user = form.username.data
    if user not in users:
        return

    user = User()
    user.id = name
    return user

def get_users(username):
    sql = text('SELECT name, password_hash FROM users WHERE name = "'+username+'"')
    user_data = [item for item in db.session.execute(sql)]
    users = dict(user_data)
    return users

@bp.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.4f s" % (time.time() - g.request_start_time)
    g.current_year = datetime.date.today().year
    g.app_version = Config.APP_VERSION

@bp.route("/")
def index():
    # get todays birthdays
    birthdays = app.main.helpers.get_todays_birthdays()

    # get upcoming races
    upcoming_races = app.main.helpers.get_upcoming_races()

    # get todays races
    todays_races = app.main.helpers.get_todays_races(upcoming_races)

    return render_template("index.html", birthdays=birthdays, \
        upcoming_races=upcoming_races, todays_races=todays_races, \
        categories=Config.CATEGORIES)

@bp.route("/latest_results")
def latest_results():
    # create unique_race_ids list
    races = app.main.helpers.get_races()
    latest_results = app.helpers.get_race_results(races)
    return render_template("_latest_results.html", latest_results=latest_results)

@bp.route("/top10_rankings")
def top10_rankings():
    return render_template("_rankings_top10.html", categories=Config.CATEGORIES, \
        rankings=app.main.helpers.get_uci_rankings_top10())

@bp.route("/login", methods=["GET", "POST"])
def login():
    form = login_form()
    if request.method == "GET":
        return render_template("login.html", form=form)
    users = get_users(form.username.data)
    for k, v in users.items():
        username = k
        password = v
    if form.username.data == username and check_password_hash(password, form.password.data):
        user = User()
        user.id = username
        login_user(user, remember=True)
        flash("Welcome "+user.id+"!", "success")
        return redirect(url_for("main.index"))
    flash("Bad Login", "danger")
    return redirect(url_for("main.login"))

@bp.route("/logout")
def logout():
    logout_user()
    flash("Logged out", "success")
    return redirect(url_for("main.index"))

@bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = contact_form()
    if form.validate_on_submit():
        flash("Your message has been sent. Thanks for your message.", "success")
        send_email(form.subject.data, form.email.data, "hello@xcodata.com", \
            form.message.data)
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)

@bp.route("/legal")
def legal():
    return render_template("legal.html")

@bp.route("/faq")
def faq():
    sql = text('SELECT id, question, answer FROM faq')
    results = db.session.execute(sql)
    faq_dict = []
    for result in results:
        faq_dict.append({"id": result[0], "question": result[1], 
            "answer": html.unescape(result[2])})
    return render_template("faq.html", faq=faq_dict)

@bp.route("/about")
def about():
    return render_template("about.html")

@bp.route("/support")
def support():
    return render_template("support.html")

@bp.route("/search", methods=["GET", "POST"])
def search():
    if request.args.get("term"):
        term = request.args.get("term")
    if request.args.get("query"):
        term = request.args.get("query")

    rider_sql = text('SELECT last_name, first_name, nationality_iso, \
        seo_url, "rider" as type FROM riders \
        WHERE CONCAT(first_name, last_name) COLLATE UTF8_GENERAL_CI LIKE \
        REPLACE("%'+term+'%", " ", "%") LIMIT 3')
    riders = [item for item in db.session.execute(rider_sql)]

    races_sql = text('SELECT name, venue, country, id, class, date_start, \
        "race" as type FROM races WHERE CONCAT(name, venue) COLLATE \
        UTF8_GENERAL_CI LIKE REPLACE("%'+term+'%", " ", "%") \
        ORDER BY date_start DESC, \
        FIELD(class, "JO", "WCh", "WC", "CC", "HC", "NC", "C1", "C2", "C3") \
        LIMIT 3')
    races = [item for item in db.session.execute(races_sql)]
    
    team_sql = text('SELECT team_name, team_code, country, seo_url, \
        "team" as type FROM teams WHERE (team_name COLLATE UTF8_GENERAL_CI \
        LIKE REPLACE("%'+term+'%", " ", "%")) ORDER BY year DESC, \
        FIELD(category, "E-MTB", "MTB") LIMIT 3')
    teams = [item for item in db.session.execute(team_sql)]

    if request.args.get('query'):
        return render_template("_search_results.html", riders=riders, \
            races=races, teams=teams)
    return render_template("_search_hints.html", riders=riders, races=races, \
                teams=teams)
    