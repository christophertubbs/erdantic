"""Example data model classes using [Pydantic](https://pydantic-docs.helpmanual.io/)."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

import pydantic


class Alignment(str, Enum):
    """
    Categorical definitions of morality
    """
    LAWFUL_GOOD = "lawful_good"
    NEUTRAL_GOOD = "neutral_good"
    CHAOTIC_GOOD = "chaotic_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    TRUE_NEUTRAL = "true_neutral"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_EVIL = "chaotic_evil"


class Adventurer(pydantic.BaseModel):
    """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et
    dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
    commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
    pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est
    laborum.

    Attributes:
        name (str): Name of this adventurer
        profession (str): Profession of this adventurer
        level (int): Level of this adventurer
        alignment (Alignment): Alignment of this adventurer
    """

    name: str
    profession: str = pydantic.Field(description="The profession of this adventurer")
    level: int = pydantic.Field(description="A measure of the proficency the adventurer has attained with their profession")
    alignment: Alignment = pydantic.Field(description="The category describing the adventurers morality")


class QuestGiver(pydantic.BaseModel):
    """A person who offers a task that needs completing.

    Attributes:
        name (str): Name of this quest giver
        faction (str): Faction that this quest giver belongs to
        location (str): Location this quest giver can be found
    """

    name: str
    faction: Optional[str] = pydantic.Field(description="Faction that this quest giver belongs to")
    location: str = pydantic.Field(description="Location this quest giver can be found")


class Quest(pydantic.BaseModel):
    """A task to complete, with some monetary reward.

    Attributes:
        name (str): Name by which this quest is referred to
        giver (QuestGiver): Person who offered the quest
        reward_gold (int): Amount of gold to be rewarded for quest completion
    """

    name: str = pydantic.Field("The name of the quest")
    giver: QuestGiver = pydantic.Field("The individual who offered the quest")
    reward_gold: int = pydantic.Field("The amount of gold that will be awarded upon completion")


class Party(pydantic.BaseModel):
    """A group of adventurers finding themselves doing and saying things altogether unexpected.

    Attributes:
        name (str): Name that party is known by
        formed_datetime (datetime): Timestamp of when the party was formed
        members (List[Adventurer]): Adventurers that belong to this party
        active_quest (Optional[Quest]): Current quest that party is actively tackling
    """

    name: str = pydantic.Field(description="The name of the party")
    formed_datetime: datetime = pydantic.Field(description="When the party was put together")
    members: List[Adventurer] = pydantic.Field(description="The members of the party")
    active_quest: Optional[Quest] = pydantic.Field(description="The quest that the party is currently on")
