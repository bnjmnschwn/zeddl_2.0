from app import app, db
from flask import render_template, request, send_file, flash, redirect, url_for
from app.forms import SpaceForm
from config import Config
# from flask_sqlalchemy import text
import sqlite3
import unidecode
import json
import sys
import logging


logging.basicConfig(level="INFO", format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")


def get_items(slug):
    sql = db.text("SELECT items.id, items.item, space_items.quantity, space_items.info FROM space_items \
        JOIN spaces ON space_items.space_id = spaces.id \
        JOIN items ON space_items.item_id = items.id \
        WHERE spaces.spacename = :slug ORDER BY space_items.created ASC")
    items = [item for item in db.session.execute(sql, {"slug": slug})]
    db.session.commit()
    return items


def create_slug(name):
    return unidecode.unidecode(name).casefold().replace(' ', '-').replace('\'','')


# PWA Stuff
@app.route('/manifest.json')
def serve_manifest():
    manifest = {
        "name": "ZEDDL App",
        "short_name": "ZEDDL",
        "theme_color": "#000000",
        "background_color": "#FFFFFF",
        "display": "standalone",
        "orientation": "portrait",
        "scope": "/",
        "start_url": request.referrer,
        "icons": [
            {
                "src": "static/images/zeddl_icon.png",
                "sizes": "144x144",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "static/icons/zeddl_icon.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "static/icons/zeddl_icon.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }]
        }
    with open("app/manifest.json", "w") as outfile:
        json.dump(manifest, outfile)
    return send_file("manifest.json", mimetype="application/manifest+json")


@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')


# index + create space
@app.route("/", methods=["POST", "GET"])
def index():
    form = SpaceForm()
    if request.method == "POST":
        name = create_slug(request.form.get("spacename"))
        try:
            sql = db.text("INSERT INTO spaces (spacename) VALUES (:name)")
            db.session.execute(sql, {'name':name})
            db.session.commit()
        except db.exc.IntegrityError:
            error = {
                "title": "Einkaufszeddl existiert bereits",
                "message": "Wähle einen anderen Namen für deinen Einkaufszeddl."
            }
            db.session.rollback()
            return render_template("index.html", form=form, error=error)
        except Exception as e:
            logging.warning("An error occurred:", e)
            error = { 
                "title": "Fehler",
                "message": "Ein Fehler ist aufgetreten."
            }
            db.session.rollback()
            return render_template("index.html", form=form, error=error)
        return render_template("space_created.html", name=name)
    else:
        return render_template("index.html", form=form)


# space index
@app.route("/<slug>")
def shoppingspace(slug, **kwargs):
    if request.args.get("action"):
        flash("Link in die Zwischenablage kopiert.", "success")
    form = SpaceForm()
    items = get_items(slug)
    return render_template("shoppinglist.html", form=form, items=items)


# add item
@app.route("/<slug>/add", methods=["POST"])
def add_item(slug, **kwargs):
    # check whether input comes from suggestion or input field
    if request.args.get("suggestion"):
        item = request.args.get("suggestion")
    else:
        item = request.form.get("item")
    try:
        if item == "":
            sys.exit(1)
        else:
            sql = db.text("SELECT items.item FROM items WHERE items.item = :item")
            item_check = [i for i in db.session.execute(sql, {"item": item})]
            db.session.commit()
            if len(item_check) == 0: 
                sql = db.text("INSERT INTO items (item) VALUES (:item) RETURNING id")
                result = db.session.execute(sql, {"item": item})
                item_id = result.fetchone()[0]
                sql = db.text("INSERT INTO space_items (space_id, item_id, quantity, info) \
                    SELECT (SELECT id FROM spaces WHERE spacename = :slug) AS space_id, \
                    :last_item_id AS item_id, \
                    1 AS quantity, NULL AS info")
                db.session.execute(sql, {"slug": slug, "last_item_id": item_id})
                db.session.commit()
            else:
                sql = db.text("INSERT INTO space_items (space_id, item_id) \
                    SELECT (SELECT id FROM spaces WHERE spacename = :slug), \
                    (SELECT id FROM items WHERE item = :item)")
                db.session.execute(sql, {"slug": slug, "item": item})
                db.session.commit()
            flash(item+" hinzugefügt.", "success")
    except db.exc.IntegrityError as e:
        db.session.rollback()
        flash("Artikel ist bereits auf der Liste.", "warning")
    except SystemExit:
        db.session.rollback()
        flash("Überprüfe deine Eingabe.", "warning")
    except:
        db.session.rollback()
        flash("Fehler beim hinzufügen", "danger")
    finally:
        items = get_items(slug)
        return render_template("item.html", items=items)


# get suggestions
@app.route("/<slug>/search", methods=["POST"])
def get_suggestions(slug):
    value = request.form.get("item")
    if len(value) >= 3:        
        sql = db.text("SELECT items.item FROM items \
            WHERE LOWER(items.item) LIKE \
            LOWER(REPLACE('%'||:value||'%', ' ', '%')) LIMIT 5")
        suggestions = db.session.execute(sql, {"value": value})
        db.session.commit()
        return render_template("suggestions.html", suggestions=suggestions)
    else:
        return "", 200


# update items
@app.route("/<slug>/update/<id>", methods=["PUT"])
def update_item(slug, id):
    conn = get_db_connection()
    item = conn.execute("SELECT items.item, items.quantity FROM items WHERE items.id = '"+str(id)+"'")
    print(item)
    return "ok"


@app.route("/<slug>/update/<id>/quantity_add", methods=["PUT"])
def add_quantity(slug, id):
    item = "quantity_"+str(id)
    print(item)
    f = request.form
    for k in f.keys():
        print(k)
    # quantity = request.form.get(item)
    # print(quantity)
    # quantity = int(quantity)+1
    # conn = get_db_connection()
    # conn.execute("UPDATE items SET item.quantity = quantity WHERE items.id = '"+str(id)+"'")
    # conn.commit()
    return "", 200


# check & delete item
@app.route("/<slug>/delete/<id>/<action>", methods=["DELETE"])
def delete_item(slug, id, action):
    sql = db.text("DELETE FROM space_items WHERE item_id = :item_id AND space_id = (SELECT spaces.id FROM spaces WHERE spacename = :slug)")
    db.session.execute(sql, {"item_id": id, "slug": slug})
    db.session.commit()
    if action == "delete":
        flash("Artikel gelöscht.", "danger")
    # return "", 200
    items = get_items(slug)
    return render_template("item.html", items=items)


# empty list
@app.route("/<slug>/delete/", methods=["DELETE"])
def clear_list(slug):
    sql = db.text("DELETE FROM space_items \
        WHERE space_id = (SELECT spaces.id FROM spaces WHERE spacename = :slug)")
    db.session.execute(sql, {"slug": slug})
    db.session.commit()
    items = get_items(slug)
    flash("Einkaufszeddl geleert.", "danger")
    return render_template("item.html", items=items)