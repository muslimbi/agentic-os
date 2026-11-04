# Contributing to Agentic OS

Agentic OS is an early-stage hierarchical orchestration prototype. Contributions
should preserve the distinction between implemented behavior and the longer-term
GOD AI OS design.

## Development setup

Requires Python 3.10 or later.

```bash
python -m pip install --editable .
python -m unittest discover -s tests -v
```

Before opening a pull request:

1. Keep changes focused and preserve unrelated work.
2. Add or update tests for behavior changes.
3. Run the test suite and ensure it passes.
4. Update documentation when behavior or supported usage changes.
5. Do not commit credentials, private data, or generated build artifacts.

## Continuous integration and delivery

GitHub Actions runs the test suite on Python 3.10, 3.12, and 3.14 for pull
requests, pushes to `main`, and version tags beginning with `v`. Once all test
jobs pass, it builds a wheel and makes it available as a workflow artifact.

The workflow does not publish to a package registry or deploy to a server.
Those actions require an explicitly configured destination, credentials, and
release policy.
