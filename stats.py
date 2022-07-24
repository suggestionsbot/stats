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


def get_total_active_users(collection: pymongo.collection.Collection) -> str:
    assert collection.name == "member_stats"
    return str(collection.count_documents({}))


def get_total_suggestions(
    collection: pymongo.collection.Collection, filter_by=None
) -> str:
    filter_by = filter_by or {}
    assert collection.name == "suggestions"
    return str(collection.count_documents(filter_by))
