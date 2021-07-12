from Guard import Histograms
import unittest

import numpy
import time



class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_learnSingleton(self):

        m = Histograms.Histograms({
            "histograms": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })
        for i in range(1000):
            r = m.assess({'histograms': [[1E10, 0, 1, 1E10, 0, 1E10]]})
            #print(r)
            #print(m.mean)
            self.assertLess(r[0], 0.25)
            m.learn()

        #print(m.mean)
        self.assertEqual(len(m.keys["test-01"]), 1)
        self.assertAlmostEqual(m.mean[0][0], 2E10, delta=1E9)
        self.assertLess(m.sdev[0][0], 1E9)
        self.assertAlmostEqual(m.mean[1][0], 0.5, delta=0.05)
        self.assertLess(m.sdev[1][0], 0.05)
        self.assertAlmostEqual(m.mean[2][0], 1E-10, delta=1E11)
        self.assertLess(m.sdev[2][0], 1E11)
        self.assertAlmostEqual(m.mean[3][0], 2E10, delta=1E9)
        self.assertLess(m.sdev[3][0], 1E9)
        self.assertAlmostEqual(m.mean[4][0], 5E-11, delta=1E-9)
        self.assertLess(m.sdev[4][0], 1E-9)
        self.assertAlmostEqual(m.mean[5][0], 2E10, delta=1E9)
        self.assertLess(m.sdev[5][0], 1E9)
        self.assertAlmostEqual(m.mean[6][0], 1, delta=0.1)
        self.assertLess(m.sdev[6][0], 0.1)
        self.assertAlmostEqual(m.mean[7][0], 5E-11, delta=1E-9)
        self.assertLess(m.sdev[7][0], 1E-9)


    def test_store(self):
        m = Histograms.Histograms({
            "histograms": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })
        for i in range(1000):
            r = m.assess({'histograms': [[1E10, 0, 1, 1E10, 0, 1E10]]})
            #print (r)
            self.assertLess(r[0], 0.25)
            m.learn()
        status = {}
        m.crdstore(status)
        #print(status)

        self.assertTrue("_n" in status)
        self.assertEqual(status["_n"], 1000)

        self.assertTrue("histograms" in status)
        values = status["histograms"]
        self.assertTrue(isinstance(values, dict))

        self.assertTrue("test-01" in values)
        val = values["test-01"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertEqual(len(keys), 1)
        key = keys[0]
        val = val[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertAlmostEqual(1000, val["c"], delta=10)
        self.assertAlmostEqual(2E13, val["s"], delta=1E12)
        self.assertAlmostEqual(4E23, val["s2"], delta=1E22)

        self.assertTrue("test-12" in values)
        val = values["test-12"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertEqual(len(keys), 1)
        key = keys[0]
        val = val[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertAlmostEqual(1000, val["c"], delta=10)
        self.assertAlmostEqual(500, val["s"], delta=10)
        self.assertAlmostEqual(250, val["s2"], delta=10)


        self.assertTrue("test-23" in values)
        val = values["test-23"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertEqual(len(keys), 1)
        key = keys[0]
        val = val[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertAlmostEqual(1000, val["c"], delta=10)
        self.assertAlmostEqual(1E-7, val["s"] , delta=1E-8)
        self.assertAlmostEqual(1E-10, val["s2"], delta=1E-6)


        self.assertTrue("test-34" in values)
        val = values["test-34"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertGreaterEqual(len(keys), 1)
        key = keys[0]
        val = val[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertAlmostEqual(1000, val["c"], delta=10)
        self.assertAlmostEqual(2E13, val["s"] , delta=1E12)
        self.assertAlmostEqual(4E23, val["s2"], delta=1E22)


        self.assertTrue("test-45" in values)
        val = values["test-45"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertEqual(len(keys), 1)
        key = keys[0]
        val = val[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertAlmostEqual(1000, val["c"], delta=10)
        self.assertAlmostEqual(5E-8, val["s"] , delta=1E-8)
        self.assertAlmostEqual(3.5E-18, val["s2"], delta=1E-18)


    def test_load(self):
        m = Histograms.Histograms({
            "histograms": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })
