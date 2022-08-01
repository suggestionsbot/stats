import datetime
import logging
import os
import threading
import time
from typing import Literal

from flask import Flask, render_template
from pymongo import MongoClient

from stats import Container, aggregate, commands

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
app.stats_container = Container(app.database)

nav_links: list[dict[Literal["name", "url"], str]] = [
    {"name": "Home", "url": "/"},
    {"name": "Aggregate", "url": "/aggregate"},
    {"name": "Suggestions Commands", "url": "/suggestions"},
    {"name": "Configuration Commands", "url": "/config"},
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
        "stats_view.html",
        nav_links=nav_links,
        header="Aggregate Statistics",
        current_nav_link="Aggregate",
        stats_items=app.stats_container.aggregate_stats,
    )


@app.route("/suggestions")
def suggestions_stats():
    return render_template(
        "stats_view.html",
        nav_links=nav_links,
        header="Suggestion Related Statistics",
        current_nav_link="Suggestions Commands",
        stats_items=app.stats_container.suggestions_stats,
    )


@app.route("/config")
def configuration_stats():
    return render_template(
        "stats_view.html",
        nav_links=nav_links,
        header="Configuration Related Statistics",
        current_nav_link="Configuration Commands",
        stats_items=app.stats_container.config_stats,
    )


def populate_stats():
    while True:
        # aggregate.update_aggregate(app.stats_container)
        commands.update_commands(app.stats_container)
        time.sleep(datetime.timedelta(hours=6).total_seconds())


target = threading.Thread(target=populate_stats)
target.start()
if __name__ == "__main__":
    app.run()
