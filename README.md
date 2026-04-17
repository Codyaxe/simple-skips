# 🔍 Simple Skips Text Editor

```
                     (                                 (                        
                     )\ )                    (         )\ )    )                
                    (()/( (      )           )\   (   (()/( ( /( (              
                     /(_)))\    (     `  )  ((_) ))\   /(_)))\()))\  `  )   (   
                    (_)) ((_)   )\  ' /(/(   _  /((_) (_)) ((_)\((_) /(/(   )\  
                    / __| (_) _((_)) ((_)_\ | |(_))   / __|| |(_)(_)((_)_\ ((_) 
                    \__ \ | || '  \()| '_ \)| |/ -_)  \__ \| / / | || '_ \)(_-< 
                    |___/ |_||_|_|_| | .__/ |_|\___|  |___/|_\_\ |_|| .__/ /__/ 
                                     |_|                            |_|         
```

## 📝 Description
This project is a Python desktop text editor built with **Tkinter**. It uses the **Boyer-Moore-Horspool (BMH)** string matching algorithm for find/replace and includes an interactive visual trace panel to show exactly how matching works—step by step.

Perfect for learning algorithm visualization or just need a solid find/replace editor with dark mode.

## ✨ Features
- 📄 **Text editing** with open, save, and save-as support
- 🔎 **Find & Replace** (Next/All) powered by Boyer-Moore-Horspool
- 🎬 **Step-by-step visualization** with match/mismatch highlighting
- ⏯️ **Animated playback** with adjustable speed control
- 📊 **Skip table display** for the active pattern
- 🌙 **Dark mode toggle** for comfortable editing
- 👁️ **View toggle** to show/hide visualization panel

## 🏗️ Architecture
Modular, component-based design for maintainability:

```
bmh_app/
├── main_window.py          ← Main orchestrator (891 lines)
├── core/
│   └── theme_manager.py    ← Centralized theme system
├── components/
│   ├── editor_panel.py     ← Text editor with syntax highlighting
│   ├── search_bar.py       ← Find/replace controls
│   ├── visualization_panel.py  ← BMH trace rendering
│   └── performance_window.py   ← Performance evaluation popup
└── ui_utils/
    ├── dropdown_menu.py    ← Custom themed dropdown
    └── custom_menu_bar.py  ← Custom styled menu bar

bmh_logic/                  ← Algorithm package
├── __init__.py
└── core.py                 ← BMH implementation
```

**Design pattern:** Event-driven callbacks for component communication, no tight coupling.

## 🧠 Algorithm: Boyer-Moore-Horspool

BMH is a **fast string matching algorithm** that excels at finding patterns in text:

1. **Skip table generation** — precompute jumps for each character in the pattern
2. **Right-to-left comparison** — compare pattern and text from right to left
3. **Intelligent skipping** — on mismatch, skip multiple positions using the skip table
4. **Repeat until found** — continue until match or text exhausted

**Why BMH here:**
- ⚡ Much faster average case than naive matching
- 📚 Excellent for interactive find/replace workflows  
- 🎓 Highly visual and educational to trace step-by-step

## 🚀 Run
```bash
python simple-skips.py
```

Or use the package directly:
```bash
python -m bmh_app
```
