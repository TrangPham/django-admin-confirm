# For some reason the working directory of tests
# And running the server are different
# (Possibly due to test_project being within a subfolder)
# This defaults settings to local unless
# DJANGO_SETTINGS_MODULE is specified.
from .local import *
