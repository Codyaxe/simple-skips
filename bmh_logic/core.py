"""String matching algorithm implementations for visualization and benchmarking."""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, TypeAlias


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


def build_bad_character_table(pattern: str) -> Dict[str, int]:
    """Build the bad-character last-occurrence table for Boyer-Moore."""
    table: Dict[str, int] = {}
    for index, char in enumerate(pattern):
        table[char] = index
    return table


def build_good_suffix_table(pattern: str) -> List[int]:
    """Build the good-suffix shift table for Boyer-Moore."""
    pattern_len = len(pattern)
    shift = [0] * (pattern_len + 1)
    border_pos = [0] * (pattern_len + 1)

    i = pattern_len
    j = pattern_len + 1
    border_pos[i] = j

    while i > 0:
        while j <= pattern_len and pattern[i - 1] != pattern[j - 1]:
            if shift[j] == 0:
                shift[j] = j - i
            j = border_pos[j]
        i -= 1
        j -= 1
        border_pos[i] = j

    j = border_pos[0]
    for i in range(pattern_len + 1):
        if shift[i] == 0:
            shift[i] = j
        if i == j:
            j = border_pos[j]

    return shift


def build_lps_table(pattern: str) -> List[int]:
    """Build the longest-prefix-suffix (LPS) table for KMP."""
    lps = [0] * len(pattern)
    length = 0
    i = 1

    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1

    return lps


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


def bm_search(text: str, pattern: str, start: int = 0) -> int:
    """Return first match index using Boyer-Moore, or -1 if missing."""
    text_len = len(text)
    pattern_len = len(pattern)

    if pattern_len == 0:
        return max(0, min(start, text_len))
    if pattern_len > text_len:
        return -1

    bad_char = build_bad_character_table(pattern)
    good_suffix = build_good_suffix_table(pattern)

    alignment = max(0, start)
    last_alignment = text_len - pattern_len

    while alignment <= last_alignment:
        j = pattern_len - 1
        while j >= 0 and pattern[j] == text[alignment + j]:
            j -= 1
        if j < 0:
            return alignment

        bad_char_index = bad_char.get(text[alignment + j], -1)
        bad_char_shift = j - bad_char_index
        good_suffix_shift = good_suffix[j + 1]
        alignment += max(1, bad_char_shift, good_suffix_shift)

    return -1


def kmp_search(text: str, pattern: str, start: int = 0) -> int:
    """Return first match index using KMP, or -1 if missing."""
    text_len = len(text)
    pattern_len = len(pattern)

    if pattern_len == 0:
        return max(0, min(start, text_len))
    if pattern_len > text_len:
        return -1

    lps = build_lps_table(pattern)
    i = max(0, start)
    j = 0

    while i < text_len:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == pattern_len:
                return i - j
        elif j != 0:
            j = lps[j - 1]
        else:
            i += 1

    return -1


def naive_search(text: str, pattern: str, start: int = 0) -> int:
    """Return first match index using naive search, or -1 if missing."""
    text_len = len(text)
    pattern_len = len(pattern)

    if pattern_len == 0:
        return max(0, min(start, text_len))
    if pattern_len > text_len:
        return -1

    start = max(0, start)
    last_alignment = text_len - pattern_len

    for alignment in range(start, last_alignment + 1):
        if text[alignment : alignment + pattern_len] == pattern:
            return alignment

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


def bm_find_all(text: str, pattern: str, allow_overlap: bool = False) -> List[int]:
    """Return all match positions using Boyer-Moore."""
    if not pattern:
        return []

    positions: List[int] = []
    search_from = 0
    step = 1 if allow_overlap else len(pattern)

    while search_from <= len(text) - len(pattern):
        index = bm_search(text, pattern, search_from)
        if index == -1:
            break

        positions.append(index)
        search_from = index + step

    return positions


