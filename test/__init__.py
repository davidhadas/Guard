import unittest
from test_Markets import MyTestCase

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(MyTestCase('test_add'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)