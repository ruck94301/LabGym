"""Provide functions to obtain the configuration values.

Configuration evaluation involves (ordered in increasing precedence)
	1.  hardcoded defaults
	2.  configuration file settings
	3.  environment variables
	4.  command-line options

This module provides ....


Notes
*   Environment variables and command-line options can be used to
	override the location of the configuration file.

*   Typical LabGym configdir organization is
		~/.labgym/config.toml  (optional)
				  logging.yaml  (optional)
				  registration.yaml  (created at registration)

*   To use a different configfile in the configdir, like
		~/.labgym/config_alt.toml
	either use command-line args to specify a relative path like
		LabGym --configfile config_alt.toml
	or assign a relative path to an environment variable before running
	LabGym, like
		export LABGYM_CONFIGFILE=config_alt.toml

	Also, absolute paths can be used, for example,
	+   use configfile ~/sandbox/config_alt.toml
			--configfile ~/sandbox/config_alt.toml

	+   use configfile config_alt.toml in the current working dir
			--configfile "$PWD"/config_alt.toml

	+   use configfile ~/sandbox/config.toml (and other config files
		relative to ~/sandbox, if they are relative, not absolute)
			--configdir ~/sandbox

	+   use configfile ./config.toml (and other config files
		relative to current dir, if they are relative, not absolute)
			--configdir "$PWD"


------------------------------------------------------------------------
	To use a different configfile elsewhere,
	either use command-line args to specify an absolute path like
		LabGym --configfile ~/sandbox/config_alt.toml
	or assign an environment variable before running LabGym, like
		export LABGYM_CONFIGFILE=~/sandbox/config_alt.toml


*   Relative paths are considered relative to configdir, not relative to
	current working dir (cwd or .).
	This is an absolute path to a toml-file in user's home directory.
		~/altconfig.toml

	This is an absolute path to a toml-file in cwd.  (The sh, bash, and
	zsh shells interpolate $PWD to the current working dir.)
		"$PWD"/altconfig.toml

	This relative path is effectively <configdir>/altconfig.toml.
		altconfig.toml

*   The configdir must be an absolute path; it is the anchor for
	relative paths.
	An attempt to set configdir to a relative path or other produces an
	exception.  (Or a fatal error?)

*   The configfile cannot be used to redefine configfile.
	An attempt to do so produces an exception.  (Or a fatal error?)

*   Environment variables can be used to define strings (incl paths)
	and expected bools, but support for lists of strings and dicts of
	bools are not supported.
	How hard would it be?  Perhaps easier to support than to raise
	exception on violation.
	+   Support lists of strings separated by ':'?  Like "/a/b:c/d:e"?
		Incompatible with Windows... some other char separator?
	+   Support dicts from
	+   Support both in json format?  This has merit!


*   The data obj construction might be simplified by refactoring into a
	custom objects with set, validate, and resolve methods, then
	aggregated, then ultimately returned as an ordinary dict.
"""

# Allow use of newer syntax Python 3.10 type hints in Python 3.9.
from __future__ import annotations

# Standard library imports.
import configparser
import copy
import logging
import os
from pathlib import Path
import pprint
import sys
try:
	# tomllib is included in the Python Standard Library since version 3.11
	import tomllib  # type: ignore
except ModuleNotFoundError:
	import tomli as tomllib  # A lil' TOML parser
from typing import Dict, List, Union

# Related third party imports.
import yaml  # PyYAML, YAML parser and emitter for Python

# Local application/library specific imports.
from . import myargparse


# CustomConfigType "type alias" for use in type annotations.
CustomConfigType = Dict[str, Union[
	str,  # configdir, configfile
		  # logging_configfile (specific, overrides potentials if present)
		  # logging_level
		  # detectors, models
	List[str],  # logging_configfiles (potentials)
	bool,  # anonymous, selftest
	Dict[str, bool],  # enable
	]]

