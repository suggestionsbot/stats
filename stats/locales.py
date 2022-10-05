from collections import Counter

from pymongo.collection import Collection

from stats import Container
from stats.container import Entry


def update_aggregate(container: Container):
    collection = container.database["locale_tracking"]
    locales: dict[str, int] = {}
    already_seen: set[tuple[int, int]] = set()

    for entry in collection.find():
        user_id = entry["user_id"]
        guild_id = entry["guild_id"]
        key = (user_id, guild_id)
        if key in already_seen:
            continue

        already_seen.add(key)

        locale = entry["locale"]
        try:
            locales[locale] += 1
        except KeyError:
            locales[locale] = 1

    sorted_locales: Counter = Counter(locales)
    sorted_locales: list[tuple[str, int]] = sorted_locales.most_common()
    chunks = [sorted_locales[x : x + 4] for x in range(0, len(sorted_locales), 4)]

    container.locale_stats = []
    for chunk in chunks:
        entry = []
        for item in chunk:
            entry.append(Entry(title=item[0], description=str(item[1])))

        container.locale_stats.append(entry)
