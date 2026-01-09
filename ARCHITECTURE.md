# Architecture

How the Presentation Generator works, why decisions were made, and where to change things.

---

## Overview

```
README.md → parse_readme() → generate_slides() → render_html() → presentation.html
```

Four functions. That's the entire pipeline.

---

## Data Flow

### 1. Parsing (`parse_readme`)

Reads the markdown file and extracts structured data:

```python
{
    'title': 'Project Name',
    'tagline': 'Short description',
    'sections': [...],      # All H2 sections
    'features': [...],      # Detected feature lists
    'tech_stack': [...],    # Technology mentions
    'installation': [...],  # Setup steps
    'raw_sections': {...}   # Section content by lowercase name
}
```

**Key patterns:**
- Title = first H1
- Tagline = first paragraph after title
- Sections = split by H2 headers
- List items = bullet points or numbered lists

**Why regex instead of a markdown parser?**
No dependencies. The stdlib `re` module handles 95% of cases. Edge cases get cleaned up manually or ignored. This isn't parsing arbitrary markdown—it's parsing READMEs you control.

### 2. Slide Generation (`generate_slides`)

Converts parsed data into slide definitions:

```python
[
    {'type': 'title', 'title': '...', 'tagline': '...'},
    {'type': 'features', 'title': 'Key Features', 'items': [...]},
    {'type': 'grid', 'title': 'Tech Stack', 'items': [...]},
    {'type': 'steps', 'title': 'Getting Started', 'items': [...]},
    {'type': 'content', 'title': 'Section Name', 'items': [...]},
    {'type': 'closing', 'title': '...', 'contact': {...}}
]
```

**Slide types:**
- `title` - Opening slide with project name
- `features` - 3-column grid with feature cards
- `grid` - 3-column grid for tech stack
- `steps` - Numbered installation steps
- `roadmap` - Two-column completed/planned
- `content` - Default bullet list
- `closing` - Final slide with contact info

**Section detection:**
Sections are categorized by keywords in the title. "Features" goes to features. "Installation" goes to steps. Everything else becomes content slides.

### 3. HTML Rendering (`render_html`)

Assembles complete HTML:

1. `get_template_head()` - DOCTYPE, meta, all CSS
2. `get_theme_panel()` - Theme selector HTML
3. `render_slide()` - Each slide's HTML
4. `get_template_scripts()` - Navigation and theme JavaScript

**Why inline everything?**
One file output. No external CSS or JS files to manage. The HTML file is completely self-contained. You can email it, upload it, open it offline.

---

## Theme System

### CSS Variables

```css
:root {
    --primary-gradient: linear-gradient(...);
    --accent-color: #ffd700;
    --accent-dim: #ccac00;
    --secondary-color: #87ceeb;
    --text-color: #ffffff;
    --text-muted: rgba(255, 255, 255, 0.7);
    --card-bg: rgba(255, 255, 255, 0.1);
    --card-border: rgba(255, 255, 255, 0.1);
}
```

### JavaScript Theme Functions

Each theme category has a setter:
- `setBackground(id, name, value)`
- `setAccent(id, name, accent, accentDim, secondary)`
- `setCard(id, name, bg, border)`
- `setFont(id, name, color, muted)`

Setters update:
1. CSS custom properties
2. Preview swatches in theme panel
3. Active state on theme options
4. localStorage for persistence

### Persistence

```javascript
localStorage.setItem('presentation_bg', JSON.stringify({...}));
localStorage.setItem('presentation_accent', JSON.stringify({...}));
localStorage.setItem('presentation_card', JSON.stringify({...}));
localStorage.setItem('presentation_font', JSON.stringify({...}));
```

Loaded on page load via `loadSavedThemes()`.

---

## Navigation

### Keyboard

```javascript
document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
    else if (e.key === 'ArrowLeft') previousSlide();
    else if (e.key === 'Escape') closeThemePanel();
});
```

### Touch

Swipe detection with 50px threshold:

```javascript
document.addEventListener('touchstart', (e) => startX = e.changedTouches[0].screenX);
document.addEventListener('touchend', (e) => {
    endX = e.changedTouches[0].screenX;
    if (startX - endX > 50) nextSlide();
    else if (endX - startX > 50) previousSlide();
});
```

### Slide Visibility

CSS-based transitions:

```css
.slide {
    opacity: 0;
    visibility: hidden;
    transition: all 0.5s ease;
}

.slide.active {
    opacity: 1;
    visibility: visible;
}
```

---

## Extension Points

### Adding a New Slide Type

1. Add detection in `generate_slides()`:
```python
elif any(word in title_lower for word in ['demo', 'example']):
    slides.append({
        'type': 'demo',
        'title': section['title'],
        'content': section['content']
    })
```

2. Add rendering in `render_slide()`:
```python
elif slide_type == 'demo':
    return f'''
    <div class="slide{active_class}">
        <h2>{slide['title']}</h2>
        <div class="demo-container">
            <pre><code>{slide['content']}</code></pre>
        </div>
    </div>'''
```

3. Add CSS in `get_template_head()`.

### Adding Theme Options

In `get_theme_panel()`, add a new option:

```html
<div class="theme-option" data-type="bg"
     onclick="setBackground('my-theme', 'My Theme', '#color')">
    <div class="theme-swatch" style="background: #color;"></div>
    <div class="theme-info">
        <div class="theme-name">My Theme</div>
        <div class="theme-desc">Description</div>
    </div>
</div>
```

### Changing Default Themes

Modify `:root` in `get_template_head()` and the `active` classes in `get_theme_panel()`.

---

## Why This Design

### Single File Generator

**Pro:** No build step, no package management, works anywhere Python exists.
**Con:** File is 1700 lines. Not modular.

Tradeoff accepted because the use case is "run once, get HTML."

### Inline Everything

**Pro:** Output is one portable file.
**Con:** Can't cache CSS/JS separately. Larger file size.

Tradeoff accepted because presentations are viewed once, shared by email/upload, and file size is under 100KB.

### Regex Parsing

**Pro:** No dependencies, fast, good enough for READMEs.
**Con:** Breaks on edge cases, not a proper markdown parser.

Tradeoff accepted because you control your README. If parsing fails, fix the README.

### CSS Variables for Theming

**Pro:** Runtime theme switching without regenerating HTML.
**Con:** Browser must support CSS custom properties (IE11 doesn't).

Tradeoff accepted because IE11 is dead.

---

*Architecture decisions should be questioned. If this doesn't fit your needs, fork it.*
