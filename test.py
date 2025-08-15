#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Run unit tests

See:
    http://pyunit.sourceforge.net/pyunit.html
"""
import typing
import unittest
import os


__HERE__=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep


class Test(unittest.TestCase):
    """
    Run unit test
    """

    def setUp(self):
        """
        Set up the test
        """

    def tearDown(self):
        """
        Tear down the test
        """

    def testName(self):
        """
        Example test
        """
        assert not True


def testSuite():
    """
    Combine unit tests into an entire suite
    """
    testSuite = unittest.TestSuite()
    testSuite.addTest(Test("testName"))
    return testSuite


def cmdline(args:typing.Iterable[str]):
    """
    Run all the test suites in the standard way.
    """
    _=args
    unittest.main()


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
