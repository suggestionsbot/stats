import pymongo


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
