# PROMPTS: Copy-paste prompts

Paste these into your AI at the matching moment. Replace anything in [brackets].

## 0. First session

```text
Read AGENTS.md, then docs/WORKFLOW.md. I'm new to this kit. Walk me through Step 0 one step at a time. Start with the checkup report on my current resume, then show me the interview plan before you ask anything. Before each step, tell me what it produces and what you need from me. Don't start the next step until I say so.
```

## 1. Checkup report on my resume (Step 0, or any time)

```text
Read AGENTS.md and docs/REPORT.md. Here is my resume [or: it's in evidence/sources/]:

[paste it here]

Make a checkup report [or: a job-fit report for this JD: paste it]. Copy report/template.html to reports/, fill in only the data block, then run scripts/report_score.py and give me the three-line summary. Don't write any Claim Cards yet. Ask me whether I want a shareable version. Then list the 3 accomplishments you'd interview me about first, and what's still missing for each.
```

## 2. Interview me and write a Claim Card (Step 0)

```text
Read evidence/claims/_TEMPLATE.md and the "Keeping the interview short" section of docs/WORKFLOW.md. Write the plan into evidence/INTAKE.md first: how many questions, about how long. Then interview me about accomplishment #[N] in this mode: [one at a time / one form / I'll just talk]. Put the progress line before every question, skip what my material already answers, and stop at 5 questions. Cover only what's missing of:
- the context
- what I personally did, and what the team did
- the numbers and what each one measures (unit, time window, cumulative vs per item vs potential)
- what I can't claim
- how I could prove it

Don't flatter me, and don't fill gaps with guesses: anything I skip goes on the card as "To fill". When I say "done" or "stop," write the Claim Card with status "Needs review", update evidence/INTAKE.md, and show me both.
```

## 3. Make a version for a job

```text
Follow docs/WORKFLOW.md, S1 through S6, for this job:

[paste the JD here]

Start by telling me the job type, the baseline you picked, and the Claim IDs you read. Use only claims marked "Safe to draft." Stop before S7 and show me the full text, the diff against the baseline, and the Coverage Report.
```

## 4. Self-review a version

```text
Review cv/resumes/[file].md against docs/REVIEW-CHECKLIST.md. Report your findings as a table, fix what you can, and list what you couldn't check.
```

## 5. Check for updates

```text
Check whether there's a newer Resume-Gate. Follow "Updating the kit" in AGENTS.md: compare VERSION, show me what changed and anything I need to do, and replace only the kit files after I say yes. Never touch my own files.
```