defaults: CustomConfigType = {
	'configdir': str(Path.home().joinpath('.labgym')),  # ~/.labgym
	'configfile': 'config.toml',  # relative path

	# list of strings of paths (relative or absolute)
	'logging_configfiles': [
		'logging.toml',  # 1. relative path to toml-file
		'logging.yaml',  # 2. relative path to yaml-file
		# 3. absolute path to LabGym/logging.yaml
		str(Path(__file__).parent.joinpath('logging.yaml')),
		],

	# intentionally, no default specified here for logging_configfile
	# intentionally, no default specified here for logging_level

	'enable': {
		'central_logger': True,  # to disable central logger, user must opt out
		'registration': True,  # to disable registration, user must opt out

		# for now, user has to opt in for assessing locations of userdata
		'assess_userdata_folders': False,
		},

	'anonymous': False,
	'selftest': False,

	'detectors': str(Path(__file__).parent.joinpath('detectors')),
	'models': str(Path(__file__).parent.joinpath('models')),
}

logger = logging.getLogger(__name__)

_cached_config = None


class AbsPath_Marker: pass  # absolute path string
class AbsPathList_Marker: pass  # list of absolute path strings
class Str_Marker: pass  # str
class Bool_Marker: pass  # bool
class BoolDict_Marker: pass  # Dict[str, bool]

# SCHEMA must remain consistent with function "validate".
SCHEMA = {
	'configdir': AbsPath_Marker,
	'configfile': AbsPath_Marker,
	'logging_configfile': AbsPath_Marker,
	'logging_configfiles': AbsPathList_Marker,

	'logging_level': Str_Marker,

	'detectors': AbsPath_Marker,
	'models': AbsPath_Marker,

	'anonymous': Bool_Marker,
	'selftest': Bool_Marker,

	'enable': BoolDict_Marker,
	}


def finalize(data: CustomConfigType) -> CustomConfigType:
	"""Resolve paths for AbsPath_Marker and AbsPathList_Marker values."""

	assert isinstance(data['configdir'], str)
	pobj = Path(data['configdir'])
	assert basis.is_absolute()

	for key, value in data.items():
		if key in SCHEMA:
			marker = SCHEMA[key]

			if marker is AbsPath_Marker:
				assert isinstance(value, str)
				if not Path(value).is_absolute():
					value = str((basis / value).resolve())
			elif marker is AbsPathList_Marker:
				assert isinstance(value, list)
				for i, item in enumerate(value):
					assert isinstance(item, str)
					if not Path(item).is_absolute():
						value[i] = str((basis / item).resolve())


def validate(data: dict) -> CustomConfigType:
	"""Validate data dictionary per markers in SCHEMA, or raise exception.

	This function "validate" must remain consistent with SCHEMA.  All
	markers present in SCHEMA must be recognized/handled in this function.

	All data dict keys are validated as str.

	AbsPath_Marker values are validated as str.
	AbsPathList_Marker values are validated as list of str.

	Values of data dict items whose keys are not represented in SCHEMA
	are validated to be str.
	"""

	for key, value in data.items():
		# All data dict keys are str.
		assert isinstance(key, str)

		if key in SCHEMA:
			marker = SCHEMA[key]

			if marker is AbsPath_Marker:
				assert isinstance(value, str)
				# assert os.path.isabs(value)
				# assert Path(value).is_absolute()
			elif marker is AbsPathList_Marker:
				assert isinstance(value, list)
				for item in value:
					assert isinstance(item, str)
					# assert os.path.isabs(item)
					# assert Path(item).is_absolute()

			elif marker is Bool_Marker:
				assert isinstance(value, bool)
			elif marker is BoolDict_Marker:
				for k, v in value.items():
					assert isinstance(k, str) and isinstance(v, bool)

			elif marker is Str_Marker:
				assert isinstance(value, str)

			else:
				# Handling for specified marker is not found.
				# SCHEMA and validate function have become inconsistent?
				msg = ('Cannot validate unrecognized schema-marker.'
					f'  (marker: {marker})')
				raise KeyError(msg)

		else:
			# Any data item whose key is not a key in SCHEMA has a str value.
			assert isinstance(value, str)


