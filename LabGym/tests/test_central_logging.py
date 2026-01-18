import logging
from pathlib import Path
import sys

import pytest

from LabGym import central_logging
# from .exitstatus import exitstatus


def myraise(e):
	"""Raise exception.  This form is useful in a lambda."""
	raise e


# success cases
def test_enable_true(monkeypatch):
	# Arrange
	_config = {'enable': {'central_logger': True}}
	monkeypatch.setattr(central_logging.config, 'get_config',
		# lambda *args: _config)
		lambda *args: _config if set(args) == {  # with arg check
			'enable', } else myraise(Exception('mismatch')))
	logging.debug('%s: %r', '_config', _config)

	# Act
	central_logger = central_logging.get_central_logger(reset=True)

	# Assert
	assert central_logger.disabled == False

	assert central_logger.name == 'Central Logger'
	assert central_logger.level == logging.INFO
