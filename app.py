import datetime
import logging
import os
import threading
import time
from typing import Literal

from flask import Flask, render_template
from pymongo import MongoClient

from stats import Container, aggregate, commands, locales, growth

log = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-7s | %(asctime)s | %(message)s",
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
    {"name": "Growth", "url": "/growth"},
    {"name": "Suggestions Commands", "url": "/suggestions"},
    {"name": "Configuration Commands", "url": "/config"},
    {"name": "Locale Data", "url": "/locales"},
    {"name": "API", "url": "/api/all"},
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


@app.route("/locales")
def locale_stats():
    return render_template(
        "stats_view.html",
        nav_links=nav_links,
        header="Our demographics, by locale.",
        current_nav_link="Locale Data",
        stats_items=app.stats_container.locale_stats,
    )


@app.route("/growth")
def growth_stats():
    return render_template(
        "stats_view.html",
        nav_links=nav_links,
        header="Statistics from the past 24 hours",
        current_nav_link="Growth",
        stats_items=app.stats_container.growth_stats,
    )


@app.route("/api/events/interaction_create")
def api_events_interaction_create():
    ic_db = app.stats_container.database["interaction_create_stats"]
    total = 0
    cluster_counts = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    for entry in ic_db.find({}):
        if entry["cluster"] in cluster_counts:
            cluster_counts[entry["cluster"]].append(entry)

            total += entry["count"]

    ts_hour = 0
    cluster_data = {}
    for k, v in cluster_counts.items():
        if not v:
            continue

        # Newest first
        v = sorted(v, reverse=True, key=lambda x: x["inserted_at"])
        ts_hour += v[0]["count"]

        cluster_data[k] = {
            "total_seen": sum([d["count"] for d in v]),
            "total_seen_this_hour": v[0]["count"],
        }

    return {
        "total_seen": total,
        "total_seen_this_hour": ts_hour,
        "cluster_data": cluster_data,
    }


@app.route("/api/all")
def api_locale_stats():
    data = {
        "aggregate": {},
        "suggestions": {},
        "config": {},
        "locales": {},
        "growth": {},
    }
    for k, v in {
        "aggregate": app.stats_container.aggregate_stats,
        "suggestions": app.stats_container.suggestions_stats,
        "config": app.stats_container.config_stats,
        "locales": app.stats_container.locale_stats,
        "growth": app.stats_container.growth_stats,
    }.items():
        for entry in v:
            for s in entry:
                title = (
                    s["title"]
                    .replace("-", "")
                    .lower()
                    .replace(" ", "_")
                    .replace(",", "")
                )
                try:
                    desc = s["description"].lower()
                    if "," in desc:
                        desc = desc.replace(",", "")
                        desc = int(desc)
                    elif "." in desc or desc.isnumeric():
                        desc = float(desc)
                except:
                    desc = s["description"].lower()

                data[k][title] = desc

    return data


def populate_stats():
    while True:
        aggregate.update_aggregate(app.stats_container)
        commands.update_commands(app.stats_container)
        locales.update_aggregate(app.stats_container)
        growth.update_growth(app.stats_container)
        time.sleep(datetime.timedelta(hours=6).total_seconds())


target = threading.Thread(target=populate_stats)
target.start()
if __name__ == "__main__":
    app.run()
