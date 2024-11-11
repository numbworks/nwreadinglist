# GLOBAL MODULES
import numpy as np
import os
import pandas as pd
import sys
import unittest
from datetime import datetime, date
from numpy import float64, int32
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from parameterized import parameterized
from typing import Literal, Tuple
from unittest.mock import Mock, call, patch

# LOCAL MODULES
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwreadinglist import RLCN, RLID, _MessageCollection, DefaultPathProvider, MDInfo, RLDataFrameHelper, RLSummary, YearProvider, SettingBag, ComponentBag
from nwreadinglist import RLDataFrameFactory, RLMarkdownFactory
from nwshared import MarkdownHelper, Formatter, FilePathManager

# SUPPORT METHODS
class SupportMethodProvider():

    '''Collection of generic purpose test-aiding methods.'''

    @staticmethod
    def get_dtype_names(df : DataFrame) -> list[str]:

        '''
            The default df.dtypes return most dtypes as "object", even if they are "string".
            This method convert them back to the standard names and return them as list[str].                 
        '''

        dtype_names : list[str] = []
        for dtype in df.convert_dtypes().dtypes:
            dtype_names.append(dtype.name)

        return dtype_names
class ObjectMother():

    '''Collects all the DTOs required by the unit tests.'''

    @staticmethod
    def create_default_sa_by_2024_df() -> DataFrame:

        default_df : DataFrame = pd.DataFrame(
            {
                "Month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "2024": ["0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)"]
            },
            index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        )

        default_df = default_df.astype({"Month": int})
        default_df = default_df.astype({"2024": str})

        return default_df

# TEST CLASSES
class MDInfoTestCase(unittest.TestCase):
    
    def test_mdinfo_shouldinitializeasexpected_wheninvoked(self):
        
        # Arrange
        # Act
        md_info : MDInfo = MDInfo(
            id = RLID.RL,
            file_name = "READINGLIST.md",
            paragraph_title = "Reading List"
        )

        # Assert
        self.assertEqual(md_info.id, RLID.RL)
        self.assertEqual(md_info.file_name, "READINGLIST.md")
        self.assertEqual(md_info.paragraph_title, "Reading List")
class RLSummaryTestCase(unittest.TestCase):

    def test_rlsummary_shouldinitializeasexpected_wheninvoked(self):
        
        # Arrange
        df : DataFrame = DataFrame({"col1": [1, 2], "col2": [3, 4]})
        tpl : Tuple[DataFrame, DataFrame] = (df, df)
        footer : str = "Some Markdown footer."
        tpl_footer: Tuple[DataFrame, DataFrame, str] = (df, df, footer)
        content : str = "Some Markdown content."

        # Act
        rl_summary : RLSummary = RLSummary(
            rl_df = df,
            rl_asrt_df = df,
            rl_by_kbsize_df = df,
            sas_by_month_tpl = tpl,
            sas_by_year_street_price_df = df,
            sas_by_topic_df = df,
            sas_by_publisher_tpl = tpl_footer,
            sas_by_rating_df = df,
            trend_by_year_topic_df = df,
            definitions_df = df,
            rl_md = content,
            rl_asrt_md = content,
            sas_md = content,
            sas_by_topic_md = content,
            sas_by_publisher_md = content,
            sas_by_rating_md = content
        )

        # Assert
        assert_frame_equal(rl_summary.rl_df, df)
        assert_frame_equal(rl_summary.rl_asrt_df, df)
        assert_frame_equal(rl_summary.rl_by_kbsize_df, df)
        assert_frame_equal(rl_summary.sas_by_month_tpl[0], df)
        assert_frame_equal(rl_summary.sas_by_month_tpl[1], df)
        assert_frame_equal(rl_summary.sas_by_year_street_price_df, df)
        assert_frame_equal(rl_summary.sas_by_topic_df, df)
        assert_frame_equal(rl_summary.sas_by_publisher_tpl[0], df)
        assert_frame_equal(rl_summary.sas_by_publisher_tpl[1], df)
        self.assertEqual(rl_summary.sas_by_publisher_tpl[2], footer)
        assert_frame_equal(rl_summary.sas_by_rating_df, df)
        assert_frame_equal(rl_summary.trend_by_year_topic_df, df)
        assert_frame_equal(rl_summary.definitions_df, df)
        self.assertEqual(rl_summary.rl_md, content)
        self.assertEqual(rl_summary.rl_asrt_md, content)
        self.assertEqual(rl_summary.sas_md, content)
        self.assertEqual(rl_summary.sas_by_topic_md, content)
        self.assertEqual(rl_summary.sas_by_publisher_md, content)
        self.assertEqual(rl_summary.sas_by_rating_md, content)
