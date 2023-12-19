from app import app
from flask import render_template, request, send_file, flash, redirect, url_for
from app.forms import SpaceForm
import sqlite3
import unidecode
import json

def get_db_connection():
    conn = sqlite3.connect('zeddl.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_items(slug):
    conn = get_db_connection()
    items = conn.execute("SELECT items.id, items.item, space_items.quantity, space_items.info FROM space_items \
        JOIN spaces ON space_items.space_id = spaces.id \
        JOIN items ON space_items.item_id = items.id \
        WHERE spaces.spacename = '{}' ORDER BY items.created ASC"
        .format(slug)).fetchall()
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
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO spaces (spacename) VALUES (?)", (name,))
            conn.commit()
        except:
            error = {
                "title": "Einkaufszeddl existiert bereits",
                "message": "Wähle einen anderen Namen für deinen Einkaufszeddl."
            }
            return render_template("index.html", form=form, error=error)
        conn.close()
        return render_template("space_created.html", name=name)
    else:
        return render_template("index.html", form=form)


# space index
@app.route("/<slug>")
def shoppingspace(slug):
    form = SpaceForm()
    items = get_items(slug)
    return render_template("shoppinglist.html", form=form, items=items)


# add item
@app.route("/<slug>/add", methods=["POST"])
def add_item(slug, **kwargs):
    conn = get_db_connection()
    # check whether input comes from suggestion or input field
    if request.args.get("suggestion"):
        item = request.args.get("suggestion")
    else:
        item = request.form.get("item")
    try:
        item_check = conn.execute("SELECT items.item FROM items WHERE items.item = '"+item+"'").fetchall()
        conn.commit()
        if len(item_check) == 0: 
            conn.execute("INSERT INTO items (item) VALUES (?)", (item,))
            conn.execute("INSERT INTO space_items (space_id, item_id, quantity, info) \
                SELECT (SELECT id FROM spaces WHERE spacename = '"+slug+"') AS space_id, \
                (SELECT id FROM items WHERE id = LAST_INSERT_ROWID()) AS item_id, \
                1 AS quantity, NULL AS info")
            conn.commit()
        else:
            conn.execute("INSERT INTO space_items (space_id, item_id) \
                SELECT (SELECT id FROM spaces WHERE spacename = '"+slug+"'), \
                (SELECT id FROM items WHERE item = '"+item+"')")
            conn.commit()
        flash(item+" hinzugefügt.", "success")
    except sqlite3.IntegrityError as e:
        flash("Artikel bereits auf der Liste.", "warning")
    except:
        flash("Fehler beim hinzufügen", "danger")
    finally:
        items = get_items(slug)
        conn.close()
        return render_template("item.html", items=items)


# get suggestions
@app.route("/<slug>/search", methods=["POST"])
def get_suggestions(slug):
    value = request.form.get("item")
    if len(value) >= 3:        
        conn = get_db_connection()
        suggestions = conn.execute("SELECT items.item FROM items \
            WHERE item COLLATE UTF8_GENERAL_CI LIKE \
            REPLACE('%"+value+"%', ' ', '%') LIMIT 5").fetchall()
        conn.commit()
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
    conn = get_db_connection()
    conn.execute("DELETE FROM space_items WHERE item_id = "+str(id)+" AND space_id = (SELECT spaces.id FROM spaces WHERE spacename = '"+str(slug)+"')")
    conn.commit()
    if action == "delete":
        flash("Artikel gelöscht.", "danger")
    # return "", 200
    items = get_items(slug)
    return render_template("item.html", items=items)


# empty list
@app.route("/<slug>/delete/", methods=["DELETE"])
def clear_list(slug):
    conn = get_db_connection()
    conn.execute("DELETE FROM space_items \
        WHERE space_id = (SELECT spaces.id FROM spaces WHERE spacename = '"+str(slug)+"')")
    conn.commit()
    items = get_items(slug)
    flash("Einkaufszeddl geleert.", "danger")
    return render_template("item.html", items=items)