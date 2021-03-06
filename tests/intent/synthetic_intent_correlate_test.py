import unittest
import os
import shutil
import numpy as np
import pandas as pd
from ds_behavioral import SyntheticBuilder
from ds_behavioral.intent.synthetic_intent_model import SyntheticIntentModel
from aistac.properties.property_manager import PropertyManager


class SyntheticIntentCorrelateTest(unittest.TestCase):

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

    def test_correlate_join(self):
        tools = self.tools
        df = pd.DataFrame()
        df['A'] = [1,2,3]
        df['B'] = list('XYZ')
        df['C'] = [4.2,7.1,4.1]
        result = tools.correlate_join(df, header='B', action="values", sep='_')
        self.assertEqual(['X_values', 'Y_values', 'Z_values'], result)
        result = tools.correlate_join(df, header='A', action=tools.action2dict(method='correlate_numbers', header='C'))
        self.assertEqual(['14.2', '27.1', '34.1'], result)

    def test_correlate_forename_to_gender(self):
        tools = self.tools
        df = pd.DataFrame(data=['M', 'F', 'M', 'M', 'M', 'F', np.nan], columns=['gender'])
        categories = ['M', 'nan']
        result = tools.correlate_forename_to_gender(canonical=df, header='gender', categories=categories)
        result = pd.Series(result)
        self.assertEqual(3, result[result.isna()].size)
        self.assertEqual(4, result[result.notna()].size)
        categories = ['nan', 'F']
        result = tools.correlate_forename_to_gender(canonical=df, header='gender', categories=categories)
        result = pd.Series(result)
        self.assertEqual(5, result[result.isna()].size)
        self.assertEqual(2, result[result.notna()].size)

    def test_correlate_number(self):
        tools = self.tools
        df = pd.DataFrame(data=[1,2,3,4.0,5,6,7,8,9,0], columns=['numbers'])
        result = tools.correlate_numbers(df, 'numbers', precision=0)
        self.assertCountEqual([1,2,3,4,5,6,7,8,9,0], result)
        # Offset
        df = pd.DataFrame(data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0], columns=['numbers'])
        result = tools.correlate_numbers(df, 'numbers', offset=1, precision=0)
        self.assertEqual([2,3,4,5,6,7,8,9,10,1], result)
        # multiply offset
        df = pd.DataFrame(data=[1, 2, 3, 4], columns=['numbers'])
        result = tools.correlate_numbers(df, 'numbers', offset=2, multiply_offset=True, precision=0)
        self.assertEqual([2,4,6,8], result)
        # spread
        df = pd.DataFrame(data=[2] * 1000, columns=['numbers'])
        result = tools.correlate_numbers(df, 'numbers', spread=5, precision=0)
        self.assertLessEqual(max(result), 4)
        self.assertGreaterEqual(min(result), 0)
        df = pd.DataFrame(data=tools.get_number(99999, size=5000), columns=['numbers'])
        result = tools.correlate_numbers(df, 'numbers', spread=5, precision=1)
        self.assertNotEqual(df['numbers'].to_list(), result)
        self.assertEqual(5000, len(result))
        for index in range(len(result)):
            loss = abs(df['numbers'][index] - result[index])
            self.assertLessEqual(loss, 5)
        df = pd.DataFrame(data=tools.get_number(99999, size=5000), columns=['numbers'])
        result = tools.correlate_numbers(df, 'numbers', spread=1, precision=1)
        self.assertNotEqual(df['numbers'].to_list(), result)
        self.assertEqual(5000, len(result))
        for index in range(len(result)):
            loss = abs(df['numbers'][index] - result[index])
            self.assertLessEqual(loss, 1)

    def test_correlate_number_extras(self):
        tools = self.tools
        # weighting
        df = pd.DataFrame(columns=['numbers'], data=[2] * 1000)
        result = tools.correlate_numbers(df, 'numbers', spread=5, precision=0, weighting_pattern=[0, 0, 1, 1])
        self.assertCountEqual([2,3,4], list(pd.Series(result).value_counts().index))
        result = tools.correlate_numbers(df, 'numbers', spread=5, precision=0, weighting_pattern=[1, 1, 0, 0])
        self.assertCountEqual([0,1,2], list(pd.Series(result).value_counts().index))
        # fill nan
        df = pd.DataFrame(columns=['numbers'], data=[1,1,2,np.nan,3,1,np.nan,3,5,np.nan,7])
        result = tools.correlate_numbers(df, 'numbers', fill_nulls=True, precision=0)
        self.assertEqual([1,1,2,1,3,1,1,3,5,1,7], result)
        df = pd.DataFrame(columns=['numbers'], data=[2] * 1000)
        # spread, offset and fillna
        result = tools.correlate_numbers(df, 'numbers', offset=2, spread=5, fill_nulls=True, precision=0)
        self.assertCountEqual([2,3,4,5,6], list(pd.Series(result).value_counts().index))
        # min
        df = pd.DataFrame(columns=['numbers'], data=[2] * 100)
        result = tools.correlate_numbers(df, 'numbers', offset=2, spread=5, min_value=4, precision=0)
        self.assertCountEqual([4, 5, 6], list(pd.Series(result).value_counts().index))
        result = tools.correlate_numbers(df, 'numbers', offset=2, spread=5, min_value=6, precision=0)
        self.assertCountEqual([6], list(pd.Series(result).value_counts().index))
        with self.assertRaises(ValueError) as context:
            result = tools.correlate_numbers(df, 'numbers', offset=2, spread=5, min_value=7, precision=0)
        self.assertTrue("The min value 7 is greater than the max result value" in str(context.exception))
        # max
        result = tools.correlate_numbers(df, 'numbers', offset=2, spread=5, max_value=4, precision=0)
        self.assertCountEqual([2, 3, 4], list(pd.Series(result).value_counts().index))
        result = tools.correlate_numbers(df, 'numbers', offset=2, spread=5, max_value=2, precision=0)
        self.assertCountEqual([2], list(pd.Series(result).value_counts().index))
        with self.assertRaises(ValueError) as context:
            result = tools.correlate_numbers(df, 'numbers', offset=2, spread=5, max_value=1, precision=0)
        self.assertTrue("The max value 1 is less than the min result value" in str(context.exception))

    def test_correlate_categories(self):
        tools = self.tools
        df = pd.DataFrame(columns=['cat'], data=list("ABCDE"))
        correlation = ['A', 'D']
        action = {0: 'F', 1: 'G'}
        result = tools.correlate_categories(df, 'cat', correlations=correlation, actions=action)
        self.assertEqual(['F', 'B', 'C', 'G', 'E'], result)
        correlation = ['A', 'D']
        action = {0: {'method': 'get_category', 'selection': list("HIJ")}, 1: {'method': 'get_number', 'to_value': 10}}
        result = tools.correlate_categories(df, 'cat', correlations=correlation, actions=action)
        self.assertIn(result[0], list("HIJ"))
        self.assertTrue(0 <= result[3] < 10)
        df = pd.DataFrame(columns=['cat'], data=tools.get_category(selection=list("ABCDE"), size=5000))
        result = tools.correlate_categories(df, 'cat', correlations=correlation, actions=action)
        self.assertEqual(5000, len(result))

    def test_correlate_categories_multi(self):
        tools = self.tools
        df = pd.DataFrame(columns=['cat'], data=list("ABCDEFGH"))
        df['cat'] = df['cat'].astype('category')
        correlation = [list("ABC"), list("DEFGH")]
        action = {0: False, 1: True}
        result = tools.correlate_categories(df, 'cat', correlations=correlation, actions=action)
        self.assertEqual([False, False, False, True, True, True, True, True], result)

    def test_correlate_date(self):
        tools = self.tools
        df = pd.DataFrame(columns=['dates'], data=['2019/01/30', '2019/02/12', '2019/03/07', '2019/03/07'])
        result = tools.correlate_dates(df, 'dates', date_format='%Y/%m/%d')
        self.assertEqual(df['dates'].to_list(), result)
        # offset
        result = tools.correlate_dates(df, 'dates', offset=2, date_format='%Y/%m/%d')
        self.assertEqual(['2019/02/01', '2019/02/14', '2019/03/09', '2019/03/09'], result)
        result = tools.correlate_dates(df, 'dates', offset=-2, date_format='%Y/%m/%d')
        self.assertEqual(['2019/01/28', '2019/02/10', '2019/03/05', '2019/03/05'], result)
        result = tools.correlate_dates(df, 'dates', offset={'years': 1, 'months': 2}, date_format='%Y/%m/%d')
        self.assertEqual(['2020/03/30', '2020/04/12', '2020/05/07', '2020/05/07'], result)
        result = tools.correlate_dates(df, 'dates', offset={'years': -1, 'months': 2}, date_format='%Y/%m/%d')
        self.assertEqual(['2018/03/30', '2018/04/12', '2018/05/07', '2018/05/07'], result)
        # spread
        df = pd.DataFrame(columns=['dates'], data=tools.get_datetime("2018/01/01,", '2018/01/02', size=1000))
        result = tools.correlate_dates(df, 'dates', spread=5, spread_units='D')
        loss = pd.Series(result) - df['dates']
        self.assertEqual(5, loss.value_counts().size)
        result = tools.correlate_dates(df, 'dates', spread=5, spread_units='s')
        loss = pd.Series(result) - df['dates']
        self.assertEqual(5, loss.value_counts().size)
        # spread weighting
        result = tools.correlate_dates(df, 'dates', spread=5, spread_units='D', spread_pattern=[0,0,1,1,1])
        loss = pd.Series(result) - df['dates']
        self.assertEqual(3, loss.value_counts().size)
        self.assertEqual(0, loss.loc[loss.apply(lambda x: x.days < 0)].size)
        self.assertEqual(1000, loss.loc[loss.apply(lambda x: x.days >= 0)].size)
        # nulls
        df = pd.DataFrame(columns=['dates'], data=['2019/01/30', np.nan, '2019/03/07', '2019/03/07'])
        result = tools.correlate_dates(df, 'dates')
        self.assertEqual('NaT', str(result[1]))

    def test_correlate_date_min_max(self):
        tools = self.tools
        # control
        df = pd.DataFrame(columns=['dates'], data=tools.get_datetime("2018/01/01", '2018/01/02', size=1000))
        result = tools.correlate_dates(df, 'dates', spread=5, date_format='%Y/%m/%d')
        self.assertEqual("2017/12/30", pd.Series(result).min())
        # min
        result = tools.correlate_dates(df, 'dates', spread=5, min_date="2018/01/01", date_format='%Y/%m/%d')
        self.assertEqual("2018/01/01", pd.Series(result).min())
        self.assertEqual("2018/01/03", pd.Series(result).max())
        # max
        result = tools.correlate_dates(df, 'dates', spread=5, max_date="2018/01/01", date_format='%Y/%m/%d')
        self.assertEqual("2018/01/01", pd.Series(result).max())
        self.assertEqual("2017/12/30", pd.Series(result).min())



if __name__ == '__main__':
    unittest.main()
