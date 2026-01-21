import logging
from pathlib import Path
import sys

# import pytest

from LabGym import central_logging
# from .exitstatus import exitstatus
from .utils import patch_config_dict


# success cases
def test_enable_true(monkeypatch):
	# Arrange
	patch_config_dict(monkeypatch, {'enable': {'central_logger': True}})

	# Act
	central_logger = central_logging.get_central_logger(reset=True)

	# Assert
	assert central_logger.disabled == False

	assert central_logger.name == 'Central Logger'
	assert central_logger.level == logging.INFO
