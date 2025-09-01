#!/Users/john/venvs/3.10+LG.v2.9.0+/bin/python3.10
# -*- coding: utf-8 -*-
import os
import re
import sys
# ?!
os.environ['PYTORCH_JIT'] = '0'
from LabGym.__main__ import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
