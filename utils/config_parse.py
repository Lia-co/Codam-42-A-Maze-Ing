#!/usr/bin/env python3

"""
This file parse the config.txt and return an immutable object with valid data
for later generating a maze.

The parsing process is separated into 3 stages:
- read the file and find valid KEY=VALUE pair per line
- validate data and convert to valid data types
- store data into an immutable class and return it

Each stage will raise error message if there is invalid input, and give back a
clear error message instead of crashing the program.
"""

from __future__ import annotations

from dataclasses import dataclass

# should it be a protective variable?
mandatory_keys = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}


def parse_coord(value: str) -> tuple[int, int]:
    """
    Parse digital strings("x,y") into a tuple {x, y} with 2 integers.
    Only digital number and white space are accepted(e.g. "x,  y" is valid)
    If receiving invalid strings, will raise error message
    """
    coords = [coor.strip() for coor in value.split(",")]
    if len(coords) != 2:
        raise ValueError(
            f"Not enough valid input {value}, "
            f"expect format: x,y are digital numbers(e.g. 20,15)"
        )
    try:
        x: int = int(coords[0])
        y: int = int(coords[1])
    except ValueError as e:
        raise ValueError(
            f"Invalid input '{value}', expect format: "
            f"x,y are digital numbers(e.g. 20,15)"
        ) from e
    return x, y


def parse_bool(value: str) -> bool:
    """
    Parse acceptable string into boolean(1/0).

    Acceptable strings look like:
    "true", "y", "yes", "1"
    "false", "n" "no" "0"

    If receiving invalid strings, will raise error message
    """
    v = value.strip().lower()
    if v in {"true", "y", "yes", "1"}:
        return True
    elif v in {"false", "n", "no", "0"}:
        return False
    raise ValueError(f"Invalid input: '{v}', expect input: true/false.")


@dataclass(frozen=True)
class Config:
    """
    Define a dataclass Config which stores valid input (key: value format).
    Returned in method parse_config after input are validated and converted.
    """
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int
    algorithm: str


def parse_config(filename: str) -> Config:
    """
    Parse config.txt file to validate KEY=VALUE pair
    per line and return an immutable class
    including valid data for later generating a maze.

    The parsing process is separated into 3 stages:
    - open, read the file and find valid KEY=VALUE pair
    per line(skip lines start with '#' or no KEY=VALUE pair found)
        - if found, convert pair into dictionary with two strings
    - validate data and convert value to valid data types
    - store data into an immutable class and return it

    Raise error messages in following conditions:
    - not config.txt file found
    - not enough mandatory keys
    - not valid string input for each key
    - if entry and exit are the same position
    - if entry and exit are outside of width or height
    - if entry and exit are located in 42 decoration pattern(conditional)
    """

    data: dict[str, str] = {}

    # open file with 'with', don't need to handle close file
    with open(filename) as f:
        # why using for loop for a file can get per line, and \n as a seperator
        # chunck each line from file into pairs with for loop, skip line start
        # with '#' and empty line
        for pair in f:
            pair = pair.strip()
            if pair.startswith("#") or not pair:
                continue
            if "=" not in pair:
                raise SyntaxError(
                    f"Key '{pair}' must have valid value, "
                    f"expect input: KEY=VALUE"
                )

            # chunck pair into keys and values
            key, value = pair.split("=", 2)
            if not key or not value:
                raise SyntaxError(
                    f"Wrong syntax for '{pair}', expect input: KEY=VALUE ")
            key = key.strip().upper()
            value = value.strip()
            data[key] = value

    # ???check if there are enough keys, how to compare them?
    missing = [
        key for key in (mandatory_keys) if key not in data
        ]
    if missing:
        raise ValueError(
            f"Missing mandatory key {missing}. Please add {missing}")

    # chekc if WIDTH and HEIGHT are valid
    # ???how to silence the base 10 error.
    try:
        width: int = int(data["WIDTH"])
        height: int = int(data["HEIGHT"])
    except ValueError as e:
        raise ValueError(
            "Invalid value for 'WIDTH' or/and 'HEIGHT', "
            "expect digital input, e.g. 10") from e

    if width <= 0 or height <= 0:
        raise ValueError(
            "Invalid value for 'WIDTH' or/and 'HEIGHT. "
            "Integers must greater than 0")

    # check if ENTRY and EXIT are the same, inside of field, or located 42
    # pattern
    entry = parse_coord(data["ENTRY"])
    exit = parse_coord(data["EXIT"])

    if entry == exit:
        raise ValueError(
            "ENTRY and EXIT are the same. "
            "Please make them locating differently.")
    # bounce check needed more discussion
    if entry[0] >= width or exit[0] > width:
        raise ValueError(
            f"ENTRY's x or/and EXIT's x are outside of width. "
            f"Expect x <= {width - 1}")
    if entry[1] >= height or exit[1] >= height:
        raise ValueError(
            f"ENTRY's y or/and EXIT's y are outside of height. "
            f"Expect y <= {height - 1}")
    # assign variable output
    output = data["OUTPUT_FILE"]
    # assign variable perfect
    perfect = parse_bool(data["PERFECT"])
    # check if SEED has valid digit strings
    try:
        seed = int(data["SEED"])
    except ValueError as e:
        raise ValueError(
            "Invalid value for 'SEED', expect digital input, e.g. 10") from e
    if seed < 0:
        raise ValueError("'SEED' must be positive integer")
    # check if ALGORITHM has valid digit strings
    algorithm = data["ALGORITHM"].upper()

    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exit,
        output_file=output,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm
    )
