from humanize import intcomma
from pymongo.collection import Collection

from stats import Container


def values_for_cmd(cmd_name: str, collection: Collection) -> tuple[str, str, str]:
    total_passed = 0
    total_failed = 0
    for entry in collection.find(projection={f"commands.{cmd_name}": 1, "_id": 0}):
        total_passed += len(entry["commands"][cmd_name]["completed_at"])
        total_failed += len(entry["commands"][cmd_name]["failed_at"])

    return (
        intcomma(total_passed + total_failed),
        intcomma(total_passed),
        intcomma(total_failed),
    )


def update_commands(container: Container):
    collection = container.database["member_stats"]
    for i, name in enumerate(["suggest", "approve", "reject"]):
        (
            container.suggestions_stats[i][0]["description"],
            container.suggestions_stats[i][1]["description"],
            container.suggestions_stats[i][2]["description"],
        ) = values_for_cmd(name, collection)

    for i, name in enumerate(
        ["guild_config_get", "guild_config_suggest_channel", "guild_config_log_channel"]
    ):
        (
            container.config_stats[i][0]["description"],
            container.config_stats[i][1]["description"],
            container.config_stats[i][2]["description"],
        ) = values_for_cmd(name, collection)
