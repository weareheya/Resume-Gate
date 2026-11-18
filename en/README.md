# cv-gate

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
  pdf_fill.swift          Renders each PDF page to PNG and reports how full it is (macOS)
examples/                 A filled-in walkthrough using made-up data
```

## Quick start

1. Copy the contents of this folder (`en/`) into the root of your own job-search project.
2. Do **Step 0** in `docs/WORKFLOW.md`. It takes your existing resume and turns it into Claim Cards and a first approved baseline.
3. In `cv/CV-INDEX.md`, replace the example job types with your own.
4. For each new job, use prompt 3 in `docs/PROMPTS.md` and paste the JD.
5. After each resume: write the Change Log, update `CV-INDEX.md`, and record any new rules you settled on in `docs/DECISIONS.md`.

To check layout (macOS, needs the Xcode command line tools):

```bash
mkdir -p /tmp/cv-check && swift scripts/pdf_fill.swift your-cv.pdf /tmp/cv-check
```

It prints the page count and how full each page is, and writes `p1.png`, `p2.png`, … so you can paste them to your AI or just look. If the last page is under 85% full, it exits with code 2, so you can wire it into a script.

## Optional: Reactive Resume

You can hand layout to [Reactive Resume](https://rxresu.me), an open-source resume builder with MCP support. Nothing here depends on it. If you use it, these conventions help:

- Name: `type number · type name · company or purpose · byline`
- Three kinds of tags: type, status (`Draft` / `Approved` / `Sent` / `Unused`), and job ID
- Lock a resume once it's sent. If you're not sure which version you sent, don't link anything to the application record.

## Keep your working copy private

The evidence bank holds your real work history: employers, numbers, and who you worked with. **Copy this kit into your own project and keep that project in a private repository.** Don't fork this repo and then fill it in publicly. If you use a public repo anyway, add `evidence/` and `cv/` to `.gitignore` first.

## Design choices

- **Docs first, no framework.** The AI follows rules by reading them, so the docs are short, specific, and full of checkboxes.
- **Accuracy beats polish.** Every gate exists to stop a resume that reads well but isn't true.
- **You're the last gate.** The AI can draft and self-review, but you decide what's final and what goes out.

## Where this came from

It was pulled out of a real job search. None of the personal facts, company names, or job data came along, and everything in `examples/` is made up.