def kmp_find_all(text: str, pattern: str, allow_overlap: bool = False) -> List[int]:
    """Return all match positions using KMP."""
    if not pattern:
        return []

    positions: List[int] = []
    text_len = len(text)
    pattern_len = len(pattern)
    lps = build_lps_table(pattern)

    i = 0
    j = 0
    while i < text_len:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == pattern_len:
                match_start = i - j
                positions.append(match_start)
                if allow_overlap:
                    j = lps[j - 1]
                else:
                    j = 0
                    i = match_start + pattern_len
        elif j != 0:
            j = lps[j - 1]
        else:
            i += 1

    return positions


def naive_find_all(text: str, pattern: str, allow_overlap: bool = False) -> List[int]:
    """Return all match positions using naive search."""
    if not pattern:
        return []

    positions: List[int] = []
    text_len = len(text)
    pattern_len = len(pattern)
    step = 1 if allow_overlap else pattern_len

    alignment = 0
    while alignment <= text_len - pattern_len:
        if text[alignment : alignment + pattern_len] == pattern:
            positions.append(alignment)
            alignment += step
        else:
            alignment += 1

    return positions


@dataclass
class BMHStep:
    alignment: int
    comparisons: List[Tuple[int, int, str, str, bool]]
    is_match: bool
    shift: int
    reason: str


TraceTable: TypeAlias = Dict[str, Any]
TraceResult: TypeAlias = Tuple[List[BMHStep], int, TraceTable]


def _build_skip_table_rows(pattern: str, skip: Dict[str, int]) -> List[str]:
    rows = [f"Default shift: {len(pattern)}"]

    if skip:
        rows.append("Custom shifts:")
        for char in sorted(skip.keys()):
            rows.append(f"  '{display_char(char)}' -> {skip[char]}")
    else:
        rows.append("Pattern length is 1, so only default shift is used.")
    return rows


def _build_lps_table_rows(pattern: str, lps: List[int]) -> List[str]:
    rows = ["Index : " + " ".join(str(i).rjust(2) for i in range(len(pattern)))]
    rows.append("Char  : " + " ".join(display_char(ch).rjust(2) for ch in pattern))
    rows.append("LPS   : " + " ".join(str(val).rjust(2) for val in lps))
    return rows


def _build_bm_table_rows(
    pattern: str,
    bad_char: Dict[str, int],
    good_suffix: List[int],
) -> List[str]:
    rows = ["Bad-character table:"]
    if bad_char:
        for char in sorted(bad_char.keys()):
            rows.append(f"  '{display_char(char)}' -> {bad_char[char]}")
    else:
        rows.append("  (pattern length is 0)")

    rows.append("")
    rows.append("Good-suffix shifts (index -> shift):")
    for index, shift in enumerate(good_suffix):
        rows.append(f"  {index} -> {shift}")
    return rows


def bmh_trace(
    text: str,
    pattern: str,
    start: int = 0,
    stop_on_first_match: bool = True,
    max_steps: int = 250,
) -> TraceResult:
    """Collect step-by-step BMH states for visualization."""
    if not pattern:
        return [], -1, {"title": "Skip Table", "rows": ["No pattern set."]}

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
            {
                "title": "Skip Table",
                "rows": _build_skip_table_rows(pattern, skip),
            },
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
            {
                "title": "Skip Table",
                "rows": _build_skip_table_rows(pattern, skip),
            },
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

    return (
        steps,
        first_match,
        {"title": "Skip Table", "rows": _build_skip_table_rows(pattern, skip)},
    )


