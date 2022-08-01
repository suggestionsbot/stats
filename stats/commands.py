from pymongo.collection import Collection

from stats import Container


def values_for_cmd(cmd_name: str, collection: Collection) -> tuple[int, int, int]:
    total_passed = 0
    total_failed = 0
    for entry in collection.find(projection={f"commands.{cmd_name}": 1, "_id": 0}):
        total_passed += len(entry["commands"][cmd_name]["completed_at"])
        total_failed += len(entry["commands"][cmd_name]["failed_at"])

    return total_passed + total_failed, total_passed, total_failed


def update_commands(container: Container):
    item = container.command_stats
    collection = container.database["member_stats"]
    for i, name in enumerate(["suggest", "approve", "reject"]):
        (
            item[i][0]["description"],
            item[i][1]["description"],
            item[i][2]["description"],
        ) = values_for_cmd(name, collection)
