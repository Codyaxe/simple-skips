# Simple Skips Text Editor

## Description
This project is a Python desktop text editor built with Tkinter. It uses the
Boyer-Moore-Horspool (BMH) string matching algorithm for find/replace and
includes a visual trace panel to show how matching works step by step.

## Features
- Text editing area with open, save, and save-as support.
- Find Next, Find All, Replace Next, and Replace All using BMH.
- Step-by-step BMH visualization with match/mismatch highlighting.
- Animated trace playback with adjustable speed.
- Skip table display for the active search pattern.
- Dark mode toggle.
- View option to show or hide the visualization panel.

## Design
The codebase is split into small modules for easier maintenance:

- `simple-skips.py`: Application entry point.
- `bmh_gui.py`: GUI, menus, theme control, editor interactions, and visualization rendering.
- `bmh_logic.py`: BMH algorithm utilities (search, find-all, trace, skip-table generation).

Core design flow:

1. User enters text and search pattern.
2. GUI calls logic functions from `bmh_logic.py`.
3. Results are rendered in the editor and visualization panel.
4. Optional animation iterates through each recorded trace step.

## Algorithm Used
This project uses the **Boyer-Moore-Horspool (BMH)** algorithm.

BMH works by:

1. Building a skip table for the pattern.
2. Aligning the pattern with the text and comparing characters from right to left.
3. On mismatch, shifting by the skip-table value of the current aligned character.
4. Repeating until a match is found or the text is exhausted.

Why BMH here:

- Faster average-case behavior than naive left-to-right matching.
- Very suitable for interactive find/replace workflows.
- Easy to visualize through alignment, comparison, and shift steps.

## Run
```bash
python simple-skips.py
```
