def get_total_guild_count(collection, total_cluster_count: int) -> str:
    total_count: int = 0
    for i in range(1, total_cluster_count + 1):
        query = {"cluster_id": i}
        cursor = collection.find(query).sort("timestamp", -1).limit(1)
        entry = cursor.next()
        total_count += entry["guild_count"]

    return str(total_count)
