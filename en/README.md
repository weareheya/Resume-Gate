# Resume-Gate

> Use AI to build your resume, but make sure every line has a source, every version can be traced, and every change goes through you.

A resume workflow for a long job search: **evidence bank → baseline resume → per-job delta → AI self-review → your sign-off → freeze**. It's docs, templates, and one layout-check script. It isn't tied to any AI or resume tool. Any AI that can read your files can follow it: Claude Code and Codex read `AGENTS.md` automatically, and with other tools you just point the AI at it.

## What it fixes

Mistakes that keep showing up when AI edits a resume:

| Problem | Mechanism |
|---|---|
| Results you already confirmed vanish from the next version | **Evidence Retrieval Gate**: the AI must read the evidence bank first and list what it read |
| A new version starts from an old one and old errors come back | **Baseline + Delta + Change Log**: always start from the latest approved version |
| Numbers get inflated or their meaning drifts | **Claim Card**: every number has a unit, scope, attribution, and a "don't rephrase as" list |
| The AI says "all checked" but skipped things | **Coverage Report**: spell out what was checked and what wasn't |
| A few stray lines spill onto a last page | **Full-page rule + `pdf_fill`**: the PDF must fill its pages, and a script measures it |
| The AI signs off on its own work | **Human review gate**: nothing is Approved until you say so, and sent versions are frozen |
| A strong experience gets dropped or written weakly because you described it in few words | **Probing questions + D-011 to D-016**: the AI asks before it filters, and picks the strongest wording the facts support |
| A corrected strength quietly comes back weaker | **Semantic check in self-review**: protected claims are compared with their approved wording, not just checked for presence |

## The flow

```
JD ─▶ pick type & baseline ─▶ read evidence (Gate) ─▶ map to JD ─▶ edit delta ─▶ Change Log
                                                                                    │
       Freeze (Sent) ◀─ You approve (Approved) ◀─ AI self-review + layout check ◀───┘
```

Details in [docs/WORKFLOW.md](docs/WORKFLOW.md).

## What's here

```
AGENTS.md                 Instructions for any AI that picks this up (read first)
docs/
  WORKFLOW.md             The seven steps and what each one produces
  REVIEW-CHECKLIST.md     AI self-review: facts / writing / layout / handoff format
  DECISIONS.md            Decision register, with 10 starter rules to adapt
  LESSONS.md              Common process mistakes and the guardrails against them
  PROMPTS.md              Copy-paste prompts for the common moments
evidence/claims/          Evidence bank: one Claim Card per accomplishment
cv/
  CV-INDEX.md             Lookup table: job type → current starting-point resume
  resumes/                The resume files themselves, one Markdown file per version
  changelogs/             What changed in each resume relative to its baseline
scripts/
  check_claims.py         Checks every bullet has a source, claims are usable, protected ones stay (Python 3)
  pdf_fill.swift          Renders each PDF page to PNG, checks the page count, and reports how far down the content reaches (macOS)
examples/                 A filled-in walkthrough using made-up data
```

## Quick start

1. Copy the contents of this folder (`en/`) into the root of your own job-search project.
2. Do **Step 0** in `docs/WORKFLOW.md`. It takes your existing resume and turns it into Claim Cards and a first approved baseline.
3. In `cv/CV-INDEX.md`, replace the example job types with your own.
4. For each new job, use prompt 3 in `docs/PROMPTS.md` and paste the JD.
5. After each resume: write the Change Log, update `CV-INDEX.md`, and record any new rules you settled on in `docs/DECISIONS.md`.

To check sourcing (any OS, needs Python 3):

```bash
python3 scripts/check_claims.py cv/resumes/<id>.md
```

To check layout (macOS, needs the Xcode command line tools):

```bash
mkdir -p /tmp/cv-check && swift scripts/pdf_fill.swift your-cv.pdf /tmp/cv-check
```

It prints the page count and how far down the content reaches on each page, and writes `p1.png`, `p2.png`, … so you can paste them to your AI or just look. If the page count isn't 1 or 2, or the content on the last page reaches less than 85% of the way down, it exits with code 2, so you can wire it into a script.

## What the scripts check, and what they don't

`check_claims.py` checks sourcing mechanically: every bullet has a Claim ID, each ID points to a `Safe to draft` card, and protected claims are still there. `pdf_fill.swift` checks the page count and how far down the content reaches. It can't measure how much of each page is used, so look at the images too. Everything else is a rule your AI follows by reading it: whether a claim is true, whether the wording stays within a card's limits, whether the choices fit the job. For those, you're the check.

## Tools: your choice

Nothing here depends on a particular AI, resume builder, or database. Use whatever you like, as long as each layer meets its minimum:

| Layer | Default in this kit | Alternatives | Minimum |
|---|---|---|---|
| Evidence (Claim Cards) | Markdown files in `evidence/claims/` | A database such as Notion or Airtable, or a spreadsheet, that your AI can reach through MCP or an export | The AI can read it; every claim has an ID and the Claim Card fields; each fact lives in one place only |
| Resume versions | Markdown in `cv/resumes/`, laid out in any tool | Reactive Resume; have the AI generate PDF or DOCX directly; LaTeX or Typst; Word or Google Docs; another resume tool with MCP | Sent versions can be frozen; you keep the exact file you sent |
| Application tracking | A table or CSV you keep | Reactive Resume's tracker; a Notion database | Each application points to one exact version; one place is the source of truth |

If your evidence lives in a database rather than `evidence/claims/`, `check_claims.py` can't read it. Export the cards to Markdown before running it, or do that check by hand.

### Reactive Resume

[Reactive Resume](https://rxresu.me) is a free, open-source resume builder (MIT license, [source on GitHub](https://github.com/amruthpillai/reactive-resume)). Use the hosted version, or self-host it with Docker; the self-hosted version has the same features. It has an official MCP server (`https://rxresu.me/mcp`, OAuth sign-in), so Claude, Cursor, Codex, and other MCP clients can edit your resumes directly. It exports PDF, Word, Markdown, and JSON, and the JSON imports back into any Reactive Resume instance, so your data isn't locked in. It also has an application tracker. If you use it, these conventions help:

- Name: `type number · type name · company or purpose · byline`
- Three kinds of tags: type, status (`Draft` / `Approved` / `Sent` / `Unused`), and job ID
- Lock a resume once it's sent. If you're not sure which version you sent, don't link anything to the application record.

### Without a resume builder

Having your AI generate the PDF or DOCX directly works fine. You then handle freezing yourself: put the date and job in the file name, record the file's SHA-256 in `cv/CV-INDEX.md`, and keep a tracking table.

### Other tools with MCP

Before you adopt one, check three things: can you export all your data, can you lock a version once it's sent, and are you comfortable with where it stores your work history.

## Keep your working copy private

The evidence bank holds your real work history: employers, numbers, and who you worked with. **Copy this kit into your own project and keep that project in a private repository.** Don't fork this repo and then fill it in publicly. If you use a public repo anyway, add `evidence/` and `cv/` to `.gitignore` first.

## Design choices

- **Docs first, no framework.** The AI follows rules by reading them, so the docs are short, specific, and full of checkboxes.
- **Accuracy beats polish.** Every gate exists to stop a resume that reads well but isn't true.
- **Too weak is a failure too.** Guarding against inflation shouldn't turn a resume into a list of disclaimers. Dig for the value first, then decide how far the wording can go.
- **You're the last gate.** The AI can draft and self-review, but you decide what's final and what goes out.

## Where this came from

It was pulled out of a real job search. None of the personal facts, company names, or job data came along, and everything in `examples/` is made up.
