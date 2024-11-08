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
from typing import Tuple
from unittest.mock import Mock, call, patch

# LOCAL MODULES
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwreadinglist import DefaultPathProvider, YearProvider, SettingBag, ComponentBag
from nwreadinglist import ReadingListManager, MarkdownProcessor
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
    def create_setting_bag() -> SettingBag:
        
        return SettingBag(

            show_rl_df = False,
            show_sas_by_month_df = True,
            show_sas_by_year_street_price_df = True,
            show_rl_asrt_df = True,
            show_sas_by_topic_df = True,
            show_sas_by_publisher_df = True,
            show_sas_by_rating_df = True,
            show_rl_by_kbsize_df = True,
            show_yearly_trend_by_topic_df = True,
            show_books_by_year_box_plot = True,
            show_rl_by_kbsize_box_plot = True,
            show_rl_asrt_md = True,
            show_rl_by_month_md = False,
            show_rl_by_publisher_md = False,
            show_rl_by_rating_md = False,
            show_rl_by_topic_md = False,
            show_rl_topic_trend_md = False,
            show_rl_md = False,
            save_rl_by_month_md = False,
            save_rl_by_publisher_md = False,
            save_rl_by_rating_md = False,
            save_rl_by_topic_md = False,
            save_rl_topic_trend_md = False,
            save_rl_md = False,
            working_folder_path = "c:/Users/Rubèn/Desktop/",
            read_years = YearProvider().get_all_years(),
            excel_path = "C:/project_dir/data/Reading List.xlsx",
            excel_books_nrows = 275,
            now = datetime(2024, 3, 4),
            rl_last_update = datetime(2024, 3, 4)
        )
    @staticmethod
    def create_reading_list_manager() -> ReadingListManager:

        return ReadingListManager(
            component_bag = ComponentBag(), 
            setting_bag = ObjectMother().create_setting_bag())
    @staticmethod
    def create_markdown_processor() -> MarkdownProcessor:

        return MarkdownProcessor(
            component_bag = ComponentBag(), 
            setting_bag = ObjectMother().create_setting_bag())
      
    @staticmethod
    def create_books_df() -> DataFrame:

        return pd.DataFrame({
            'Title': np.array(['ProxMox VE Administration Guide - Release 7.2', 'Clean Architecture', 'Python How-To', 'Python Foundation', 'Python Unit Test Automation (2nd Edition)', 'Testing in Python', 'Python Object-Oriented Programming (4th Edition)', 'Intermediate Python [MLI]', 'Learning Advanced Python By Studying Open-Source Projects', 'Python in a Nutshell (4th Edition)', 'Python 3 And Feature Engineering', 'Python Testing Cookbook (2nd Edition)', 'Python Testing with pytest (2nd Edition)', 'Python Packages'], dtype=object),
            'Year': np.array([2022, 2018, 2023, 2022, 2022, 2020, 2021, 2023, 2024, 2023, 2024, 2018, 2022, 2022], dtype=int32),
            'Type': np.array(['Book', 'Book', 'Book', 'Book', 'Book', 'Book', 'Book', 'Book', 'Book', 'Book', 'Book', 'Book', 'Book', 'Book'], dtype=object),
            'Format': np.array(['Digital', 'Digital', 'Digital', 'Digital', 'Digital', 'Digital', 'Digital', 'Digital', 'Digital', 'Digital', 'Digital', 'Digital', 'Digital', 'Digital'], dtype=object),
            'Language': np.array(['EN', 'EN', 'EN', 'EN', 'EN', 'EN', 'EN', 'EN', 'EN', 'EN', 'EN', 'EN', 'EN', 'EN'], dtype=object),
            'Pages': np.array([535, 429, 455, 205, 94, 132, 715, 192, 139, 963, 229, 978, 264, 243], dtype=int32),
            'ReadDate': np.array([date(2024, 2, 19), date(2024, 2, 19), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 26), date(2024, 2, 26), date(2024, 2, 26)], dtype=object),
            'ReadYear': np.array([2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024], dtype=int32),
            'ReadMonth': np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], dtype=int32),
            'WorthBuying': np.array(['No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'Yes'], dtype=object),
            'WorthReadingAgain': np.array(['No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'Yes', 'No', 'No', 'No'], dtype=object),
            'Publisher': np.array(['Self-Published', 'Pearson Education', 'Manning', 'Self-Published', 'Apress', 'Self-Published', 'Packt', 'MLI', 'CRC Press', "O'Reilly", 'MLI', 'Packt', 'Pragmatic Bookshelf', 'CRC Press'], dtype=object),
            'Rating': np.array([2, 3, 1, 1, 1, 1, 2, 1, 1, 3, 2, 2, 3, 4], dtype=int32),
            'StreetPrice': np.array([0.0, 30.39, 49.99, 22.49, 38.88, 49.99, 38.24, 54.99, 59.95, 65.23, 54.99, 33.99, 39.49, 48.95], dtype= np.float64),
            'Currency': np.array(['USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD'], dtype=object),
            'Comment': np.array(['Useful. It shows how well ProxMox has been designed.', 'Useful. A good book for beginners, well-written and clear. The last part about the history of computers could be easily removed.', 'Useless. Well-written, but it contains no original nor well-structured knowledge. In addition, the second half of the book is not about Python but about Flask. Totally useless book.', 'Useless. Very basic overview about multiple Python-related topics. The layout of the book is horrible (dense, lack of bold face, ...).', 'Useless. Just a walkthrough of Python unit test frameworks. No original content.', 'Useless. Too much opinionated towards pytest, not able to explain why pytest is better than unittest in a convincing way.', 'Useful. An ok getting started guide for whom wants to learn OOP and Python from scratch at the same time.', 'Useless. Well-written (organized like a recipe book and without ramblings), but contains no different knowledge than hundreds of Python books.', "Useless. The book title is misleading: the author doesn't study any open-source project. It's just a Python cookbook like hundreds others.", "Useful. Well-written and comprehensive, it contains few bits of information I didn't know.", 'Useful. No-frills introduction to feature engineering in a cookbook format.', "Useful. It's a long list of testing techniques and Python tools to perform them. Good to have all collected in the same book.", 'Useful. A well-written and comprehensive book about pytest.', "Useful. Excellent book about the topic. It's well-written, comprehensive and pragmatic. It would become perfect by removing the repetitions."], dtype=object),
            'Topic': np.array(['Development Tools', 'Software Engineering', 'Python', 'Python', 'Python', 'Python', 'Python', 'Python', 'Python', 'Python', 'Python', 'Python', 'Python', 'Python'], dtype=object),
            'OnGoodreads': np.array(['No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No'], dtype=object),
            'CommentLenght': np.array([52, 128, 181, 134, 80, 121, 105, 142, 138, 90, 75, 125, 59, 140], dtype=int32),
            'KBSize': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=int32),
        }, index=pd.RangeIndex(start=260, stop=274, step=1))
    @staticmethod
    def create_books_df_column_names() -> list[str]:

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
    def create_books_df_dtype_names() -> list[str]:

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
    def create_sas_by_topic_df() -> DataFrame:

        return pd.DataFrame({
            'Topic': np.array(['Python', 'Development Tools', 'Software Engineering'], dtype=object),
            'Books': np.array([12, 1, 1], dtype= np.int64),
            'Pages': np.array([4609, 535, 429], dtype=int32),
        }, index=pd.RangeIndex(start=0, stop=3, step=1))
    @staticmethod
    def create_sas_by_rating_df() -> DataFrame:

        return pd.DataFrame({
            'Rating': np.array(['★★★★☆', '★★★☆☆', '★★☆☆☆', '★☆☆☆☆'], dtype=object),
            'Books': np.array([1, 3, 4, 6], dtype= np.int64),
        }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def create_cumulative_df() -> DataFrame:

        return pd.DataFrame({
            'Years': np.array(['1'], dtype=object),
            'Books': np.array(['14'], dtype=object),
            'Pages': np.array(['5573'], dtype=object),
            'TotalSpend': np.array(['$587.57'], dtype=object),
            'LastUpdate': np.array(['2024-03-04'], dtype=object),
        }, index=pd.Index([0], dtype='int64'))
    @staticmethod
    def create_yt_by_topic_df() -> DataFrame:

        return pd.DataFrame({
            'Topic': np.array(['Development Tools', 'Python', 'Software Engineering'], dtype=object),
            'Books': pd.Series([[0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 12], [0, 0, 0, 0, 0, 0, 0, 0, 1]]).to_numpy(),
            'Trend': np.array(['▁▁▁▁▁▁▁▁▂', '▁▁▁▁▁▁▁▁█', '▁▁▁▁▁▁▁▁▂'], dtype=object),
        }, index=pd.RangeIndex(start=0, stop=3, step=1))

    @staticmethod
    def create_dtos_for_readmemd() -> Tuple[DataFrame, str]:

        data : dict = {
            "Years": [9],
            "Books": [304],
            "Pages": [83104],
            "TotalSpend": ["$8581.65"],
            "LastUpdate": ["2024-09-25"]
        }        
        df : DataFrame = pd.DataFrame(data)

        lines : list[str] = [
            "|   Years |   Books |   Pages | TotalSpend   | LastUpdate   |",
            "|--------:|--------:|--------:|:-------------|:-------------|",
            "|       9 |     304 |   83104 | $8581.65     | 2024-09-25   |"
        ]
        expected : str = "\n".join(lines) + "\n"

        return (df, expected)
    @staticmethod
    def create_dtos_for_rlbymonthmd() -> Tuple[Tuple[DataFrame, DataFrame], DataFrame, str]:

        sas_by_month_0_data : dict = {
            "Month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "2023": ["0 (0)", "0 (0)", "1 (139)", "0 (0)", "0 (0)", "8 (642)", "0 (0)", "4 (1170)", "9 (1969)", "0 (0)", "0 (0)", "3 (588)"],
            "↕": ["↑", "↑", "↓", "=", "↑", "↓", "↑", "↓", "↓", "=", "=", "↓"],
            "2024": ["3 (855)", "14 (5573)", "0 (0)", "0 (0)", "2 (590)", "4 (2572)", "22 (6366)", "2 (491)", "0 (0)", "0 (0)", "0 (0)", "0 (0)"]
        }
        sas_by_month_0_df : DataFrame = pd.DataFrame(sas_by_month_0_data)
        sas_by_month_tpl : Tuple[DataFrame, DataFrame] = (sas_by_month_0_df, Mock())

        sas_by_year_street_price_data : dict = {
            "2023": ["25 (4508)", "$594.80"],
            "↕": ["↑", "↑"],
            "2024": ["47 (16447)", "$1690.06"]
        }
        sas_by_year_street_price_df = pd.DataFrame(sas_by_year_street_price_data)

        lines : list[str] = [
            "## Revision History",
            "",
            "|Date|Author|Description|",
            "|---|---|---|",
            "|2020-12-22|numbworks|Created.|",
            "|2024-09-29|numbworks|Last update.|",
            "",
            "## Reading List By Month",
            "",
            "|   Month | 2023     | ↕   | 2024      |",
            "|--------:|:---------|:----|:----------|",
            "|       1 | 0 (0)    | ↑   | 3 (855)   |",
            "|       2 | 0 (0)    | ↑   | 14 (5573) |",
            "|       3 | 1 (139)  | ↓   | 0 (0)     |",
            "|       4 | 0 (0)    | =   | 0 (0)     |",
            "|       5 | 0 (0)    | ↑   | 2 (590)   |",
            "|       6 | 8 (642)  | ↓   | 4 (2572)  |",
            "|       7 | 0 (0)    | ↑   | 22 (6366) |",
            "|       8 | 4 (1170) | ↓   | 2 (491)   |",
            "|       9 | 9 (1969) | ↓   | 0 (0)     |",
            "|      10 | 0 (0)    | =   | 0 (0)     |",
            "|      11 | 0 (0)    | =   | 0 (0)     |",
            "|      12 | 3 (588)  | ↓   | 0 (0)     |",
            "",
            "| 2023      | ↕   | 2024       |",
            "|:----------|:----|:-----------|",
            "| 25 (4508) | ↑   | 47 (16447) |",
            "| $594.80   | ↑   | $1690.06   |"
        ]
        expected : str = "\n".join(lines) + "\n"

        return (sas_by_month_tpl, sas_by_year_street_price_df, expected)
    @staticmethod
    def create_dtos_for_rlbyratingmd() -> Tuple[DataFrame, str]:

        data : dict = {
            'Rating': ['★★★★★', '★★★★☆', '★★★☆☆', '★★☆☆☆', '★☆☆☆☆'],
            'Books': [9, 22, 87, 102, 84]
        }
        sas_by_rating_df = pd.DataFrame(data)

        lines : list[str] = [
            "## Revision History",
            "",
            "|Date|Author|Description|",
            "|---|---|---|",
            "|2020-12-22|numbworks|Created.|",
            "|2024-09-29|numbworks|Last update.|",
            "",
            "## Reading List By Rating",
            "",
            "| Rating   |   Books |",
            "|:---------|--------:|",
            "| ★★★★★    |       9 |",
            "| ★★★★☆    |      22 |",
            "| ★★★☆☆    |      87 |",
            "| ★★☆☆☆    |     102 |",
            "| ★☆☆☆☆    |      84 |"
        ]
        expected : str = "\n".join(lines) + "\n"

        return (sas_by_rating_df, expected)

    @staticmethod
    def create_service_objects_for_readmemd(show_readme_md : bool) -> Tuple[ComponentBag, SettingBag, MarkdownProcessor]:

        component_bag : Mock = Mock()
        
        setting_bag : Mock = Mock()
        setting_bag.show_readme_md = show_readme_md

        markdown_processor : MarkdownProcessor = MarkdownProcessor(
			component_bag = component_bag, 
			setting_bag = setting_bag
			)        

        return (component_bag, setting_bag, markdown_processor)    
    @staticmethod
    def create_service_objects_for_rlbymonthmd(rl_by_month_smaller_font : bool) -> Tuple[ComponentBag, SettingBag, MarkdownProcessor]:

        component_bag : Mock = Mock()
        component_bag.logging_function = Mock()
        component_bag.file_manager.save_content = Mock()
        component_bag.markdown_helper = MarkdownHelper(formatter = Formatter())
        component_bag.file_path_manager = FilePathManager()

        setting_bag : Mock = Mock()
        setting_bag.rl_last_update = datetime(2024, 9, 29)
        setting_bag.rl_by_month_file_name = "READINGLISTBYMONTH.md"
        setting_bag.working_folder_path = "/home/nwreadinglist/"
        setting_bag.show_rl_by_month_md = True
        setting_bag.save_rl_by_month_md = True
        setting_bag.rl_by_month_smaller_font = rl_by_month_smaller_font

        markdown_processor : MarkdownProcessor = MarkdownProcessor(
			component_bag = component_bag, 
			setting_bag = setting_bag
			)        

        return (component_bag, setting_bag, markdown_processor)    
    @staticmethod    
    def create_service_objects_for_rlbyratingmd() -> Tuple[ComponentBag, SettingBag, MarkdownProcessor]:

        component_bag : Mock = Mock()
        component_bag.logging_function = Mock()
        component_bag.file_manager.save_content = Mock()
        component_bag.markdown_helper = MarkdownHelper(formatter = Formatter())
        component_bag.file_path_manager = FilePathManager()

        setting_bag : Mock = Mock()
        setting_bag.rl_last_update = datetime(2024, 9, 29)
        setting_bag.rl_by_rating_file_name = "READINGLISTBYRATING.md"
        setting_bag.working_folder_path = "/home/nwreadinglist/"
        setting_bag.show_rl_by_rating_md = True
        setting_bag.save_rl_by_rating_md = True

        markdown_processor : MarkdownProcessor = MarkdownProcessor(
			component_bag = component_bag, 
			setting_bag = setting_bag
			)        

        return (component_bag, setting_bag, markdown_processor)    

# TEST CLASSES
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
class ReadingListManagerTestCase(unittest.TestCase):

    @parameterized.expand([
        [0, 0, "0 (0)"],
        [13, 5157, "13 (5157)"]
    ])
    def test_formatreadingstatus_shouldreturnexpectedstring_wheninvoked(self, books : int, pages : int, expected : str):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : str = reading_list_manager._ReadingListManager__format_reading_status(books = books, pages = pages)

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        ["0 (0)", 0],
        ["13 (5157)", 13]
    ])
    def test_extractbooksfromtrend_shouldreturnexpectedint_wheninvoked(self, trend : str, expected : int):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : int = reading_list_manager._ReadingListManager__extract_books_from_trend(trend = trend)

        # Assert
        self.assertEqual(expected, actual)    
    @parameterized.expand([
        [13, 16, "↑"],
        [16, 13, "↓"],
        [0, 0, "="]
    ])
    def test_gettrend_shouldreturnexpectedstring_wheninvoked(self, value_1 : int, value_2 : int, expected : str):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : str = reading_list_manager._ReadingListManager__get_trend(value_1 = value_1, value_2 = value_2)

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        ["13 (5157)", "16 (3816)", "↑"],
        ["16 (3816)", "13 (5157)", "↓"],
        ["0 (0)", "0 (0)", "="]
    ])
    def test_gettrendbybooks_shouldreturnexpectedstring_wheninvoked(self, trend_1 : str, trend_2 : str, expected : str):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : str = reading_list_manager._ReadingListManager__get_trend_by_books(trend_1 = trend_1, trend_2 = trend_2)

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        ["2016", "2016"],
        ["↕1", "↕"]
    ])
    def test_tryconsolidatetrendcolumnname_shouldreturnexpectedstring_wheninvoked(self, column_name : str, expected : str):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : str = reading_list_manager._ReadingListManager__try_consolidate_trend_column_name(column_name = column_name)

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        ["13 (5157)", 5157],
        ["0 (0)", 0]
    ])
    def test_extractpagesfromtrend_shouldreturnexpectedint_wheninvoked(self, trend : str, expected : int):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : int = reading_list_manager._ReadingListManager__extract_pages_from_trend(trend = trend)

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        ["2016", "2016_Books"]
    ])
    def test_formatyearbookscolumnname_shouldreturnexpectedstring_wheninvoked(self, year_cn : str, expected : str):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : str = reading_list_manager._ReadingListManager__format_year_books_column_name(year_cn = year_cn)

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        ["2016", "2016_Pages"]
    ])
    def test_formatyearpagescolumnname_shouldreturnexpectedstring_wheninvoked(self, year_cn : str, expected : str):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : str = reading_list_manager._ReadingListManager__format_year_pages_column_name(year_cn = year_cn)

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        ["2016_Books", "2016"],
        ["2016_Pages", "2016"]
    ])
    def test_extractyearfromcolumnname_shouldreturnexpectedstring_wheninvoked(self, column_name : str, expected : str):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : str = reading_list_manager._ReadingListManager__extract_year_from_column_name(column_name = column_name)

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        [1447.14, 2123.36, "↑"],
        [2123.36, 1447.14, "↓"],
        [0, 0, "="]
    ])
    def test_gettrendwhenfloat64_shouldreturnexpectedstring_wheninvoked(self, value_1 : float64, value_2 : float64, expected : str):
        
        # Arrange
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual : str = reading_list_manager._ReadingListManager__get_trend_when_float64(value_1 = value_1, value_2 = value_2)

        # Assert
        self.assertEqual(expected, actual)
    
    def test_getdefaultsabyyear_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        expected_df : DataFrame = ObjectMother().create_default_sa_by_2024_df()
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual_df : DataFrame = reading_list_manager._ReadingListManager__get_default_sa_by_year(read_year = 2024)

        # Assert
        assert_frame_equal(expected_df, actual_df)

    def test_getbooksdataset_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        books_df : DataFrame = ObjectMother().create_books_df()
        expected_column_names : list[str] = ObjectMother().create_books_df_column_names()
        expected_dtype_names : list[str] = ObjectMother().create_books_df_dtype_names()
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual_df : DataFrame = pd.DataFrame()
        with patch.object(pd, 'read_excel', return_value = books_df) as mocked_context:
            actual_df = reading_list_manager.get_rl()

        # Assert
        self.assertEqual(expected_column_names, actual_df.columns.tolist())
        self.assertEqual(expected_dtype_names, SupportMethodProvider().get_dtype_names(df = actual_df))
    def test_getsasbytopic_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        books_df : DataFrame = ObjectMother().create_books_df()
        expected_df : DataFrame = ObjectMother().create_sas_by_topic_df()
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual_df : DataFrame = reading_list_manager.get_sas_by_topic(rl_df = books_df)

        # Assert
        assert_frame_equal(expected_df, actual_df)
    def test_getsasbyrating_shouldreturnexpecteddataframe_whenformattedratingequalstotrue(self):
        
        # Arrange
        books_df : DataFrame = ObjectMother().create_books_df()
        expected_df : DataFrame = ObjectMother().create_sas_by_rating_df()
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual_df : DataFrame = reading_list_manager.get_sas_by_rating(rl_df = books_df)

        # Assert
        assert_frame_equal(expected_df, actual_df)
    def test_getrollingtotal_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        books_df : DataFrame = ObjectMother().create_books_df()
        expected_df : DataFrame = ObjectMother().create_cumulative_df()
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual_df : DataFrame = reading_list_manager.get_rl_asrt(rl_df = books_df)

        # Assert
        assert_frame_equal(expected_df, actual_df)
    def test_getyearlytrendbytopic_shouldreturnexpecteddataframe_wheninvoked(self):
        
        # Arrange
        books_df : DataFrame = ObjectMother().create_books_df()
        expected_df : DataFrame = ObjectMother().create_yt_by_topic_df()
        reading_list_manager : ReadingListManager = ObjectMother().create_reading_list_manager()

        # Act
        actual_df : DataFrame = reading_list_manager.get_trend_by_year_topic(rl_df = books_df)

        # Assert
        assert_frame_equal(expected_df, actual_df)
