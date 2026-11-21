# PROMPTS: Copy-paste prompts

Paste these into your AI at the matching moment. Replace anything in [brackets].

**Saving cost.** If your tool lets you pick a model, a faster, cheaper one is fine for saving a JD, running the scripts and small edits. Use the strongest one for positioning (S1–S3), interviewing you for evidence, and self-review: those are where a weak model overclaims or misses a gap. After many corrections in one chat, start a fresh session: the cards hold what's true, so nothing is lost.

## 0. First session

```text
Read AGENTS.md, then docs/WORKFLOW.md. I'm new to this kit. Walk me through Step 0 one step at a time. Start with the checkup report on my current resume, then show me the interview plan before you ask anything. Before each step, tell me what it produces and what you need from me. Don't start the next step until I say so.
```

## 1. Checkup report on my resume (Step 0, or any time)

```text
Read AGENTS.md and docs/REPORT.md. Here is my resume [or: it's in evidence/sources/]:

[paste it here]

Make a checkup report [or: a job-fit report for this JD: paste it]. Copy report/template.html to reports/, fill in only the data block, then run scripts/report_score.py and give me the three-line summary, and show me the card with scripts/report_png.py. Don't write any Claim Cards yet. Ask me whether I want a shareable version. Then list the 3 accomplishments you'd interview me about first, and what's still missing for each.
```

## 2. Interview me and write a Claim Card (Step 0)

```text
Read evidence/claims/_TEMPLATE.md and the "Keeping the interview short" section of docs/WORKFLOW.md. Write the plan into evidence/INTAKE.md first: how many questions, about how long. Then interview me about accomplishment #[N] in this mode: [one at a time / one form / I'll just talk]. Put the progress line before every question, skip what my material already answers, and stop at 5 questions. Cover only what's missing of:
- the context
- what I personally did, and what the team did
- the numbers and what each one measures (unit, time window, cumulative vs per item vs potential)
- what I can't claim
- how I could prove it

Don't flatter me, and don't fill gaps with guesses: anything I skip goes on the card as "To fill". When I say "done" or "stop," write the Claim Card and show me its essentials; when I say it's right, mark it "Safe to draft". Anything I haven't confirmed, or that hits "What counts as risky" in docs/WORKFLOW.md, gets one question from you and stays "Needs review" until it's answered. Set `evidence:` from how clearly I can explain it; mark numbers I gave `✓` and ones I called rough `to verify`. Then update evidence/INTAKE.md, and show me both.
```

## 3. Make a version for a job

```text
Follow docs/WORKFLOW.md, S0 through S6, for this job:

[paste the JD here]

Start by saving the JD in jobs/, then tell me the positioning (with options if this job is a stretch; if you give options, stop and wait for my pick before you go on), the baseline you picked, and the evidence table: every Claim Card, whether it's used, and why not. Use only claims marked "Safe to draft." Stop before S7 and show me the full text, the diff against the baseline, and the Coverage Report.
```

## 4. Self-review a version

```text
Review cv/resumes/[file].md against docs/REVIEW-CHECKLIST.md. Report your findings as a table, fix what you can, and list what you couldn't check.
```

## 5. Check for updates

```text
Check whether there's a newer Resume-Gate. Follow docs/UPDATING.md: compare VERSION, show me what changed and anything I need to do, and replace only the kit files after I say yes. Never touch my own files.
```

## 6. Before-and-after poster

```text
Rerun the checkup on [cv/resumes/file.md] the same way as the first one, then make a before-and-after poster from reports/[first report] and the new one with scripts/report_compare.py. Before you make it, show me the module menu in docs/REPORT.md with the exact text you'd use for each; add only what I tick.
```

## 7. Follow-up cards (after you get an interview)

```text
I've got an interview for [job ID]. Following "After you get an interview: follow-up cards" in docs/WORKFLOW.md and the format of interview/_TEMPLATE.md, make follow-up cards for [cv/resumes/file.md] and save them to interview/[job ID].md. First read every Claim Card this version uses and the Coverage Report in cv/changelogs/, and list the Claim IDs you read. Answers use only facts on the cards; anything they don't cover goes under "Fill before the interview" as a question for me. Don't make anything up.
```

## 8. Reuse a reviewed answer

```text
For [job ID], run python3 scripts/list_claims.py --answers [job ID]. Use the answers marked current as they are. For any marked recheck, rewrite it from the current Claim Cards and show me before saving. Don't use an answer outside its scope.
```
