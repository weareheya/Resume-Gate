# MY-DECISIONS: Your own rules

> Rules you've settled on ("from now on, always…"). **The AI must follow every one with status Active.** Where one conflicts with a starter rule in [DECISIONS.md](DECISIONS.md), yours wins.
> This file is yours: updating the kit never touches it.
> Number your rules from D-101. Before adding one, run `grep "^## D-" docs/MY-DECISIONS.md`, take the highest number, and add 1 (start at D-101 if there are none). To overturn one, change its status to `Superseded by D-xxx`. Don't delete it.

Same fields as the starter rules: **scope** `cv` · `process` · `strategy`, and **applies-to** `all`, `type: 01` or `job: ACME-01`. To change or switch off a starter rule, say which one: `overrides: D-009`.

---

<!-- Template:
## D-101 · One-line title
- scope: cv|process|strategy · status: Active · applies-to: all · date: YYYY-MM-DD
- overrides: (optional, e.g. D-009)
- The rule, where it applies, and any exceptions.
-->
