from app import app
from flask import render_template, request, send_file
from app.forms import SpaceForm
import sqlite3


def get_db_connection():
    conn = sqlite3.connect('zeddl.db')
    conn.row_factory = sqlite3.Row
    return conn

# PWA Stuff
@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')


@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')


# index + create space
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        name = request.form.get("spacename")
        conn = get_db_connection()
        conn.execute("INSERT INTO spaces (spacename) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return render_template("space_created.html", name=name)
        # redirect to new space
    else:
        form = SpaceForm()
        return render_template("index.html", form=form)


# space index
@app.route("/<slug>")
def shoppingspace(slug):
    form = SpaceForm()
    conn = get_db_connection()
    items = conn.execute("SELECT items.id, items.item, items.quantity FROM space_items \
        JOIN spaces ON space_items.space_id = spaces.id \
        JOIN items ON space_items.item_id = items.id \
        WHERE spaces.spacename = '{}'"
        .format(slug)).fetchall()
    return render_template("shoppinglist.html", form=form, items=items)


# add item
@app.route("/<slug>/add", methods=["POST"])
def add_item(slug):
        # add item to db and update view
    conn = get_db_connection()
    item = request.form.get("item")
    conn.execute("INSERT INTO items (item) VALUES (?)", (item,))
    conn.execute("INSERT INTO space_items (space_id, item_id) \
        SELECT (SELECT id FROM spaces WHERE spacename = '"+slug+"') AS space_id, \
        id AS item_id FROM items WHERE id = LAST_INSERT_ROWID();")
    conn.commit()
    items = conn.execute("SELECT items.id, items.item, items.quantity FROM space_items \
        JOIN spaces ON space_items.space_id = spaces.id \
        JOIN items ON space_items.item_id = items.id \
        WHERE spaces.spacename = '{}' ORDER BY items.id DESC LIMIT 1"
        .format(slug)).fetchall()
    return render_template("item.html", items=items)


# check item


# update items
@app.route("/<slug>/update/<id>", methods=["PUT"])
def update_item(slug, id):
    conn = get_db_connection()
    item = conn.execute("SELECT items.item, items.quantity FROM items WHERE items.id = '"+str(id)+"'")
    print(item)
    return "ok"
    # conn.execute("UPDATE ")

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


# delete item
@app.route("/<slug>/delete/<id>", methods=["DELETE"])
def delete_item(slug, id):
    conn = get_db_connection()
    conn.execute("DELETE FROM space_items WHERE item_id = "+str(id))
    conn.commit()
    return "", 200


# empty list
@app.route("/<slug>/delete/", methods=["DELETE"])
def clear_list(slug):
    conn = get_db_connection()
    conn.execute("DELETE FROM space_items \
        WHERE space_id = (SELECT space_id FROM spaces WHERE spacename = '"+slug+"')")
    conn.commit()
    items = conn.execute("SELECT items.id, items.item, items.quantity FROM space_items \
        JOIN spaces ON space_items.space_id = spaces.id \
        JOIN items ON space_items.item_id = items.id \
        WHERE spaces.spacename = '{}' ORDER BY items.id DESC"
        .format(slug)).fetchall()
    return render_template("item.html", items=items)