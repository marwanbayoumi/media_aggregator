from flask import Flask, render_template, request, redirect, send_from_directory, url_for
import sqlite3
import os
from metadata import fetch_album_metadata

app = Flask(__name__)
FIELDNAMES = ["id", "artist", "title", "year", "cover", "rating"]
DB_FILE = "albums.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

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
    sort = request.args.get('sort', 'year_desc')
    min_rating = request.args.get('min_rating', 0, type=int)
    
    order_clause = "year DESC"
    if sort == 'year_asc':
        order_clause = "year ASC"
    elif sort == 'artist_asc':
        order_clause = "artist ASC"
    elif sort == 'title_asc':
        order_clause = "title ASC"
    elif sort == 'rating_desc':
        order_clause = "rating DESC"

    conn = get_db()
    query = "SELECT * FROM albums WHERE rating >= ? ORDER BY " + order_clause
    albums = conn.execute(query, (min_rating,)).fetchall()
    songs = conn.execute("SELECT * FROM favorite_songs").fetchall()
    conn.close()
    return render_template("_albums.html", albums=albums, songs=songs)

@app.route("/favorite/<int:album_id>", methods=["POST"])
def add_favorite(album_id):
    conn = get_db()
    track_title = request.form["track_title"]
    conn.execute(
        "INSERT INTO favorite_songs (album_id, track_title) VALUES (?, ?)",
        (album_id, track_title),
    )
    conn.commit()
    song = conn.execute("SELECT * FROM favorite_songs ORDER BY id DESC LIMIT 1;").fetchone()
    conn.close()
    return f"<li>{song['track_title']}</li>"


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

        # Fetch tracks and runtime metadata dynamically
        fetch_album_metadata(album['id'], album['artist'], album['title'])

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

@app.route("/album/<int:id>/populate", methods=["POST"])
def populate_metadata(id):
    conn = get_db()
    album = conn.execute("SELECT * FROM albums WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if album:
        fetch_album_metadata(id, album['artist'], album['title'])
    
    # Return a refresh trigger or just redirect back
    return redirect(url_for('albumView', id=id))

@app.route("/album/<int:id>", methods=["GET"])
def albumView(id):
    conn = get_db()
    album = conn.execute("select * from albums where id=?", (id,)).fetchone()
    tracks = conn.execute("select * from favorite_songs where album_id=? ORDER BY id", (id,)).fetchall()
    conn.close()
    return render_template("album_view.html", album=album, tracks=tracks)


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")
