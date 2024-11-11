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

    @staticmethod
    def create_rl_tpl() -> Tuple[DataFrame, list[int]]:

        rl_df : DataFrame = pd.DataFrame({
            "Title": np.array(["ProxMox VE Administration Guide - Release 7.2", "Clean Architecture", "Python How-To", "Python Foundation", "Python Unit Test Automation (2nd Edition)", "Testing in Python", "Python Object-Oriented Programming (4th Edition)", "Intermediate Python [MLI]", "Learning Advanced Python By Studying Open-Source Projects", "Python in a Nutshell (4th Edition)", "Python 3 And Feature Engineering", "Python Testing Cookbook (2nd Edition)", "Python Testing with pytest (2nd Edition)", "Python Packages"], dtype=object),
            "Year": np.array([2022, 2018, 2023, 2022, 2022, 2020, 2021, 2023, 2024, 2023, 2024, 2018, 2022, 2022], dtype=int32),
            "Type": np.array(["Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book", "Book"], dtype=object),
            "Format": np.array(["Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital", "Digital"], dtype=object),
            "Language": np.array(["EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN", "EN"], dtype=object),
            "Pages": np.array([535, 429, 455, 205, 94, 132, 715, 192, 139, 963, 229, 978, 264, 243], dtype=int32),
            "ReadDate": np.array([date(2024, 2, 19), date(2024, 2, 19), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 26), date(2024, 2, 26), date(2024, 2, 26)], dtype=object),
            "ReadYear": np.array([2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024], dtype=int32),
            "ReadMonth": np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], dtype=int32),
            "WorthBuying": np.array(["No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "Yes"], dtype=object),
            "WorthReadingAgain": np.array(["No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "Yes", "No", "No", "No"], dtype=object),
            "Publisher": np.array(["Self-Published", "Pearson Education", "Manning", "Self-Published", "Apress", "Self-Published", "Packt", "MLI", "CRC Press", "O'Reilly", "MLI", "Packt", "Pragmatic Bookshelf", "CRC Press"], dtype=object),
            "Rating": np.array([2, 3, 1, 1, 1, 1, 2, 1, 1, 3, 2, 2, 3, 4], dtype=int32),
            "StreetPrice": np.array([0.0, 30.39, 49.99, 22.49, 38.88, 49.99, 38.24, 54.99, 59.95, 65.23, 54.99, 33.99, 39.49, 48.95], dtype= np.float64),
            "Currency": np.array(["USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD", "USD"], dtype=object),
            "Comment": np.array(["Useful. It shows how well ProxMox has been designed.", "Useful. A good book for beginners, well-written and clear. The last part about the history of computers could be easily removed.", "Useless. Well-written, but it contains no original nor well-structured knowledge. In addition, the second half of the book is not about Python but about Flask. Totally useless book.", "Useless. Very basic overview about multiple Python-related topics. The layout of the book is horrible (dense, lack of bold face, ...).", "Useless. Just a walkthrough of Python unit test frameworks. No original content.", "Useless. Too much opinionated towards pytest, not able to explain why pytest is better than unittest in a convincing way.", "Useful. An ok getting started guide for whom wants to learn OOP and Python from scratch at the same time.", "Useless. Well-written (organized like a recipe book and without ramblings), but contains no different knowledge than hundreds of Python books.", "Useless. The book title is misleading: the author doesn't study any open-source project. It's just a Python cookbook like hundreds others.", "Useful. Well-written and comprehensive, it contains few bits of information I didn't know.", "Useful. No-frills introduction to feature engineering in a cookbook format.", "Useful. It's a long list of testing techniques and Python tools to perform them. Good to have all collected in the same book.", "Useful. A well-written and comprehensive book about pytest.", "Useful. Excellent book about the topic. It's well-written, comprehensive and pragmatic. It would become perfect by removing the repetitions."], dtype=object),
            "Topic": np.array(["Development Tools", "Software Engineering", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python", "Python"], dtype=object),
            "OnGoodreads": np.array(["No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No"], dtype=object),
            "CommentLenght": np.array([52, 128, 181, 134, 80, 121, 105, 142, 138, 90, 75, 125, 59, 140], dtype=int32),
            "KBSize": np.array([8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=int32)
        }, index=pd.RangeIndex(start=260, stop=274, step=1))

        read_years : list[int] = [ 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 ]

        return (rl_df, read_years)
    @staticmethod
    def create_rl_df_column_names() -> list[str]:

        column_names : list[str] = []
        column_names.append("Title")                # [0], str
        column_names.append("Year")                 # [1], int
        column_names.append("Type")                 # [2], str
        column_names.append("Format")               # [3], str
        column_names.append("Language")             # [4], str
        column_names.append("Pages")                # [5], int
        column_names.append("ReadDate")             # [6], date
        column_names.append("ReadYear")             # [7], int
        column_names.append("ReadMonth")            # [8], int    
        column_names.append("WorthBuying")          # [9], str
        column_names.append("WorthReadingAgain")    # [10], str
        column_names.append("Publisher")            # [11], str
        column_names.append("Rating")               # [12], int
        column_names.append("StreetPrice")          # [13], float
        column_names.append("Currency")             # [14], str
        column_names.append("Comment")              # [15], str
        column_names.append("Topic")                # [16], str
        column_names.append("OnGoodreads")          # [17], str
        column_names.append("CommentLenght")        # [18], int
        column_names.append("KBSize")               # [19], int

        return column_names
    @staticmethod
    def create_rl_df_dtype_names() -> list[str]:

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
            "Int64"
        ]

        return expected_dtype_names
    @staticmethod
    def create_rl_asrt_tpl() -> Tuple[DataFrame, datetime]:

        rl_asrt_df : DataFrame = pd.DataFrame({
            "Years": np.array(["1"], dtype = object),
            "Books": np.array(["14"], dtype = object),
            "Pages": np.array(["5573"], dtype = object),
            "TotalSpend": np.array(["$587.57"], dtype = object),
            "LastUpdate": np.array(["2024-03-04"], dtype = object),
        }, index = pd.Index([0], dtype = "int64")) 

        now : datetime = datetime(2024, 3, 4)

        return (rl_asrt_df, now)
    @staticmethod
    def create_rl_by_kbsize_df() -> DataFrame:

        return pd.DataFrame({
            "Title": np.array(["ProxMox VE Administration Guide - Release 7.2"], dtype = object),
            "ReadYear": np.array(["2024"], dtype = int32),
            "Topic": np.array(["Development Tools"], dtype = object),
            "Publisher": np.array(["Self-Published"], dtype = object),
            "Rating": np.array(["2"], dtype = int32),
            "KBSize": np.array(["8"], dtype = int32),
            "A4Sheets": np.array(["1"], dtype = np.int64),
        }, index = pd.Index([1], dtype = "int64"))   
    @staticmethod
    def create_sas_by_month_tpl() -> Tuple[DataFrame, DataFrame]:

        sas_by_month_df : DataFrame = DataFrame({
            "Month": np.array([str(i) for i in range(1, 13)], dtype=np.int64),
            "2023": np.array(["0 (0)"] * 12, dtype=object),
            "↕": np.array(["=", "↑", "=", "=", "=", "=", "=", "=", "=", "=", "=", "="], dtype=object),
            "2024": np.array(["0 (0)", "14 (5573)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", 
                            "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)"], dtype=object)
        }, index=pd.Index(range(12), dtype="int64"))

        sas_by_month_upd_df : DataFrame = DataFrame({
            "Month": np.array([str(i) for i in range(1, 13)], dtype=np.int64),
            "2023": np.array(["0 (0)"] * 12, dtype=object),
            "↕": np.array(["=", "↑", "", "", "", "", "", "", "", "", "", ""], dtype=object),
            "2024": np.array(["0 (0)", "14 (5573)", "", "", "", "", "", "", "", "", "", ""], dtype=object)
        }, index=pd.Index(range(12), dtype="int64"))

        return (sas_by_month_df, sas_by_month_upd_df)
    @staticmethod
    def create_sas_by_year_street_price_df() -> DataFrame:

        return DataFrame({
            "2023": np.array(["0 (0)", "$0.00"], dtype = object),
            "↕": np.array(["↑", "↑"], dtype = object),
            "2024": np.array(["14 (5573)", "$587.57"], dtype = object)
        }, index=pd.Index([0, 1], dtype="int64")) 
    @staticmethod
    def create_sas_by_topic_df() -> DataFrame:

        return pd.DataFrame({
            "Topic": np.array(["Python", "Development Tools", "Software Engineering"], dtype=object),
            "Books": np.array([12, 1, 1], dtype = np.int64),
            "Pages": np.array([4609, 535, 429], dtype = int32),
            "A4Sheets": np.array([0, 1, 0], dtype = np.int64)
        }, index=pd.RangeIndex(start=0, stop=3, step=1))
    @staticmethod
    def create_sas_by_publisher_tpl() -> Tuple[DataFrame, DataFrame, str]:

        sas_by_publisher_df : DataFrame = DataFrame({
            "Publisher": np.array(["Self-Published", "Packt", "CRC Press", "MLI", "Apress", "O'Reilly", "Manning", "Pearson Education", "Pragmatic Bookshelf"], dtype=object),
            "Books": np.array([3, 2, 2, 2, 1, 1, 1, 1, 1], dtype=np.int64),
            "A4Sheets": np.array([1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int64),
            "AB%": np.array([33.33, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=float64),
            "AvgRating": np.array([1.33, 2.0, 2.5, 1.5, 1.0, 3.0, 1.0, 3.0, 3.0], dtype=float64),
            "IsWorth": np.array(["No", "No", "No", "No", "No", "No", "No", "No", "No"], dtype=object)
        }, index=pd.Index([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype="int64"))

        sas_by_publisher_flt_df : DataFrame = DataFrame({
            "Publisher": np.array([], dtype=object),
            "Books": np.array([], dtype=np.int64),
            "A4Sheets": np.array([], dtype=np.int64),
            "AB%": np.array([], dtype=float64),
            "AvgRating": np.array([], dtype=float64),
            "IsWorth": np.array([], dtype=object)
        }, index=pd.Index([], dtype="int64"))

        sas_by_publisher_footer : str = "'Yes' if 'Books' >= '8' & ('AvgRating' >= '100' | 'AB%' >= '2.5')"
    
        return (sas_by_publisher_df, sas_by_publisher_flt_df, sas_by_publisher_footer)  
    @staticmethod
    def create_sas_by_rating_df() -> DataFrame:

        return pd.DataFrame({
            "Rating": np.array(["★★★★☆", "★★★☆☆", "★★☆☆☆", "★☆☆☆☆"], dtype = object),
            "Books": np.array([1, 3, 4, 6], dtype = np.int64),
        }, index=pd.RangeIndex(start = 0, stop = 4, step = 1))
    @staticmethod
    def create_trend_by_year_topic_df() -> DataFrame:

        return pd.DataFrame({
            "Topic": np.array(["Development Tools", "Python", "Software Engineering"], dtype=object),
            "Books": pd.Series([[0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 12], [0, 0, 0, 0, 0, 0, 0, 0, 1]]).to_numpy(),
            "Trend": np.array(["▁▁▁▁▁▁▁▁▂", "▁▁▁▁▁▁▁▁█", "▁▁▁▁▁▁▁▁▂"], dtype=object),
        }, index=pd.RangeIndex(start=0, stop=3, step=1))

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
        self.kbsize_ascending : bool = False
        self.kbsize_remove_if_zero : bool = True  
        self.kbsize_n : int = 10
        self.md_stars_rating : bool = True
        self.publisher_n : int = 10
        self.publisher_formatters : dict = { "AvgRating" : "{:.2f}", "AB%" : "{:.2f}" }
        self.publisher_min_books : int = 8
        self.publisher_min_ab_perc : float = 2.50
        self.publisher_min_avgrating : float = 100
        self.publisher_criteria : Literal["Yes", "No"] = "Yes"
        self.trend_sparklines_maximum : bool = True
        self.rounding_digits : int = 2

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
    def test_createrl_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        rl_df : DataFrame = ObjectMother().create_rl_tpl()[0]
        expected_column_names : list[str] = ObjectMother().create_rl_df_column_names()
        expected_dtype_names : list[str] = ObjectMother().create_rl_df_dtype_names()
        
        # Act
        actual : DataFrame = pd.DataFrame()
        with patch.object(pd, 'read_excel', return_value = rl_df) as mocked_context:
            actual = self.df_factory.create_rl(
                excel_path = self.excel_path,
                excel_books_skiprows = self.excel_books_skiprows,
                excel_books_nrows = self.excel_books_nrows,
                excel_books_tabname = self.excel_books_tabname,
                excel_null_value = self.excel_null_value
            )

        # Assert
        self.assertEqual(expected_column_names, actual.columns.tolist())
        self.assertEqual(expected_dtype_names, SupportMethodProvider().get_dtype_names(df = actual))    
    def test_createrlasrt_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().create_rl_tpl()[0]
        (expected, now) = ObjectMother().create_rl_asrt_tpl()

        # Act
        actual : DataFrame = self.df_factory.create_rl_asrt(
            rl_df = rl_df,
            rounding_digits = self.rounding_digits,
            now = now
        )

        # Assert
        assert_frame_equal(expected, actual)        
    def test_createrlbykbsize_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().create_rl_tpl()[0]
        expected : DataFrame = ObjectMother().create_rl_by_kbsize_df()

        # Act
        actual : DataFrame = self.df_factory.create_rl_by_kbsize(
            rl_df = rl_df,
            kbsize_ascending = self.kbsize_ascending,
            kbsize_remove_if_zero = self.kbsize_remove_if_zero,
            kbsize_n = self.kbsize_n
        )

        # Assert
        assert_frame_equal(expected, actual)
    def test_createsasbymonth_shouldreturnexpecteddataframes_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().create_rl_tpl()[0]
        now : datetime = datetime(2024, 2, 19)
        read_years : list[int] = [ 2023, 2024 ]
        (expected_1, expected_2) = ObjectMother().create_sas_by_month_tpl()

        # Act
        (actual_1, actual_2) = self.df_factory.create_sas_by_month(
            rl_df = rl_df,
            read_years = read_years,
            now = now
        )

        # Assert
        assert_frame_equal(expected_1, actual_1)    
        assert_frame_equal(expected_2, actual_2)     
    def test_createsasbyyearstreetprice_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().create_rl_tpl()[0]
        sas_by_month_tpl : Tuple[DataFrame, DataFrame] = ObjectMother().create_sas_by_month_tpl()
        read_years : list[int] = [ 2023, 2024 ]
        expected : DataFrame = ObjectMother().create_sas_by_year_street_price_df()

        # Act
        actual : DataFrame = self.df_factory.create_sas_by_year_street_price(
            sas_by_month_tpl = sas_by_month_tpl,
            rl_df = rl_df,
            read_years = read_years,
            rounding_digits = self.rounding_digits
        )

        # Assert
        assert_frame_equal(expected, actual)       
    def test_createsasbytopic_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().create_rl_tpl()[0]
        expected : DataFrame = ObjectMother().create_sas_by_topic_df()

        # Act
        actual : DataFrame = self.df_factory.create_sas_by_topic(rl_df = rl_df)

        # Assert
        assert_frame_equal(expected, actual)
    def test_createsasbypublisher_shouldreturnexpecteddataframes_wheninvoked(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().create_rl_tpl()[0]
        (expected_1, expected_2, expected_3) = ObjectMother().create_sas_by_publisher_tpl()

        # Act
        (actual_1, actual_2, actual_3) = self.df_factory.create_sas_by_publisher(
            rl_df = rl_df,
            rounding_digits = 2,
            publisher_min_books = self.publisher_min_books,
            publisher_min_ab_perc = self.publisher_min_ab_perc,
            publisher_min_avgrating = self.publisher_min_avgrating,
            publisher_criteria = self.publisher_criteria
        )

        # Assert
        assert_frame_equal(expected_1, actual_1)
        assert_frame_equal(expected_2, actual_2)
        self.assertEqual(expected_3, actual_3)
    def test_createsasbyrating_shouldreturnexpecteddataframe_whenformattedratingequalstotrue(self):
        
        # Arrange
        rl_df : DataFrame = ObjectMother().create_rl_tpl()[0]
        expected : DataFrame = ObjectMother().create_sas_by_rating_df()

        # Act
        actual : DataFrame = self.df_factory.create_sas_by_rating(rl_df = rl_df, md_stars_rating = self.md_stars_rating)

        # Assert
        assert_frame_equal(expected, actual)
    def test_createtrendbyyeartopic_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        (rl_df, read_years) = ObjectMother().create_rl_tpl()
        expected : DataFrame = ObjectMother().create_trend_by_year_topic_df()

        # Act
        actual : DataFrame = self.df_factory.create_trend_by_year_topic(
            rl_df = rl_df,
            read_years = read_years,
            trend_sparklines_maximum = self.trend_sparklines_maximum
            )

        # Assert
        assert_frame_equal(expected, actual)
class ComponentBagTestCase(unittest.TestCase):
    
    def test_componentbag_shouldinitializeasexpected_wheninvoked(self):
        
        # Arrange, Act
        component_bag = ComponentBag()

        # Assert
        self.assertIsInstance(component_bag, ComponentBag)
        self.assertIsInstance(component_bag.file_path_manager, FilePathManager)
        self.assertIsInstance(component_bag.file_manager, FileManager)
        self.assertIsInstance(component_bag.df_factory, RLDataFrameFactory)
        self.assertIsInstance(component_bag.md_factory, RLMarkdownFactory)
        self.assertIsInstance(component_bag.displayer, Displayer)
        self.assertIsInstance(component_bag.plot_manager, PlotManager)
        self.assertTrue(callable(component_bag.logging_function))


# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)