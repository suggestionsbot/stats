from typing import Literal

from flask import Flask, render_template

app = Flask(__name__)

nav_links: list[dict[Literal["name", "url"], str]] = [
    {"name": "Home", "url": "/"},
    {"name": "Aggregate", "url": "/aggregate"},
]


@app.route("/")
def index():
    return render_template("index.html", nav_links=nav_links, current_nav_link="Home")


@app.route("/aggregate")
def aggregate_stats():
    return render_template(
        "aggregate_stats.html", nav_links=nav_links, current_nav_link="Aggregate"
    )


if __name__ == "__main__":
    app.run()
