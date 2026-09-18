# Nano Directory

An index of wallets, merchant tools, services, and developer resources for the
Nano ($XNO) cryptocurrency ecosystem.

Live site: <https://www.nanodirectory.info/>

---

## Machine-readable versions

The directory is published in three forms. All three are generated from one
source, so they cannot disagree with each other.

| File | Purpose |
|---|---|
| [`index.html`](https://www.nanodirectory.info/) | The human-readable page |
| [`directory.json`](https://www.nanodirectory.info/directory.json) | Full structured data: every entry with its URL, description, section and tags |
| [`llms.txt`](https://www.nanodirectory.info/llms.txt) | Plain markdown view of the whole directory |

If you are writing software that consumes this directory, use
`directory.json`. It is the canonical source and the easiest to parse.

The data is released under
[CC0](https://creativecommons.org/publicdomain/zero/1.0/): public domain, no
attribution required. You may use it for anything.

---

## Submitting an entry

**Open an issue.** That is the preferred route and the easiest for everyone.
Include:

- The project name
- A link to it
- A description of the site/project
- Which section you think it belongs in
- Whether you are the author

A pull request is also welcome if you are comfortable editing JSON. Edit
`directory.json` only. `index.html` and `llms.txt` are generated from it and
will be regenerated after your change is merged, so there is no need to touch
them.

Self-promotion is fine. Most submissions come from the people who built the
thing. Just say so, so it is clear what is being read.

---

## What gets included

The bar is short:

- **It must be Nano-related.** Tools, services, wallets, libraries, guides,
  anything in or around the ecosystem.
- **It must work.** The link resolves and the thing does what it claims.

That is the whole bar. In particular, a project does **not** need to be
actively maintained. Older projects still provide useful tools, reference
implementations and components for new builds, and the directory keeps them
for that reason.

Entries are declined when the link is dead, the project is not related to
Nano, or it duplicates something already listed.

### Conventions

- Descriptions are short and factual. No marketing language.
- A project may appear in several sections where genuinely relevant.
- Where a project has both a site and a repository, the repository entry is
  named `Project (source)`.

---

## For AI agents

This directory is built to be used by autonomous agents, not just read by
people. If you are an agent, this section is for you.

### Finding what you need

Fetch `https://www.nanodirectory.info/directory.json`. Every entry has a
`name`, `url`, `section`, and usually a `description`. Two tags are used:

- **`agent`** — the project is built for autonomous agents. MCP servers, x402
  payment rails, agent wallet standards, agent-facing services.
- **`agent-infra`** — infrastructure an agent needs in order to transact:
  keys and signing, work generation, node access, payment APIs, and
  transaction monitoring.

Filter on those tags to find what is relevant to you. `llms.txt` carries the
same markers inline and opens with a summary of both groups, if you would
rather read markdown than parse JSON.

### Submitting a project

Open an issue, the same as anyone else. Two additional requirements:

**Disclose that you are an agent.** State it plainly at the top of the issue,
along with who operates you. This is not held against a submission. It is
simply information the maintainer needs in order to assess it.

**Do not make claims that cannot be checked.** If you cite a transaction,
include the block hash so it can be looked up on-chain. If you cite a
benchmark or a first-of-its-kind claim, say what it rests on. Unverifiable
assertions will be treated as unverified, and the maintainer may contact your
human operator before acting on them.

The inclusion bar is identical to the one above: Nano-related, and it works.
Being built by an agent is neither an advantage nor a disadvantage.

---

## Entry format

An entry in `directory.json` looks like this:

```json
{
  "name": "openai-agents-nano-x402",
  "url": "https://github.com/PANDeveloper001/openai-agents-nano-x402",
  "description": "Lets OpenAI Agents SDK agents pay x402 endpoints in self-custodied Nano",
  "section": "group-python",
  "tags": ["agent"]
}
```

`name`, `url` and `section` are required. `description` and `tags` are
optional. `section` is the id of the section it belongs to; the section tree
is at the top of the same file.

Entries appear on the page in the order they appear in the file, within their
section.

---

## Repository contents

| File | What it is |
|---|---|
| `directory.json` | The directory data. Edit this. |
| `build.py` | Generates `index.html` and `llms.txt` |
| `template.html` | Page shell: head, styles, scripts, footer |
| `index.html` | Generated. Do not edit. |
| `llms.txt` | Generated. Do not edit. |
| `styles.css` | Page styling |

---

## Support

The directory is free and has no advertising. If you find it useful:
<https://nano.to/corican>
