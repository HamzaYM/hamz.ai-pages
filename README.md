# hamz.ai-pages

Source for the hosted interactive pages behind [hamz.ai](https://www.hamz.ai). These are the standalone HTML pages that the Framer landing site embeds and links to: the lab (research write-ups, the effort lattice, the skills library, field notes), the builder page, the agentic-systems design guide, anonymized client work case studies, a case-study playtest write-up, and the Clara prototype showcase. Each page is a single self-contained HTML file (inline CSS + JS, Google Fonts as the only external dependency).

This repo is the source of truth for these pages. The Framer landing site (www.hamz.ai) is managed separately inside Framer and is not checked in here; it embeds and links to the pages below via their GitHub Pages URLs.

## Live URLs

Served via GitHub Pages from the `main` branch at `https://hamzaym.github.io/hamz.ai-pages/`:

- Lab: https://hamzaym.github.io/hamz.ai-pages/lab/
- Builder: https://hamzaym.github.io/hamz.ai-pages/builder/
- Designing agentic systems: https://hamzaym.github.io/hamz.ai-pages/designing-agentic-ai/
- Work case studies: https://hamzaym.github.io/hamz.ai-pages/work/
- Case playtesting: https://hamzaym.github.io/hamz.ai-pages/case-playtesting/
- Clara showcase: https://hamzaym.github.io/hamz.ai-pages/clara/

The repo root `index.html` is a meta-refresh redirect to the live homepage, `https://www.hamz.ai`.

## Structure

```
index.html                 redirect to https://www.hamz.ai
lab/
  index.html                landing page for the lab
  lattice/                  the effort lattice research study (+ explorer/, tasks/, visual/ subpages)
  skills/index.html         the skills library
  evidence/index.html       the skills study
  learn/index.html          glossary / how-this-works page
  chain/index.html          the Assurance Chain methodology page
  notes/index.html          dated field notes
  proof/index.html          artifacts page
  og/                       social-preview images
builder/
  index.html                monthly "what I'm building" page
  og/                       social-preview images
designing-agentic-ai/
  index.html                field guide on agentic system design
  visual/index.html         the same guide as a 3D walkthrough
work/
  advisory-overnight/index.html   case study: capital-markets advisory platform
  aviation-operations/index.html  case study: business-aviation feasibility engine
case-playtesting/
  index.html                case-study playtest write-up
clara/
  index.html                Clara prototype showcase page
  clara-letter.png          image asset
  clara-overview.png        image asset
scripts/
  verify-lab-claims.py      self-auditing verifier for claims made on the lab pages
  lab-claims.json           the claims verify-lab-claims.py checks
llms.txt                    machine-readable site index for AI crawlers
```

## Deploy

GitHub Pages, `main` branch, root directory. Any push to `main` redeploys automatically (usually live within about a minute). No build step - the files are served as-is. There is no CI/CD; commit and push and Pages picks it up.
