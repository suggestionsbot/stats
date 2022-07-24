import logging
import os
import threading
from typing import Literal

from flask import Flask, render_template, request, abort, redirect, flash

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
log = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-7s | %(asctime)s | %(filename)12s:%(funcName)-12s | %(message)s",
    datefmt="%I:%M:%S %p %d/%m/%Y",
    level=logging.INFO,
)

nav_links: list[dict[Literal["name", "url"], str]] = [
    {"name": "Home", "url": "/"},
    {"name": "Aggregate", "url": "/aggregate"},
]


@app.errorhandler(403)
def page_not_found(e):
    return render_template("codes/403.html", nav_links=nav_links), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("codes/404.html", nav_links=nav_links), 404


@app.route("/")
def index():
    return render_template("index.html", nav_links=nav_links, current_nav_link="Home")


@app.route("/aggregate")
def aggregate_stats():
    return render_template(
        "aggregate_stats.html", nav_links=nav_links, current_nav_link="Aggregate"
    )


@app.route("/stats", methods=["POST", "GET"])
def update_stats():
    if request.method == "GET":
        return render_template("update_stats.html", nav_links=nav_links)

    key = request.args.get("key")
    form_key = request.form["key"]
    if not key and not form_key:
        abort(403)

    if key != os.environ["STATS_KEY"] and form_key != os.environ["STATS_KEY"]:
        abort(403)

    target = threading.Thread(target=populate_stats)
    target.start()  # Possible mem leak by not closing?

    if form_key:
        # User so give nice ui
        flash("Statistics are refreshing in the background.")
        return redirect("/", code=302)

    return "", 204


def populate_stats():
    pass


target = threading.Thread(target=populate_stats)
target.start()
if __name__ == "__main__":
    app.run()
