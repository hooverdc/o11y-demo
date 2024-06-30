import flask


from pydantic import BaseModel

import sqlite3
from flask import g, request

# look ma no obvious tracing

DATABASE = "db.sqlite"


app = flask.Flask(__name__)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # give us dicts!
        db.row_factory = sqlite3.Row
        # setup
    return db


# setup db
with app.app_context():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            text VARCHAR,
            status BOOLEAN
        );
        CREATE TABLE IF NOT EXISTS list_items (
            list_id INTEGER,
            item_id INTEGER
        );
        CREATE TABLE IF NOT EXISTS lists (
            id INTEGER PRIMARY KEY,
            name VARCHAR
        );
        """
    )
    db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


class TodoItem(BaseModel):
    id: int
    text: str
    status: bool


@app.route("/api/v1/items", methods=["GET"])
def list():
    cur = get_db().cursor()
    items = []
    for item in cur.execute("SELECT id, text, status FROM items"):
        items.append(TodoItem(**item))
    return flask.jsonify({"items": [todo.model_dump() for todo in items]})


@app.route("/api/v1/item", methods=["POST"])
def create():
    todo = TodoItem(**request.json)  # type: ignore
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO items (text, status) VALUES (:text, :status)",
        {
            "text": todo.text,
            "status": todo.status,
        },
    )
    db.commit()
    return flask.jsonify(todo.model_dump())


@app.route("/api/v1/item", methods=["PUT"])
def update():
    todo = TodoItem(**request.json)  # type: ignore
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE items SET text = :text, status = :status WHERE id = :id",
        todo.model_dump(),
    )
    db.commit()
    return flask.jsonify(todo.model_dump())


@app.route("/api/v1/todo/<id>", methods=["DELETE"])
def delete(id: str):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM items WHERE id = :id", {"id": id})
    db.commit()
    return flask.jsonify(), 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
