#!venv/bin/python2.7
# -*- coding: utf-8 -*-

import os
from google.appengine.ext import vendor

# Add any libraries install in the "lib" folder.
# https://cloud.google.com/appengine/docs/standard/python/tools/using-libraries-python-27#installing_a_library
vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs'))