def get_config_from_argv() -> CustomConfigType:
	"""Get config values, validate them, and return them as a dict.

	Get config values from argv.
	Validate values for some keys as specified in SCHEMA.
	"""

	data = myargparse.parse_args()

	# Validate before returning.
	# Other more forgiving approaches include
	# (a) Keep only valid values, and warn of invalid items.
	#         data = cleanse(data)
	# (b) Wrap validate(data) in try/except, and if any not-valid, then
	#     nullify data from this source (data = {}), and warn.
	#          try:
	#              validate(data)
	#          except:
	#              logger.warning('config data from ... is fouled')
	#              data = {}

	validate(data)  # raises an exception if data surprises
	return data


def str2bool(value: str) -> bool:
	"""Given a str like 'True' or 'False', return the corresponding bool."""

	if value.lower() == 'true':
		result = True
	elif value.lower() == 'false':
		result = False
	else:
		# Bad value
		msg = f"Can't convert str {value!r} to bool"
		raise TypeError(msg)
	return result


def json2booldict(jsonstr: str) -> Dict[str, bool]:
	"""Raise an exception (because functionality isn't implemented)."""
	msg = f"Not implemented.  Can't convert json str {value!r} dict of bool"
	raise TypeError(msg)


def json2abspathlist(jsonstr: str) -> List[str, str]:
	"""Raise an exception (because functionality isn't implemented)."""
	msg = f"Not implemented.  Can't convert json str {value!r} list of str"
	raise TypeError(msg)


def get_config_from_environ() -> CustomConfigType:
	"""Get config values, validate them, and return them as a dict.

	Get config values from os.environ.
	Validate values for some keys as specified in SCHEMA.

	Weaknesses
	*   Environment variables are case-sensitive.
		There could be a collision when mapping names to lowercase,
		which should generate a warning or an exception, but that is not
		implemented.
		As implemented, the retained value is the value of the
		environment variable whose name sorts later.  For example, if
		both LABGYM_Configdir and LABGYM_CONFIGDIR are defined, the former
		sorts later, so its value is retained.

	*   No implementation exists now for using environment to specify
		list items or dict items.
		In other words, these environment variables foul the result:
			LABGYM_LOGGING_CONFIGFILES
			LABGYM_ENABLE
		The support could be implemented, but for now seems unjustified.
	"""
	prefix = 'LABGYM_'

	# # Simple implementation using a dict comprehension.
	# data = {name.removeprefix(prefix).lower(): value
	#     for name, value in sorted(os.environ.items())
	#         if name.startswith(prefix)}

	# Instead of a simple implementation using a dict comprehension,
	# use a loop, and construct both the data dict and a shadowing
	# provenance dict.
	data = provenance = {}
	for name, value in sorted(os.environ.items()):
		if name.startswith(prefix):
			key = name.removeprefix(prefix).lower()
			data[key] = value
			provenance[key] = name

	# Convert and unpack.
	# iterate over a list containing a copy of the items at the start
	for key, value in list(data.items()):
		if key in SCHEMA:
			marker = SCHEMA[key]

			if marker is Bool_Marker:
				data[key] = str2bool(value)
			elif marker is BoolDict_Marker:
				data[key] = json2booldict(value)
			elif marker is AbsPathList_Marker:
				data[key] = json2abspathlist(value)


	# # unpack values of specific keys ('enable', ...) as json
	# ...
	#
	# # Validate before returning.  Other gentler approaches incl
	# # (a) data = cleanse(data)
	# # (b) try/except to validate(data) or nullify data and warning.
	# validate(data)
	# return data

	# Convert 'True'/'False' strings to True/False bool now?
	# Not strictly necessary now... can be done later.
	# OTOH, if there's an unconvertible value, it's better to recognize
	# and report sooner instead of later.
	#
	# Convert values in the data dict obtained by list comprehension?
	# Warning messages benefit from the original env var name, so
	# instead of converting as a second op, construct the data dict
	# with the conversions during construction.

	validate(data)
	return data


