# Development for Ops: verifiable labs

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/dev-pour-ops-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/dev-pour-ops-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/dev-pour-ops-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/dev-pour-ops-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/dev-pour-ops-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/dev-pour-ops-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

The labs of the blog's
[Développer pour les Ops](https://www.stephane-robert.info/docs/developper/)
course (in French), played with [dsoxlab](https://github.com/stephrobert/dsoxlab).

## What it is

**Ten labs, one inherited tool.** The course teaches an ops engineer to develop
the way a developer does, in Python, and the common thread is `certcheck`, a
TLS certificate expiry check that someone else wrote before you. You read its
code, structure it as a real Python project (src layout, `pyproject.toml`, uv)
that honours a contract, call an API, test it with pytest, debug a certificate
it cannot read, review a pull request with four defects in it, lock the
dependencies and ship an installable version. The final exam takes over an
operations tool end to end.

The inherited code is the point. Most of what an ops engineer writes is code
someone else will read, and most of what they fix is code someone else wrote.
A lab that starts from a blank file teaches the easy half.

## Requirements

- **`mise`**: it installs `uv` and Python at the versions pinned in
  [`mise.toml`](./mise.toml), without curling an archive or touching the system
  package manager.
- **`git`**: one lab reviews a pull request, and the labs work in real
  repositories.
- **`openssl`**, the system one: `certcheck` reads real certificates.
- **`dsoxlab`**, the engine, installed as a standalone tool (see below).
- **Outbound network access**: a few labs install packages from PyPI.

**No VM, no `dsoxlab provision`.** This catalog declares no `infra:` block at
all: every lab is `runtime: shell` and runs on your own machine, in its own
`uv` project.

## Install

`dsoxlab` is published on [PyPI](https://pypi.org/project/dsoxlab/). Install it
as a standalone tool, so it stays out of this repository:

```bash
# 1. The dsoxlab CLI (external tool, stays out of this repo)
uv tool install dsoxlab

# 2. This lab catalog
git clone https://github.com/stephrobert/dev-pour-ops-dsoxlab-training.git
cd dev-pour-ops-dsoxlab-training

# 3. The toolchain, at the pinned versions
mise install

# 4. Check the contract is valid
dsoxlab validate-structure
```

### Your first lab, in five minutes

```bash
export LAB_HOME=$PWD
dsoxlab list-labs                    # the ten labs, in teaching order
dsoxlab run       lire-du-code       # set the starting state
dsoxlab challenge lire-du-code       # read the mission
# ... you work in challenge/work ...
dsoxlab check     lire-du-code       # run the tests, record the score
```

`run` is what prepares `challenge/work` and copies the fixtures the lab
declares. Running `check` on a lab you never started measures nothing, and says
so rather than recording a 0.

### Keeping it up to date

```bash
uv tool upgrade dsoxlab        # the engine, published on PyPI
git -C <this repo> pull        # the catalog
```

The engine and the catalog move independently: a new `dsoxlab` never requires
re-cloning the labs, and new labs never require upgrading the tool, as long as
the contract version matches. `dsoxlab doctor` says what this repository needs
and what it does not.

## How it works

### The declarative contract (two levels)

The catalog is described by data, not code, which is what keeps the `dsoxlab`
engine domain-agnostic:

- **`meta.yml`** at the root declares the repository identity and the **order**
  of the sections shown by `list-labs`;
- **`lab.yaml`** per lab declares its `skills`, `level`, `runtime` (type,
  fixtures, services), `distros`, `doc_url` and a `validation` block. A
  `lab.fr.yaml` overrides `title` and `description` in French, and nothing else.

`dsoxlab validate-structure` checks the whole contract: `meta.yml` is well
formed, every referenced lab exists with a valid `lab.yaml`, every declared test
and fixture file is really there, and every relative link in a README leads
somewhere.

### The lab lifecycle

```bash
dsoxlab list-labs              # browse the catalog
dsoxlab show      <id>         # metadata and status of one lab
dsoxlab run       <id>         # set the starting state
dsoxlab challenge <id>         # read the mission, no step-by-step
dsoxlab hint      <id>         # reveal a hint (deducted from the score)
dsoxlab check     <id>         # run the tests, compute and record the score
dsoxlab clean     <id>         # remove the work directory
dsoxlab progress               # per-section progress, average score
```

### Runtimes

| Runtime | What the lab asks for |
|---|---|
| `shell` | a terminal, `uv`, Python, `git` and the system `openssl`. Your tool runs in **its own** `uv` project, with its own dependencies. |

Two labs work against a **local fake forge**, shipped as a git bundle rather
than a live service: the lab that calls an API opens a ticket against it, and
the review lab reads a pull request from it. No account, no token, no network.

### The validation model

Validation **proves what a caller observes, it does not trust the learner**.
Each lab ships `pytest` tests under `challenge/tests/` that read the tool's
output, its exit code, the requests the fake forge received, and the files left
in the repository: never what a source file contains.

And a lab is proven **in both directions**: the tests must fail before the work
and pass after it. A test that is green before the work is not a test, it is an
assumption about the setup. `scripts/valider-labs.py` plays that whole cycle on
every lab and writes its verdict to
[`validation-labs.json`](./validation-labs.json), which is versioned: a lab
shipped without a verdict proves nothing.

Reference solutions live under `labs/<lab>/solution/`, **in clear text**: the
chained labs copy them as the next lab's starting point, so the files have to
be readable. Read one and you spoil that lab for yourself.

### Scoring, hints, progress

`check` records a score (tests passed out of total, minus the cost of any hints
revealed). Hints are **base64-encoded** in `challenge/hints.yaml`, so that
opening the file does not give them away, and their cost grows with their
precision. History lives in a SQLite database **local to this repository**.

A run that measured nothing is neither a pass nor a failure: if every collected
test skips, `check` records no score and says why. A score of 0 would accuse the
lab of what is missing from the machine.

## Catalog

<!-- LABS:START -->
### The common thread: read, modify, test and review a small tool

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `lire-du-code` | Read and modify a small Python script: the inherited certcheck | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/pratiques/lire-du-code/) (in French) |
| `script-en-outil` | Understand a Python tool, then modify it: certcheck and its contract | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/pratiques/script-en-outil/) (in French) |
| `dependances-reproductibles` | Dependencies: certcheck installs elsewhere too | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/pratiques/dependances-reproductibles/) (in French) |
| `tester-une-automatisation` | Use the tests: a red test, read, fixed, and one more test | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/pratiques/tester-une-automatisation/) (in French) |
| `deboguer` | Debug step by step: the certificate certcheck cannot read | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/pratiques/deboguer/) (in French) |
| `relire-une-automatisation` | Review a pull request: four defects in certcheck #42 | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/pratiques/relire-une-automatisation/) (in French) |

