from unittest import TestCase

import crowdai

class TestCrowdAI(TestCase):
    def test_is_string(self):
        s = crowdai.test()
        self.assertTrue(isinstance(s, basestring))
