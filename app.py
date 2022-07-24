import logging
import os
import threading
from typing import Literal

from flask import Flask, render_template, request, abort, redirect, flash
from pymongo import MongoClient

from stats import get_total_guild_count

log = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-7s | %(asctime)s | %(filename)12s:%(funcName)-12s | %(message)s",
    datefmt="%I:%M:%S %p %d/%m/%Y",
    level=logging.INFO,
)

app = Flask(__name__)
app.client = MongoClient(os.environ["MONGO_URL"])
app.database = app.client["suggestions-rewrite"]
app.secret_key = os.environ["SECRET_KEY"]
app.stats = [
    [
        {"title": "Total guilds", "description": "..."},
        {"title": "Total users", "description": "..."},
        {
            "title": "Active guild count",
            "description": "...",
        },
        {
            "title": "Active user count",
            "description": "...",
        },
    ],
    [
        {"title": "Total suggestions", "description": "..."},
        {"title": "Total open suggestions", "description": "..."},
        {"title": "Total resolved suggestions", "description": "..."},
        {"title": "Average suggestions per guild", "description": "..."},
        {"title": "Average suggestions per member", "description": "..."},
    ],
    [
        {
            "title": "Guilds with dm messages disabled",
            "description": "... guilds have dm messages disabled",
        },
        {
            "title": "Users with dm messages disabled",
            "description": "... users have dm messages disabled disabled",
        },
    ],
]

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
        "aggregate_stats.html",
        nav_links=nav_links,
        current_nav_link="Aggregate",
        stats_items=app.stats,
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
    # Total guilds
    app.stats[0][0]["description"] = get_total_guild_count(
        app.database["cluster_guild_counts"], 6
    )
    # Total users
    app.stats[0][1]["description"] = "Unknown"
    # Active guild count
    app.stats[0][2]["description"] = "Unknown"
    # Active user count
    app.stats[0][3]["description"] = "Unknown"

    # Total suggestions
    app.stats[1][0]["description"] = "Unknown"
    # Total open suggestions
    app.stats[1][1]["description"] = "Unknown"
    # Total resolved suggestions
    app.stats[1][2]["description"] = "Unknown"
    # Average suggestions per guild
    app.stats[1][3]["description"] = "Unknown"
    # Average suggestions per member
    app.stats[1][4]["description"] = "Unknown"

    # Guilds with dm messages disabled
    app.stats[2][0]["description"] = "Unknown"
    # Users with dm messages disabled
    app.stats[2][1]["description"] = "Unknown"


target = threading.Thread(target=populate_stats)
target.start()
if __name__ == "__main__":
    app.run()
