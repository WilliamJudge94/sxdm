import unittest
import os
import sys
import warnings

if __name__ == '__main__':
    start_dir = os.path.dirname(__file__)
    tests = unittest.defaultTestLoader.discover(start_dir)
    runner = unittest.runner.TextTestRunner(buffer=False)

    with warnings.catch_warnings():
        # Run tests
        result = runner.run(tests)
    sys.exit(not result.wasSuccessful())
