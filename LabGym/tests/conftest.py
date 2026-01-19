"""Provide pytest configuration fixtures.

"Is conftest.py a special file to pytest?"
Gemini responds
	Yes, conftest.py is a special file in the pytest ecosystem. It serves as a centralized configuration hub for your test suite and is automatically discovered by pytest without needing to be imported.
	1. Automatic Discovery ...
	2. Fixture Sharing ...
	3. Hook Functions ...
	4. Scope and Hierarchy ...
"""

import pytest


def pytest_addoption(parser):
	parser.addoption(
		"--multiplier",
		action="store",
		default="1.0",
		help="Multiplier for sleep/delay values"
	)


@pytest.fixture
def delay_multiplier(request):
	return float(request.config.getoption("--multiplier"))