class SettingBagTestCase(unittest.TestCase):

    def test_settingbag_shouldinitializeasexpected_wheninvoked(self):
        
        # Arrange
        options_rl : list[Literal["display", "save"]] = ["display", "save"]
        options_rl_asrt : list[Literal["display", "log"]] = ["display", "log"]
        options_rl_by_kbsize : list[Literal["display", "plot"]] = ["display", "plot"]
        options_rl_by_books_year : list[Literal["plot"]] = ["plot"]
        options_sas : list[Literal["display", "save"]] = ["display", "save"]
        options_sas_by_topic : list[Literal["display", "save"]] = ["display", "save"]
        options_sas_by_publisher : list[Literal["display", "log", "save"]] = ["display", "log", "save"]
        options_sas_by_rating : list[Literal["display", "save"]] = ["display", "save"]
        options_trend_by_year_topic : list[Literal["display", "save"]] = ["display", "save"]
        options_definitions : list[Literal["display"]] = ["display"]
        read_years : list[int] = [2022, 2023]
        excel_path : str = "Reading List.xlsx"
        excel_books_nrows : int = 100
        excel_books_skiprows : int = 0
        excel_books_tabname : str = "Books"
        excel_null_value : str = "-"
        kbsize_ascending : bool = False
        kbsize_remove_if_zero : bool = True
        kbsize_n : int = 10
        md_stars_rating : bool = True
        md_last_update : datetime = datetime.now()
        md_infos : list[MDInfo] = [ MDInfo(id = RLID.RL, file_name = "READINGLIST.md", paragraph_title = "Reading List") ]
        publisher_n : int = 10
        publisher_formatters : dict[str, str] = {"AvgRating": "{:.2f}", "AB%": "{:.2f}"}
        publisher_min_books : int = 8
        publisher_min_avgrating : float = 2.5
        publisher_min_ab_perc : float = 100.0
        publisher_criteria : Literal["Yes", "No"] = "Yes"
        trend_sparklines_maximum : bool = False
        working_folder_path : str = "/home/nwreadinglist/"
        now : datetime = datetime.now()
        n : int = 5
        rounding_digits : int = 2

        # Act
        setting_bag : SettingBag = SettingBag(
            options_rl = options_rl,
            options_rl_asrt = options_rl_asrt,
            options_rl_by_kbsize = options_rl_by_kbsize,
            options_rl_by_books_year = options_rl_by_books_year,
            options_sas = options_sas,
            options_sas_by_topic = options_sas_by_topic,
            options_sas_by_publisher = options_sas_by_publisher,
            options_sas_by_rating = options_sas_by_rating,
            options_trend_by_year_topic = options_trend_by_year_topic,
            options_definitions = options_definitions,
            read_years = read_years,
            excel_path = excel_path,
            excel_books_nrows = excel_books_nrows,
            excel_books_skiprows = excel_books_skiprows,
            excel_books_tabname = excel_books_tabname,
            excel_null_value = excel_null_value,
            kbsize_ascending = kbsize_ascending,
            kbsize_remove_if_zero = kbsize_remove_if_zero,
            kbsize_n = kbsize_n,
            md_stars_rating = md_stars_rating,
            md_last_update = md_last_update,
            md_infos = md_infos,
            publisher_n = publisher_n,
            publisher_formatters = publisher_formatters,
            publisher_min_books = publisher_min_books,
            publisher_min_avgrating = publisher_min_avgrating,
            publisher_min_ab_perc = publisher_min_ab_perc,
            publisher_criteria = publisher_criteria,
            trend_sparklines_maximum = trend_sparklines_maximum,
            working_folder_path = working_folder_path,
            now = now,
            n = n,
            rounding_digits = rounding_digits
        )

        # Assert
        self.assertEqual(setting_bag.options_rl, options_rl)
        self.assertEqual(setting_bag.options_rl_asrt, options_rl_asrt)
        self.assertEqual(setting_bag.options_rl_by_kbsize, options_rl_by_kbsize)
        self.assertEqual(setting_bag.options_rl_by_books_year, options_rl_by_books_year)
        self.assertEqual(setting_bag.options_sas, options_sas)
        self.assertEqual(setting_bag.options_sas_by_topic, options_sas_by_topic)
        self.assertEqual(setting_bag.options_sas_by_publisher, options_sas_by_publisher)
        self.assertEqual(setting_bag.options_sas_by_rating, options_sas_by_rating)
        self.assertEqual(setting_bag.options_trend_by_year_topic, options_trend_by_year_topic)
        self.assertEqual(setting_bag.options_definitions, options_definitions)
        self.assertEqual(setting_bag.read_years, read_years)
        self.assertEqual(setting_bag.excel_path, excel_path)
        self.assertEqual(setting_bag.excel_books_nrows, excel_books_nrows)
        self.assertEqual(setting_bag.excel_books_skiprows, excel_books_skiprows)
        self.assertEqual(setting_bag.excel_books_tabname, excel_books_tabname)
        self.assertEqual(setting_bag.excel_null_value, excel_null_value)
        self.assertEqual(setting_bag.kbsize_ascending, kbsize_ascending)
        self.assertEqual(setting_bag.kbsize_remove_if_zero, kbsize_remove_if_zero)
        self.assertEqual(setting_bag.kbsize_n, kbsize_n)
        self.assertEqual(setting_bag.md_stars_rating, md_stars_rating)
        self.assertEqual(setting_bag.md_last_update, md_last_update)
        self.assertEqual(setting_bag.md_infos[0].id, md_infos[0].id)
        self.assertEqual(setting_bag.md_infos[0].file_name, md_infos[0].file_name)
        self.assertEqual(setting_bag.md_infos[0].paragraph_title, md_infos[0].paragraph_title)
        self.assertEqual(setting_bag.publisher_n, publisher_n)
        self.assertEqual(setting_bag.publisher_formatters, publisher_formatters)
        self.assertEqual(setting_bag.publisher_min_books, publisher_min_books)
        self.assertEqual(setting_bag.publisher_min_avgrating, publisher_min_avgrating)
        self.assertEqual(setting_bag.publisher_min_ab_perc, publisher_min_ab_perc)
        self.assertEqual(setting_bag.publisher_criteria, publisher_criteria)
        self.assertEqual(setting_bag.trend_sparklines_maximum, trend_sparklines_maximum)
        self.assertEqual(setting_bag.working_folder_path, working_folder_path)
        self.assertEqual(setting_bag.now, now)
        self.assertEqual(setting_bag.n, n)
        self.assertEqual(setting_bag.rounding_digits, rounding_digits)
