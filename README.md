# Presentation Generator

**Turn your README into a presentation. No PowerPoint. No Canva. No subscriptions.**

```bash
# Clone and run
git clone https://github.com/Jjohnston70/presentation-generator.git
cd presentation-generator
python generate_presentation.py your-readme.md slides.html
open slides.html
```

---

## What This Is

A Python script that converts any README.md into a themeable HTML slide presentation.

Zero dependencies. Python standard library only. One file does everything.

---

## Why This Exists

You wrote documentation. Now someone wants a "deck" for a meeting. You have two options:

1. Copy-paste into PowerPoint, fight with formatting, export to PDF, email it, wait for feedback
2. Run one command

This is option 2.

---

## What It Does

- **Parses README.md** - Extracts title, features, tech stack, installation steps, sections
- **Generates HTML slides** - One file, no build step, opens in any browser
- **Includes theme selector** - 40+ theme combinations (background, accent, card, font)
- **Saves preferences** - localStorage persistence, no accounts
- **Works offline** - No CDN dependencies, no internet required
- **Mobile ready** - Touch/swipe navigation, responsive layout

---

## Requirements

- Python 3.6+
- That's it

---

## Usage

```bash
# Basic - uses README.md in current directory
python generate_presentation.py

# Specify input and output
python generate_presentation.py path/to/README.md output.html

# With config file for custom theming
python generate_presentation.py README.md presentation.html config.json
```

---

## What Gets Parsed

The script looks for standard README sections:

| Section Type | Becomes |
|--------------|---------|
| Title (H1) | Title slide |
| Features/Highlights | Feature grid cards |
| Tech Stack/Built With | Grid layout |
| Installation/Setup | Numbered steps |
| Roadmap/Status | Two-column completed/planned |
| Contact/Author | Closing slide with links |
| Everything else | Bullet point slides |

---

## Theme Selector

Click "Themes" on the right edge. Four sections:

1. **Background** - 11 options (gradients + solids, dark + light)
2. **Accent Color** - 11 options (gold, cyan, burnt orange, etc.)
3. **Card Style** - 8 options (glass transparency levels, solid colors)
4. **Font Color** - 8 options (white, black, grays, cream)

Mix and match. Preferences save to localStorage.

---

## Config File (Optional)

```json
{
  "theme": {
    "primary_gradient": "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)",
    "accent_color": "#ffd700"
  },
  "slides": {
    "max_items_per_slide": 6,
    "max_features": 9
  },
  "company": {
    "name": "Your Company Name"
  },
  "date": "January 2026"
}
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Right Arrow / Space | Next slide |
| Left Arrow | Previous slide |
| Escape | Close theme panel |

---

## Tradeoffs

**What it does well:**
- Fast iteration (change README, regenerate, refresh)
- No vendor lock-in
- Works on any machine with Python
- Self-contained output (one HTML file)

**What it doesn't do:**
- No speaker notes
- No animations beyond slide transitions
- No collaborative editing
- No export to PDF (use browser print)

---

## When to Use Something Else

- **Complex diagrams** - Use Mermaid or draw.io, embed as images in README
- **Live demos** - Screen share instead
- **Team collaboration** - Google Slides still wins for real-time editing
- **Print handouts** - Export from browser (Ctrl+P), but it's not optimized for print

---

## File Structure

```
presentation-generator/
├── README.md              # This file
├── generate_presentation.py  # The generator script
├── ARCHITECTURE.md        # How the code works
├── FAILURES.md            # What breaks and why
└── examples/
    ├── sample-readme.md   # Example input
    └── sample-output.html # Generated presentation
```

---

## Fork It

This is meant to be modified. Common customizations:

1. **Add your logo** - Edit `get_template_head()`, add an image
2. **Change default theme** - Modify CSS variables in `:root`
3. **Add slide types** - Create new `render_slide()` conditions
4. **Parse different formats** - Modify regex patterns in `parse_readme()`

---

## License

MIT. Do whatever you want.

---

*Part of [Pipeline Punks](https://www.pipelinepunks.com) - documentation for builders who learn by wiring real systems.*
