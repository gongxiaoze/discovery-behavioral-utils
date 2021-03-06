import unittest
import os
import shutil
import pandas as pd
import numpy as np
from ds_behavioral.intent.synthetic_intent_model import SyntheticIntentModel
from ds_behavioral import SyntheticBuilder
from aistac.properties.property_manager import PropertyManager


class SyntheticIntentGetTest(unittest.TestCase):

    def setUp(self):
        os.environ['HADRON_PM_PATH'] = os.path.join('work', 'config')
        os.environ['HADRON_DEFAULT_PATH'] = os.path.join('work', 'data')
        try:
            os.makedirs(os.environ['HADRON_PM_PATH'])
            os.makedirs(os.environ['HADRON_DEFAULT_PATH'])
        except:
            pass
        PropertyManager._remove_all()

    def tearDown(self):
        try:
            shutil.rmtree('work')
        except:
            pass

    @property
    def tools(self) -> SyntheticIntentModel:
        return SyntheticBuilder.scratch_pad()

    def test_runs(self):
        """Basic smoke test"""
        im = SyntheticBuilder.from_env('tester', default_save=False, default_save_intent=False,
                                       reset_templates=False).intent_model
        self.assertTrue(SyntheticIntentModel, type(im))

    def test_get_number(self):
        tools = self.tools
        sample_size = 10000
        # from to int
        ref_ids = tools.get_number(range_value=1000, to_value=10000, precision=0, at_most=1, size=10)
        self.assertTrue(all(isinstance(x, np.int64) for x in ref_ids))
        result = tools.get_number(10, 1000, size=sample_size)
        self.assertEqual(sample_size, len(result))
        self.assertGreaterEqual(min(result), 10)
        self.assertLessEqual(max(result), 1000)
        self.assertTrue(type)
        result = tools.get_number(10, size=sample_size)
        self.assertEqual(sample_size, len(result))
        self.assertGreaterEqual(min(result), 0)
        self.assertLessEqual(max(result), 10)
        # from to float
        result = tools.get_number(0.1, 0.9, size=sample_size)
        self.assertEqual(sample_size, len(result))
        self.assertGreaterEqual(min(result), 0.1)
        self.assertLessEqual(max(result), 0.9)
        result = tools.get_number(1.0, size=sample_size)
        self.assertEqual(sample_size, len(result))
        self.assertGreaterEqual(min(result), 0)
        self.assertLessEqual(max(result), 1.0)
        # from
        result = tools.get_number(10, 1000, size=sample_size)
        self.assertEqual(sample_size, len(result))
        self.assertGreaterEqual(min(result), 10)
        self.assertLessEqual(max(result), 1000)
        # set both
        result = tools.get_number(range_value=10, to_value=1000, size=sample_size)
        self.assertEqual(sample_size, len(result))
        self.assertGreaterEqual(min(result), 10)
        self.assertLessEqual(max(result), 1000)
        # set to_value
        result = tools.get_number(to_value=1000, size=sample_size)
        self.assertEqual(sample_size, len(result))
        self.assertGreaterEqual(min(result), 0)
        # self.assertLessEqual(max(result), 1000)

    def test_get_number_at_most(self):
        tools = self.tools
        sample_size = 100000
        result = tools.get_number(100000, 200000, precision=0, at_most=1, size=sample_size)
        self.assertEqual(sample_size, pd.Series(result).nunique())
        result = tools.get_number(100000.0, 200000.0, precision=2, at_most=1, size=sample_size)
        self.assertEqual(sample_size, pd.Series(result).nunique())
        tools = self.tools
        sample_size = 19
        result = tools.get_number(10, 20, precision=0, at_most=2, size=sample_size)
        self.assertEqual(2, pd.Series(result).value_counts().max())
        self.assertEqual(sample_size, len(result))

    def test_get_number_large(self):
        tools = self.tools
        sample_size = 1000
        result = tools.get_number(1000000, 9999999999, precision=1, size=sample_size)
        self.assertEqual(sample_size,len(result))
        result = tools.get_number(1000000.0, 9999999999.0, precision=1, size=sample_size)
        self.assertEqual(sample_size, len(result))
        # at_most
        result = tools.get_number(1000000, 9999999999, at_most=1, precision=1, size=sample_size)
        self.assertEqual(sample_size, len(result))
        result = tools.get_number(1000000.0, 9999999999.0, at_most=1, precision=1, size=sample_size)
        self.assertEqual(sample_size, len(result))

    def test_get_number_dominant(self):
        tools = self.tools
        sample_size = 5000
        result = tools.get_number(10, 1000, dominant_values=0, dominant_percent=91.74, precision=2, size=sample_size)
        self.assertEqual(sample_size, len(result))
        result = pd.Series(result)
        count = result.where(result == 0).dropna()
        self.assertTrue(0.91 <= round(len(count)/sample_size, 2) <= 0.93)

    def test_get_number_weighting(self):
        tools = self.tools
        sample_size = 10
        result = tools.get_number(0, 10, ordered='asc', size=sample_size)
        result = pd.Series(result)
        print(result)

    def test_get_number_weighting(self):
        tools = self.tools
        sample_size = 100000
        result = tools.get_number(10, 20, weight_pattern=[0,1], size=sample_size)
        result = pd.Series(result)
        self.assertGreaterEqual(result.min(), 15)
        self.assertLess(result.max(), 20)
        result = tools.get_number(10.0, 20.0, weight_pattern=[0,1], size=sample_size)
        result = pd.Series(result)
        self.assertGreaterEqual(result.min(), 15)
        self.assertLess(result.max(), 20)

    def test_get_datetime_at_most(self):
        tools = self.tools
        sample_size = 10000
        result = tools.get_datetime('2018/01/01', '2019/01/01', at_most=1, size=sample_size)
        result = pd.Series(result)
        self.assertEqual(sample_size, pd.Series(result).nunique())

    def test_get_datetime(self):
        tools = self.tools
        sample_size = 10000
        result = tools.get_datetime('2019/01/01', '2019/01/02', date_format="%Y-%m-%d", size=sample_size)
        self.assertEqual(1, pd.Series(result).nunique())
        result = tools.get_datetime(0, 1, date_format="%Y-%m-%d", ignore_time=True, size=sample_size)
        self.assertEqual(pd.Timestamp.now().strftime("%Y-%m-%d"), pd.Series(result).value_counts().index[0])



if __name__ == '__main__':
    unittest.main()
