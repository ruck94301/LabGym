from LabGym import config

"""
To arrange the configuration dict returned by get_config, need to choose
whether to patch the outer wrapper (get_config) or the inner function
(get_fullconfig).

Because module M has already imported config.get_config, the "Golden
Guidance" applies: you must
*   patch the outer wrapper (get_config) where module M sees it,
*   or, patch the inner function (get_fullconfig) within module config
	before the outer wrapper (get_config) is called.

------------------------------------------------------------------------

------------------------------------------------------------------------
To patch the inner function (get_fullconfig), keeping the logic of the
outer wrapper (get_config) intact (:




"""

def patch_config_dict(mp, data_dict):
	"""Patch the dict returned by config.get_fullconfig.

	Calling function passes in its monkeypatch fixture.

	Why patch get_fullconfig like
		a.  (config, 'get_fullconfig', lambda: data_dict)
	instead of get_config
		b.  (<module>.config, 'get_config', lambda *args: data_dict)

	Doesn't the Golden Guidance "Patch where the object is USED, not
	where it is DEFINED" suggest the latter (b)?

	Because (a) ensures the get_config args are employed for the test,
	instead of ignored.  Also, (a)
	"""
	mp.setattr(config, 'get_fullconfig', lambda: data_dict)
