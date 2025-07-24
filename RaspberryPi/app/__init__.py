# app/__init__.py

# This file marks 'app' as a package.
# Optionally, you can import submodules here for easier access.

# For example, you might do:
# from .receive import server
# from .detection import predictor
# from .wait_prediction import predict
# from .core import data_formatter, storage

## Sample ##
# app/__init__.py

from .receive import server
from .detection import predictor
from .wait_prediction import predict
from .core import data_formatter, storage
##  ##