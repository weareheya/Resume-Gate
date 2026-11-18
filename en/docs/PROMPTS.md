# PROMPTS: Copy-paste prompts

Paste these into your AI at the matching moment. Replace anything in [brackets].

## 1. Import my existing resume (Step 0)

```text
Read AGENTS.md and docs/WORKFLOW.md (Step 0). Here is my current resume:

[paste it here]

Don't write any Claim Cards yet. List every accomplishment you can find as a numbered list, one line each. Flag any that are vague or have no number. Then wait for me.
```

## 2. Interview me and write a Claim Card (Step 0)

```text
Read evidence/claims/_TEMPLATE.md. Interview me about accomplishment #[N] from your list, one question at a time. Cover:
- the context
- what I personally did, and what the team did
- the numbers and what each one measures (unit, time window, cumulative vs per item vs potential)
- what I can't claim
- how I could prove it

Don't flatter me, and don't fill gaps with guesses. When I say "done," write the Claim Card with status "Needs review" and show it to me.
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
