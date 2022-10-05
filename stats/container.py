from typing import Literal, TypedDict, Union

from pymongo.database import Database


class Entry(TypedDict):
    title: str
    description: str


StatEntry = list[list[Union[Entry, dict[Literal["title", "description"], str]]]]


class Container:
    """A generic container for state variables"""

    # This file will likely be the worst code wise
    # as it's just a mess of hard coded nonce

    def __init__(self, database: Database):
        self.database: Database = database
        self.aggregate_stats: StatEntry = [
            [
                {"title": "Total guilds", "description": "..."},
                {"title": "Total users", "description": "..."},
                {
                    "title": "Active guild count",
                    "description": "...",
                },
                {
                    "title": "Active user count",
                    "description": "...",
                },
            ],
            [
                {"title": "Total suggestions", "description": "..."},
                {"title": "Total pending suggestions", "description": "..."},
                {"title": "Total resolved suggestions", "description": "..."},
                {"title": "Total cleared suggestions", "description": "..."},
                {"title": "Average suggestions per guild", "description": "..."},
                {"title": "Average suggestions per user", "description": "..."},
            ],
            [
                {
                    "title": "Fully configured guilds",
                    "description": "...",
                },
                {
                    "title": "Guilds with dm messages disabled",
                    "description": "...",
                },
                {
                    "title": "Users with dm messages disabled",
                    "description": "...",
                },
            ],
        ]

        self.suggestions_stats: StatEntry = [
            [
                Entry(title="Suggestion command usage", description="..."),
                Entry(title="Times succeeded", description="..."),
                Entry(title="Times failed", description="..."),
            ],
            [
                Entry(title="Approval command usage", description="..."),
                Entry(title="Times succeeded", description="..."),
                Entry(title="Times failed", description="..."),
            ],
            [
                Entry(title="Reject command usage", description="..."),
                Entry(title="Times succeeded", description="..."),
                Entry(title="Times failed", description="..."),
            ],
        ]
        self.config_stats: StatEntry = [
            [
                Entry(title="View guild config command usage", description="..."),
                Entry(title="Times succeeded", description="..."),
                Entry(title="Times failed", description="..."),
            ],
            [
                Entry(title="Set suggestions channel command usage", description="..."),
                Entry(title="Times succeeded", description="..."),
                Entry(title="Times failed", description="..."),
            ],
            [
                Entry(title="Set logs channel usage command usage", description="..."),
                Entry(title="Times succeeded", description="..."),
                Entry(title="Times failed", description="..."),
            ],
        ]

        self.locale_stats: StatEntry = [
            [Entry(title="N/A", description="No locale data")]
        ]
