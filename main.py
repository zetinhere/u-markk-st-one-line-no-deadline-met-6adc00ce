#!/usr/bin/env python3
"""One Line, No Deadline Met.

Writes a single-line joke excusing a missed deadline to
/output/entry.txt: one sentence of plain text, at most 200 characters,
no setup line, no picture, no link, just the excuse itself.

The program holds a small pool of candidate excuses, scores each one
against the judge's published brief, and writes the best-scoring line.
"""

import os

# Candidate excuses, all in the voice of someone cornered about a missed
# deadline: first person, a little defensive, each built around one fresh,
# specific image instead of the usual "my dog ate it" or "the Wi-Fi died".
CANDIDATES = [
    # A: the snooze loop, until the deadline reports *me* missing.
    # The twist flips the roles: the deadline files the report, not me.
    # Tightened from a "kept telling myself ... until" setup to a single
    # breath: "so many times" escalates, and the punch lands on "on me".
    "I told myself 'five more minutes' so many times the deadline filed "
    "a missing persons report on me.",
    # B: my brain treats ASAP and whenever as synonyms, and my brain
    # runs the project. Self-deprecating, punch lands on the last words.
    "Turns out 'ASAP' and 'whenever' are the same word in my brain, and "
    "my brain is the project manager.",
    # C: the deadline as a situationship that ghosted me first.
    # Modern, but the blame-shift is a metaphor rather than a turn.
    "I didn't miss the deadline \u2014 I was giving it space, and like "
    "every situationship, it ghosted me first.",
    # D: two people waving at the wrong Uber. Vivid, but the punch is a
    # simile, and the excuse itself is thin.
    "The deadline moved, I moved, and somehow we still missed each other "
    "like two people waving at the wrong Uber.",
]

# Words that mark the tired, overused deadline excuses the judge's brief
# warns against; a candidate carrying one is penalised hard.
CLICHE_WORDS = ("dog ate", "wi-fi died", "wifi died", "traffic", "alarm")

# Phrases where the punch reverses who is at fault: the deadline acts
# against *me*, or my own brain is the one in charge. The sharpest kind
# of turn this judge rewards, because the reader expects an apology and
# gets a reversal instead.
REVERSAL_TWISTS = ("missing persons report on me", "my brain is the project manager")
# A blame-shift by metaphor: real joke, but a weaker turn than a reversal.
METAPHOR_TWISTS = ("ghosted me first", "wrong uber")


def twist(line: str) -> float:
    """Rate the punch: how unexpected is the turn in the final clause?"""
    tail = line.lower()
    if any(phrase in tail for phrase in REVERSAL_TWISTS):
        # The blamed party turns out to be the accuser, or my own brain:
        # the reader expects an excuse and gets the roles flipped.
        return 2.0
    if any(phrase in tail for phrase in METAPHOR_TWISTS):
        return 1.0
    return 0.0


def score(line: str) -> float:
    """Score a candidate against the judge's brief, most important first."""
    points = 0.0
    # 1. It must be an excuse for a missed deadline, in the voice of the
    #    person who missed it: first person, and it names the deadline.
    if "deadline" in line.lower():
        points += 2.0
    if line.startswith("I ") or line.startswith("Turns out"):
        points += 2.0
    # 2. A real joke with a turn the reader does not see coming: the punch
    #    lands in the second half, after the setup clause.
    tail = line.split(",", 1)[-1] if "," in line else line
    if any(word in tail.lower() for word in ("missing persons", "project manager", "ghosted", "wrong uber")):
        points += 3.0
    # The twist itself is scored on its own: a reversal beats a metaphor,
    # and both beat a line whose ending only describes.
    points += twist(line)
    # The punch must land at the very end, not in the middle: a reversal
    # phrase inside the last 45 characters earns the closing bonus.
    if any(phrase in line[-45:].lower() for phrase in REVERSAL_TWISTS):
        points += 1.0
    # 3. One sentence that reads cleanly aloud: a single line, no dialogue
    #    tags, comfortably under the 200-character cap.
    if 40 <= len(line) <= 160 and "\n" not in line and '"' not in line:
        points += 1.0
    if line.count(".") == 1 and line.endswith("."):
        points += 1.0
    # 4. Sounds like something a person would actually say when cornered:
    #    a confessed habit ("five more minutes", "my brain") rather than
    #    a formal apology.
    if any(word in line.lower() for word in ("five more minutes", "my brain", "giving it space")):
        points += 2.0
    # 5. A fresh, specific detail instead of the usual excuse.
    if any(word in line.lower() for word in ("missing persons", "project manager", "situationship", "wrong uber")):
        points += 2.0
    # Penalty: the worn-out deadline gags.
    if any(word in line.lower() for word in CLICHE_WORDS):
        points -= 5.0
    return points


def validate(line: str) -> None:
    """Enforce the sealed gate ourselves before writing anything out."""
    assert line == line.strip(), "no leading or trailing whitespace"
    assert 1 <= len(line) <= 200, f"line is {len(line)} chars"
    assert "\n" not in line and "\r" not in line, "entry must be a single line"
    assert '"' not in line and not line.startswith(("Boss:", "Me:")), (
        "no dialogue tags"
    )
    assert not any(word in line.lower() for word in CLICHE_WORDS), (
        "entry repeats a worn-out deadline gag"
    )
    # The punch must sit in the final clause: a reversal phrase in the
    # last 45 characters, so the line lands on the twist, not after it.
    assert any(
        phrase in line[-45:].lower() for phrase in REVERSAL_TWISTS
    ), "punch must land at the very end of the line"
    line.encode("utf-8")  # the gate requires UTF-8 text


def pick() -> str:
    """Return the best-scoring candidate; ties go to the shorter line."""
    ranked = sorted(CANDIDATES, key=lambda line: (-score(line), len(line)))
    best = ranked[0]
    # Freshness self-check: the winner must beat every other candidate
    # outright, so the choice is a decision, not a coin flip on a tie.
    assert score(best) > score(ranked[1]), "winner must lead outright"
    validate(best)
    return best


def main() -> None:
    line = pick()
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "w", encoding="utf-8") as handle:
        handle.write(line)


if __name__ == "__main__":
    main()