### Going further

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `data-json-yaml` | Normalize JSON and YAML service inventories | o2 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/programmation/golang/) (in French) |
| `json-schema` | Enforce a deployment contract with JSON Schema | o2 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/autres-langages/json/ecrire-un-schema/) (in French) |
| `yaml-validation` | Validate a YAML service policy before deployment | o2 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/autres-langages/yaml/valider-schema/) (in French) |
| `go-cli` | Build a small, predictable Go CLI | o2 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/programmation/golang/) (in French) |
| `appeler-une-api` | Call an API with requests: certcheck opens its ticket | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/api-rest/) (in French) |
| `livrer-un-outil` | Ship a tool: certcheck 1.0.0, versioned and installable | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) (in French) |
| `level-exams-outil` | Challenge: take over an operations tool | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) (in French) |

### Level exam

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `level-exams-intervenir` | Exam: step in on a small operations tool | o1 | - | shell | [guide](https://www.stephane-robert.info/docs/developper/pratiques/epreuve-intervenir/) (in French) |

_14 labs, table generated by `scripts/gen_catalog.py`._
<!-- LABS:END -->

## Contributing

Read [`CONTRIBUTING.md`](./CONTRIBUTING.md). In short: a lab is proven **in both
directions** before it is merged, `dsoxlab validate-structure` is green, and the
statement exists in English and in French.

Anything user-facing is bilingual. A document translated on one side only is
reported by the validator, not left to goodwill.

## License

See [`LICENSE`](./LICENSE).
