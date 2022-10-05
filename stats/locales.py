from collections import Counter

from pymongo.collection import Collection

from stats import Container
from stats.container import Entry

lookups: dict[str, str] = {
    "bg": "Bulgarian",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en-GB": "English, UK",
    "en-US": "English, US",
    "es-ES": "Spanish",
    "fi": "Finnish",
    "fr": "French",
    "hi": "Hindi",
    "hr": "Croatian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "lt": "Lithuanian",
    "hu": "Hungarian",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt-BR": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sv-SE": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "vi": "Vietnamese",
    "zh-CN": "Chinese, China",
    "zh-TW": "Chinese, Taiwan",
}


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
            key = lookups.get(item[0], item[0])
            entry.append(Entry(title=key, description=str(item[1])))

        container.locale_stats.append(entry)
