"""Boyer-Moore-Horspool string matching algorithm implementation."""

from dataclasses import dataclass
from typing import Dict, List, Tuple


def display_char(char: str) -> str:
    """Return a printable one-token representation for UI messages."""
    mapping = {
        "\n": "\\n",
        "\t": "\\t",
        "\r": "\\r",
        " ": "space",
    }
    return mapping.get(char, char)


def visual_char(char: str) -> str:
    """Map non-printable characters to one-character placeholders for alignment views."""
    mapping = {
        "\n": "|",
        "\t": ">",
        "\r": "^",
    }
    return mapping.get(char, char)


def build_skip_table(pattern: str) -> Dict[str, int]:
    """Create Boyer-Moore-Horspool skip table for a pattern."""
    table: Dict[str, int] = {}
    pattern_len = len(pattern)
    for i in range(pattern_len - 1):
        table[pattern[i]] = pattern_len - 1 - i
    return table


def bmh_search(text: str, pattern: str, start: int = 0) -> int:
    """Return first match index of pattern in text using BMH, or -1 if missing."""
    text_len = len(text)
    pattern_len = len(pattern)

    if pattern_len == 0:
        return max(0, min(start, text_len))
    if pattern_len > text_len:
        return -1

    skip = build_skip_table(pattern)
    i = max(0, start)

    while i <= text_len - pattern_len:
        j = pattern_len - 1

        while j >= 0 and text[i + j] == pattern[j]:
            j -= 1

        if j < 0:
            return i

        i += skip.get(text[i + pattern_len - 1], pattern_len)

    return -1


def bmh_find_all(text: str, pattern: str, allow_overlap: bool = False) -> List[int]:
    """Return all match positions for pattern in text using repeated BMH searches."""
    if not pattern:
        return []

    positions: List[int] = []
    search_from = 0
    step = 1 if allow_overlap else len(pattern)

    while search_from <= len(text) - len(pattern):
        index = bmh_search(text, pattern, search_from)
        if index == -1:
            break

        positions.append(index)
        search_from = index + step

    return positions


@dataclass
class BMHStep:
    alignment: int
    comparisons: List[Tuple[int, int, str, str, bool]]
    is_match: bool
    shift: int
    reason: str


def bmh_trace(
    text: str,
    pattern: str,
    start: int = 0,
    stop_on_first_match: bool = True,
    max_steps: int = 250,
) -> Tuple[List[BMHStep], int, Dict[str, int]]:
    """Collect step-by-step BMH states for visualization."""
    if not pattern:
        return [], -1, {}

    text_len = len(text)
    pattern_len = len(pattern)
    skip = build_skip_table(pattern)

    if pattern_len > text_len:
        return (
            [
                BMHStep(
                    alignment=0,
                    comparisons=[],
                    is_match=False,
                    shift=0,
                    reason=(
                        "Pattern is longer than the text, so there is no valid "
                        "alignment to compare."
                    ),
                )
            ],
            -1,
            skip,
        )

    last_alignment = text_len - pattern_len
    i = max(0, start)

    if i > last_alignment:
        return (
            [
                BMHStep(
                    alignment=last_alignment,
                    comparisons=[],
                    is_match=False,
                    shift=0,
                    reason=(
                        f"Start index {i} is beyond the last valid alignment "
                        f"({last_alignment}), so no comparisons were possible "
                        "from that start."
                    ),
                )
            ],
            -1,
            skip,
        )

    steps: List[BMHStep] = []
    first_match = -1

    while i <= last_alignment and len(steps) < max_steps:
        j = pattern_len - 1
        comparisons: List[Tuple[int, int, str, str, bool]] = []

        while j >= 0:
            text_index = i + j
            text_char = text[text_index]
            pattern_char = pattern[j]
            matched = text_char == pattern_char
            comparisons.append((text_index, j, text_char, pattern_char, matched))

            if not matched:
                break

            j -= 1

        if j < 0:
            rightmost = text[i + pattern_len - 1]
            shift = max(1, skip.get(rightmost, pattern_len))
            reason = f"All compared chars matched. Found pattern at index {i}."

            steps.append(
                BMHStep(
                    alignment=i,
                    comparisons=comparisons,
                    is_match=True,
                    shift=shift,
                    reason=reason,
                )
            )

            if first_match == -1:
                first_match = i
            if stop_on_first_match:
                break

            i += shift
            continue

        rightmost = text[i + pattern_len - 1]
        shift = max(1, skip.get(rightmost, pattern_len))
        mismatch_text_index = i + j
        reason = (
            f"Mismatch at text[{mismatch_text_index}] and pattern[{j}]. "
            f"Rightmost aligned char '{display_char(rightmost)}' shifts by {shift}."
        )

        steps.append(
            BMHStep(
                alignment=i,
                comparisons=comparisons,
                is_match=False,
                shift=shift,
                reason=reason,
            )
        )

        i += shift

    if i <= last_alignment and len(steps) >= max_steps:
        steps.append(
            BMHStep(
                alignment=i,
                comparisons=[],
                is_match=False,
                shift=0,
                reason=f"Trace truncated at {max_steps} steps to keep the UI responsive.",
            )
        )

    return steps, first_match, skip
