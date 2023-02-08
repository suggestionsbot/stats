from __future__ import annotations

import datetime
import os

import pymongo
from humanize import intcomma

from stats import Container


def get_total_guild_count(
    collection: pymongo.collection.Collection, total_cluster_count: int
) -> str:
    assert collection.name == "cluster_guild_counts"
    total_count: int = 0
    for i in range(1, total_cluster_count + 1):
        query = {"cluster_id": i}
        cursor = collection.find(query).sort("timestamp", -1).limit(1)
        entry = cursor.next()
        total_count += entry["guild_count"]

    return str(total_count)


def get_total_active_guilds(collection: pymongo.collection.Collection) -> str:
    assert collection.name == "guild_configs"
    return str(collection.count_documents({}))


def get_distinct_total_active_users(collection: pymongo.collection.Collection) -> str:
    assert collection.name == "member_stats"
    total = collection.distinct("member_id")
    return str(len(total))


def get_total_suggestions(
    collection: pymongo.collection.Collection, filter_by=None
) -> str:
    filter_by = filter_by or {}
    assert collection.name == "suggestions"
    return str(collection.count_documents(filter_by))


def get_total_guilds_with_dms_disabled(
    collection: pymongo.collection.Collection,
) -> str:
    assert collection.name == "guild_configs"
    return str(collection.count_documents({"dm_messages_disabled": True}))


def get_total_users_with_dms_disabled(
    collection: pymongo.collection.Collection,
) -> str:
    assert collection.name == "user_configs"
    return str(collection.count_documents({"dm_messages_disabled": True}))


def get_total_guilds_with_suggestions_queue(
    collection: pymongo.collection.Collection,
) -> str:
    assert collection.name == "guild_configs"
    return str(collection.count_documents({"uses_suggestion_queue": True}))


def get_total_fully_configured_guilds(collection: pymongo.collection.Collection) -> str:
    assert collection.name == "guild_configs"
    total = collection.find(
        {
            "$and": [
                {"log_channel_id": {"$exists": True}},
                {"suggestions_channel_id": {"$exists": True}},
            ]
        },
        projection={"_id": 1},
    )
    return str(len(list(total)))


def get_cluster_count(collection: pymongo.collection.Collection) -> int:
    assert collection.name == "cluster_guild_counts"
    total = collection.distinct("cluster_id")
    return len(total) - 1  # Remove cluster 0 (debug cluster)


def update_aggregate(app: Container):
    total_clusters = get_cluster_count(app.database["cluster_guild_counts"])

    # Total guilds
    app.aggregate_stats[0][0]["description"] = intcomma(
        get_total_guild_count(app.database["cluster_guild_counts"], total_clusters)
    )
    # Total users
    app.aggregate_stats[0][1]["description"] = "Unknown"
    # Active guild count
    total_active_guilds = get_total_active_guilds(app.database["guild_configs"])
    app.aggregate_stats[0][2]["description"] = intcomma(total_active_guilds)
    # Active user count
    total_active_users = get_distinct_total_active_users(app.database["member_stats"])
    app.aggregate_stats[0][3]["description"] = intcomma(total_active_users)

    # Total suggestions
    total_suggestions = get_total_suggestions(app.database["suggestions"])
    app.aggregate_stats[1][0]["description"] = intcomma(total_suggestions)
    # Total pending suggestions
    app.aggregate_stats[1][1]["description"] = intcomma(
        get_total_suggestions(app.database["suggestions"], {"state": "pending"})
    )
    # Total resolved suggestions
    app.aggregate_stats[1][2]["description"] = intcomma(
        get_total_suggestions(
            app.database["suggestions"], {"state": {"$in": ["approved", "rejected"]}}
        )
    )
    app.aggregate_stats[1][3]["description"] = intcomma(
        get_total_suggestions(app.database["suggestions"], {"state": "cleared"})
    )
    # Average suggestions per guild
    app.aggregate_stats[1][4]["description"] = str(
        round(int(total_suggestions) / int(total_active_guilds), 2)
    )
    # Average suggestions per member
    app.aggregate_stats[1][5]["description"] = str(
        round(int(total_suggestions) / int(total_active_users), 2)
    )

    # Fully configured guilds
    app.aggregate_stats[2][0]["description"] = intcomma(
        get_total_fully_configured_guilds(app.database["guild_configs"])
    )
    # Guilds with dm messages disabled
    app.aggregate_stats[2][1]["description"] = intcomma(
        get_total_guilds_with_dms_disabled(app.database["guild_configs"])
    )
    # Users with dm messages disabled
    app.aggregate_stats[2][2]["description"] = intcomma(
        get_total_users_with_dms_disabled(app.database["user_configs"])
    )
    # Guilds using queue
    app.aggregate_stats[2][3]["description"] = intcomma(
        get_total_guilds_with_suggestions_queue(app.database["guild_configs"])
    )

    # Errors
    total_errors = app.database["error_tracking"].count_documents({})
    total_handled_errors = app.database["error_tracking"].count_documents(
        {
            "error": {
                "$in": [
                    "ErrorHandled",
                    "BetaOnly",
                    "MissingSuggestionsChannel",
                    "MissingLogsChannel",
                    "MissingPermissions",
                    "SuggestionNotFound",
                    "SuggestionTooLong",
                    "InvalidGuildConfigOption",
                    "CallableOnCooldown",
                    "ConfiguredChannelNoLongerExists",
                    "LocalizationKeyError",
                ]
            }
        }
    )
    reraised_errors = app.database["error_tracking"].count_documents(
        {"error": {"$in": ["Forbidden", "NotFound"]}}
    )
    total_unhandled_errors = total_errors - total_handled_errors - reraised_errors
    app.aggregate_stats[3][0]["description"] = intcomma(str(total_errors))
    app.aggregate_stats[3][1]["description"] = intcomma(str(total_handled_errors))
    app.aggregate_stats[3][2]["description"] = intcomma(str(reraised_errors))
    app.aggregate_stats[3][3]["description"] = intcomma(str(total_unhandled_errors))

    if os.environ.get("PROD", False):
        stats_db = app.database["site_stats_db"]
        stats_db.insert_one(
            {
                "timestamp": datetime.datetime.now(),
                "aggregate_stats": app.aggregate_stats,
            }
        )