class MarkdownProcessorTestCase(unittest.TestCase):

    def test_processreadmemd_shouldlogreadmemd_whensettingistrue(self) -> None:
        
		# Arrange
        df, expected = ObjectMother().create_dtos_for_readmemd()        
        component_bag, _, markdown_processor = ObjectMother().create_service_objects_for_readmemd(show_readme_md = True)
				       
        # Act
        markdown_processor.process_rl_asrt_md(rl_asrt_df = df)
        
        # Assert
        component_bag.logging_function.assert_called_once_with(expected)	
    def test_processreadmemd_shouldnotcallloggingfunction_whensettingisfalse(self) -> None:
        
		# Arrange
        df, _ = ObjectMother().create_dtos_for_readmemd()
        component_bag, _, markdown_processor = ObjectMother().create_service_objects_for_readmemd(show_readme_md = False)

        # Act
        markdown_processor.process_rl_asrt_md(rl_asrt_df = df)
        
        # Assert
        component_bag.logging_function.assert_not_called()
    def test_processrlbymonthmd_shouldlogandsave_whensmallerfontisfalse(self) -> None:

		# Arrange
        file_name : str = "READINGLISTBYMONTH.md"
        file_path : str = f"/home/nwreadinglist/{file_name}"
        sas_by_month_tpl, sas_by_year_street_price_df, expected = ObjectMother().create_dtos_for_rlbymonthmd()
        component_bag, _, markdown_processor = ObjectMother().create_service_objects_for_rlbymonthmd(rl_by_month_smaller_font = False)        

        # Act
        markdown_processor.process_rl_by_month_md(
            sas_by_month_tpl = sas_by_month_tpl, 
            sas_by_year_street_price_df = sas_by_year_street_price_df
        )

        # Assert
        self.assertEqual(component_bag.logging_function.call_count, 2)
        component_bag.logging_function.assert_has_calls([
            call(file_name + "\n"),
            call(expected)
        ])
        component_bag.file_manager.save_content.assert_called_with(content = expected, file_path = file_path)
    def test_processrlbyratingmd_shouldlogandsave_wheninvoked(self) -> None:

		# Arrange
        file_name : str = "READINGLISTBYRATING.md"
        file_path : str = f"/home/nwreadinglist/{file_name}"
        sas_by_rating_df, expected = ObjectMother().create_dtos_for_rlbyratingmd()
        component_bag, _, markdown_processor = ObjectMother().create_service_objects_for_rlbyratingmd()        

        # Act
        markdown_processor.process_rl_by_rating_md(sas_by_rating_df = sas_by_rating_df)

        # Assert
        self.assertEqual(component_bag.logging_function.call_count, 2)
        component_bag.logging_function.assert_has_calls([
            call(file_name + "\n"),
            call(expected)
        ])
        component_bag.file_manager.save_content.assert_called_with(content = expected, file_path = file_path)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)