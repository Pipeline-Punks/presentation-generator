# Failure Modes

Things that break and why. Check here before opening an issue.

---

## Parsing Failures

### Title Not Detected

**Symptom:** Presentation shows empty title or "Presentation"

**Cause:** No H1 header in README, or H1 has unusual formatting

**Check:**
```markdown
# This works
#This doesn't (no space)
## This is H2, not title
```

**Fix:** Ensure first line is `# Title` with a space after the hash.

---

### Features Not Recognized

**Symptom:** Features appear as regular content slides instead of card grid

**Cause:** Section header doesn't contain keywords: `feature`, `capability`, `what`, `highlight`

**Fix:** Rename section to "Features" or "Key Features" or "What It Does"

---

### Installation Steps Missing Numbers

**Symptom:** Setup section renders as bullets instead of numbered steps

**Cause:** Section isn't detected as installation type

**Check:** Section title must contain: `install`, `setup`, `getting started`, `quick start`

**Fix:** Rename section or use the `steps` slide type detection keywords.

---

### Empty Sections

**Symptom:** Slides with title but no content

**Cause:** Section has only prose text (no list items), and text is treated as empty

**Debug:** The parser extracts list items. Paragraphs without bullets are often ignored.

**Fix:** Add bullet points to your content, or modify `extract_list_items()` to handle paragraphs.

---

### Code Blocks Not Rendered

**Symptom:** Code blocks disappear or appear as plain text

**Cause:** Code block extraction only works in `usage` sections by default

**Fix:** Modify `extract_code_blocks()` usage in `generate_slides()` to include your section.

---

## Theme Failures

### Themes Not Saving

**Symptom:** Theme resets on page reload

**Cause:** localStorage blocked or full

**Check:**
1. Private/incognito mode blocks localStorage
2. Browser storage quota exceeded
3. localStorage disabled in settings

**Debug:**
```javascript
// In browser console
localStorage.setItem('test', 'value');
console.log(localStorage.getItem('test'));
```

**Fix:** Use regular browsing mode, or clear localStorage.

---

### Theme Panel Won't Open

**Symptom:** Click "Themes" button, nothing happens

**Cause:** JavaScript error blocking execution

**Debug:** Open browser console (F12), check for errors

**Common causes:**
1. Missing closing tag in HTML
2. Syntax error if you modified the script
3. Content Security Policy blocking inline scripts

**Fix:** Check browser console, restore original script if modified.

---

### Light Background + Light Text

**Symptom:** Text invisible on light backgrounds

**Cause:** User selected white/cream background but didn't change font color

**Fix:** After selecting light background, select dark font color (black, dark gray).

---

### Theme Looks Different Across Browsers

**Symptom:** Gradients or transparency render differently

**Cause:** Browser-specific rendering of:
- `linear-gradient()` syntax variations
- `backdrop-filter: blur()` (Safari handles differently)
- RGBA transparency

**Fix:** Not really fixable without browser-specific CSS. Accept minor variations.

---

## Navigation Failures

### Keyboard Not Working

**Symptom:** Arrow keys don't change slides

**Cause:** Focus is in input field or theme panel

**Fix:** Click anywhere on the slide area, press Escape to close panels.

---

### Swipe Not Working

**Symptom:** Touch navigation fails on mobile

**Cause:** Swipe distance under 50px threshold

**Fix:** Use longer, deliberate swipes. Or use arrow buttons.

---

### Slides Show Stacked

**Symptom:** All slides visible at once, overlapping

**Cause:** CSS not applied, or JavaScript didn't initialize

**Debug:**
1. Check if `.active` class exists on first slide
2. Check if `slides` variable has correct count in console
3. Look for CSS loading errors

**Fix:** Ensure no CSS modifications broke `.slide` positioning.

---

## Generation Failures

### Script Won't Run

**Symptom:** `python generate_presentation.py` fails immediately

**Cause:** Python not installed, wrong version, or path issues

**Check:**
```bash
python --version  # Must be 3.6+
python3 --version  # Try this on Mac/Linux
```

**Fix:** Install Python 3.6+ or use correct command (`python3`).

---

### File Not Found

**Symptom:** "README file not found" error

**Cause:** Path is wrong or file doesn't exist

**Check:**
```bash
ls README.md  # Does it exist?
pwd  # Are you in the right directory?
```

**Fix:** Provide correct path: `python generate_presentation.py ./docs/README.md`

---

### Encoding Errors

**Symptom:** `UnicodeDecodeError` on Windows

**Cause:** File has non-UTF8 encoding

**Fix:**
1. Open README in editor, save as UTF-8
2. Or modify script: `open(readme_path, 'r', encoding='latin-1')`

---

### Output File Not Created

**Symptom:** Script runs but no HTML file appears

**Cause:** Permission error or disk full

**Check:**
```bash
touch test.html  # Can you create files?
df -h  # Disk space?
```

**Fix:** Check permissions, try different output directory.

---

## Content Quality Issues

### Slides Too Dense

**Symptom:** Too many items crammed on one slide

**Cause:** Default `max_items_per_slide` is 6, but section has more

**Fix:** Use config file:
```json
{
  "slides": {
    "max_items_per_slide": 4
  }
}
```

Or split section in README into multiple H2 sections.

---

### Feature Cards Too Wide

**Symptom:** Feature text overflows card boundaries

**Cause:** Feature description too long for 3-column grid

**Fix:** Shorten feature descriptions, or modify CSS grid to 2 columns.

---

### Contact Info Missing

**Symptom:** Closing slide shows no contact links

**Cause:** Contact section doesn't contain recognizable patterns

**Parser looks for:**
- Email: `user@domain.com` pattern
- GitHub: `github.com/username`
- Website: `https://...`
- LinkedIn: `linkedin.com/in/username`

**Fix:** Ensure contact section uses these formats.

---

## Edge Cases

### Nested Lists

**Not supported.** Only top-level list items are extracted.

```markdown
- Item 1
  - Subitem  # This is ignored
- Item 2
```

**Workaround:** Flatten lists, or combine into single items.

---

### Tables

**Not supported.** Tables are ignored by the parser.

**Workaround:** Convert table data to bullet points, or screenshot table as image.

---

### Images

**Not parsed.** Images in README don't appear in slides.

**Workaround:** Add images manually to generated HTML, or modify `render_slide()` to handle image markdown.

---

### Multiple H1 Headers

**Only first H1 is used.** Additional H1s are ignored.

**Fix:** Use H2 for subsequent major sections.

---

## Recovery

### Regenerate from Scratch

If things are broken:
```bash
# Remove generated file
rm presentation.html

# Regenerate
python generate_presentation.py README.md presentation.html
```

### Reset Themes

In browser console:
```javascript
localStorage.removeItem('presentation_bg');
localStorage.removeItem('presentation_accent');
localStorage.removeItem('presentation_card');
localStorage.removeItem('presentation_font');
location.reload();
```

Or click "Reset to Defaults" in theme panel.

---

*Most failures are quick to diagnose. If you're stuck, re-read the README parsing rules.*