class MessageCollectionTestCase(unittest.TestCase):

    def test_nomdinfofound_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        expected : str = "No MDInfo object found for id='rl'."
        
        # Act
        actual : str = _MessageCollection.no_mdinfo_found(id = RLID.RL)
        
        # Assert
        self.assertEqual(actual, expected)
    def test_pleaseruninitializefirst_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        expected : str = "Please run the 'initialize' method first."

        # Act
        actual : str = _MessageCollection.please_run_initialize_first()
        
        # Assert
        self.assertEqual(actual, expected)
    def test_thiscontentsuccessfullysaved_shouldreturnexpectedmessage_wheninvoked(self):

        # Arrange
        expected : str = "This content (id: 'rl') has been successfully saved as '/home/nwreadinglist/READINGLIST.md'."
        
        # Act
        actual : str = _MessageCollection.this_content_successfully_saved_as(id = RLID.RL, file_path = "/home/nwreadinglist/READINGLIST.md")
        
        # Assert
        self.assertEqual(actual, expected)
class DefaultPathProviderTestCase(unittest.TestCase):

    def test_getdefaultreadinglistpath_shouldreturnexpectedpath_wheninvoked(self):
        
        '''"C:/project_dir/src/" => "C:/project_dir/data/Reading List.xlsx"'''

        # Arrange
        expected : str = "C:/project_dir/data/Reading List.xlsx"

        # Act
        with patch.object(os, 'getcwd', return_value="C:/project_dir/src/") as mocked_context:
            actual : str = DefaultPathProvider().get_default_reading_list_path()

        # Assert
        self.assertEqual(expected, actual)
