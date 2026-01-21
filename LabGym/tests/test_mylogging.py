import logging
from pathlib import Path
import sys

import pytest

from LabGym import mylogging
from .utils import patch_config_dict


rootlogger = logging.getLogger()


@pytest.fixture
def logging_reset(scope='module'):  # invoke once in the test module
	# Clear rootlogger's, level.
	original_level = rootlogger.level
	rootlogger.setLevel(logging.NOTSET)

	# Clear handlers.  Otherwise, the original handlers are exposed and
	# modifiable by the test functions.
	original_handlers = rootlogger.handlers
	rootlogger.handlers = []

	yield

	# Restore rootlogger's level.
	rootlogger.setLevel(original_level)

	# Restore rootlogger's handlers.
	rootlogger.handlers = []
	for h in original_handlers:
		rootlogger.addHandler(h)


# success cases
def test_success(monkeypatch, logging_reset):
	# Arrange
	rootlogger.setLevel(logging.DEBUG)
	config_dict = {
		'logging_configfiles':
			[Path(mylogging.__file__).parent.joinpath('logging.yaml')],
		'logging_configfile': None,
		'logging_level': 'INFO',
		}
	patch_config_dict(monkeypatch, config_dict)

	# Act
	mylogging.configure()

	# Assert
	assert rootlogger.level == logging.INFO  # per logging.yaml


# Bad logging_level produces a warning message.
def test_bad_logging_level(monkeypatch, logging_reset):
	# Arrange
	rootlogger.setLevel(logging.DEBUG)
	config_dict = {
		'logging_configfiles':
			[Path(mylogging.__file__).parent.joinpath('logging.yaml')],
		'logging_configfile': None,
		'logging_level': 'WALNUT',  # bad value
		}
	patch_config_dict(monkeypatch, config_dict)

	# Act
	mylogging.configure()

	# Assert
	# WARNING Trouble overriding root logger level.
	assert rootlogger.level == logging.INFO  # per logging.yaml


# Bad specific logging_configfile produces a warning message.
def test_bad_specific_logging_configfile(monkeypatch, logging_reset):
	# Arrange
	rootlogger.setLevel(logging.DEBUG)
	config_dict = {
		'logging_configfiles': [],
		'logging_configfile': Path('/bravo/charlie.yaml'),
		# 'logging_level': None,
		}
	patch_config_dict(monkeypatch, config_dict)

	# Act
	logrecords = []
	mylogging.configure(logrecords)

	# Assert
	# DEBUG:Unsuitable logging configfile /bravo/charlie.yaml.  ([Errno 2] No such file or directory: '/bravo/charlie.yaml')
	# WARNING:No suitable logging configfile found.
	# WARNING:Trouble overriding root logger level.
	assert rootlogger.level == logging.DEBUG
