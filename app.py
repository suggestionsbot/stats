import datetime
import logging
import os
import threading
import time
from typing import Literal, TYPE_CHECKING

from flask import Flask, render_template
from pymongo import MongoClient

from stats import aggregate

if TYPE_CHECKING:
    from pymongo.database import Database

    class Flask:
        client: MongoClient = ...
        database: Database = ...
        stats: list[list[dict]] = ...


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
        {"title": "Total pending suggestions", "description": "..."},
        {"title": "Total resolved suggestions", "description": "..."},
        {"title": "Average suggestions per guild", "description": "..."},
        {"title": "Average suggestions per user", "description": "..."},
    ],
    [
        {
            "title": "Fully configured guilds",
            "description": "...",
        },
        {
            "title": "Guilds with dm messages disabled",
            "description": "...",
        },
        {
            "title": "Users with dm messages disabled",
            "description": "...",
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


def populate_stats():
    while True:
        aggregate.update_aggregate(app)
        time.sleep(datetime.timedelta(hours=6).total_seconds())


target = threading.Thread(target=populate_stats)
target.start()
if __name__ == "__main__":
    app.run()
