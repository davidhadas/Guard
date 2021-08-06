from Guard import Combinations
import unittest

import numpy as np
import time



class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.usamples = np.random.uniform(0, 1, 1000)
        pass

    def test_new_concepts(self):
        x = [[0.5,0.0002], [1, 1], [1E-5, -1E-5], [2, -2], [10, -20]]

        for p in x:
            m = Combinations.Combinations({
                "combinations": ["test"]
                , "AllowLimit": 10
                , "LearnLimit": 3
                , "collectorId": "mygate"
                , "minimumLearning": 200
            })
            fname_idx = 0
            key_idx = m.getKeyIdx(fname_idx)
            m.addConcept(fname_idx, key_idx, np.array([p[0]]*100) + self.usamples[0:100], np.array([p[1]]*100) + self.usamples[0:100])
            status = {}
            m.crdstore(status)
            print(status)

            self.assertTrue("combinations" in status)
            val = status["combinations"]
            self.assertTrue(isinstance(val, dict))
            self.assertTrue("test" in val)
            values = val["test"]
            self.assertTrue(isinstance(values, dict))
            keys = list(values.keys())
            print(keys, type(keys))
            self.assertEqual(len(keys), 1)
            v = values[keys[0]]
            self.assertIsInstance(v, dict)
            print(v)
            self.assertTrue("wi1h" in v)
            self.assertTrue("wi2h" in v)
            self.assertTrue("bih" in v)
            self.assertTrue("who1" in v)
            self.assertTrue("who2" in v)
            self.assertTrue("bho1" in v)
            self.assertTrue("bho2" in v)
            self.assertIsInstance(v["wi1h"], float)
            self.assertIsInstance(v["wi2h"], float)
            self.assertIsInstance(v["bih"], float)
            self.assertIsInstance(v["who1"], float)
            self.assertIsInstance(v["who2"], float)
            self.assertIsInstance(v["bho1"], float)
            self.assertIsInstance(v["bho2"], float)
            self.assertLess(abs(v["wi1h"]), 1E10)
            self.assertLess(abs(v["wi2h"]), 1E10)
            self.assertLess(abs(v["bih"]), 1E10)
            self.assertLess(abs(v["who1"]), 1E10)
            self.assertLess(abs(v["who2"]), 1E10)
            self.assertLess(abs(v["bho1"]), 1E10)
            self.assertLess(abs(v["bho2"]), 1E10)
            self.assertGreater(abs(v["wi1h"]), 1E-10)
            self.assertGreater(abs(v["wi2h"]), 1E-10)
            self.assertGreater(abs(v["bih"]), 1E-10)
            self.assertGreater(abs(v["who1"]), 1E-10)
            self.assertGreater(abs(v["who2"]), 1E-10)
            self.assertGreater(abs(v["bho1"]), 1E-10)
            self.assertGreater(abs(v["bho2"]), 1E-10)


    def test_learnSingletonWithCorellation(self):
        x = [[0.5, 0.02], [1, 1], [1E-5, -1E-5], [2, -2], [10, -20], [7777, -7777]]

        startTime = time.time()
        for p in x:
            print("------------> ",p)
            m = Combinations.Combinations({
                "combinations": ["test"]
                , "AllowLimit": 10
                , "LearnLimit": 3
                , "collectorId": "mygate"
                , "minimumLearning": 200
            })

            for i in range(110):
                r = m.assess({'combinations': [[p[0]+self.usamples[i], p[1]+self.usamples[i]]]})
                m.learn()

            for i in range(890):
                r = m.assess({'combinations': [[p[0]+self.usamples[i], p[1]+self.usamples[i]]]})
                #print ("r[0]", r[0])
                m.learn()

            self.assertFalse(m.unused[0][0])
            self.assertTrue(m.unused[0][1])
            self.assertTrue(m.unused[0][2])
            self.assertTrue(m.unused[0][3])

            status = {}
            m.crdstore(status)
            print(status)

            self.assertTrue("combinations" in status)
            val = status["combinations"]
            self.assertTrue(isinstance(val, dict))
            self.assertTrue("test" in val)
            values = val["test"]
            self.assertTrue(isinstance(values, dict))
            keys = list(values.keys())
            print(keys, type(keys))
            self.assertEqual(1, len(keys))
            v = values[keys[0]]
            self.assertIsInstance(v, dict)
            print(v)
            self.assertTrue("wi1h" in v)
            self.assertTrue("wi2h" in v)
            self.assertTrue("bih" in v)
            self.assertTrue("who1" in v)
            self.assertTrue("who2" in v)
            self.assertTrue("bho1" in v)
            self.assertTrue("bho2" in v)
            self.assertIsInstance(v["wi1h"], float)
            self.assertIsInstance(v["wi2h"], float)
            self.assertIsInstance(v["bih"], float)
            self.assertIsInstance(v["who1"], float)
            self.assertIsInstance(v["who2"], float)
            self.assertIsInstance(v["bho1"], float)
            self.assertIsInstance(v["bho2"], float)
            self.assertLess(abs(v["wi1h"]), 1E10)
            self.assertLess(abs(v["wi2h"]), 1E10)
            self.assertLess(abs(v["bih"]), 1E10)
            self.assertLess(abs(v["who1"]), 1E10)
            self.assertLess(abs(v["who2"]), 1E10)
            self.assertLess(abs(v["bho1"]), 1E10)
            self.assertLess(abs(v["bho2"]), 1E10)
            self.assertGreater(abs(v["wi1h"]), 1E-10)
            self.assertGreater(abs(v["wi2h"]), 1E-10)
            self.assertGreater(abs(v["bih"]), 1E-10)
            self.assertGreater(abs(v["who1"]), 1E-10)
            self.assertGreater(abs(v["who2"]), 1E-10)
            self.assertGreater(abs(v["bho1"]), 1E-10)
            self.assertGreater(abs(v["bho2"]), 1E-10)

            r = m.assess({'combinations': [[p[0], p[1]]]})
            self.assertLess(r[0], 3)

            r = m.assess({'combinations': [[p[0] + 0.5, p[1] + 0.5]]})
            self.assertLess(r[0], 3)

            r = m.assess({'combinations': [[p[0]+1, p[1]+1]]})
            self.assertLess(r[0], 3)

            r = m.assess({'combinations': [[p[0]+10, p[1]]]})
            self.assertGreater(r[0], 10)

            r = m.assess({'combinations': [[p[0], p[1]+10]]})
            self.assertGreater(r[0], 10)

            r = m.assess({'combinations': [[p[0] + 1, p[1]]]})
            self.assertGreater(r[0], 10)

            r = m.assess({'combinations': [[p[0], p[1] + 1]]})
            self.assertGreater(r[0], 10)

    def test_learnSingletonPoint(self):
        x = [[0.5, 0.02], [1, 1], [1E-5, -1E-5], [2, -2], [10, -20], [7777, -7777]]
        #x = [[0.5, 0.02]]

        startTime = time.time()
        for p in x:
            print("------------> ",p)
            m = Combinations.Combinations({
                "combinations": ["test"]
                , "AllowLimit": 10
                , "LearnLimit": 3
                , "collectorId": "mygate"
                , "minimumLearning": 200
            })

            for i in range(110):
                r = m.assess({'combinations': [[p[0], p[1]]]})
                m.learn()

            for i in range(890):
                r = m.assess({'combinations': [[p[0], p[1]]]})
                #print ("r[0]", r[0])
                m.learn()

            self.assertFalse(m.unused[0][0])
            self.assertTrue(m.unused[0][1])
            self.assertTrue(m.unused[0][2])
            self.assertTrue(m.unused[0][3])

            status = {}
            m.crdstore(status)
            print(status)

            self.assertTrue("combinations" in status)
            val = status["combinations"]
            self.assertTrue(isinstance(val, dict))
            self.assertTrue("test" in val)
            values = val["test"]
            self.assertTrue(isinstance(values, dict))
            keys = list(values.keys())
            print(keys, type(keys))
            self.assertEqual(1, len(keys))
            v = values[keys[0]]
            self.assertIsInstance(v, dict)
            print(v)
            self.assertTrue("wi1h" in v)
            self.assertTrue("wi2h" in v)
            self.assertTrue("bih" in v)
            self.assertTrue("who1" in v)
            self.assertTrue("who2" in v)
            self.assertTrue("bho1" in v)
            self.assertTrue("bho2" in v)
            self.assertIsInstance(v["wi1h"], float)
            self.assertIsInstance(v["wi2h"], float)
            self.assertIsInstance(v["bih"], float)
            self.assertIsInstance(v["who1"], float)
            self.assertIsInstance(v["who2"], float)
            self.assertIsInstance(v["bho1"], float)
            self.assertIsInstance(v["bho2"], float)
            self.assertLess(abs(v["wi1h"]), 1E10)
            self.assertLess(abs(v["wi2h"]), 1E10)
            self.assertLess(abs(v["bih"]), 1E10)
            self.assertLess(abs(v["who1"]), 1E10)
            self.assertLess(abs(v["who2"]), 1E10)
            self.assertLess(abs(v["bho1"]), 1E10)
            self.assertLess(abs(v["bho2"]), 1E10)
            self.assertGreater(abs(v["wi1h"]), 1E-10)
            self.assertGreater(abs(v["wi2h"]), 1E-10)
            self.assertGreater(abs(v["bih"]), 1E-10)
            self.assertGreater(abs(v["who1"]), 1E-10)
            self.assertGreater(abs(v["who2"]), 1E-10)
            self.assertGreater(abs(v["bho1"]), 1E-10)
            self.assertGreater(abs(v["bho2"]), 1E-10)

            r = m.assess({'combinations': [[p[0], p[1]]]})
            self.assertLess(r[0], 3)

            r = m.assess({'combinations': [[p[0]-1, p[1]]]})
            self.assertGreater(r[0], 10)

            r = m.assess({'combinations': [[p[0], p[1]-1]]})
            self.assertGreater(r[0], 10)

            r = m.assess({'combinations': [[p[0] + 1, p[1]]]})
            self.assertGreater(r[0], 10)

            r = m.assess({'combinations': [[p[0], p[1] + 1]]})
            self.assertGreater(r[0], 10)

            r = m.assess({'combinations': [[p[0] - 1, p[1] + 1]]})
            self.assertGreater(r[0], 3)

            r = m.assess({'combinations': [[p[0] + 1, p[1] + 1]]})
            self.assertGreater(r[0], 3)

            r = m.assess({'combinations': [[p[0] - 1, p[1] - 1]]})
            self.assertGreater(r[0], 3)

            r = m.assess({'combinations': [[p[0] + 1, p[1] - 1]]})
            self.assertGreater(r[0], 3)

    def test_learnConcepts(self):
        m = Combinations.Combinations({
            "combinations": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        startTime = time.time()

        for i in range(300):
            r = m.assess({'combinations': [[1 , 2 ]]})
            #r = m.assess({'combinations': [[1+self.usamples[i], 2+self.usamples[i]]]})
            m.learn()
            #r = m.assess({'combinations': [[100 , 200 ]]})
            #m.learn()
            r = m.assess({'combinations': [[9 , 3 ]]})
            #r = m.assess({'combinations': [[5000 + 10*self.usamples[i], 5200 + self.usamples[i]]]})
            m.learn()

        self.assertFalse(m.unused[0][0])
        self.assertFalse(m.unused[0][1])
        self.assertTrue(m.unused[0][2])
        self.assertTrue(m.unused[0][3])

        m.debug(3)
        r = m.assess({'combinations': [[-700, 20]]})
        self.assertGreater(r[0], 1)
        r = m.assess({'combinations': [[1, 3]]})
        self.assertGreater(r[0], 1)
        r = m.assess({'combinations': [[2, 2]]})
        self.assertGreater(r[0], 1)
        r = m.assess({'combinations': [[2, 3]]})
        self.assertGreater(r[0], 1)
        r = m.assess({'combinations': [[1, 2]]})
        self.assertLessEqual(r[0], 1)
        r = m.assess({'combinations': [[9, 3]]})
        self.assertLessEqual(r[0], 1)

        delta = time.time() - startTime
        self.assertLess(delta, 10)

        status = {}
        m.crdstore(status)
        print(status)

        self.assertTrue("combinations" in status)
        val = status["combinations"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        print(keys, type(keys))
        self.assertEqual(2, len(keys))
        v = values[keys[0]]
        self.assertIsInstance(v, dict)
        print(v)
        self.assertTrue("wi1h" in v)
        self.assertTrue("wi2h" in v)
        self.assertTrue("bih" in v)
        self.assertTrue("who1" in v)
        self.assertTrue("who2" in v)
        self.assertTrue("bho1" in v)
        self.assertTrue("bho2" in v)
        self.assertIsInstance(v["wi1h"], float)
        self.assertIsInstance(v["wi2h"], float)
        self.assertIsInstance(v["bih"], float)
        self.assertIsInstance(v["who1"], float)
        self.assertIsInstance(v["who2"], float)
        self.assertIsInstance(v["bho1"], float)
        self.assertIsInstance(v["bho2"], float)
        self.assertLess(abs(v["wi1h"]), 1E10)
        self.assertLess(abs(v["wi2h"]), 1E10)
        self.assertLess(abs(v["bih"]), 1E10)
        self.assertLess(abs(v["who1"]), 1E10)
        self.assertLess(abs(v["who2"]), 1E10)
        self.assertLess(abs(v["bho1"]), 1E10)
        self.assertLess(abs(v["bho2"]), 1E10)
        self.assertGreater(abs(v["wi1h"]), 1E-10)
        self.assertGreater(abs(v["wi2h"]), 1E-10)
        self.assertGreater(abs(v["bih"]), 1E-10)
        self.assertGreater(abs(v["who1"]), 1E-10)
        self.assertGreater(abs(v["who2"]), 1E-10)
        self.assertGreater(abs(v["bho1"]), 1E-10)
        self.assertGreater(abs(v["bho2"]), 1E-10)


