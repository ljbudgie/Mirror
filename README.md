# Mirror — see where you stand.

Tell it what happened. It maps your rights, generates the question, and gives you the next step.

Local-first. No data leaves your device. Built on the [Burgess Principle](https://github.com/ljbudgie/burgess-principle) (UK00004343685).

MIT licence.

---

## Quickstart

```bash
pip install -e ".[dev]"
pytest
```

Open `web/index.html` in your browser. No server needed.

## Structure

```
/core        Python modules — conversation, rights, next step, templates, commitment, timeline
/templates   Ready-to-send letter templates
/web         Local-first chat interface (HTML + CSS, no dependencies)
/docs        User guide, SECURITY.md, CONTRIBUTING.md
```

## Documentation

See [`docs/user_guide.md`](docs/user_guide.md) for full usage instructions.
