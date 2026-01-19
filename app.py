from flask import Flask, render_template, request, redirect, send_from_directory, url_for
import csv
import os

app = Flask(__name__)
CSV_FILE = "albums.csv"
FIELDNAMES = ["id", "artist", "title", "year", "cover", "rating"]


def read_albums():
    albums = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            albums = list(reader)
    return albums


def write_albums(albums):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(albums)


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
def albums():
    return render_template("_albums.html", albums=read_albums())


@app.route("/form")
def create_form():
    return render_template("_form.html", album=None, action="/create")


@app.route("/form/<id>")
def edit_form(id):
    albums = read_albums()
    album = next(a for a in albums if a["id"] == id)
    return render_template("_form.html", album=album, action=f"/edit/{id}")


@app.route("/create", methods=["POST"])
def create():
    albums = read_albums()
    album = {
        "id": next_id(albums),
        "artist": request.form["artist"],
        "title": request.form["title"],
        "year": request.form["year"],
        "cover": request.form["cover"],
        "rating": request.form["rating"],
    }
    albums.append(album)
    write_albums(albums)
    return render_template("_albums_card.html", albums=albums)


@app.route("/edit/<id>", methods=["POST"])
def edit(id):
    albums = read_albums()
    album = next(a for a in albums if a["id"] == id)

    for field in FIELDNAMES:
        if field != "id":
            album[field] = request.form[field]

    write_albums(albums)
    return render_template("_album_card.html", albums=albums)


@app.route("/delete/<id>", methods=["DELETE"])
def delete(id):
    albums = read_albums()
    albums = [a for a in albums if a["id"] != id]
    write_albums(albums)
    return render_template("_albums.html", albums=albums)


if __name__ == "__main__":
    app.run(debug=True)
