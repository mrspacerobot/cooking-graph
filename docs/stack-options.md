# Stack options for the graph repository

For the owner, for [issue 4](https://github.com/mrspacerobot/cooking-graph/issues/4). A draft to decide from. Nothing here is built.

## Where we start

- The graph is 632 JSON files (2.7 MB) plus 592 probe files (2.4 MB). One file per thing, read strictly.
- `tools/` is about 2,900 lines of Python in 24 modules. `tests/` is about 2,600 lines and 287 tests. Neither uses anything outside the standard library.
- The model is `schema/model.json`, a small schema language of our own, with closed word lists in `schema/words.json`. The checker reads both.
- `./check` takes about 19 seconds. Reading and ruling on all 1,224 files takes about 1 second of that. The tests take the rest.
- No tool calls a network or a model. Model batches are written by agent sessions, then tidied and checked. No database exists yet.
- There is no `.github/` folder, so no CI exists yet.
- The tests also pass on Python 3.11 (run here). The README promises 3.9, which I did not test.

## The options

### A. Stay on the standard library: files in git, one SQLite build

Keep every tool as it is. Add a `./build` that loads the checked files into one SQLite file (`sqlite3` is in the standard library). The file is generated, ignored by git, and thrown away each time.

### B. Python with a few pinned dependencies

Same language, same files. Add `pydantic` (typed models and JSON Schema output), `pytest`, `ruff` and a type checker, pinned in a lock file. The model becomes typed Python classes. SQLite still comes from the standard library, or DuckDB if queries grow.

### C. TypeScript on Node

Rewrite the tools in TypeScript with `zod` or JSON Schema, `vitest`, and `better-sqlite3`. Types could be shared with a web app or a service written in TypeScript.

## Against what we care about

| Need | A. Standard library | B. Python and pins | C. TypeScript |
|---|---|---|---|
| Strict schema validation | Works today: unknown, missing, out of order and dangling are all errors. We maintain the schema language ourselves | Better messages and editor help. Cross-file rules (cycles, groups, held-back) stay hand written. Risk of two sources of truth for the model | As B, in another language. All cross-file rules rewritten |
| Tests | 287 pass, `unittest`, no install | Same tests run; `pytest` is nicer but optional | Rewrite about 2,600 lines of tests |
| Model-batch runs | Agents write files, `./tidy`, `./check`. Needs nothing. The run is not recorded by code yet (see story "batch log") | Same | Same. An SDK would be easy to add, but it is not needed |
| Database build | `sqlite3` is built in. A few hundred lines. Fast at this size | Same, plus typed rows | Needs a native module or WASM |
| Exports for the app | A SQLite file or JSON from the build. Fine for mobile, and nothing needs a Mac | As A, and JSON Schema can be the contract with the app | Best if the app or service is also TypeScript. No gain if it is not |
| CI on GitHub | One job, `python3 ./check`. No cache, no install | One job with an install step and a lock file to keep fresh | One job with Node setup and an install step |
| Parallel worktrees and merge | Works today. New files rarely clash; `./merge` and `./twins` catch the same name added twice. Nothing to install per worktree | Each worktree needs an environment (or a shared one) | Each worktree needs `node_modules` or a shared store |
| Contributor onboarding | `git clone`, `./check`. Python is on most machines | Clone, install, then `./check` | Clone, install Node and packages |
| Cost to switch later | Low. Data is JSON files and the model is a JSON file, so nothing is locked in. Tools are about 2,900 lines | Low. It is the same language | High for the rewrite, but the data does not move |

## Recommendation

Choose A for now, and add the SQLite build and a CI workflow on top of it.

- It is the only option with nothing to install, which suits agents working in several worktrees at once.
- The thing that is hard here is the content and its review, not the code. A new stack would not move that.
- Nothing is locked in. The graph is JSON, the model is JSON, and the build is generated. A later switch rewrites tools, not data.
- Keep `schema/model.json` free of Python ideas, so any later language can read it.
- Raise the Python floor. Python 3.9 reached end of life in October 2025 (from my own knowledge, not checked today). Pick 3.11 or 3.12 and test the floor and the newest in CI.

Add dev-only tools later (for example `ruff`) only if they stay outside `./check`. A tool in `./check` must need no install.

## What would change my mind

- **To B:** the checker's schema language becomes hard to extend, or a second program (the service or the export) needs the same model as typed code. Then generate JSON Schema from typed classes and keep one source.
- **To C:** the owner picks TypeScript for the question service and the app, and wants one model in both. A shared language would then pay for a rewrite.
- **Away from A for speed:** `./check` passes about 2 minutes, or the graph grows about ten times. The read is cheap now (1 second), so the tests would be the first thing to split.
- **To a bigger database:** queries no longer fit in SQLite, for example many readers at once. That is the service's choice, not the repository's.

## Checks a pull request should run

1. `./check` on the lowest Python we support and on the newest. This covers the tests, strict reading, tidiness, the em dash, the model document and the written documents.
2. `./tidy` leaves no change (`git diff --exit-code` after it). `./check` already says not-tidy, so this is a second guard.
3. The build, once it exists: load into SQLite, then run integrity queries (every reference resolves, every tier is a word of the list).
4. `./probe` and `./numbers`, printed into the job summary so the pull request shows counts. Held-back probes are only counted, as now.
5. A probe guard: a pull request may add probe files but not edit a committed batch (a batch is closed once committed), and a pull request that adds probes must say who wrote them.
6. A held-back guard: no dish, name or alias may match a held-back probe. `./check` has this (drafted-towards-held-back). CI must never print a held-back word.
7. No file under `out/`, no `__pycache__`, no generated page committed.
8. A secret scan on the diff. AGENTS says no secrets, ever.
9. A pull request body check: it says how much and of what, and lists doubts.
10. Branch protection on `main`: these checks required, no direct push. Only the owner merges.

## What the owner must decide

1. The stack: A, B or C.
2. The Python floor (3.9 as written, or 3.11 or 3.12).
3. Whether dev-only dependencies are ever allowed, and if so the rule that `./check` stays install-free. AGENTS says "until the stack is decided, standard library only", so that line changes in the same pull request.
4. The stack of the question service and the app, if known. It may decide between A and C.
5. The export format for the app: a SQLite file, JSON, or both.
6. Whether CI may use paid minutes, and whether `main` gets branch protection.
7. Who reads CI failures and how fast, since agents open pull requests and stop.
8. A model budget per round. The stopping rule on cost per answered probe has none set.

## Things I could not verify

- Whether the owner's GitHub plan allows required checks and branch protection on a private repository.
- How many CI minutes the owner has, and the real run time on a GitHub runner (19 seconds is from this machine).
- Python 3.9 compatibility. Only 3.13 and 3.11 were run.
- The app's and the service's stack. Nothing in the repository says.
- How the graph behaves at ten or a hundred times its size. I measured the read at 1 second for 1,224 files, and nothing larger.
- The full text of epic 2. I worked from the summary I was given and from the repository documents.
- Library versions and their current state (`pydantic`, `zod`, `better-sqlite3`). I did not look them up.
- Whether a secret scanner is available to the repository on the owner's plan.
