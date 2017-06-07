#!/usr/bin/env python
from __future__ import print_function
import json
from cornbread.xorg import *

print(FocusedWindow.get().to_json())