def bm_trace(
    text: str,
    pattern: str,
    start: int = 0,
    stop_on_first_match: bool = True,
    max_steps: int = 250,
) -> TraceResult:
    """Collect step-by-step Boyer-Moore states for visualization."""
    if not pattern:
        return [], -1, {"title": "BM Tables", "rows": ["No pattern set."]}

    text_len = len(text)
    pattern_len = len(pattern)
    bad_char = build_bad_character_table(pattern)
    good_suffix = build_good_suffix_table(pattern)

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
            {
                "title": "BM Tables",
                "rows": _build_bm_table_rows(pattern, bad_char, good_suffix),
            },
        )

    last_alignment = text_len - pattern_len
    alignment = max(0, start)
    if alignment > last_alignment:
        return (
            [
                BMHStep(
                    alignment=last_alignment,
                    comparisons=[],
                    is_match=False,
                    shift=0,
                    reason=(
                        f"Start index {alignment} is beyond the last valid alignment "
                        f"({last_alignment}), so no comparisons were possible "
                        "from that start."
                    ),
                )
            ],
            -1,
            {
                "title": "BM Tables",
                "rows": _build_bm_table_rows(pattern, bad_char, good_suffix),
            },
        )

    steps: List[BMHStep] = []
    first_match = -1

    while alignment <= last_alignment and len(steps) < max_steps:
        j = pattern_len - 1
        comparisons: List[Tuple[int, int, str, str, bool]] = []

        while j >= 0:
            text_index = alignment + j
            text_char = text[text_index]
            pattern_char = pattern[j]
            matched = text_char == pattern_char
            comparisons.append((text_index, j, text_char, pattern_char, matched))
            if not matched:
                break
            j -= 1

        if j < 0:
            reason = f"All compared chars matched. Found pattern at index {alignment}."
            steps.append(
                BMHStep(
                    alignment=alignment,
                    comparisons=comparisons,
                    is_match=True,
                    shift=0,
                    reason=reason,
                )
            )

            if first_match == -1:
                first_match = alignment
            if stop_on_first_match:
                break

            shift = good_suffix[0]
            alignment += max(1, shift)
            continue

        bad_char_index = bad_char.get(text[alignment + j], -1)
        bad_char_shift = j - bad_char_index
        good_suffix_shift = good_suffix[j + 1]
        shift = max(1, bad_char_shift, good_suffix_shift)
        reason = (
            f"Mismatch at text[{alignment + j}] and pattern[{j}]. "
            f"Bad-char shift {bad_char_shift}, good-suffix shift {good_suffix_shift}."
        )

        steps.append(
            BMHStep(
                alignment=alignment,
                comparisons=comparisons,
                is_match=False,
                shift=shift,
                reason=reason,
            )
        )

        alignment += shift

    if alignment <= last_alignment and len(steps) >= max_steps:
        steps.append(
            BMHStep(
                alignment=alignment,
                comparisons=[],
                is_match=False,
                shift=0,
                reason=f"Trace truncated at {max_steps} steps to keep the UI responsive.",
            )
        )

    return (
        steps,
        first_match,
        {
            "title": "BM Tables",
            "rows": _build_bm_table_rows(pattern, bad_char, good_suffix),
        },
    )


