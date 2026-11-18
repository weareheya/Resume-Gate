# Cases: what the rules look like in practice

Ten **entirely made-up** cases (the people, companies, and numbers are all invented). The structure of each one comes from a problem that really happened in a real job search; only the industry has changed. Each case lists the rule it shows.

| Case | Rule shown | Industry |
|---|---|---|
| E1 | D-002, D-011 | Hospital operations → medical devices |
| E2 | D-012 | Architecture firm |
| E3 | D-003, D-013 | Textbook publishing |
| E4 | D-003, D-013, D-014 | Sports events |
| E5 | D-004 | Retail chain → SaaS |
| E6 | D-002, L-12 | Logistics |
| E7 | D-014 (plans vs results) | Management consulting → corporate strategy |
| E8 | D-014 (how contributions relate) | Nonprofit |
| E9 | D-015 | Hotel revenue management + side business |
| E10 | D-016 | Consumer goods → e-commerce platform |

## E1 · Hospital operations lead → medical-device Market Access Manager

The candidate led a redesign of a regional referral pathway and persuaded 4 partner hospitals to adopt it. The model didn't know what "referral pathway design" was and rewrote it into the safest generic phrase.

- ✗ Version 2: Managed relationships with regional partner hospitals
- ✓ Fixed: Designed a regional referral pathway and got 4 partner hospitals to adopt it, cutting average referral wait time by 30%

Takeaway: the downgraded version is closer to the JD's keywords, but it lost the only proof that she can get institutions to change how they work, which is the core of Market Access.

## E2 · Project manager at an architecture firm

One experience holds two skills: during the bid, she reframed the project scope through client interviews and won an HK$8M design contract; after the win, she coordinated 6 subcontractors to deliver on time.

- For a business development role: Reframed project scope through client interviews and proposed a differentiated design, winning an HK$8M contract
- For a construction project manager role: Coordinated 6 subcontractors and the client to deliver on schedule over 14 months
- ✗ Blended: Managed projects end to end, from bid to delivery

Takeaway: both versions rest on exactly the same facts; only the selection and order differ. The blended version is weaker for both jobs.

## E3 · Textbook project manager at a publisher → operations role

The candidate led a textbook series. The content was written by a team of authors, and the illustrations by an outside studio. The publisher estimated the series' potential market at about RMB 500M.

- ✗ Version 1: Created a textbook series that opened up a RMB 500M market
- ✓ Fixed: As project lead, coordinated 12 authors and an outside illustration studio to deliver 3 textbooks on schedule, adopted by 40 schools in the first year

Takeaway: "created" credits the project manager with the authors' work, and "opened up a RMB 500M market" turns a potential size into a result. What transfers to an operations role is coordinating many parties and delivering on time. When a number needs a long qualifier to be read correctly, swap in a number that's unambiguous on its own.

## E4 · Event coordinator at a sports-event company → brand partnerships / BD

The title was coordinator, and in the first round the candidate described only on-site execution. After the question "Which decisions involving money were you part of?", it came out that she had designed sponsorship packages, taken part in negotiations, and run a weekly cross-team review.

- ✗ Written from the title: Coordinated on-site event execution and vendors
- ✓ After probing: Designed three-tier sponsorship packages and took part in negotiations that closed an HK$1.5M sponsorship; set up a weekly cross-team review and dashboard

Takeaway: "took part in negotiations" can't become "negotiated." The verb before an amount sets the credit, and the category after it (cash, in kind, potential) sets what it is. Both have to stay.

## E5 · Retail store operations manager → SaaS Customer Success Manager

The candidate has no experience on the SaaS vendor side, but led the rollout of a new POS system across 35 stores.

- ✗ Swapped terms: Drove SaaS product adoption and reduced customer churn
- ✓ Adjacent skill: Led a new POS rollout across 35 stores, trained staff and tracked usage data, raising daily usage from 40% to 85% within 3 months

Takeaway: the swapped-terms version falls apart at the first interview question. The adjacent version lets the hiring manager conclude on their own that she understands user adoption.

## E6 · Four rounds for a logistics candidate

How a semantic regression happens, and how it gets caught.

1. v1: The candidate confirms "Redesigned the South China delivery network, cutting cost per parcel by 18%." It goes into a Claim Card marked `protected`.
2. v2: The summary is adjusted for another JD; this line stays unchanged.
3. v3: To "fit the JD better," the model rewrites it as "Helped optimize regional logistics processes." The Claim ID is still there and `check_claims.py` passes. During self-review, a sentence-by-sentence comparison with the approved wording shows the strong verb and the number are gone, and the change is stopped.
4. v4: The original wording is restored, and the Change Log notes "this round changed only the summary and skills order."

## E7 · Management consulting analyst → corporate strategy role

The candidate described one experience as "Prepared a channel expansion proposal for a client (not implemented)." After the question "Was any part of the proposal used later?", it turned out the client had adopted its distributor tiering criteria for the next year's distributor review.

- ✗ Dropped: it's only a proposal, so it stays off the resume
- ✗ Inflated: Led the client's channel expansion
- ✓ After probing: Designed distributor tiering criteria that the client adopted for its annual distributor review

Takeaway: the proposal as a whole never launched, but part of it was put to use. Only a probing question finds that.

## E8 · Program officer at a nonprofit

The candidate wrote a needs assessment on older adults living alone in a community; later, a foundation launched a home-visit program.

- ✗ Implied causation: The needs assessment led the foundation to launch a new program
- ✗ Split apart by reflex: the two are written separately, with no link
- ✓ After probing: the foundation's review committee had cited the report as one basis for approving the program. Wording: Wrote a needs assessment cited as one basis for approving the foundation's home-visit program

Takeaway: find out what the link actually is, then decide how to write it. "One basis for" states the value without claiming all the credit.

## E9 · Hotel revenue manager who co-founded a café on the side

While working full time in hotel revenue management, the candidate co-founded a café with a friend. She handled pricing and menu margin design; her partner ran day-to-day operations.

- ✗ Vague: Entrepreneur, F&B ventures
- ✗ Written as a disclaimer: Co-founded a café (part-time, weekends only, run day to day by partner, not involved in management)
- ✓ Strongest defensible: Co-founder (2021–2023, alongside full-time role); designed pricing and menu margins, reaching break-even in the first year

Takeaway: the second and third versions are both accurate. The difference is where the words go: the second spends them on what she didn't do, the third on proving what she did.

## E10 · Consumer-goods distributor manager → merchant growth manager at an e-commerce platform

The JD asks for "data-driven, expert in SQL." The candidate has 6 years of distributor management and only basic SQL. Looking at the public backgrounds of people in the same role at the company showed that most came from merchant operations and sales, and that data skills were a plus, not a gate.

- Adjustment: distributor management goes first; SQL is written honestly as "uses SQL for basic analysis"
- ✗ The wrong moves: calling the SQL "expert" to match the JD, or skipping the job because it isn't

Takeaway: the research changed the order of the experience and the decision to apply. It didn't change the facts.
