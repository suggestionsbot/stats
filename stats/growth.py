from stats import Container
from stats.aggregate import (
    get_total_guild_count,
    get_cluster_count,
    get_total_suggestions,
    get_distinct_total_active_users,
)
from stats.container import Entry


def update_stat(container: Container, field, value):
    container.raw_growth_stats[field].append(value)
    c = len(container.raw_growth_stats[field])
    if c == 1:
        return

    if c > 4:
        container.raw_growth_stats[field].pop(-1)


def update_fields(container: Container):
    total_guilds = get_total_guild_count(
        container.database["cluster_guild_counts"],
        get_cluster_count(container.database["cluster_guild_counts"]),
    )
    update_stat(container, "guilds", total_guilds)

    total_suggestions = get_total_suggestions(container.database["suggestions"])
    update_stat(container, "suggestions", total_suggestions)

    total_active_users = get_distinct_total_active_users(
        container.database["member_stats"]
    )
    update_stat(container, "active_users", total_active_users)


def update_growth(container: Container):
    update_fields(container)

    entries = []
    for k, v in container.raw_growth_stats.items():
        if v and len(v) != 1:
            growth = v[0] - v[-1]
            sign = "+" if growth > 0 else "-"
            entries.append(
                Entry(
                    title=" ".join(k.split("_")).capitalize(),
                    description=f"{sign}{growth}",
                )
            )