class YearProviderTestCase(unittest.TestCase):

    def test_getallyears_shouldreturnexpectedlist_wheninvoked(self):

        # Arrange
        expected : list[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

        # Act
        actual : list[int] = YearProvider().get_all_years()

        # Assert
        self.assertEqual(expected, actual)
class RLDataFrameHelperTestCase(unittest.TestCase):

    @parameterized.expand([
        [0, 0, "0 (0)"],
        [13, 5157, "13 (5157)"]
    ])
    def test_formatreadingstatus_shouldreturnexpectedstring_wheninvoked(self, books : int, pages : int, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().format_reading_status(books = books, pages = pages)

        # Assert
        self.assertEqual(expected, actual)

    def test_getdefaultsabyyear_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        expected : DataFrame = ObjectMother().create_default_sa_by_2024_df()

        # Act
        actual : DataFrame = RLDataFrameHelper().get_default_sa_by_year(read_year = 2024)

        # Assert
        assert_frame_equal(expected, actual)

    @parameterized.expand([
        ["0 (0)", 0],
        ["13 (5157)", 13]
    ])
    def test_extractbooksfromtrend_shouldreturnexpectedint_wheninvoked(self, trend : str, expected : int):
        
        # Arrange
        # Act
        actual : int = RLDataFrameHelper().extract_books_from_trend(trend = trend)

        # Assert
        self.assertEqual(expected, actual)    

    @parameterized.expand([
        [13, 16, "↑"],
        [16, 13, "↓"],
        [0, 0, "="]
    ])
    def test_gettrend_shouldreturnexpectedstring_wheninvoked(self, value_1 : int, value_2 : int, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().get_trend(value_1 = value_1, value_2 = value_2)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ["13 (5157)", "16 (3816)", "↑"],
        ["16 (3816)", "13 (5157)", "↓"],
        ["0 (0)", "0 (0)", "="]
    ])
    def test_gettrendbybooks_shouldreturnexpectedstring_wheninvoked(self, trend_1 : str, trend_2 : str, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().get_trend_by_books(trend_1 = trend_1, trend_2 = trend_2)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ["2016", "2016"],
        ["↕1", "↕"]
    ])
    def test_tryconsolidatetrendcolumnname_shouldreturnexpectedstring_wheninvoked(self, column_name : str, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().try_consolidate_trend_column_name(column_name = column_name)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ["13 (5157)", 5157],
        ["0 (0)", 0]
    ])
    def test_extractpagesfromtrend_shouldreturnexpectedint_wheninvoked(self, trend : str, expected : int):
        
        # Arrange
        # Act
        actual : int = RLDataFrameHelper().extract_pages_from_trend(trend = trend)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ["2016", "2016_Books"]
    ])
    def test_formatyearbookscolumnname_shouldreturnexpectedstring_wheninvoked(self, year_cn : str, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().format_year_books_column_name(year_cn = year_cn)

        # Assert
        self.assertEqual(expected, actual)
    
    @parameterized.expand([
        ["2016", "2016_Pages"]
    ])
    def test_formatyearpagescolumnname_shouldreturnexpectedstring_wheninvoked(self, year_cn : str, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().format_year_pages_column_name(year_cn = year_cn)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ["2016_Books", "2016"],
        ["2016_Pages", "2016"]
    ])
    def test_extractyearfromcolumnname_shouldreturnexpectedstring_wheninvoked(self, column_name : str, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().extract_year_from_column_name(column_name = column_name)

        # Assert
        self.assertEqual(expected, actual)
    
    @parameterized.expand([
        [1447.14, 2123.36, "↑"],
        [2123.36, 1447.14, "↓"],
        [0, 0, "="]
    ])
    def test_gettrendwhenfloat64_shouldreturnexpectedstring_wheninvoked(self, value_1 : float64, value_2 : float64, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().get_trend_when_float64(value_1 = value_1, value_2 = value_2)

        # Assert
        self.assertEqual(expected, actual)

    def test_createreadyearsdataframe_shouldreturnexpecteddataframe_whenreadyears(self):
        
        # Arrange
        read_years : list[int] = [2020, 2021, 2022]
        expected : DataFrame = pd.DataFrame(data = [2020, 2021, 2022], columns = [RLCN.READYEAR])

        # Act
        actual : DataFrame = RLDataFrameHelper().create_read_years_dataframe(read_years = read_years)

        # Assert
        assert_frame_equal(actual, expected)
    def test_createreadyearsdataframe_shouldreturnemptydataframe_whenemptyreadyears(self):
        
        # Arrange
        read_years : list[int] = []
        expected : DataFrame = pd.DataFrame(data = [], columns = [RLCN.READYEAR])

        # Act
        actual : DataFrame = RLDataFrameHelper().create_read_years_dataframe(read_years = read_years)

        # Assert
        assert_frame_equal(actual, expected)


# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)