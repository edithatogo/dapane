"""Shared inputs for tests of an independently installed native wheel."""

import json
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures"


@pytest.fixture
def load_request():
    def load(name):
        return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))

    return load


@pytest.fixture
def expected_cases():
    return json.loads((FIXTURE_DIR / "expected.json").read_text(encoding="utf-8"))["fixtures"]
