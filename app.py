import datetime
import logging
import os
import threading
import time
from typing import Literal

from flask import Flask, render_template, request, abort, redirect, flash
from pymongo import MongoClient

import stats

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
        total_clusters = stats.get_cluster_count(app.database["cluster_guild_counts"])

        # Total guilds
        app.stats[0][0]["description"] = stats.get_total_guild_count(
            app.database["cluster_guild_counts"], total_clusters
        )
        # Total users
        app.stats[0][1]["description"] = "Unknown"
        # Active guild count
        total_active_guilds = stats.get_total_active_guilds(
            app.database["guild_configs"]
        )
        app.stats[0][2]["description"] = total_active_guilds
        # Active user count
        total_active_users = stats.get_distinct_total_active_users(
            app.database["member_stats"]
        )
        app.stats[0][3]["description"] = total_active_users

        # Total suggestions
        total_suggestions = stats.get_total_suggestions(app.database["suggestions"])
        app.stats[1][0]["description"] = total_suggestions
        # Total pending suggestions
        app.stats[1][1]["description"] = stats.get_total_suggestions(
            app.database["suggestions"], {"state": "pending"}
        )
        # Total resolved suggestions
        app.stats[1][2]["description"] = stats.get_total_suggestions(
            app.database["suggestions"], {"state": {"$ne": "pending"}}
        )
        # Average suggestions per guild
        app.stats[1][3]["description"] = str(
            round(int(total_suggestions) / int(total_active_guilds), 2)
        )
        # Average suggestions per member
        app.stats[1][4]["description"] = str(
            round(int(total_suggestions) / int(total_active_users), 2)
        )

        # Fully configured guilds
        app.stats[2][0]["description"] = stats.get_total_fully_configured_guilds(
            app.database["guild_configs"]
        )
        # Guilds with dm messages disabled
        app.stats[2][1]["description"] = stats.get_total_guilds_with_dms_disabled(
            app.database["guild_configs"]
        )
        # Users with dm messages disabled
        app.stats[2][2]["description"] = stats.get_total_users_with_dms_disabled(
            app.database["user_configs"]
        )

        if os.environ.get("PROD", False):
            stats_db = app.database["site_stats_db"]
            stats_db.insert_one(
                {"timestamp": datetime.datetime.now(), "aggregate_stats": app.stats}
            )

        time.sleep(datetime.timedelta(hours=6).total_seconds())


target = threading.Thread(target=populate_stats)
target.start()
if __name__ == "__main__":
    app.run()
