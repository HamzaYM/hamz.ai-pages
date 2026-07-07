# hamz.ai-pages

Source for the hosted interactive pages behind [hamz.ai](https://www.hamz.ai). These are the standalone HTML pages that the Framer landing site embeds and links to: a living resume, a case-study playtest write-up, and the Clara prototype showcase. Each page is a single self-contained HTML file (inline CSS + JS, Google Fonts as the only external dependency).

This repo is the source of truth for these pages. The Framer landing site (www.hamz.ai) is managed separately inside Framer and is not checked in here; it embeds the pages below via their GitHub Pages URLs.

## Live URLs

Served via GitHub Pages from the `main` branch at `https://hamzaym.github.io/hamz.ai-pages/`:

- Resume: https://hamzaym.github.io/hamz.ai-pages/resume/
- Resume admin editor: https://hamzaym.github.io/hamz.ai-pages/resume/edit/
- Case playtesting: https://hamzaym.github.io/hamz.ai-pages/case-playtesting/
- Clara showcase: https://hamzaym.github.io/hamz.ai-pages/clara/

The repo root `index.html` is a meta-refresh redirect to `/resume/`.

## Structure

```
index.html                 redirect to /resume/
resume/
  index.html               resume page shell; fetches resume-data.json and renders every section
  resume-data.json         all resume content (17 top-level sections) - edit this to change the resume
  edit/index.html          browser-based admin editor for resume-data.json (see below)
case-playtesting/
  index.html               case-study playtest write-up
clara/
  index.html               Clara prototype showcase page
  clara-letter.png         image asset
  clara-overview.png       image asset
```

### Resume data

`resume/index.html` is a static shell. On load it does `fetch("resume-data.json")` and boots the page from that JSON, so all content lives in `resume/resume-data.json`. Top-level keys:

`meta, identity, now, projects, tips, topologies, timeline, methods, selfref, education, teaching, awards, clubs, service, languages, interests, skills`

To change resume content, edit `resume-data.json` (directly or via the admin editor) - no HTML edits needed.

## Deploy

GitHub Pages, `main` branch, root directory. Any push to `main` redeploys automatically (usually live within about a minute). No build step - the files are served as-is. There is no CI/CD; commit and push and Pages picks it up.

## Resume admin editor

A client-only editor for `resume-data.json` at `/resume/edit/`. No backend - it talks directly to the GitHub Contents API from the browser.

- **Login**: a passphrase gate (client-side SHA-256 compare, remembered for the session). This is a friction gate, not real security - the write protection is the GitHub token below. To change the passphrase, replace `PASS_HASH` in `resume/edit/index.html` (a console snippet for generating the hash is in a comment in that file).
- **Load**: on unlock it pulls the live `resume-data.json` via the GitHub Contents API (capturing the file `sha`) and generates a recursive form - a collapsible panel per section, string/number/bool inputs, add/remove/reorder cards for arrays, inline editing for projects' nested metrics/deep-dives/links. A "Raw JSON" tab with live validation is the escape hatch.
- **Save**: paste a fine-grained GitHub PAT once (scoped to `HamzaYM/hamz.ai-pages`, Contents: Read and write). It is stored in `localStorage` with a Forget button. "Preview changes" shows the exact commit JSON and a changed-sections summary; "Confirm save" PUTs `resume/resume-data.json` back to the repo (refuses invalid JSON, handles 401/409 conflicts, optional date-stamp). On success the change is live in about a minute. Full PAT-creation instructions are in the editor's token panel.
