from flask import Flask, render_template, request, redirect, send_from_directory, url_for
import sqlite3
import csv
import os

app = Flask(__name__)
CSV_FILE = "albums.csv"
FIELDNAMES = ["id", "artist", "title", "year", "cover", "rating"]
DB_FILE = "albums.db"


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


# def read_albums():
#     albums = []
#     if os.path.exists(CSV_FILE):
#         with open(CSV_FILE, newline="", encoding="utf-8") as f:
#             reader = csv.DictReader(f)
#             albums = list(reader)
#     return albums


# def write_albums(albums):
#     with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
#         writer.writeheader()
#         writer.writerows(albums)


def next_id(albums):
    if not albums:
        return "1"
    return str(max(int(a["id"]) for a in albums) + 1)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/albums")
def getAlbums():
    conn = get_db()
    albums = conn.execute("SELECT * FROM albums ORDER BY year DESC").fetchall()
    songs = conn.execute("SELECT * FROM favorite_songs").fetchall()
    conn.close()
    return render_template("_albums.html", albums=albums, songs=songs)

@app.route("/favorite/<int:album_id>", methods=["POST"])
def add_favorite(album_id):
    conn = get_db()
    song_title = request.form["song_title"]
    conn.execute(
        "INSERT INTO favorite_songs (album_id, song_title) VALUES (?, ?)",
        (album_id, song_title),
    )
    conn.commit()
    song = conn.execute("SELECT * FROM favorite_songs ORDER BY id DESC LIMIT 1;").fetchone()
    conn.close()
    return f"<li>{song['song_title']}</li>"


@app.route("/form")
def create_form():
    return render_template("_form.html", album=None, action="/create")


@app.route("/form/<int:id>")
def edit_form(id):
    conn = get_db()
    album = conn.execute(
        "SELECT * FROM albums WHERE id = ?",
        (id,)
    ).fetchone()
    conn.close()
    return render_template("_form.html", album=album, action=f"/edit/{id}")


@app.route("/create", methods=["POST"])
def create():
    if request.method == "POST":
        conn = get_db()
        conn.execute(
            "INSERT INTO albums (artist, title, year, cover, rating) VALUES (?, ?, ?, ?, ?)",
            (
                request.form["artist"],
                request.form["title"],
                request.form["year"],
                request.form["cover"],
                request.form["rating"],
            ),
        )
        conn.commit()

        album = conn.execute("SELECT * FROM albums ORDER BY id DESC LIMIT 1;").fetchone()
    conn.close()

    return render_template("_album_card.html", album=album)


@app.route("/edit/<id>", methods=["POST"])
def edit(id):
    conn = get_db()

    if request.method == "POST":
        conn.execute(
            """UPDATE albums
               SET artist=?, title=?, year=?, cover=?, rating=?
               WHERE id=?""",
            (
                request.form["artist"],
                request.form["title"],
                request.form["year"],
                request.form["cover"],
                request.form["rating"],
                id,
            ),
        )
        conn.commit()

    album = conn.execute("SELECT * FROM albums WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("_album_card.html", album=album)


@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM albums WHERE id=?", (id,))
    conn.commit()
    albums = conn.execute("SELECT * FROM albums ORDER BY year DESC").fetchall()
    conn.close()
    return render_template("_albums.html", albums=albums)


if __name__ == "__main__":
    init_db()
    app.run(debug=True,host="0.0.0.0")