def get_config_from_configfile(configfilestr: str) -> CustomConfigType:
	"""Get config values, validate them, and return them as a dict.

	Get config values from a configfile.
	Specification of 'configfile' in configfile is disallowed.
	Validate values for some keys as specified in SCHEMA.
	"""

	# inside this function, configfile is a Path object
	configfile = Path(configfilestr)

	assert configfile.is_absolute()

	extension = configfile.suffix

	if extension == '.ini':
		parser = configparser.ConfigParser()
		data = parser.read(configfile)
	elif extension == '.toml':
		with open(configfile, 'rb') as f:
			data = tomllib.load(f)
	elif extension in ['.yaml', '.yml']:
		with open(configfile, 'r', encoding='utf-8') as f:
			data = yaml.safe_load(f)
	else:
		msg = ('Unsupported configfile extension.'
			f'  configfile: {str(configfile)!r}')
		raise ValueError(msg)

	if 'configfile' in data:
		msg = ('Improper attempt in configfile to redefine configfile.'
			f'  configfile: {str(configfile)!r}')
		raise ValueError(msg)

	assert isinstance(data, dict)  # for mypy

	validate(data)
	return data


def get_config(*args: str) -> dict:
	"""
	Return a copy of the cached config dict (or a subset of its items).

	If args are passed, then return a new dict of only those keys and
	their values from the cached config dict.

	If an arg is missing from the keys of the cached config dict, what
	should happen?  (a) raise an exception, or, (b) assign None, or,
	(c) skip.
	"""

	fullconfig: CustomConfigType = get_fullconfig()

	if len(args) == 0:
		buf = fullconfig
	else:
		# # (a) if missing key, then raise an exception
		# buf = {key: fullconfig[key] for key in args}

		buf = {}
		for key in args:
			# (a) if missing key, then raise an exception
			buf[key] = fullconfig[key]
			# # (b) if missing key, then assign None
			# buf[key] = fullconfig.get(key)
			# # (c) if missing key, then skip
			# buf[key] = fullconfig[key] if key in fullconfig.keys()

	# Protect the original items in fullconfig from alteration.
	result: CustomConfigType = copy.deepcopy(buf)
	return result


def get_fullconfig() -> dict:
	"""Return a copy of the cached config dict. Construct it if necessary.

	To construct,
	1.  Collect config info from argv and from environment variables.
	2.  Determine the configuration file location.
	3.  Read config info from the configuration file.
	4.  Combine config info from sources per precedence

	Strengths
	*   Instead of reconstructing the config dict each time this
		function is called, the config dict is determined the first time
		this function is run and then the function always returns the
		same value without reconstructing it.
		This implementation uses the common approach of using a module-
		level variable to store the value after its initial creation.
		This pattern is often referred to as memoization or lazy
		initialization.

	Weaknesses
	*   Each override could be logged.
		The cost of implementation including unit test and complexity
		and maintainability may exceed benefit.

	*   Provenances for all settings could be kept in a provenance
		dictionary, and be logged before the function returns.
		The cost of implementation including unit test and complexity
		and maintainability may exceed benefit.
	"""

	global _cached_config

	if _cached_config is not None:
		return _cached_config

	# Milestone -- This must be the first time running this function.
	# Construct the config dict, cache it, and return it.

	validate(defaults)

	# Collect config info from argv and from environment variables.
	config_from_argv = get_config_from_argv()  # returns validated data
	config_from_environ = get_config_from_environ()  # returns validated data

	# Determine the configuration file location.
	if (val := config_from_argv.get('configfile')):
		configfile = val
		flag_mustexist = True  # important for exception handling
	elif (val := config_from_environ.get('configfile')):
		configfile = val
		flag_mustexist = True  # important for exception handling
	else:
		configfile = defaults['configfile']
		flag_mustexist = False  # important for exception handling

	if not os.path.isabs(configfile):
		if (val := config_from_argv.get('configdir')):
			configdir = val
		elif (val := config_from_environ.get('configdir')):
			configdir = val
		else:
			configdir = defaults['configdir']

		configfile = str(Path(configdir).joinpath(Path(configfile)).resolve())

	effective_configfile = configfile  # keep to stuff back into result

	# Read config info from the configuration file.
	# What if the configfile is missing or fouled?
	# *   If the configfile is user-specified, the expectation is that
	#     it exists and is valid.  If missing or fouled, raise an
	#     exception.
	# *   If the configfile is defined by the default, the expectation
	#     is that if it exists, it is valid.  If missing, then log it
	#     and carry on.  If extant but fouled, raise an exception.
	try:
		config_from_configfile = get_config_from_configfile(configfile)
	except FileNotFoundError as e:
		if flag_mustexist:
			raise
		else:
			logger.info(e)
			config_from_configfile = {}

	# Combine config info from sources per precedence

