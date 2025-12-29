# GLOBAL MODULES
import importlib
import numpy as np
import os
import pandas as pd
import sys
import unittest
from datetime import datetime, date
from numpy import float64, int32
from pandas import DataFrame
from pandas import RangeIndex
from pandas.testing import assert_frame_equal
from parameterized import parameterized
from pathlib import Path
from typing import Any, Literal, Optional, Tuple, cast
from unittest.mock import _Call, Mock, call, patch

# LOCAL/NW MODULES
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwreadinglist import REPORTSTR, RLCN, DEFINITIONSTR, OPTION, RSMODE, _MessageCollection, RLReportManager, RLSummary, DefaultPathProvider, RSCell, RSHighlighter
from nwreadinglist import SettingBag, RLDataFrameHelper, RLDataFrameFactory, YearProvider
from nwreadinglist import RLAdapter, ComponentBag, ReadingListProcessor
from nwshared import Converter, Formatter, FilePathManager, FileManager, Displayer, PlotManager

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
    def get_default_sa_by_2024_df() -> DataFrame:

        default_df : DataFrame = pd.DataFrame(
            {
                RLCN.MONTH: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "2024": ["0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)"]
            },
            index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        )

        default_df = default_df.astype({RLCN.MONTH: int})
        default_df = default_df.astype({"2024": str})

        return default_df

    @staticmethod
    def get_rl_tpl() -> Tuple[DataFrame, list[int]]:

        rl_df : DataFrame = pd.DataFrame({
            RLCN.TITLE: np.array(["ProxMox VE Administration Guide - Release 7.2", "Clean Architecture", "Python How-To", "Python Foundation", "Python Unit Test Automation (2nd Edition)", "Testing in Python", "Python Object-Oriented Programming (4th Edition)", "Intermediate Python [MLI]", "Learning Advanced Python By Studying Open-Source Projects", "Python in a Nutshell (4th Edition)", "Python 3 And Feature Engineering", "Python Testing Cookbook (2nd Edition)", "Python Testing with pytest (2nd Edition)", "Python Packages"], dtype=object),
            RLCN.YEAR: np.array([2022, 2018, 2023, 2022, 2022, 2020, 2021, 2023, 2024, 2023, 2024, 2018, 2022, 2022], dtype=int32),
            RLCN.TYPE: np.array(["Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book"], dtype=object),
            RLCN.FORMAT: np.array(["Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital"], dtype=object),
            RLCN.LANGUAGE: np.array(["EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN"], dtype=object),
            RLCN.PAGES: np.array([535, 429, 455, 205, 94, 132, 715, 192, 139, 963, 229, 978, 264, 243], dtype=int32),
            RLCN.READDATE: np.array([date(2024, 2, 19), date(2024, 2, 19), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 26), date(2024, 2, 26), date(2024, 2, 26)], dtype=object),
            RLCN.READYEAR: np.array([2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024], dtype=int32),
            RLCN.READMONTH: np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], dtype=int32),
            RLCN.WORTHBUYING: np.array(["No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "Yes"], dtype=object),
            RLCN.WORTHREADINGAGAIN: np.array(["No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "Yes", "No", "No", "No"], dtype=object),
            RLCN.PUBLISHER: np.array(["Self-Published", "Pearson Education", "Manning", "Self-Published", "Apress", "Self-Published", "Packt", "MLI", "CRC Press", "O'Reilly", "MLI", "Packt", "Pragmatic Bookshelf", "CRC Press"], dtype=object),
            RLCN.RATING: np.array([2, 3, 1, 1, 1, 1, 2, 1, 1, 3, 2, 2, 3, 4], dtype=int32),
            RLCN.STREETPRICE: np.array([0.0, 30.39, 49.99, 22.49, 38.88, 49.99, 38.24, 54.99, 59.95, 65.23, 54.99, 33.99, 39.49, 48.95], dtype= np.float64),
            RLCN.CURRENCY: np.array(["USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD"], dtype=object),
            RLCN.COMMENT: np.array(["Useful. It shows how well ProxMox has been designed.", "Useful. A good book for beginners, well-written and clear. The last part about the history of computers could be easily removed.", "Useless. Well-written, but it contains no original nor well-structured knowledge. In addition, the second half of the book is not about Python but about Flask. Totally useless book.", "Useless. Very basic overview about multiple Python-related topics. The layout of the book is horrible (dense, lack of bold face, ...).", "Useless. Just a walkthrough of Python unit test frameworks. No original content.", "Useless. Too much opinionated towards pytest, not able to explain why pytest is better than unittest in a convincing way.", "Useful. An ok getting started guide for whom wants to learn OOP and Python from scratch at the same time.", "Useless. Well-written (organized like a recipe book and without ramblings), but contains no different knowledge than hundreds of Python books.", "Useless. The book title is misleading: the author doesn't study any open-source project. It's just a Python cookbook like hundreds others.", "Useful. Well-written and comprehensive, it contains few bits of information I didn't know.", "Useful. No-frills introduction to feature engineering in a cookbook format.", "Useful. It's a long list of testing techniques and Python tools to perform them. Good to have all collected in the same book.", "Useful. A well-written and comprehensive book about pytest.", "Useful. Excellent book about the topic. It's well-written, comprehensive and pragmatic. It would become perfect by removing the repetitions."], dtype=object),
            RLCN.TOPIC: np.array(["Development Tools", "Software Engineering", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python"], dtype=object),
            RLCN.ONGOODREADS: np.array(["No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No"], dtype=object),
            RLCN.COMMENTLENGHT: np.array([52, 128, 181, 134, 80, 121, 105, 142, 138, 90, 75, 125, 59, 140], dtype=int32),
            RLCN.KBSIZE: np.array([8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=int32),
            RLCN.UNDERLINES: np.array([1, 0, 2, 0, 4, 0, 0, 0, 2, 0, 0, 15, 0, 0], dtype=int32),
        }, index=pd.RangeIndex(start=260, stop=274, step=1))

        read_years : list[int] = [ 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 ]

        return (rl_df, read_years)
    @staticmethod
    def get_rl_df_column_names() -> list[str]:

        column_names : list[str] = []
        column_names.append(RLCN.TITLE)             # [0], str
        column_names.append(RLCN.YEAR)              # [1], int
        column_names.append(RLCN.TYPE)              # [2], str
        column_names.append(RLCN.FORMAT)            # [3], str
        column_names.append(RLCN.LANGUAGE)          # [4], str
        column_names.append(RLCN.PAGES)             # [5], int
        column_names.append(RLCN.READDATE)          # [6], date
        column_names.append(RLCN.READYEAR)          # [7], int
        column_names.append(RLCN.READMONTH)         # [8], int    
        column_names.append(RLCN.WORTHBUYING)       # [9], str
        column_names.append(RLCN.WORTHREADINGAGAIN) # [10], str
        column_names.append(RLCN.PUBLISHER)         # [11], str
        column_names.append(RLCN.RATING)            # [12], int
        column_names.append(RLCN.STREETPRICE)       # [13], float
        column_names.append(RLCN.CURRENCY)          # [14], str
        column_names.append(RLCN.COMMENT)           # [15], str
        column_names.append(RLCN.TOPIC)             # [16], str
        column_names.append(RLCN.ONGOODREADS)       # [17], str
        column_names.append(RLCN.COMMENTLENGHT)     # [18], int
        column_names.append(RLCN.KBSIZE)            # [19], int
        column_names.append(RLCN.UNDERLINES)        # [20], int

        return column_names
    @staticmethod
    def get_rl_df_dtype_names() -> list[str]:

        '''Note: the 7th should be "date", but it's rendered by Pandas as "object".'''

        expected_dtype_names : list[str] = [
            "string",
            "Int64",
            "string",
            "string",
            "string",
            "Int64",
            "object",
            "Int64",
            "Int64",
            "string",
            "string",
            "string",
            "Int64",
            "Float64",
            "string",
            "string",
            "string",
            "string",
            "Int64",
            "Int64",
            "Int64"
        ]

        return expected_dtype_names
    @staticmethod
    def get_rls_by_range_df() -> DataFrame:

        col_name = f"1 {RLCN.YEARS}"
        values = [
            f"14 (5573)",
            "$587.57"
        ]

        rls_by_range_df : DataFrame = pd.DataFrame(values, columns = [col_name])

        return rls_by_range_df
    @staticmethod
    def get_rls_by_kbsize_df() -> DataFrame:

        return pd.DataFrame({
            RLCN.TITLE: np.array(["ProxMox VE Administration Guide - Release 7.2"], dtype = object),
            RLCN.READYEAR: np.array(["2024"], dtype = int32),
            RLCN.TOPIC: np.array(["Development Tools"], dtype = object),
            RLCN.PUBLISHER: np.array(["Self-Published"], dtype = object),
            RLCN.RATING: np.array(["2"], dtype = int32),
            RLCN.KBSIZE: np.array(["8"], dtype = int32),
            RLCN.A4SHEETS: np.array(["1"], dtype = np.int64),
        }, index = pd.Index([1], dtype = "int64"))   
    @staticmethod
    def get_rls_by_month_tpl() -> Tuple[DataFrame, DataFrame]:

        rls_by_month_df : DataFrame = DataFrame({
            RLCN.MONTH: np.array([str(i) for i in range(1, 13)], dtype=np.int64),
            "2023": np.array(["0 (0)"] * 12, dtype=object),
            RLCN.TRENDSYMBOL: np.array(["=", "↑", "=", "=", "=", "=", "=", "=", "=", "=", "=", "="], dtype=object),
            "2024": np.array(["0 (0)", "14 (5573)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", 
                            "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)"], dtype=object)
        }, index=pd.Index(range(12), dtype="int64"))

        rls_by_month_upd_df : DataFrame = DataFrame({
            "2023": np.array(["0 (0)"] * 12, dtype=object),
            RLCN.TRENDSYMBOL: np.array(["=", "↑", "", "", "", "", "", "", "", "", "", ""], dtype=object),
            "2024": np.array(["0 (0)", "14 (5573)", "", "", "", "", "", "", "", "", "", ""], dtype=object)
        }, index=pd.Index(range(12), dtype="int64"))

        return (rls_by_month_df, rls_by_month_upd_df)
    @staticmethod
    def get_rls_by_year_df() -> DataFrame:

        return DataFrame({
            "2023": np.array(["0 (0)", "$0.00"], dtype = object),
            RLCN.TRENDSYMBOL: np.array(["↑", "↑"], dtype = object),
            "2024": np.array(["14 (5573)", "$587.57"], dtype = object)
        }, index=pd.Index([0, 1], dtype="int64")) 
    @staticmethod
    def get_rls_by_topic_df() -> DataFrame:

        return pd.DataFrame({
            RLCN.TOPIC: np.array(["Python", "Development Tools", "Software Engineering"], dtype=object),
            RLCN.BOOKS: np.array([12, 1, 1], dtype = np.int64),
            RLCN.PAGES: np.array([4609, 535, 429], dtype = int32),
            RLCN.A4SHEETS: np.array([0, 1, 0], dtype = np.int64)
        }, index=pd.RangeIndex(start=0, stop=3, step=1))
    @staticmethod
    def get_rls_by_publisher_tpl() -> Tuple[DataFrame, DataFrame, str]:

        rls_by_publisher_df : DataFrame = DataFrame({
            RLCN.PUBLISHER: np.array(["Self-Published", "Packt", "CRC Press", "MLI", "Apress", "O'Reilly", "Manning", "Pearson Education", "Pragmatic Bookshelf"], dtype=object),
            RLCN.BOOKS: np.array([3, 2, 2, 2, 1, 1, 1, 1, 1], dtype=np.int64),
            RLCN.AVGRATING: np.array([1.33, 2.0, 2.5, 1.5, 1.0, 3.0, 1.0, 3.0, 3.0], dtype=float64),
            RLCN.A4SHEETS: np.array([1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int64),
            RLCN.ABPERC: np.array([33.33, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=float64),
            RLCN.AVGUNDERLINES: np.array([0.33, 7.5, 1.0, 0.0, 4.0, 0.0, 2.0, 0.0, 0.0], dtype=float64),
            RLCN.ISWORTH: np.array(["No", "No", "No", "No", "No", "No", "No", "No", "No"], dtype=object)
        }, index=pd.Index([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype="int64"))

        rls_by_publisher_flt_df : DataFrame = DataFrame({
            RLCN.PUBLISHER: np.array([], dtype=object),
            RLCN.BOOKS: np.array([], dtype=np.int64),
            RLCN.AVGRATING: np.array([], dtype=float64),
            RLCN.A4SHEETS: np.array([], dtype=np.int64),
            RLCN.ABPERC: np.array([], dtype=float64),
            RLCN.AVGUNDERLINES: np.array([], dtype=float64),
            RLCN.ISWORTH: np.array([], dtype=object)
        }, index=pd.Index([], dtype="int64"))

        rls_by_publisher_footer : str = "'Yes' if 'Books' >= '8' & ('AvgRating' >= '100' | 'AB%' >= '2.5')"
    
        return (rls_by_publisher_df, rls_by_publisher_flt_df, rls_by_publisher_footer)  
    @staticmethod
    def get_rls_by_rating_df() -> DataFrame:

        return pd.DataFrame({
            RLCN.RATING: np.array(["★★★★☆", "★★★☆☆", "★★☆☆☆", "★☆☆☆☆"], dtype = object),
            RLCN.BOOKS: np.array([1, 3, 4, 6], dtype = np.int64),
        }, index=pd.RangeIndex(start = 0, stop = 4, step = 1))
    @staticmethod
    def get_rls_by_topic_trend_df() -> DataFrame:

        return pd.DataFrame({
            RLCN.TOPIC: np.array(["Development Tools", "Python", "Software Engineering"], dtype=object),
            RLCN.BOOKS: pd.Series([[0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 12], [0, 0, 0, 0, 0, 0, 0, 0, 1]]).to_numpy(),
            RLCN.TREND: np.array(["▁▁▁▁▁▁▁▁▂", "▁▁▁▁▁▁▁▁█", "▁▁▁▁▁▁▁▁▂"], dtype=object),
        }, index=pd.RangeIndex(start=0, stop=3, step=1))
    @staticmethod
    def get_definitions_df() -> DataFrame:

        columns : list[str] = [DEFINITIONSTR.TERM, DEFINITIONSTR.DEFINITION]

        definitions : dict[str, str] = {
            DEFINITIONSTR.READINGLIST: f"A {DEFINITIONSTR.READINGLIST} is a list of books read as part of a continuous learning process.",
            RLCN.TOPIC: f"A {RLCN.TOPIC} is a category label that best summarizes a book's content.",
            RLCN.KBSIZE: "This metric is the total word count of the notes taken while reading a given book.",
            RLCN.A4SHEETS: f"This metric represents {RLCN.KBSIZE} converted to the corresponding amount of A4 sheets (500 words ≅ 1 A4 sheet). The higher the amount, the better the book.",
            RLCN.ABPERC: f"For a given publisher, {RLCN.ABPERC} is calculated as the total number of {RLCN.A4SHEETS} of notes taken across all books read from that publisher. The higher is {RLCN.ABPERC}, the better the publisher.",
            RLCN.UNDERLINES: "Underlines are sentences that express a fundamental concept that can be understood as-is.",
            RLCN.UPERC: f"For a given book, {RLCN.UPERC} is calculated as the number of {RLCN.UNDERLINES} in that book compared with the average number of {RLCN.UNDERLINES} across the entire reading list. The higher the {RLCN.UPERC}, the better the book.",
            DEFINITIONSTR.READINGSTATUS: f"A {DEFINITIONSTR.READINGSTATUS} is a string that reports, at a specified time grain, the number of books read and the corresponding total pages.",
            f"{RLCN.TREND} ({RLCN.TRENDSYMBOL})": "A trend is a gamification metric that indicates whether a measure (e.g., total books read) has increased or decreased over time."
        }
        
        definitions_df : DataFrame = DataFrame(
            data = definitions.items(), 
            columns = columns
        )

        return definitions_df

    @staticmethod
    def get_setting_bag(enable_rs_highlighting : bool = True) -> SettingBag:

        setting_bag : SettingBag = SettingBag(
            options_rl_rating_five = [OPTION.display],            
            options_rl_most_underlines = [OPTION.display],
            options_rls_by_month = [OPTION.display],
            options_rls_by_year = [OPTION.display],
            options_rls_by_range = [OPTION.display],
            options_rls_by_topic = [OPTION.display],
            options_rls_by_topic_trend = [OPTION.display],
            options_rls_by_publisher = [OPTION.display, OPTION.log],
            options_rls_by_rating = [OPTION.display],
            options_rls_by_underlines = [OPTION.display],
            options_definitions = [OPTION.display],
            options_report = [OPTION.save_html, OPTION.save_pdf],
            read_years = YearProvider().get_all_years(),
            excel_path = DefaultPathProvider().get_default_reading_list_path(),
            excel_nrows = 323,
            enable_rs_highlighting = enable_rs_highlighting
        )

        return setting_bag

# TEST CLASSES
class MessageCollectionTestCase(unittest.TestCase):

    def test_pleaseruninitializefirst_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        expected : str = "Please run the 'initialize' method first."

        # Act
        actual : str = _MessageCollection.please_run_initialize_first()
        
        # Assert
        self.assertEqual(actual, expected)
class RLSummaryTestCase(unittest.TestCase):

    def test_rlsummary_shouldinitializeasexpected_wheninvoked(self):
        
        # Arrange
        df : DataFrame = DataFrame({"col1": [1, 2], "col2": [3, 4]})
        tpl : Tuple[DataFrame, DataFrame] = (df, df)
        footer : str = "Some Markdown footer."
        tpl_footer: Tuple[DataFrame, DataFrame, str] = (df, df, footer)

        # Act
        rl_summary : RLSummary = RLSummary(
            rl_df = df,
            rl_enriched_df = df,
            rl_rating_five_df = df,
            rl_most_underlines_df = df,
            rls_by_month_tpl = tpl,
            rls_by_year_df = df,
            rls_by_range_df = df,
            rls_by_topic_df = df,
            rls_by_topic_trend_df = df,
            rls_by_publisher_tpl = tpl_footer,
            rls_by_rating_df = df,
            rls_by_underlines_df = df,
            definitions_df = df,

            rls_by_kbsize_df = df
        )

        # Assert
        assert_frame_equal(rl_summary.rl_df, df)
        assert_frame_equal(rl_summary.rl_enriched_df, df)
        assert_frame_equal(rl_summary.rl_rating_five_df, df)
        assert_frame_equal(rl_summary.rl_most_underlines_df, df)        
        assert_frame_equal(rl_summary.rls_by_month_tpl[0], df)
        assert_frame_equal(rl_summary.rls_by_month_tpl[1], df)
        assert_frame_equal(rl_summary.rls_by_year_df, df)
        assert_frame_equal(rl_summary.rls_by_range_df, df)
        assert_frame_equal(rl_summary.rls_by_topic_df, df)
        assert_frame_equal(rl_summary.rls_by_topic_trend_df, df)
        assert_frame_equal(rl_summary.rls_by_publisher_tpl[0], df)
        assert_frame_equal(rl_summary.rls_by_publisher_tpl[1], df)
        self.assertEqual(rl_summary.rls_by_publisher_tpl[2], footer)
        assert_frame_equal(rl_summary.rls_by_rating_df, df)
        assert_frame_equal(rl_summary.definitions_df, df)

        assert_frame_equal(rl_summary.rls_by_kbsize_df, df)
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
        expected : list[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

        # Act
        actual : list[int] = YearProvider().get_all_years()

        # Assert
        self.assertEqual(expected, actual)
class SettingBagTestCase(unittest.TestCase):

    def test_settingbag_shouldinitializeasexpected_wheninvoked(self):
        
        # Arrange
        options_rl_rating_five : list[Literal[OPTION.display]] = [OPTION.display]                                   # type: ignore[valid-type]
        options_rl_most_underlines : list[Literal[OPTION.display]] = [OPTION.display]                               # type: ignore[valid-type]
        options_rls_by_month : list[Literal[OPTION.display]] = [OPTION.display]                                     # type: ignore[valid-type]
        options_rls_by_year : list[Literal[OPTION.display]] = [OPTION.display]                                      # type: ignore[valid-type]
        options_rls_by_range : list[Literal[OPTION.display]] = [OPTION.display]                                     # type: ignore[valid-type]
        options_rls_by_topic : list[Literal[OPTION.display]] = [OPTION.display]                                     # type: ignore[valid-type]
        options_rls_by_topic_trend : list[Literal[OPTION.display]] = [OPTION.display]                               # type: ignore[valid-type]
        options_rls_by_publisher : list[Literal[OPTION.display, OPTION.log]] = [OPTION.display, OPTION.log]   # type: ignore[valid-type]
        options_rls_by_rating : list[Literal[OPTION.display]] = [OPTION.display]                                    # type: ignore[valid-type]
        options_rls_by_underlines : list[Literal[OPTION.display]] = [OPTION.display]                                # type: ignore[valid-type]
        options_definitions : list[Literal[OPTION.display]] = [OPTION.display]                                      # type: ignore[valid-type]
        options_report : list[Literal[OPTION.save_html, OPTION.save_pdf]] = [OPTION.save_html, OPTION.save_pdf]     # type: ignore[valid-type]
        read_years : list[int] = [2022, 2023]
        excel_path : str = "Reading List.xlsx"
        excel_nrows : int = 100

        options_rl : list[Literal[OPTION.display]] = [OPTION.display]                                               # type: ignore[valid-type]
        options_rl_enriched : list[Literal[OPTION.display]] = [OPTION.display]                                      # type: ignore[valid-type]
        options_rls_by_books_year : list[Literal[OPTION.plot]] = [OPTION.plot]                                      # type: ignore[valid-type]
        options_rls_by_kbsize : list[Literal[OPTION.display, OPTION.plot]] = [OPTION.display, OPTION.plot]          # type: ignore[valid-type]
        excel_skiprows : int = 0
        excel_tabname : str = "Books"
        excel_null_value : str = "-"
        working_folder_path : str = "/home/nwreadinglist/"
        rounding_digits : int = 2
        now : datetime = datetime(2025, 12, 28, 1, 12, 13, 890)
        enable_rs_highlighting : bool = False
        report_last_update : datetime = datetime(2025, 12, 28, 1, 12, 13, 890)
        rl_most_underlines_formatters : dict[str, str] = {"AvgRating": "{:.2f}", "AB%": "{:.2f}", "AvgUnderlines": "{:.2f}"}
        rls_by_kbsize_ascending : bool = False
        rls_by_kbsize_remove_if_zero : bool = True
        rls_by_kbsize_n : int = 10
        rls_by_rating_number_as_stars : bool = True
        rls_by_publisher_n : Optional[int] = 10
        rls_by_publisher_formatters : dict[str, str] = {"AvgUnderlines": "{:.2f}", "U%": "{:.2f}"}
        rls_by_publisher_min_books : int = 8
        rls_by_publisher_min_avgrating : float = 2.5
        rls_by_publisher_min_ab_perc : float = 100.0
        rls_by_publisher_criteria : Optional[Literal["Yes", "No"]] = "Yes"
        rls_by_topic_bt_sparklines_maximum : bool = False

        # Act
        setting_bag : SettingBag = SettingBag(
            options_rl_rating_five = options_rl_rating_five,
            options_rl_most_underlines = options_rl_most_underlines,
            options_rls_by_month = options_rls_by_month,
            options_rls_by_year = options_rls_by_year,
            options_rls_by_range = options_rls_by_range,
            options_rls_by_topic = options_rls_by_topic,
            options_rls_by_topic_trend = options_rls_by_topic_trend,
            options_rls_by_publisher = options_rls_by_publisher,
            options_rls_by_rating = options_rls_by_rating,
            options_rls_by_underlines = options_rls_by_underlines,
            options_definitions = options_definitions,
            options_report = options_report,
            read_years = read_years,
            excel_path = excel_path,
            excel_nrows = excel_nrows,

            options_rl = options_rl,
            options_rl_enriched = options_rl_enriched,
            options_rls_by_kbsize = options_rls_by_kbsize,
            options_rls_by_books_year = options_rls_by_books_year,
            excel_skiprows = excel_skiprows,
            excel_tabname = excel_tabname,
            excel_null_value = excel_null_value,
            working_folder_path = working_folder_path,
            rounding_digits = rounding_digits,
            now = now,
            enable_rs_highlighting = enable_rs_highlighting,
            report_last_update = report_last_update,
            rl_most_underlines_formatters = rl_most_underlines_formatters,
            rls_by_kbsize_ascending = rls_by_kbsize_ascending,
            rls_by_kbsize_remove_if_zero = rls_by_kbsize_remove_if_zero,
            rls_by_kbsize_n = rls_by_kbsize_n,
            rls_by_publisher_n = rls_by_publisher_n,
            rls_by_publisher_formatters = rls_by_publisher_formatters,
            rls_by_publisher_min_books = rls_by_publisher_min_books,
            rls_by_publisher_min_avgrating = rls_by_publisher_min_avgrating,
            rls_by_publisher_min_ab_perc = rls_by_publisher_min_ab_perc,
            rls_by_publisher_criteria = rls_by_publisher_criteria,
            rls_by_rating_number_as_stars = rls_by_rating_number_as_stars,
            rls_by_topic_trend_sparklines_maximum = rls_by_topic_bt_sparklines_maximum
        )

        # Assert
        self.assertEqual(setting_bag.options_rl_rating_five, options_rl_rating_five)
        self.assertEqual(setting_bag.options_rl_most_underlines, options_rl_most_underlines)
        self.assertEqual(setting_bag.options_rls_by_month, options_rls_by_month)
        self.assertEqual(setting_bag.options_rls_by_year, options_rls_by_year)        
        self.assertEqual(setting_bag.options_rls_by_range, options_rls_by_range)
        self.assertEqual(setting_bag.options_rls_by_topic, options_rls_by_topic)
        self.assertEqual(setting_bag.options_rls_by_topic_trend, options_rls_by_topic_trend)
        self.assertEqual(setting_bag.options_rls_by_publisher, options_rls_by_publisher)
        self.assertEqual(setting_bag.options_rls_by_rating, options_rls_by_rating)
        self.assertEqual(setting_bag.options_definitions, options_definitions)
        self.assertEqual(setting_bag.options_report, options_report)
        self.assertEqual(setting_bag.read_years, read_years)
        self.assertEqual(setting_bag.excel_path, excel_path)
        self.assertEqual(setting_bag.excel_nrows, excel_nrows)

        self.assertEqual(setting_bag.options_rl, options_rl)
        self.assertEqual(setting_bag.options_rl_enriched, options_rl_enriched)
        self.assertEqual(setting_bag.options_rls_by_books_year, options_rls_by_books_year)
        self.assertEqual(setting_bag.options_rls_by_kbsize, options_rls_by_kbsize)
        self.assertEqual(setting_bag.excel_skiprows, excel_skiprows)
        self.assertEqual(setting_bag.excel_tabname, excel_tabname)
        self.assertEqual(setting_bag.excel_null_value, excel_null_value)
        self.assertEqual(setting_bag.working_folder_path, working_folder_path)
        self.assertEqual(setting_bag.rounding_digits, rounding_digits)
        self.assertEqual(setting_bag.now, now)
        self.assertEqual(setting_bag.enable_rs_highlighting, enable_rs_highlighting)
        self.assertEqual(setting_bag.report_last_update, report_last_update)
        self.assertEqual(setting_bag.rl_most_underlines_formatters, rl_most_underlines_formatters)
        self.assertEqual(setting_bag.rls_by_kbsize_ascending, rls_by_kbsize_ascending)
        self.assertEqual(setting_bag.rls_by_kbsize_remove_if_zero, rls_by_kbsize_remove_if_zero)
        self.assertEqual(setting_bag.rls_by_kbsize_n, rls_by_kbsize_n)
        self.assertEqual(setting_bag.rls_by_publisher_n, rls_by_publisher_n)
        self.assertEqual(setting_bag.rls_by_publisher_formatters, rls_by_publisher_formatters)
        self.assertEqual(setting_bag.rls_by_publisher_min_books, rls_by_publisher_min_books)
        self.assertEqual(setting_bag.rls_by_publisher_min_avgrating, rls_by_publisher_min_avgrating)
        self.assertEqual(setting_bag.rls_by_publisher_min_ab_perc, rls_by_publisher_min_ab_perc)
        self.assertEqual(setting_bag.rls_by_publisher_criteria, rls_by_publisher_criteria)
        self.assertEqual(setting_bag.rls_by_rating_number_as_stars, rls_by_rating_number_as_stars)
        self.assertEqual(setting_bag.rls_by_topic_trend_sparklines_maximum, rls_by_topic_bt_sparklines_maximum)
class RLDataFrameHelperTestCase(unittest.TestCase):

    @parameterized.expand([
        [0, 0, "0 (0)"],
        [13, 5157, "13 (5157)"]
    ])
    def test_boxrs_shouldreturnexpectedstring_wheninvoked(self, books : int, pages : int, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().box_rs(books = books, pages = pages)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ["0 (0)", (0, 0)],
        ["13 (5157)", (13, 5157)]
    ])
    def test_unboxrs_shouldreturnexpectedtuple_wheninvoked(self, rs : str, expected : Tuple[int, int]):
        
        # Arrange
        # Act
        actual : Tuple[int, int] = RLDataFrameHelper().unbox_rs(rs = rs)

        # Assert
        self.assertEqual(expected, actual)   

    def test_getdefaultsabyyear_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        expected : DataFrame = ObjectMother().get_default_sa_by_2024_df()

        # Act
        actual : DataFrame = RLDataFrameHelper().get_default_sa_by_year(read_year = 2024)

        # Assert
        assert_frame_equal(expected, actual)

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
    def test_gettrendbybooks_shouldreturnexpectedstring_wheninvoked(self, rs_1 : str, rs_2 : str, expected : str):
        
        # Arrange
        # Act
        actual : str = RLDataFrameHelper().get_trend_by_books(rs_1 = rs_1, rs_2 = rs_2)

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
class RLDataFrameFactoryTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.df_factory : RLDataFrameFactory = RLDataFrameFactory(
                converter = Converter(),
                formatter = Formatter(),
                df_helper = RLDataFrameHelper()
            )
        
        self.excel_path : str = "Reading List.xlsx"
        self.excel_books_nrows : int = 100
        self.excel_books_skiprows : int = 0
        self.excel_books_tabname : str = "Books"
        self.excel_null_value : str = "-"
        self.rls_by_kbsize_ascending : bool = False
        self.rls_by_kbsize_remove_if_zero : bool = True  
        self.rls_by_kbsize_n : int = 10
        self.rls_by_rating_number_as_stars : bool = True
        self.rls_by_publisher_n : int = 10
        self.rls_by_publisher_formatters : dict = { "AvgRating" : "{:.2f}", "AB%" : "{:.2f}" }
        self.rls_by_publisher_min_books : int = 8
        self.rls_by_publisher_min_ab_perc : float = 2.50
        self.rls_by_publisher_min_avgrating : float = 100
        self.rls_by_publisher_criteria : Literal["Yes", "No"] = "Yes"
        self.rls_by_topic_trend_sparklines_maximum : bool = True
        self.rounding_digits : int = 2

    def test_createrldf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        rl_df : DataFrame = ObjectMother().get_rl_tpl()[0]
        expected_column_names : list[str] = ObjectMother().get_rl_df_column_names()
        expected_dtype_names : list[str] = ObjectMother().get_rl_df_dtype_names()
        
        # Act
        actual : DataFrame = pd.DataFrame()
        with patch.object(pd, 'read_excel', return_value = rl_df) as mocked_context:
            actual = self.df_factory.create_rl_df(
                excel_path = self.excel_path,
                excel_skiprows = self.excel_books_skiprows,
                excel_nrows = self.excel_books_nrows,
                excel_tabname = self.excel_books_tabname,
                excel_null_value = self.excel_null_value
            )

        # Assert
        self.assertEqual(expected_column_names, actual.columns.tolist())
        self.assertEqual(expected_dtype_names, SupportMethodProvider().get_dtype_names(df = actual))
    def test_createrlsbymonthtpl_shouldreturnexpecteddataframes_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().get_rl_tpl()[0]
        now : datetime = datetime(2024, 2, 19)
        read_years : list[int] = [ 2023, 2024 ]
        (expected_1, expected_2) = ObjectMother().get_rls_by_month_tpl()

        # Act
        (actual_1, actual_2) = self.df_factory.create_rls_by_month_tpl(
            rl_df = rl_df,
            read_years = read_years,
            now = now
        )

        # Assert
        assert_frame_equal(expected_1, actual_1)    
        assert_frame_equal(expected_2, actual_2)   
    def test_createrlsbyyeardf_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().get_rl_tpl()[0]
        rls_by_month_tpl : Tuple[DataFrame, DataFrame] = ObjectMother().get_rls_by_month_tpl()
        read_years : list[int] = [ 2023, 2024 ]
        expected : DataFrame = ObjectMother().get_rls_by_year_df()

        # Act
        actual : DataFrame = self.df_factory.create_rls_by_year_df(
            rls_by_month_tpl = rls_by_month_tpl,
            rl_df = rl_df,
            read_years = read_years,
            rounding_digits = self.rounding_digits
        )

        # Assert
        assert_frame_equal(expected, actual)   
    def test_createrlsbyrangedf_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().get_rl_tpl()[0]
        expected : DataFrame = ObjectMother().get_rls_by_range_df()

        # Act
        actual : DataFrame = self.df_factory.create_rls_by_range_df(
            rl_df = rl_df,
            rounding_digits = self.rounding_digits
        )

        # Assert
        assert_frame_equal(expected, actual)    
    
    def test_createrlsbykbsizedf_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().get_rl_tpl()[0]
        expected : DataFrame = ObjectMother().get_rls_by_kbsize_df()

        # Act
        actual : DataFrame = self.df_factory.create_rls_by_kbsize_df(
            rl_df = rl_df,
            ascending = self.rls_by_kbsize_ascending,
            remove_if_zero = self.rls_by_kbsize_remove_if_zero,
            n = self.rls_by_kbsize_n
        )

        # Assert
        assert_frame_equal(expected, actual)
    def test_createrlsbytopicdf_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().get_rl_tpl()[0]
        expected : DataFrame = ObjectMother().get_rls_by_topic_df()

        # Act
        actual : DataFrame = self.df_factory.create_rls_by_topic_df(rl_df = rl_df)

        # Assert
        assert_frame_equal(expected, actual)
    def test_createrlsbypublishertpl_shouldreturnexpecteddataframes_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().get_rl_tpl()[0]
        (expected_1, expected_2, expected_3) = ObjectMother().get_rls_by_publisher_tpl()

        # Act
        (actual_1, actual_2, actual_3) = self.df_factory.create_rls_by_publisher_tpl(
            rl_df = rl_df,
            rounding_digits = 2,
            min_books = self.rls_by_publisher_min_books,
            min_ab_perc = self.rls_by_publisher_min_ab_perc,
            min_avgrating = self.rls_by_publisher_min_avgrating,
            n = None,
            criteria = self.rls_by_publisher_criteria
        )

        # Assert
        assert_frame_equal(expected_1, actual_1)
        assert_frame_equal(expected_2, actual_2)
        self.assertEqual(expected_3, actual_3)
    def test_createrlsbyratingdf_shouldreturnexpecteddataframe_whenformattedratingequalstotrue(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().get_rl_tpl()[0]
        expected : DataFrame = ObjectMother().get_rls_by_rating_df()

        # Act
        actual : DataFrame = self.df_factory.create_rls_by_rating_df(rl_df = rl_df, number_as_stars = self.rls_by_rating_number_as_stars)

        # Assert
        assert_frame_equal(expected, actual)
    def test_createtrlsbytopicbtdf_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        (rl_df, read_years) = ObjectMother().get_rl_tpl()
        expected : DataFrame = ObjectMother().get_rls_by_topic_trend_df()

        # Act
        actual : DataFrame = self.df_factory.create_rls_by_topic_trend_df(
            rl_df = rl_df,
            read_years = read_years,
            sparklines_maximum = self.rls_by_topic_trend_sparklines_maximum
            )

        # Assert
        assert_frame_equal(expected, actual)
    def test_createdefinitionsdf_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        expected : DataFrame = ObjectMother().get_definitions_df()

        # Act
        actual : DataFrame = self.df_factory.create_definitions_df()

        # Assert
        assert_frame_equal(expected, actual)
    def test_trycompletesabyyear_shouldreturnoriginaldataframe_whenmonthcountis12(self):
        
        # Arrange
        sa_by_year_dict: dict[str, list] = {
            RLCN.MONTH: [str(i) for i in range(1, 13)], 
            RLCN.READYEAR: [2023] * 12
        }
        sa_by_year_df : DataFrame = pd.DataFrame(sa_by_year_dict)
        read_year: int = 2023

        # Act
        actual : DataFrame = self.df_factory._RLDataFrameFactory__try_complete_sa_by_year(sa_by_year_df = sa_by_year_df, read_year = read_year) # type: ignore

        # Assert
        assert_frame_equal(sa_by_year_df, actual)
class RSCellTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_whenvalidarguments(self) -> None:

        # Arrange
        coordinate_pair : Tuple[int, int] = (5, 10)
        rs : str = "13 (5157)"
        books : int = 13
        pages : int = 5157

        # Act
        rs_cell : RSCell = RSCell(
            coordinate_pair = coordinate_pair,
            rs = rs,
            books = books,
            pages = pages
        )

        # Assert
        self.assertEqual(rs_cell.coordinate_pair, coordinate_pair)
        self.assertEqual(rs_cell.rs, rs)
        self.assertEqual(rs_cell.books, books)
        self.assertEqual(rs_cell.pages, pages)
class RSHighlighterTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.rs_highlighter : RSHighlighter = RSHighlighter(df_helper = RLDataFrameHelper())

        data : dict[str, list] = {
            "Month": ["1", "2"],
            "2015": ["0 (0)", "0 (0)"],
            "↕": ["↑", "↑"],
            "2016": ["13 (5157)", "2 (275)"],
            "↕_duplicate_1": ["↑", "↑"],
            "2017": ["88 (30123)", "63 (18578)"]
        }
        columns_01 : list[str] = ["Month", "2015", "↕", "2016", "↕", "2017"]
        self.df_with_duplicates : DataFrame = DataFrame(data, columns = columns_01)

        columns_02 : list[str] = ["Month", "2015", "↕", "2016", "↕_duplicate_1", "2017"]
        self.df_without_duplicates : DataFrame = DataFrame(data, columns = columns_02)

    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:

        # Arrange
        df_helper : RLDataFrameHelper = RLDataFrameHelper()

        # Act
        actual : RSHighlighter = RSHighlighter(df_helper = df_helper)

        # Assert
        self.assertIsInstance(actual, RSHighlighter)

    @parameterized.expand([
        ("0 (0)", True),
        ("2 (275)", True),
        ("13 (5157)", True),
        ("63 (18578)", True),
        ("invalid", False),
        ("2 (27", False),
        (" (275)", False),
        ("(5157)", False)
    ])
    def test_isrs_shouldreturnexpectedresult_wheninvoked(self, rs: str, expected: bool) -> None:
        
        # Arrange
        # Act
        actual : bool = self.rs_highlighter._RSHighlighter__is_rs(cell_content = rs)    # type: ignore

        # Assert
        self.assertEqual(actual, expected)

    def test_appendnewrscell_shouldappendprovidedcell_wheninvoked(self) -> None:
        
        # Arrange
        rs_cells : list[RSCell] = []
        coordinate_pair : Tuple[int, int] = (5, 10)
        rs : str = "13 (5157)"
        books : int = 13
        pages : int = 5157

        # Act
        self.rs_highlighter._RSHighlighter__append_new_rs_cell(rs_cells, coordinate_pair, rs) # type: ignore

        # Assert
        self.assertEqual(len(rs_cells), 1)
        self.assertEqual(rs_cells[0].coordinate_pair, coordinate_pair)
        self.assertEqual(rs_cells[0].rs, rs)
        self.assertEqual(rs_cells[0].books, books)
        self.assertEqual(rs_cells[0].pages, pages)
    def test_extractrow_shouldreturnrscells_whenrowhasvalidtimes(self) -> None:
        
        # Arrange
        df : DataFrame = DataFrame({"2015": ["0 (0)"], "↕": ["↑"], "2016": ["63 (18578)"]})
        column_names : list[str] = ["2015", "2016"]

        # Act
        actual : list[RSCell] = self.rs_highlighter._RSHighlighter__extract_row(df = df, row_idx = 0, column_names = column_names)   # type: ignore

        # Assert
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0].rs, "0 (0)")
        self.assertEqual(actual[1].rs, "63 (18578)")

    @parameterized.expand([
        (RSMODE.top_one_per_row, 1),
        (RSMODE.top_three, 3)
    ])
    def test_extractn_shouldreturnexpected_whenvalid(self, mode: RSMODE, expected: int) -> None:
        
        # Arrange
        # Act
        actual : int = self.rs_highlighter._RSHighlighter__extract_n(mode = mode)   # type: ignore

        # Assert
        self.assertEqual(actual, expected)

    def test_extractn_shouldraiseexception_wheninvalid(self) -> None:
        
        # Arrange
        mode : RSMODE = cast(RSMODE, "Invalid")

        # Act & Assert
        with self.assertRaises(Exception):
            self.rs_highlighter._RSHighlighter__extract_n(mode = mode)   # type: ignore
    def test_extracttopnrscells_shouldreturntopncells_wheninvoked(self) -> None:

        # Arrange
        rs_cells : list[RSCell] = [
            RSCell(coordinate_pair = (0, 0), rs = "13 (5157)", books = 13, pages = 5157),
            RSCell(coordinate_pair = (0, 1), rs = "2 (275)", books = 2, pages = 275),
            RSCell(coordinate_pair = (0, 2), rs = "63 (18578)", books = 63, pages = 18578)
        ]

        # Act
        actual : list[RSCell] = self.rs_highlighter._RSHighlighter__extract_top_n_rs_cells(rs_cells = rs_cells, n = 2)   # type: ignore

        # Assert
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0].rs, "63 (18578)")
        self.assertEqual(actual[1].rs, "13 (5157)")
    def test_calculaterscells_shouldreturnexpectedcells_whentoponeperrow(self) -> None:
        
        # Arrange
        df : DataFrame = DataFrame({"2015": ["0 (0)", "2 (275)"], "↕": ["↑", "↑"], "2016": ["63 (18578)", "13 (5157)"]})
        mode : RSMODE = RSMODE.top_one_per_row
        column_names : list[str] = ["2015", "2016"]

        # Act
        actual : list[RSCell] = self.rs_highlighter._RSHighlighter__calculate_rs_cells(df = df, mode = mode, column_names = column_names)   # type: ignore

        # Assert
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0].rs, "63 (18578)")
        self.assertEqual(actual[1].rs, "13 (5157)")
    def test_calculaterscells_shouldreturnexpectedcells_whentopthree(self) -> None:
        
        # Arrange
        df : DataFrame = DataFrame({"2015": ["0 (0)", "2 (275)"], "↕": ["↑", "↑"], "2016": ["63 (18578)", "13 (5157)"]})
        mode : RSMODE = RSMODE.top_three
        column_names : list[str] = ["2015", "2016"]

        # Act
        actual : list[RSCell] = self.rs_highlighter._RSHighlighter__calculate_rs_cells(df = df, mode = mode, column_names = column_names)   # type: ignore

        # Assert
        self.assertEqual(len(actual), 3)
        self.assertEqual(actual[0].rs, "63 (18578)")
        self.assertEqual(actual[1].rs, "13 (5157)")
        self.assertEqual(actual[2].rs, "2 (275)")
    def test_calculaterscells_shouldraiseexception_wheninvalidmode(self) -> None:

        # Arrange
        df : DataFrame = DataFrame({"2015": ["0 (0)", "2 (275)"], "↕": ["↑", "↑"], "2016": ["63 (18578)", "13 (5157)"]})
        mode : RSMODE = cast(RSMODE, "Invalid")
        column_names : list[str] = ["2015", "2016"]

        expected : str = _MessageCollection.provided_mode_not_supported(mode)
        
        # Act
        with self.assertRaises(Exception) as context:
            self.rs_highlighter._RSHighlighter__calculate_rs_cells(df = df, mode = mode, column_names = column_names)   # type: ignore

        # Assert
        self.assertEqual(expected, str(context.exception))
    def test_addtags_shouldsurroundrscellsswithtokens_wheninvoked(self) -> None:

        # Arrange
        rs_cells : list[RSCell] = [
            RSCell(coordinate_pair = (0, 1), rs = "0 (0)", books = 0, pages = 1),
            RSCell(coordinate_pair = (1, 3), rs = "2 (275)", books = 2, pages = 275)
        ]
        tags : Tuple[str, str] = ("[[ ", " ]]")
        expected : DataFrame = self.df_without_duplicates.copy(deep = True)
        expected.iloc[0, 1] = "[[ 0 (0) ]]"
        expected.iloc[1, 3] = "[[ 2 (275) ]]"

        # Act
        actual : DataFrame = self.rs_highlighter._RSHighlighter__add_tags(self.df_without_duplicates, rs_cells, tags)   # type: ignore

        # Assert
        self.assertTrue(expected.equals(actual))
    def test_highlightdataframe_shouldhighlightexpectedcells_whencolumnnamesareprovided(self) -> None:

        # Arrange
        mode : RSMODE = RSMODE.top_one_per_row
        column_names : list[str] = ["2015", "2016", "2017"]

        expected : DataFrame = self.df_without_duplicates.copy(deep = True)
        expected.iloc[0, 5] = "<mark style='background-color: pink'>88 (30123)</mark>"
        expected.iloc[1, 5] = "<mark style='background-color: pink'>63 (18578)</mark>"

        # Act
        actual : DataFrame = self.rs_highlighter._RSHighlighter__highlight_dataframe(self.df_without_duplicates, mode, column_names) # type: ignore

        # Assert
        assert_frame_equal(expected, actual)
    def test_highlightdataframe_shouldhighlightexpectedcells_whencolumnnamesarenotprovided(self) -> None:

        # Arrange
        mode : RSMODE = RSMODE.top_one_per_row
        column_names : list[str] = []

        expected : DataFrame = self.df_without_duplicates.copy(deep = True)
        expected.iloc[0, 5] = "<mark style='background-color: pink'>88 (30123)</mark>"
        expected.iloc[1, 5] = "<mark style='background-color: pink'>63 (18578)</mark>"

        # Act
        actual : DataFrame = self.rs_highlighter._RSHighlighter__highlight_dataframe(self.df_without_duplicates, mode, column_names) # type: ignore

        # Assert
        assert_frame_equal(expected, actual)

    def test_highlightrlsbymonth_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        rls_by_month_df : DataFrame = DataFrame()

        highlighted_df : Mock = Mock()
        self.rs_highlighter._RSHighlighter__highlight_dataframe = highlighted_df  # type: ignore

        # Act
        self.rs_highlighter.highlight_rls_by_month(rls_by_month_df = rls_by_month_df)

        # Assert
        highlighted_df.assert_called_once_with(
            df = rls_by_month_df,
            mode = RSMODE.top_three
        )
    def test_highlightttsbyyear_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        rls_by_year_df : DataFrame = DataFrame()

        highlighted_df : Mock = Mock()
        self.rs_highlighter._RSHighlighter__highlight_dataframe = highlighted_df  # type: ignore

        # Act
        self.rs_highlighter.highlight_rls_by_year(rls_by_year_df = rls_by_year_df)

        # Assert
        highlighted_df.assert_called_once_with(
            df = rls_by_year_df,
            mode = RSMODE.top_three
        )
class ComponentBagTestCase(unittest.TestCase):
    
    def test_componentbag_shouldinitializeasexpected_wheninvoked(self):
        
        # Arrange, Act
        component_bag = ComponentBag()

        # Assert
        self.assertIsInstance(component_bag, ComponentBag)
        self.assertIsInstance(component_bag.file_path_manager, FilePathManager)
        self.assertIsInstance(component_bag.file_manager, FileManager)
        self.assertIsInstance(component_bag.rl_adapter, RLAdapter)
        self.assertIsInstance(component_bag.displayer, Displayer)
        self.assertIsInstance(component_bag.plot_manager, PlotManager)
        self.assertTrue(callable(component_bag.logging_function))
class RLAdapterTestCase(unittest.TestCase):

    def setUp(self) -> None:
        
        # Without Defaults
        self.read_years : list[int] = [2020, 2021, 2022]

        # With Defaults
        self.excel_path : str = "/home/nwreadinglist/Reading List.xlsx"
        self.excel_skiprows : int = 0
        self.excel_nrows : int = 100
        self.excel_tabname : str = "Books"
        self.excel_null_value : str = "-"
        self.rounding_digits : int = 2
        self.now : datetime = datetime(2024, 1, 1)
        self.rls_by_kbsize_n  : int = 5
        self.rls_by_kbsize_ascending : bool = True
        self.rls_by_kbsize_remove_if_zero : bool = False
        self.rls_by_publisher_n = None
        self.rls_by_publisher_min_books : int = 8
        self.rls_by_publisher_min_ab_perc : float = 100
        self.rls_by_publisher_min_avgrating : float = 2.50
        self.rls_by_publisher_criteria : str = "Yes"
        self.rls_by_rating_number_as_stars = True

        self.mocked_df_factory : Mock = Mock(spec = RLDataFrameFactory)
        self.mocked_rs_highlighter : Mock = Mock(spec = RSHighlighter)

        self.adapter : RLAdapter = RLAdapter(
            df_factory = self.mocked_df_factory,            # type: ignore
            rs_highlighter = self.mocked_rs_highlighter     # type: ignore
        )

    def test_createrldf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : RLDataFrameFactory = Mock()
        rl_adapter : RLAdapter = RLAdapter(
            df_factory = df_factory, 
            rs_highlighter = RSHighlighter(
                df_helper = RLDataFrameHelper()))

        setting_bag : SettingBag = Mock()
        setting_bag.excel_path = self.excel_path
        setting_bag.excel_skiprows = self.excel_skiprows
        setting_bag.excel_nrows = self.excel_nrows
        setting_bag.excel_tabname = self.excel_tabname
        setting_bag.excel_null_value = self.excel_null_value

        # Act
        rl_adapter.create_rl_df(setting_bag = setting_bag)

        # Assert
        df_factory.create_rl_df.assert_called_once_with(
            excel_path = self.excel_path,
            excel_skiprows = self.excel_skiprows,
            excel_nrows = self.excel_nrows,
            excel_tabname = self.excel_tabname,
            excel_null_value = self.excel_null_value
        )
    def test_createrlsbymonthtpl_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : RLDataFrameFactory = Mock()
        rl_adapter : RLAdapter = RLAdapter(
            df_factory = df_factory, 
            rs_highlighter = RSHighlighter(
                df_helper = RLDataFrameHelper()))

        setting_bag : SettingBag = Mock()
        setting_bag.read_years = self.read_years
        setting_bag.now = self.now

        rl_df : DataFrame = Mock()

        # Act
        rl_adapter.create_rls_by_month_tpl(rl_df = rl_df, setting_bag = setting_bag)

        # Assert
        df_factory.create_rls_by_month_tpl.assert_called_once_with(
            rl_df = rl_df,
            read_years = self.read_years,
            now = self.now
        )
    def test_createrlsbyyeardf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : RLDataFrameFactory = Mock()
        rl_adapter : RLAdapter = RLAdapter(
            df_factory = df_factory, 
            rs_highlighter = RSHighlighter(
                df_helper = RLDataFrameHelper()))

        setting_bag : SettingBag = Mock()
        setting_bag.read_years = self.read_years
        setting_bag.rounding_digits = self.rounding_digits

        rl_df : DataFrame = Mock()
        rls_by_month_tpl : Tuple[DataFrame, DataFrame] = (Mock(), Mock())

        # Act
        rl_adapter.create_rls_by_year_df(
            rls_by_month_tpl = rls_by_month_tpl,
            rl_df = rl_df,
            setting_bag = setting_bag
        )

        # Assert
        df_factory.create_rls_by_year_df.assert_called_once_with(
            rls_by_month_tpl = rls_by_month_tpl,
            rl_df = rl_df,
            read_years = self.read_years,
            rounding_digits = self.rounding_digits
        )
    def test_createrlsbyrangedf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : RLDataFrameFactory = Mock()
        rl_adapter : RLAdapter = RLAdapter(
            df_factory = df_factory, 
            rs_highlighter = RSHighlighter(
                df_helper = RLDataFrameHelper()))

        setting_bag : SettingBag = Mock()
        setting_bag.rounding_digits = self.rounding_digits
        setting_bag.now = self.now

        rl_df : DataFrame = Mock()

        # Act
        rl_adapter.create_rls_by_range_df(rl_df = rl_df, setting_bag = setting_bag)

        # Assert
        df_factory.create_rls_by_range_df.assert_called_once_with(
            rl_df = rl_df,
            rounding_digits = self.rounding_digits
        )        

    def test_createrlsbykbdf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : RLDataFrameFactory = Mock()
        rl_adapter : RLAdapter = RLAdapter(
            df_factory = df_factory, 
            rs_highlighter = RSHighlighter(
                df_helper = RLDataFrameHelper()))

        setting_bag : SettingBag = Mock()
        setting_bag.rls_by_kbsize_n = self.rls_by_kbsize_n
        setting_bag.rls_by_kbsize_ascending = self.rls_by_kbsize_ascending
        setting_bag.rls_by_kbsize_remove_if_zero = self.rls_by_kbsize_remove_if_zero

        rl_df : DataFrame = Mock()

        # Act
        rl_adapter.create_rls_by_kbsize_df(rl_df = rl_df, setting_bag = setting_bag)

        # Assert
        df_factory.create_rls_by_kbsize_df.assert_called_once_with(
            rl_df = rl_df,
            n = self.rls_by_kbsize_n,
            ascending = self.rls_by_kbsize_ascending,
            remove_if_zero = self.rls_by_kbsize_remove_if_zero,
        )
    def test_createrlsbypublishertpl_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : RLDataFrameFactory = Mock()
        rl_adapter : RLAdapter = RLAdapter(
            df_factory = df_factory, 
            rs_highlighter = RSHighlighter(
                df_helper = RLDataFrameHelper()))

        setting_bag : SettingBag = Mock()
        setting_bag.rounding_digits = self.rounding_digits
        setting_bag.rls_by_publisher_min_books = self.rls_by_publisher_min_books
        setting_bag.rls_by_publisher_min_ab_perc = self.rls_by_publisher_min_ab_perc
        setting_bag.rls_by_publisher_min_avgrating = self.rls_by_publisher_min_avgrating
        setting_bag.rls_by_publisher_criteria = self.rls_by_publisher_criteria
        setting_bag.rls_by_publisher_n = self.rls_by_publisher_n

        rl_df : DataFrame = Mock()

        # Act
        rl_adapter.create_rls_by_publisher_tpl(rl_df = rl_df, setting_bag = setting_bag)

        # Assert
        df_factory.create_rls_by_publisher_tpl.assert_called_once_with(
            rl_df = rl_df,
            rounding_digits = self.rounding_digits,
            min_books = self.rls_by_publisher_min_books,
            min_ab_perc = self.rls_by_publisher_min_ab_perc,
            min_avgrating = self.rls_by_publisher_min_avgrating,
            n = self.rls_by_publisher_n,
            criteria = self.rls_by_publisher_criteria
        )
    def test_createrlsbyratingdf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : RLDataFrameFactory = Mock()
        rl_adapter : RLAdapter = RLAdapter(
            df_factory = df_factory, 
            rs_highlighter = RSHighlighter(
                df_helper = RLDataFrameHelper()))

        setting_bag : SettingBag = Mock()
        setting_bag.rls_by_rating_number_as_stars = self.rls_by_rating_number_as_stars

        rl_df : DataFrame = Mock()

        # Act
        rl_adapter.create_rls_by_rating_df(rl_df = rl_df, setting_bag = setting_bag)

        # Assert
        df_factory.create_rls_by_rating_df.assert_called_once_with(
            rl_df = rl_df,
            number_as_stars = self.rls_by_rating_number_as_stars
        )

    def test_createsummary_shouldreturnexpectedsummary_wheninvoked(self) -> None:

        # Arrange
        rl_df : DataFrame = ObjectMother.get_rl_tpl()[0]

        rls_by_month_tpl : Tuple[DataFrame, DataFrame] = ObjectMother.get_rls_by_month_tpl()
        rls_by_year_df : DataFrame = ObjectMother.get_rls_by_year_df()
        rls_by_range_df : DataFrame = ObjectMother.get_rls_by_range_df()
        rls_by_topic_df : DataFrame = ObjectMother.get_rls_by_topic_df()
        rls_by_topic_trend_df : DataFrame = ObjectMother.get_rls_by_topic_trend_df()
        rls_by_publisher_tpl : Tuple[DataFrame, DataFrame, str] = ObjectMother.get_rls_by_publisher_tpl()

        rls_by_kbsize_df : DataFrame = ObjectMother.get_rls_by_kbsize_df()
        rls_by_rating_df : DataFrame = ObjectMother.get_rls_by_rating_df()
        definitions_df : DataFrame = ObjectMother.get_definitions_df()

        df_factory : RLDataFrameFactory = Mock()
        df_factory.create_rl_df = Mock(return_value = rl_df)
        df_factory.create_rls_by_month_tpl = Mock(return_value = rls_by_month_tpl)
        df_factory.create_rls_by_year_df = Mock(return_value = rls_by_year_df)
        df_factory.create_rls_by_range_df = Mock(return_value = rls_by_range_df)
        df_factory.create_rls_by_topic_df.return_value = rls_by_topic_df
        df_factory.create_rls_by_topic_trend_df = Mock(return_value = rls_by_topic_trend_df)
        df_factory.create_rls_by_publisher_tpl = Mock(return_value = rls_by_publisher_tpl)

        df_factory.create_rls_by_kbsize_df = Mock(return_value = rls_by_kbsize_df)
        df_factory.create_rls_by_rating_df = Mock(return_value = rls_by_rating_df)
        df_factory.create_definitions_df.return_value = definitions_df

        rl_adapter : RLAdapter = RLAdapter(
            df_factory = df_factory, 
            rs_highlighter = RSHighlighter(
                df_helper = RLDataFrameHelper()))
				
        setting_bag : SettingBag = ObjectMother.get_setting_bag(enable_rs_highlighting = False)

        # Act
        actual : RLSummary = rl_adapter.create_summary(setting_bag = setting_bag)

        # Assert
        assert_frame_equal(actual.rl_df, rl_df)
        assert_frame_equal(actual.rls_by_month_tpl[0], rls_by_month_tpl[0])
        assert_frame_equal(actual.rls_by_month_tpl[1], rls_by_month_tpl[1])
        assert_frame_equal(actual.rls_by_year_df, rls_by_year_df)        
        assert_frame_equal(actual.rls_by_range_df, rls_by_range_df)
        assert_frame_equal(actual.rls_by_topic_df, rls_by_topic_df)
        assert_frame_equal(actual.rls_by_topic_trend_df, rls_by_topic_trend_df)
        assert_frame_equal(actual.rls_by_publisher_tpl[0], rls_by_publisher_tpl[0])
        assert_frame_equal(actual.rls_by_publisher_tpl[1], rls_by_publisher_tpl[1])
        self.assertEqual(actual.rls_by_publisher_tpl[2], rls_by_publisher_tpl[2])

        assert_frame_equal(actual.rls_by_kbsize_df, rls_by_kbsize_df)
        assert_frame_equal(actual.rls_by_rating_df, rls_by_rating_df)
        assert_frame_equal(actual.definitions_df, definitions_df)
    def test_createsummary_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        rl_df : DataFrame = DataFrame()
        rl_enriched_df : DataFrame = DataFrame()
        rl_rating_five_df : DataFrame = DataFrame()
        rl_most_underlines_df : DataFrame = DataFrame()
        rls_by_month_df_a : DataFrame = DataFrame()
        rls_by_month_df_b : DataFrame = DataFrame()
        rls_by_month_tpl : Tuple[DataFrame, DataFrame] = (rls_by_month_df_a, rls_by_month_df_b)
        rls_by_year_df : DataFrame = DataFrame()
        rls_by_range_df : DataFrame = DataFrame()
        rls_by_topic_df : DataFrame = DataFrame()
        rls_by_topic_trend_df : DataFrame = DataFrame()
        rls_by_publisher_tpl : Tuple[DataFrame, DataFrame, str] = (DataFrame(), DataFrame(), "")
        rls_by_rating_df : DataFrame = DataFrame()
        rls_by_underlines_df : DataFrame = DataFrame()
        definitions_df : DataFrame = DataFrame()
        rls_by_kbsize_df : DataFrame = DataFrame()

        setting_bag : SettingBag = ObjectMother.get_setting_bag(enable_rs_highlighting = True)

        with (
            patch.object(self.adapter, "create_rl_df", return_value = rl_df) as mocked_create_rl_df,
            patch.object(self.adapter, "create_rl_enriched_df", return_value = rl_enriched_df) as mocked_create_rl_enriched_df,
            patch.object(self.adapter, "create_rl_rating_five_df", return_value = rl_rating_five_df) as mocked_create_rl_rating_five_df,
            patch.object(self.adapter, "create_rl_most_underlines_df", return_value = rl_most_underlines_df) as mocked_create_rl_most_underlines_df,
            patch.object(self.adapter, "create_rls_by_month_tpl", return_value = rls_by_month_tpl) as mocked_create_rls_by_month_tpl,
            patch.object(self.adapter, "create_rls_by_year_df", return_value = rls_by_year_df) as mocked_create_rls_by_year_df,
            patch.object(self.adapter, "create_rls_by_range_df", return_value = rls_by_range_df) as mocked_create_rls_by_range_df,
            patch.object(self.mocked_df_factory, "create_rls_by_topic_df", return_value = rls_by_topic_df) as mocked_create_rls_by_topic_df,
            patch.object(self.adapter, "create_rls_by_topic_trend_df", return_value = rls_by_topic_trend_df) as mocked_create_rls_by_topic_trend_df,
            patch.object(self.adapter, "create_rls_by_publisher_tpl", return_value = rls_by_publisher_tpl) as mocked_create_rls_by_publisher_tpl,
            patch.object(self.adapter, "create_rls_by_rating_df", return_value = rls_by_rating_df) as mocked_create_rls_by_rating_df,
            patch.object(self.mocked_df_factory, "create_rls_by_underlines_df", return_value = rls_by_underlines_df) as mocked_create_rls_by_underlines_df,
            patch.object(self.mocked_df_factory, "create_definitions_df", return_value = definitions_df) as mocked_create_definitions_df,
            patch.object(self.adapter, "create_rls_by_kbsize_df", return_value = rls_by_kbsize_df) as mocked_create_rls_by_kbsize_df
        ):

            self.mocked_rs_highlighter.highlight_rls_by_month = Mock(return_value = rls_by_month_df_a)
            self.mocked_rs_highlighter.highlight_rls_by_year = Mock(return_value = rls_by_year_df)

            # Act
            self.adapter.create_summary(setting_bag = setting_bag)

            # Assert
            mocked_create_rl_df.assert_called_once_with(setting_bag = setting_bag)
            mocked_create_rl_enriched_df.assert_called_once_with(rl_df = rl_df)
            mocked_create_rl_rating_five_df.assert_called_once_with(rl_enriched_df = rl_enriched_df, setting_bag = setting_bag)
            mocked_create_rl_most_underlines_df.assert_called_once_with(rl_enriched_df = rl_enriched_df, setting_bag = setting_bag)
            mocked_create_rls_by_month_tpl.assert_called_once_with(rl_df = rl_df, setting_bag = setting_bag)
            mocked_create_rls_by_year_df.assert_called_once_with(rls_by_month_tpl = rls_by_month_tpl, rl_df = rl_df, setting_bag = setting_bag)
            mocked_create_rls_by_range_df.assert_called_once_with(rl_df = rl_df, setting_bag = setting_bag)
            mocked_create_rls_by_topic_df.assert_called_once_with(rl_df = rl_df)
            mocked_create_rls_by_topic_trend_df.assert_called_once_with(rl_df = rl_df, setting_bag = setting_bag)
            mocked_create_rls_by_publisher_tpl.assert_called_once_with(rl_df = rl_df, setting_bag = setting_bag)
            mocked_create_rls_by_rating_df.assert_called_once_with(rl_df = rl_df, setting_bag = setting_bag)
            mocked_create_rls_by_underlines_df.assert_called_once_with(rl_enriched_df = rl_enriched_df)
            mocked_create_definitions_df.assert_called_once_with()
            mocked_create_rls_by_kbsize_df.assert_called_once_with(rl_df = rl_df, setting_bag = setting_bag)

            self.mocked_rs_highlighter.highlight_rls_by_month.assert_called()
            self.mocked_rs_highlighter.highlight_rls_by_year.assert_called_once_with(rls_by_year_df = rls_by_year_df)
class RLReportManagerTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.report_manager : RLReportManager = RLReportManager(formatter = Formatter())
        self.report_module : Any = importlib.import_module(RLReportManager.__module__)

        empty_df : DataFrame = DataFrame()
        self.rl_summary : RLSummary = RLSummary(
            rl_df = empty_df,
            rl_enriched_df = empty_df,
            rl_rating_five_df = empty_df,
            rl_most_underlines_df = empty_df,
            rls_by_month_tpl = (empty_df, empty_df),
            rls_by_year_df = empty_df,
            rls_by_range_df = empty_df,
            rls_by_topic_df = empty_df,
            rls_by_topic_trend_df = empty_df,
            rls_by_publisher_tpl = (empty_df, empty_df, ""),
            rls_by_rating_df = empty_df,
            rls_by_underlines_df = empty_df,
            definitions_df = empty_df,
            rls_by_kbsize_df = empty_df
        )

        self.rl_enriched_df : DataFrame = DataFrame(data = {
            RLCN.ID: [998, 999],
            RLCN.TITLE: ["ProxMox VE Administration Guide - Release 7.2", "Clean Architecture"],
            RLCN.YEAR: [2022, 2018],
            RLCN.PAGES: [535, 429],
            RLCN.READDATE: [date(2024, 2, 19), date(2024, 2, 19)],
            RLCN.PUBLISHER: ["Self-Published", "Pearson Education"],
            RLCN.TOPIC: ["Development Tools", "Software Engineering"],
            RLCN.A4SHEETS: [10, 20],
            RLCN.UNDERLINES: [1, 0],
            RLCN.RATING: [2, 3]
        }, index = RangeIndex(start = 0, stop = 2, step = 1))
    def test_formatforfilename_shouldreturnexpectedstring_wheninvoked(self) -> None:

        # Arrange
        last_update : datetime = datetime(year = 2025, month = 12, day = 22, hour = 15, minute = 30, second = 45)
        expected : str = "20251222"

        # Act
        actual : str = self.report_manager._RLReportManager__format_for_file_name(last_update = last_update)  # type: ignore

        # Assert
        self.assertEqual(actual, expected)
    def test_formatfortitle_shouldreturnexpectedstring_wheninvoked(self) -> None:

        # Arrange
        last_update : datetime = datetime(year = 2025, month = 12, day = 22, hour = 15, minute = 30, second = 45)
        expected : str = "2025-12-22"

        # Act
        actual : str = self.report_manager._RLReportManager__format_for_title(last_update = last_update)  # type: ignore

        # Assert
        self.assertEqual(actual, expected)
    def test_reportifyrl_shouldsetidbasedonindexplusone_wheninvoked(self) -> None:

        # Arrange
        expected : list[int] = [1, 2]

        # Act
        actual : DataFrame = self.report_manager._RLReportManager__reportify_rl(rl_enriched_df = self.rl_enriched_df)  # type: ignore

        # Assert
        self.assertEqual(expected, actual[RLCN.ID].tolist())
    def test_reportifyrl_shouldreturncolumnsinreportorder_wheninvoked(self) -> None:

        # Arrange
        expected_columns : list[Any] = [
            RLCN.ID,
            RLCN.TITLE,
            RLCN.YEAR,
            RLCN.PAGES,
            RLCN.READDATE,
            RLCN.PUBLISHER,
            RLCN.TOPIC,
            RLCN.A4SHEETS,
            RLCN.UNDERLINES,
            RLCN.RATING
        ]

        # Act
        actual : DataFrame = self.report_manager._RLReportManager__reportify_rl(rl_enriched_df = self.rl_enriched_df)  # type: ignore

        # Assert
        actual_columns : list[Any] = list(actual.columns)
        self.assertEqual(actual_columns, expected_columns)
    def test_reportifyrl_shouldformatratingasstars_wheninvoked(self) -> None:

        # Arrange
        expected_ratings : list[str] = ["★★☆☆☆", "★★★☆☆"]

        # Act
        actual : DataFrame = self.report_manager._RLReportManager__reportify_rl(rl_enriched_df = self.rl_enriched_df)  # type: ignore

        # Assert
        actual_ratings : list[str] = actual[RLCN.RATING].tolist()
        self.assertEqual(actual_ratings, expected_ratings)
    def test_createreportfilepaths_shouldreturnexpectedpaths_wheninvoked(self) -> None:

        # Arrange
        folder_path : str = "/home/nwreadinglist"
        last_update : datetime = datetime(year = 2025, month = 12, day = 22)
        expected_html_path : Path = Path("/home/nwreadinglist") / "READINGLISTREPORT20251222.html"
        expected_pdf_path : Path = Path("/home/nwreadinglist") / "READINGLISTREPORT20251222.pdf"

        # Act
        actual : Tuple[Path, Path] = self.report_manager._RLReportManager__create_report_file_paths(folder_path = folder_path,last_update = last_update)  # type: ignore
        actual_html_path : Path = actual[0]
        actual_pdf_path : Path = actual[1]

        # Assert
        self.assertEqual(actual_html_path, expected_html_path)
        self.assertEqual(actual_pdf_path, expected_pdf_path)
    def test_createhtml_shouldcontainexpectedhtmlexcerpts_whenfooterisnotprovided(self) -> None:

        # Arrange
        df : DataFrame = DataFrame(data = {"A": [1.234]})
        title : str = "Some Title"
        formatters : Optional[dict] = {"A": "{:.2f}"}

        # Act
        actual : str = self.report_manager._RLReportManager__create_html(df = df, title = title, formatters = formatters)  # type: ignore

        # Assert
        self.assertIn("<div style='margin-bottom: 20px;'>", actual)
        self.assertIn(f"<h2>{title}</h2>", actual)
        self.assertIn("</div>", actual)
        self.assertIn(">1.23<", actual)
        self.assertIn("background-color: #eeeeee", actual)
        self.assertIn("white-space: nowrap", actual)
        self.assertIn("border-collapse: collapse", actual)
        self.assertNotIn("margin-top: 6px", actual)
    def test_createhtml_shouldcontainexpectedhtmlexcerpts_whenfooterisprovided(self) -> None:

        # Arrange
        df : DataFrame = DataFrame(data = {"A": [1.234]})
        title : str = "Some Title"
        formatters : Optional[dict] = {"A": "{:.2f}"}
        footer : Optional[str] = "Some Footer"

        # Act
        actual : str = self.report_manager._RLReportManager__create_html(df = df, title = title, formatters = formatters, footer = footer)  # type: ignore

        # Assert
        self.assertIn(f"{footer}", actual)
        self.assertIn("margin-top: 6px", actual)
        self.assertIn("<br/><div", actual)
    def test_createhtmlsections_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        empty_df : DataFrame = DataFrame()
        formatters : Optional[dict] = None

        expected_call_00 : _Call = call(self.rl_summary.rls_by_month_tpl[1], REPORTSTR.RLSBYMONTH, formatters)
        expected_call_01 : _Call = call(self.rl_summary.rls_by_year_df, REPORTSTR.RLSBYYEAR, formatters)
        expected_call_02 : _Call = call(self.rl_summary.rls_by_range_df, REPORTSTR.RLSBYRANGE, formatters)
        expected_call_03 : _Call = call(self.rl_summary.rls_by_topic_df, REPORTSTR.RLSBYTOPIC, formatters)
        expected_call_04 : _Call = call(self.rl_summary.rls_by_topic_trend_df, REPORTSTR.RLSBYTOPICTREND, formatters)
        expected_call_05 : _Call = call(self.rl_summary.rls_by_publisher_tpl[1], REPORTSTR.RLSBYPUBLISHER, formatters, self.rl_summary.rls_by_publisher_tpl[2])
        expected_call_06 : _Call = call(self.rl_summary.rls_by_rating_df, REPORTSTR.RLSBYRATING, formatters)
        expected_call_07 : _Call = call(self.rl_summary.rl_rating_five_df, REPORTSTR.RLRATINGFIVE, formatters)
        expected_call_08 : _Call = call(self.rl_summary.rls_by_underlines_df, REPORTSTR.RLSBYUNDERLINES, formatters)
        expected_call_09 : _Call = call(self.rl_summary.rl_most_underlines_df, REPORTSTR.RLMOSTUNDERLINES, formatters)
        expected_call_10 : _Call = call(self.rl_summary.definitions_df, REPORTSTR.DEFINITIONS, formatters)

        with patch.object(self.report_manager, "_RLReportManager__create_html", return_value = "<div></div>") as mocked_create_html:
            with patch.object(self.report_manager, "_RLReportManager__reportify_rl", return_value = empty_df) as mocked_reportify_rl:

                expected_call_11 : _Call = call(self.report_manager._RLReportManager__reportify_rl(self.rl_summary.rl_enriched_df), REPORTSTR.RL, formatters)   # type: ignore
                expected_calls : int = 12

                # Act
                actual : list[str] = self.report_manager._RLReportManager__create_html_sections(rl_summary = self.rl_summary, formatters = formatters)  # type: ignore

                # Assert
                self.assertEqual(expected_call_00, mocked_create_html.call_args_list[0])
                self.assertEqual(expected_call_01, mocked_create_html.call_args_list[1])
                self.assertEqual(expected_call_02, mocked_create_html.call_args_list[2])
                self.assertEqual(expected_call_03, mocked_create_html.call_args_list[3])
                self.assertEqual(expected_call_04, mocked_create_html.call_args_list[4])
                self.assertEqual(expected_call_05, mocked_create_html.call_args_list[5])
                self.assertEqual(expected_call_06, mocked_create_html.call_args_list[6])
                self.assertEqual(expected_call_07, mocked_create_html.call_args_list[7])
                self.assertEqual(expected_call_08, mocked_create_html.call_args_list[8])
                self.assertEqual(expected_call_09, mocked_create_html.call_args_list[9])
                self.assertEqual(expected_call_10, mocked_create_html.call_args_list[10])
                self.assertEqual(expected_call_11, mocked_create_html.call_args_list[11])
                self.assertEqual(len(actual), expected_calls)
    def test_createhtmltemplate_shouldcontainexpectedhtmlexcerpts_wheninvoked(self) -> None:

        # Arrange
        html_sections : list[str] = ["<div>One</div>", "<div>Two</div>"]
        last_update : datetime = datetime(year = 2025, month = 12, day = 22)
        report_title : str = "Reading List Report"
        app_name : str = "nwreadinglist"

        # Act
        actual : str = self.report_manager._RLReportManager__create_html_template(html_sections = html_sections, last_update = last_update) # type: ignore

        # Assert
        self.assertIn("<meta charset=\"utf-8\">", actual)
        self.assertIn(f"<title>{report_title} | 2025-12-22</title>", actual)
        self.assertIn(f"<h1>{report_title} | 2025-12-22</h1>", actual)
        self.assertIn("".join(html_sections), actual)
        self.assertIn("avatars.githubusercontent.com/u/10279234", actual)
        self.assertIn(f"This report is generated by '{app_name}'", actual)
        self.assertIn("© numbworks.", actual)
    def test_createstylesheet_shouldcallcsswiththeexpectedstring_wheninvoked(self) -> None:

        # Arrange
        css_mock = Mock()

        with patch.object(self.report_module, "CSS", css_mock):

            # Act
            self.report_manager._RLReportManager__create_stylesheet()  # type: ignore

            # Assert
            css_mock.assert_called_once_with(string = "@page { size: A3 landscape; margin: 20mm; }")
    def test_saveasreport_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        folder_path : str = "/home"
        last_update : datetime = datetime(year = 2025, month = 12, day = 22)
        save_html : bool = True
        save_pdf : bool = True
        formatters : Optional[dict] = None

        html_sections : list[str] = ["<div>Section</div>"]
        full_html : str = "<html><body>Report</body></html>"
        stylesheet : object = object()
        html_path : Path = Path("/home/some_file_name.html")
        pdf_path : Path = Path("/home/some_file_name.pdf")

        html_instance : Mock = Mock()

        with (
            patch.object(self.report_manager, "_RLReportManager__create_report_file_paths", return_value = (html_path, pdf_path)) as mocked_create_report_file_paths,
            patch.object(self.report_manager, "_RLReportManager__create_html_sections", return_value = html_sections) as mocked_create_html_sections,
            patch.object(self.report_manager, "_RLReportManager__create_html_template", return_value = full_html) as mocked_create_html_template,
            patch.object(self.report_manager, "_RLReportManager__create_stylesheet", return_value = stylesheet) as mocked_create_stylesheet,
            patch.object(Path, "write_text", autospec = True) as mocked_write_text,
            patch.object(self.report_module, "HTML", return_value = html_instance) as mocked_html
        ):

            # Act
            self.report_manager.save_as_report(
                rl_summary = self.rl_summary,
                folder_path = folder_path,
                last_update = last_update,
                save_html = save_html,
                save_pdf = save_pdf,
                formatters = formatters
            )

            # Assert
            mocked_create_report_file_paths.assert_called_once_with(folder_path = folder_path, last_update = last_update)
            mocked_create_html_sections.assert_called_once_with(rl_summary = self.rl_summary, formatters = formatters)
            mocked_create_html_template.assert_called_once_with(html_sections = html_sections, last_update = last_update)
            mocked_write_text.assert_called_once_with(html_path, data = full_html, encoding = "utf-8")
            mocked_html.assert_called_once_with(string = full_html)
            mocked_create_stylesheet.assert_called_once()
            html_instance.write_pdf.assert_called_once_with(target = str(pdf_path), stylesheets = [stylesheet])
class ReadingListProcessorTestCase(unittest.TestCase):

    def test_mergeformatters_shouldmergeformatters_wheninvoked(self) -> None:

        # Arrange
        component_bag : Mock = Mock()

        setting_bag : Mock = Mock()
        setting_bag.rl_most_underlines_formatters = {"a": "{:.2f}"}
        setting_bag.rls_by_publisher_formatters = {"b": "{:.2f}"}

        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)

        # Act
        actual : dict = rl_processor._ReadingListProcessor__merge_formatters()  # type: ignore

        # Assert
        self.assertEqual(actual, {"a": "{:.2f}", "b": "{:.2f}"})

    def test_initialize_shouldcreatesummaryandassign_wheninvoked(self) -> None:

        # Arrange
        rl_summary : Mock = Mock()

        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()

        # Assert
        rl_adapter.create_summary.assert_called_once_with(setting_bag = setting_bag)
    def test_processrl_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rl_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rl_df = rl_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rl = [OPTION.display]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rl()

        # Assert
        displayer.display.assert_called_once_with(obj = rl_df)
    def test_processrlenriched_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rl_enriched_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rl_enriched_df = rl_enriched_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rl_enriched = [OPTION.display]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rl_enriched()

        # Assert
        displayer.display.assert_called_once_with(obj = rl_enriched_df)
    def test_processrlratingfive_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rl_rating_five_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rl_rating_five_df = rl_rating_five_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rl_rating_five = [OPTION.display]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rl_rating_five()

        # Assert
        displayer.display.assert_called_once_with(obj = rl_rating_five_df)
    def test_processrlmostunderlines_shoulddisplaywithformatters_whenoptionisdisplay(self) -> None:

        # Arrange
        rl_most_underlines_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rl_most_underlines_df = rl_most_underlines_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        formatters : dict = {RLCN.UNDERLINES: "{:.0f}"}

        setting_bag : Mock = Mock()
        setting_bag.options_rl_most_underlines = [OPTION.display]
        setting_bag.rl_most_underlines_formatters = formatters

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rl_most_underlines()

        # Assert
        displayer.display.assert_called_once_with(obj = rl_most_underlines_df, formatters = formatters)
    def test_processrlsbymonth_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rls_by_month_df : DataFrame = Mock()
        rls_by_month_tpl : tuple = ("ignored", rls_by_month_df, "ignored")

        rl_summary : Mock = Mock()
        rl_summary.rls_by_month_tpl = rls_by_month_tpl

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_month = [OPTION.display]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_month()

        # Assert
        displayer.display.assert_called_once_with(obj = rls_by_month_df)
    def test_processrlsbyyear_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rls_by_year_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rls_by_year_df = rls_by_year_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_month = [OPTION.display]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_year()

        # Assert
        displayer.display.assert_called_once_with(obj = rls_by_year_df)
    def test_processrlsbyrange_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rls_by_range_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rls_by_range_df = rls_by_range_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_range = [OPTION.display]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_range()

        # Assert
        displayer.display.assert_called_once_with(obj = rls_by_range_df)
    def test_processrlsbytopic_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rls_by_topic_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rls_by_topic_df = rls_by_topic_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_topic = [OPTION.display]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_topic()

        # Assert
        displayer.display.assert_called_once_with(obj = rls_by_topic_df)
    def test_processrlsbytopictrend_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rls_by_topic_trend_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rls_by_topic_trend_df = rls_by_topic_trend_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_topic_trend = [OPTION.display]  # type: ignore

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_topic_trend()

        # Assert
        displayer.display.assert_called_once_with(obj = rls_by_topic_trend_df)
    def test_processrlsbypublisher_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rls_by_publisher_df : Mock = Mock()
        rls_by_publisher_tpl : tuple = ("ignored", rls_by_publisher_df, "FOOTER")

        rl_summary : Mock = Mock()
        rl_summary.rls_by_publisher_tpl = rls_by_publisher_tpl

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter
        component_bag.logging_function = Mock()

        formatters : dict = {RLCN.AVGRATING: "{:.2f}"}

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_publisher = [OPTION.display]
        setting_bag.rls_by_publisher_n = 5
        setting_bag.rls_by_publisher_formatters = formatters

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_publisher()

        # Assert
        displayer.display.assert_called_once_with(obj = rls_by_publisher_df, formatters = formatters)
    def test_processrlsbypublisher_shouldlogfooterwithnewline_whenoptionislog(self) -> None:

        # Arrange
        publisher_df : Mock = Mock()
        publisher_df.head.return_value = Mock()

        footer : str = "FOOTER"
        rls_by_publisher_tpl : tuple = (publisher_df, "ignored", footer)

        rl_summary : Mock = Mock()
        rl_summary.rls_by_publisher_tpl = rls_by_publisher_tpl

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        logging_function : Mock = Mock()

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter
        component_bag.logging_function = logging_function

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_publisher = [OPTION.log]
        setting_bag.rls_by_publisher_n = 5
        setting_bag.rls_by_publisher_formatters = {}

        expected : str = footer + "\n"        

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_publisher()

        # Assert
        logging_function.assert_called_once_with(expected)
    def test_processrlsbyrating_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rls_by_rating_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rls_by_rating_df = rls_by_rating_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_rating = [OPTION.display]  # type: ignore

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_rating()

        # Assert
        displayer.display.assert_called_once_with(obj = rls_by_rating_df)
    def test_processrlsbyunderlines_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        rls_by_underlines_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rls_by_underlines_df = rls_by_underlines_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_underlines = [OPTION.display]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_underlines()

        # Assert
        displayer.display.assert_called_once_with(obj = rls_by_underlines_df)
    def test_processdefinitions_shoulddisplay_whenoptionisdisplay(self) -> None:

        # Arrange
        definitions_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.definitions_df = definitions_df

        displayer : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_definitions = [OPTION.display]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_definitions()

        # Assert
        displayer.display.assert_called_once_with(obj = definitions_df)

    def test_processrlsbykbsize_shoulddisplayandplot_whenoptionsaredisplayandplot(self) -> None:

        # Arrange
        rls_by_kbsize_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rls_by_kbsize_df = rls_by_kbsize_df

        displayer : Mock = Mock()
        plot_manager : Mock = Mock()

        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.plot_manager = plot_manager
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_kbsize = [OPTION.display, OPTION.plot]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_kbsize()

        # Assert
        displayer.display.assert_called_once_with(obj = rls_by_kbsize_df)
        plot_manager.show_box_plot.assert_called_once_with(df = rls_by_kbsize_df, x_name = RLCN.A4SHEETS)
    def test_processrlsbybooksyear_shouldplot_whenoptionisplot(self) -> None:

        # Arrange
        rl_df : DataFrame = Mock()

        rl_summary : Mock = Mock()
        rl_summary.rl_df = rl_df

        plot_manager : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = rl_summary

        component_bag : Mock = Mock()
        component_bag.plot_manager = plot_manager
        component_bag.rl_adapter = rl_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_rls_by_books_year = [OPTION.plot]

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.process_rls_by_books_year()

        # Assert
        plot_manager.show_box_plot.assert_called_once_with(df = rl_df, x_name = RLCN.YEAR)

    def test_saveasreport_shouldsavehtmlandpdf_whenoptionsaresavehtmlandsavepdf(self) -> None:

        # Arrange
        summary : Mock = Mock()

        rlr_manager : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.rlr_manager = rlr_manager
        component_bag.rl_adapter = rl_adapter

        working_folder_path : str = "/home/readinglist"
        now : datetime = datetime(2025, 12, 29, 1, 12,13)
        rl_most_underlines_formatters : dict = {"a": "{:.2f}"}
        rls_by_publisher_formatters : dict = {"b": "{:.0f}"}

        setting_bag : Mock = Mock()
        setting_bag.options_report = [OPTION.save_html, OPTION.save_pdf]
        setting_bag.working_folder_path = working_folder_path
        setting_bag.now = now
        setting_bag.rl_most_underlines_formatters = rl_most_underlines_formatters
        setting_bag.rls_by_publisher_formatters = rls_by_publisher_formatters

        # Act
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        rl_processor.initialize()
        rl_processor.save_as_report()

        # Assert
        rlr_manager.save_as_report.assert_called_once_with(
            rl_summary = summary,
            folder_path = working_folder_path,
            last_update = now,
            save_html = True,
            save_pdf = True,
            formatters = (rl_most_underlines_formatters | rls_by_publisher_formatters)
        )
    def test_saveasreport_shoulddonothing_whenoptionsreportisempty(self) -> None:

        # Arrange
        summary : Mock = Mock()

        rlr_manager : Mock = Mock()
        rl_adapter : Mock = Mock()
        rl_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.rlr_manager = rlr_manager
        component_bag.rl_adapter = rl_adapter

        working_folder_path : str = "/home/readinglist"
        now : datetime = datetime(2025, 12, 29, 1, 12,13)
        rl_most_underlines_formatters : dict = {"a": "{:.2f}"}
        rls_by_publisher_formatters : dict = {"b": "{:.0f}"}

        setting_bag : Mock = Mock()
        setting_bag.options_report = []
        setting_bag.working_folder_path = working_folder_path
        setting_bag.now = now
        setting_bag.rl_most_underlines_formatters = rl_most_underlines_formatters
        setting_bag.rls_by_publisher_formatters = rls_by_publisher_formatters

        # Act
        processor : ReadingListProcessor = ReadingListProcessor(component_bag = component_bag, setting_bag = setting_bag)
        processor.initialize()
        processor.save_as_report()

        # Assert
        rlr_manager.save_as_report.assert_called_once_with(
            rl_summary = summary,
            folder_path = working_folder_path,
            last_update = now,
            save_html = False,
            save_pdf = False,
            formatters = (rl_most_underlines_formatters | rls_by_publisher_formatters)
        )

    @parameterized.expand([
        ["process_rl"],
        ["process_rl_enriched"],
        ["process_rl_rating_five"],
        ["process_rl_most_underlines"],
        ["process_rls_by_month"],
        ["process_rls_by_year"],        
        ["process_rls_by_range"],
        ["process_rls_by_topic"],
        ["process_rls_by_topic_trend"],        
        ["process_rls_by_publisher"],
        ["process_rls_by_rating"],
        ["process_rls_by_underlines"],
        ["process_definitions"],
        ["process_rls_by_kbsize"],
        ["process_rls_by_books_year"],
        ["get_summary"],
        ["save_as_report"]
    ])
    def test_method_shouldraiseexception_wheninitializenotrun(self, method_name : str) -> None:
        
        # Arrange
        rl_processor : ReadingListProcessor = ReadingListProcessor(component_bag = Mock(), setting_bag = Mock())

        # Act & Assert
        with self.assertRaises(Exception) as context:
            getattr(rl_processor, method_name)()

        self.assertEqual(str(context.exception), "Please run the 'initialize' method first.")

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)