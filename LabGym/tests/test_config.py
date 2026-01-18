import logging
from pathlib import Path
import re
import sys

import pytest  # pytest: simple powerful testing with Python

from LabGym import config
from .exitstatus import exitstatus


testdir = Path(__file__[:-3])  # dir containing support files for unit tests
assert testdir.is_dir()


# success cases
def test_success_parse_args_empty(monkeypatch):
	# Arrange
	monkeypatch.setattr(config, '_cached_config', None)
	monkeypatch.setattr(config.myargparse, 'parse_args', lambda: {})

	# Act
	_config = config.get_config()

	# Assert


def test_success_parse_args_has_enable(monkeypatch):
	# Arrange
	monkeypatch.setattr(config, '_cached_config', None)
	result = {'enable': {'alfa': True, 'bravo': False}}
	monkeypatch.setattr(config.myargparse, 'parse_args', lambda: result)

	# Act
	_config = config.get_config()

	# Assert


# Missing "default" configfile.
# If the provenance of configfile definition is defaults data,
# a missing configfile produces a logging info message.
def test_missing_default_configfile(monkeypatch, caplog, capsys):
	# Arrange
	monkeypatch.setattr(config, '_cached_config', None)
	result = {'configdir': str(testdir)}
	monkeypatch.setattr(config.myargparse, 'parse_args', lambda: result)

	# Act
	with caplog.at_level(logging.INFO):
		_config = config.get_config()

	record = caplog.records[0]
	# with capsys.disabled():
	#     print(f'\n{record.message!r}\n')
	# "[Errno 2] No such file or directory: '/.../test_config/config.toml'"

	# Assert
	assert record.levelname == 'INFO'
	assert re.match('.*No such file or directory: ', record.message)


# Missing "nondefault" configfile.
# If the provenance of configfile definition is args or environment var,
# a missing configfile produces a FileNotFoundError exception.
def test_missing_nondefault_configfile(monkeypatch):
	# Arrange
	monkeypatch.setattr(config, '_cached_config', None)
	result = {'configfile': str(testdir / 'missing.yaml')}
	assert not Path(result['configfile']).exists()
	monkeypatch.setattr(config.myargparse, 'parse_args', lambda: result)

	# # Act
	# with pytest.raises(SystemExit,
	#         match='Trouble reading user-specified configfile'
	#         ) as e:
	#     _config = config.get_config()
	#
	# "SystemExit: Trouble reading user-specified configfile (..."
	#
	# # Assert
	# assert exitstatus(e.value) == 1

	# Act
	with pytest.raises(FileNotFoundError):
		_config = config.get_config()

	# Assert


# A defective/fouled or unreadable configfile produces an exception.
def test_bad_configfile(monkeypatch):
	# Arrange
	monkeypatch.setattr(config, '_cached_config', None)
	result = {'configfile': str(testdir / 'bad.yaml')}
	monkeypatch.setattr(config.myargparse, 'parse_args', lambda: result)

	# # Act
	# with pytest.raises(SystemExit,
	#         # match='Trouble reading user-specified configfile '
	#         ) as e:
	#     _config = config.get_config()
	#
	# # Assert
	# # SystemExit: Trouble reading user-specified configfile (/charlie/delta.yaml)
	# assert exitstatus(e.value) == 1

	# Act
	with pytest.raises(config.yaml.reader.ReaderError,
			) as e:
		_config = config.get_config()

	# Assert