#---
	# .  Initialize result dict from a copy of defaults
	# .  Update result dict with config info from
#---

	# Aggregate 4 dicts.  Use myupdate instead of dict update method.
	result = copy.deepcopy(defaults)  # this preserves the defaults dict
	myupdate(result, config_from_configfile)
	myupdate(result, config_from_environ)
	myupdate(result, config_from_argv)

	result['configfile'] = effective_configfile

	# mypathexpand(result)  # replace relative paths with absolute paths

	# finalize or resolve...
	finalize(result)  # replace relative paths with absolute paths per SCHEMA

	# logger.debug('%s: %s', 'provenance', provenance)
	logger.debug('%s:\n%s', 'result', pprint.pformat(result))
	_cached_config = result
	return result


def myupdate(target: dict, addendum: dict) -> None:
	"""..."""

	# if the addendum has 'enable' dict, then merge the existing
	# target['enable'] into addendum['enable'] before target.update()

	if target.get('enable') is not None and addendum.get('enable') is not None:
		buf = {}
		buf.update(target['enable'])
		buf.update(addendum['enable'])
		addendum['enable'] = buf

	target.update(addendum)


def finalize(data: dict) -> None:
	configdir = Path(data['configdir'])
	assert configdir.is_absolute()
	configfile = Path(data['configfile'])
	assert configfile.is_absolute()

	files = data['logging_configfiles']
	for i, item in enumerate(files):
		if not Path(item).is_absolute():
			files[i] = str(configdir / files[i])


def mypathexpand(target: dict) -> None:
	"""
	For all items in the target that should be Path objects, ensure
	they are absolute paths.
	Overrides from environment variables need to be converted from str
	to Path, and, relative paths need to be anchored to configdir.
	"""

	if not isinstance(target['configdir'], Path):
		target['configdir'] = Path(target['configdir'])
	configdir = target['configdir']
	assert configdir.is_absolute()

	if not isinstance(target['configfile'], Path):
		target['configfile'] = Path(target['configfile'])
	if not target['configfile'].is_absolute():
		target['configfile'] = configdir.joinpath(Path(target['configfile']))

	files = target['logging_configfiles']
	for i, item in enumerate(files):
		if not isinstance(files[i], Path):
			files[i] = Path(files[i])
		if not files[i].is_absolute():
			files[i] = configdir.joinpath(files[i])

	# Actually, never mind.
	# We want them
	return


def mypathexpand(target: dict) -> None:
	"""
	For all items in the target that should be Path objects, ensure
	they are absolute paths.
	Overrides from environment variables need to be converted from str
	to Path, and, relative paths need to be anchored to configdir.
	"""

	if not isinstance(target['configdir'], Path):
		target['configdir'] = Path(target['configdir'])
	configdir = target['configdir']
	assert configdir.is_absolute()

	if not isinstance(target['configfile'], Path):
		target['configfile'] = Path(target['configfile'])
	if not target['configfile'].is_absolute():
		target['configfile'] = configdir.joinpath(Path(target['configfile']))

	files = target['logging_configfiles']
	for i, item in enumerate(files):
		if not isinstance(files[i], Path):
			files[i] = Path(files[i])
		if not files[i].is_absolute():
			files[i] = configdir.joinpath(files[i])

	return
