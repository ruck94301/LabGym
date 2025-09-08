#!/Users/john/venvs/3.10+LG.v2.9.0+/bin/python3.10
# -*- coding: utf-8 -*-
import os
import re
import sys

# (from https://docs.pytorch.org/docs/stable/jit.html)
# Setting the environment variable PYTORCH_JIT=0 will disable all
# script and tracing annotations. If there is hard-to-debug error in
# one of your TorchScript models, you can use this flag to force
# everything to run using native Python. Since TorchScript (scripting
# and tracing) is disabled with this flag, you can use tools like pdb
# to debug the model code.
#
# This is a workaround for pyinstaller discovery trouble which is
# manifest during app execution, during import of detectron2, like
#     Traceback (most recent call last):
#       File "torch/_sources.py", line 23, in get_source_lines_and_file
#       File "inspect.py", line 1121, in getsourcelines
#       File "inspect.py", line 958, in findsource
#     OSError: could not get source code
# 
#     The above exception was the direct cause of the following exception:
# 
#     Traceback (most recent call last):
#     ...
#     OSError: Can't get source for <class
#     'LabGym.detectron2.modeling.box_regression.Box2BoxTransform'>.
#     TorchScript requires source access in order to carry out compilation,
#     make sure original .py files are available.
#     [PYI-85218:ERROR] Failed to execute script 'myapp' due to unhandled
#     exception!
#
# John is uncertain about the performance impact of this workaround.
# The better solution would be to identify the libraries/files that
# are required but not automatically discovered, and specify them to
# pyinstaller for inclusion.
os.environ['PYTORCH_JIT'] = '0'

from LabGym.__main__ import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