def kmp_trace(
    text: str,
    pattern: str,
    start: int = 0,
    stop_on_first_match: bool = True,
    max_steps: int = 250,
) -> TraceResult:
    """Collect step-by-step KMP states for visualization."""
    if not pattern:
        return [], -1, {"title": "LPS Table", "rows": ["No pattern set."]}

    text_len = len(text)
    pattern_len = len(pattern)
    lps = build_lps_table(pattern)

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
            {"title": "LPS Table", "rows": _build_lps_table_rows(pattern, lps)},
        )

    i = max(0, start)
    j = 0
    steps: List[BMHStep] = []
    first_match = -1

    while i < text_len and len(steps) < max_steps:
        alignment = i - j
        comparisons: List[Tuple[int, int, str, str, bool]] = []

        while i < text_len and j < pattern_len and text[i] == pattern[j]:
            comparisons.append((i, j, text[i], pattern[j], True))
            i += 1
            j += 1
            if j == pattern_len:
                break

        if j == pattern_len:
            match_index = i - j
            reason = f"Matched pattern at index {match_index}."
            steps.append(
                BMHStep(
                    alignment=alignment,
                    comparisons=comparisons,
                    is_match=True,
                    shift=0,
                    reason=reason,
                )
            )

            if first_match == -1:
                first_match = match_index
            if stop_on_first_match:
                break

            new_j = lps[j - 1]
            new_alignment = i - new_j
            shift = max(1, new_alignment - alignment)
            steps[-1].shift = shift
            steps[-1].reason = (
                f"Matched pattern at index {match_index}. Shift by {shift} using LPS."
            )
            j = new_j
            continue

        if i >= text_len:
            break

        comparisons.append((i, j, text[i], pattern[j], False))

        if j != 0:
            new_j = lps[j - 1]
            new_alignment = i - new_j
            shift = max(1, new_alignment - alignment)
            reason = (
                f"Mismatch at text[{i}] and pattern[{j}]. "
                f"Shift by {shift} using LPS."
            )
            j = new_j
        else:
            i += 1
            new_alignment = i - j
            shift = max(1, new_alignment - alignment)
            reason = f"Mismatch at text[{i - 1}] and pattern[0]. Shift by 1."

        steps.append(
            BMHStep(
                alignment=alignment,
                comparisons=comparisons,
                is_match=False,
                shift=shift,
                reason=reason,
            )
        )

    if len(steps) >= max_steps:
        steps.append(
            BMHStep(
                alignment=max(0, i - j),
                comparisons=[],
                is_match=False,
                shift=0,
                reason=f"Trace truncated at {max_steps} steps to keep the UI responsive.",
            )
        )

    return (
        steps,
        first_match,
        {"title": "LPS Table", "rows": _build_lps_table_rows(pattern, lps)},
    )


def naive_trace(
    text: str,
    pattern: str,
    start: int = 0,
    stop_on_first_match: bool = True,
    max_steps: int = 250,
) -> TraceResult:
    """Collect step-by-step naive search states for visualization."""
    if not pattern:
        return [], -1, {"title": "Naive", "rows": ["No pattern set."]}

    text_len = len(text)
    pattern_len = len(pattern)
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
            {"title": "Naive", "rows": ["No auxiliary table for naive search."]},
        )

    last_alignment = text_len - pattern_len
    alignment = max(0, start)
    if alignment > last_alignment:
        return (
            [
                BMHStep(
                    alignment=last_alignment,
                    comparisons=[],
                    is_match=False,
                    shift=0,
                    reason=(
                        f"Start index {alignment} is beyond the last valid alignment "
                        f"({last_alignment}), so no comparisons were possible "
                        "from that start."
                    ),
                )
            ],
            -1,
            {"title": "Naive", "rows": ["No auxiliary table for naive search."]},
        )

    steps: List[BMHStep] = []
    first_match = -1

    while alignment <= last_alignment and len(steps) < max_steps:
        comparisons: List[Tuple[int, int, str, str, bool]] = []
        j = 0
        while j < pattern_len:
            text_index = alignment + j
            matched = text[text_index] == pattern[j]
            comparisons.append((text_index, j, text[text_index], pattern[j], matched))
            if not matched:
                break
            j += 1

        if j == pattern_len:
            reason = f"All compared chars matched. Found pattern at index {alignment}."
            steps.append(
                BMHStep(
                    alignment=alignment,
                    comparisons=comparisons,
                    is_match=True,
                    shift=0 if stop_on_first_match else 1,
                    reason=reason,
                )
            )
            if first_match == -1:
                first_match = alignment
            if stop_on_first_match:
                break
            alignment += 1
            continue

        reason = f"Mismatch at text[{alignment + j}] and pattern[{j}]. Shift by 1."
        steps.append(
            BMHStep(
                alignment=alignment,
                comparisons=comparisons,
                is_match=False,
                shift=1,
                reason=reason,
            )
        )
        alignment += 1

    if alignment <= last_alignment and len(steps) >= max_steps:
        steps.append(
            BMHStep(
                alignment=alignment,
                comparisons=[],
                is_match=False,
                shift=0,
                reason=f"Trace truncated at {max_steps} steps to keep the UI responsive.",
            )
        )

    return (
        steps,
        first_match,
        {"title": "Naive", "rows": ["No auxiliary table for naive search."]},
    )
