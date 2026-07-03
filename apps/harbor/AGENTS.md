# Terminal-Bench task

You are solving one Terminal-Bench task autonomously, on a time budget. A
graded, working solution beats an elegant one you don't finish. These rules
target the failure modes we've seen in traces.

## Move decisively — don't grind one command at a time

- **Batch shell steps into one `execute` call** with `&&` (e.g.
  `cd /app && make && ./run`). Do NOT run one command per turn — every model
  turn re-sends the whole context and burns your time budget.
- Front-load exploration: a single `ls -R` / `glob` / `grep` pass to map the
  repo, then act. Don't re-explore paths you've already seen.
- Plan the whole approach up front (a short todo list), then execute it — don't
  discover the next micro-step turn by turn.

## Use the dedicated tools, not shell

- `read_file` (not `cat`/`head`/`tail`), `hashline_edit` (not `sed`/`awk`),
  `write_file` (not `echo >` or heredocs), `glob` (not `find`), `grep` (not
  shell `grep`/`rg`). They're faster and don't spend a turn parsing shell.
- Write a file in ONE `write_file` call. Don't build a file up with dozens of
  tiny edits, and don't re-read a file you just wrote.

## Finish and verify

- Match the EXACT output paths, filenames, and formats the task specifies — it
  is graded by automated tests. `/app/result.txt` ≠ `/app/results.txt`.
- Before stopping, run what the task asks for and confirm the real output
  exists and is correct. Don't declare done on an unverified or failing build.
- If a build/run fails, read the FULL error and fix the root cause — don't retry
  blindly or add random flags.
