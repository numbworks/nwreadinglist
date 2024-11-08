'''
A collection of components to handle "Reading List.xlsx".

Alias: nwrl
'''

# GLOBAL MODULES
import copy
import numpy as np
import openpyxl
import os
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from numpy import float64
from pandas import DataFrame
from pandas import Series
from sparklines import sparklines
from typing import Any, Callable, Literal, Optional, Tuple

# LOCAL MODULES
from nwshared import Formatter, Converter, FilePathManager, FileManager
from nwshared import LambdaProvider, MarkdownHelper

# CONSTANTS
# DTOs
class SettingBag():

    '''Represents a collection of settings.'''

    save_rl_by_month_md : bool
    save_rl_by_publisher_md : bool
    save_rl_by_rating_md : bool
    save_rl_by_topic_md : bool
    save_rl_topic_trend_md : bool
    save_rl_md : bool
    read_years : list[int]
    excel_path : str
    excel_books_nrows : int

    show_rl_df : bool
    show_sas_by_month_df : bool
    show_sas_by_year_street_price_df : bool
    show_rl_asrt_df : bool
    show_sas_by_topic_df : bool
    show_sas_by_publisher_df : bool
    show_sas_by_rating_df : bool
    show_rl_by_kbsize_df : bool
    show_yearly_trend_by_topic_df : bool
    show_books_by_year_box_plot : bool
    show_rl_by_kbsize_box_plot : bool
    show_rl_asrt_md : bool
    show_rl_by_month_md : bool
    show_rl_by_publisher_md : bool
    show_rl_by_rating_md : bool
    show_rl_by_topic_md : bool
    show_rl_topic_trend_md : bool
    show_rl_md : bool
    working_folder_path : str    
    excel_books_skiprows : int
    excel_books_tabname : str
    excel_null_value : str
    now : datetime
    n_generic : int
    n_by_month : int
    n_by_kbsize : int
    rounding_digits : int
    is_worth_min_books : int
    is_worth_min_avgrating : float
    is_worth_criteria : str
    kbsize_ascending : bool
    kbsize_remove_if_zero : bool
    formatted_rating : bool
    enable_sparklines_maximum : bool
    rl_by_month_file_name : str
    rl_by_publisher_file_name : str
    rl_by_rating_file_name : str
    rl_by_topic_file_name : str
    rl_topic_trend_file_name : str
    rl_file_name : str
    rl_last_update : datetime
    rl_smaller_font : bool
    rl_by_month_smaller_font : bool
    definitions : dict

    def __init__(
        self,
        save_rl_by_month_md : bool,
        save_rl_by_publisher_md : bool,
        save_rl_by_rating_md : bool,
        save_rl_by_topic_md : bool,
        save_rl_topic_trend_md : bool,
        save_rl_md : bool,
        read_years : list[int],
        excel_path : str,
        excel_books_nrows : int,

        show_rl_df : bool = False,
        show_sas_by_month_df : bool = True,
        show_sas_by_year_street_price_df : bool = True,
        show_rl_asrt_df : bool = True,
        show_sas_by_topic_df : bool = True,
        show_sas_by_publisher_df : bool = True,
        show_sas_by_rating_df : bool = True,
        show_rl_by_kbsize_df : bool = True,
        show_yearly_trend_by_topic_df : bool = True,
        show_books_by_year_box_plot : bool = True,
        show_rl_by_kbsize_box_plot : bool = True,
        show_rl_asrt_md : bool = True,
        show_rl_by_month_md : bool = False,
        show_rl_by_publisher_md : bool = False,
        show_rl_by_rating_md : bool = False,
        show_rl_by_topic_md : bool = False,
        show_rl_topic_trend_md : bool = False,
        show_rl_md : bool = False,
        working_folder_path : str = "/home/nwreadinglist/",        
        excel_books_skiprows : int = 0,
        excel_books_tabname : str = "Books",
        excel_null_value : str = "-",
        now : datetime  = datetime.now(),
        n_generic : int = 5,
        n_by_month : int = 12,
        n_by_kbsize : int = 10,
        rounding_digits : int = 2,
        is_worth_min_books : int = 8,
        is_worth_min_avgrating : float = 2.50,
        is_worth_criteria : str = "Yes",
        kbsize_ascending : bool = False,
        kbsize_remove_if_zero : bool = True,      
        formatted_rating : bool = True,
        enable_sparklines_maximum : bool = True,
        rl_by_month_file_name : str = "READINGLISTBYMONTH.md",
        rl_by_publisher_file_name : str = "READINGLISTBYPUBLISHER.md",
        rl_by_rating_file_name : str = "READINGLISTBYRATING.md",
        rl_by_topic_file_name : str = "READINGLISTBYTOPIC.md",
        rl_topic_trend_file_name : str = "READINGLISTTOPICTREND.md",
        rl_file_name : str = "READINGLIST.md",
        rl_last_update : datetime = datetime.now(),
        rl_smaller_font : bool = False,
        rl_by_month_smaller_font : bool = False,
        definitions : dict = {
            "RL": "Reading List",
            "KBSize": "This metric is the word count of the notes I took about a given book.",
            "SAS": "Studying Activity Summary."
            }
        ) -> None:

        self.show_rl_df = show_rl_df
        self.show_sas_by_month_df = show_sas_by_month_df
        self.show_sas_by_year_street_price_df = show_sas_by_year_street_price_df
        self.show_rl_asrt_df = show_rl_asrt_df
        self.show_sas_by_topic_df = show_sas_by_topic_df
        self.show_sas_by_publisher_df = show_sas_by_publisher_df
        self.show_sas_by_rating_df = show_sas_by_rating_df
        self.show_rl_by_kbsize_df = show_rl_by_kbsize_df
        self.show_yearly_trend_by_topic_df = show_yearly_trend_by_topic_df
        self.show_books_by_year_box_plot = show_books_by_year_box_plot
        self.show_rl_by_kbsize_box_plot = show_rl_by_kbsize_box_plot
        self.show_rl_asrt_md = show_rl_asrt_md
        self.show_rl_by_month_md = show_rl_by_month_md
        self.show_rl_by_publisher_md = show_rl_by_publisher_md
        self.show_rl_by_rating_md = show_rl_by_rating_md
        self.show_rl_by_topic_md = show_rl_by_topic_md
        self.show_rl_topic_trend_md = show_rl_topic_trend_md
        self.show_rl_md = show_rl_md
        self.save_rl_by_month_md = save_rl_by_month_md
        self.save_rl_by_publisher_md = save_rl_by_publisher_md
        self.save_rl_by_rating_md = save_rl_by_rating_md
        self.save_rl_by_topic_md = save_rl_by_topic_md
        self.save_rl_topic_trend_md = save_rl_topic_trend_md
        self.save_rl_md = save_rl_md
        self.working_folder_path = working_folder_path
        self.read_years = read_years
        self.excel_path = excel_path
        self.excel_books_nrows = excel_books_nrows

        self.excel_books_skiprows = excel_books_skiprows
        self.excel_books_tabname = excel_books_tabname 
        self.excel_null_value = excel_null_value
        self.now = now
        self.n_generic = n_generic 
        self.n_by_month = n_by_month
        self.n_by_kbsize = n_by_kbsize
        self.rounding_digits = rounding_digits
        self.is_worth_min_books = is_worth_min_books
        self.is_worth_min_avgrating = is_worth_min_avgrating
        self.is_worth_criteria = is_worth_criteria
        self.kbsize_ascending = kbsize_ascending
        self.kbsize_remove_if_zero = kbsize_remove_if_zero
        self.formatted_rating = formatted_rating
        self.enable_sparklines_maximum = enable_sparklines_maximum
        self.rl_by_month_file_name = rl_by_month_file_name
        self.rl_by_publisher_file_name = rl_by_publisher_file_name 
        self.rl_by_rating_file_name = rl_by_rating_file_name
        self.rl_by_topic_file_name = rl_by_topic_file_name
        self.rl_topic_trend_file_name = rl_topic_trend_file_name 
        self.rl_file_name = rl_file_name
        self.rl_last_update = rl_last_update
        self.rl_smaller_font = rl_smaller_font
        self.rl_by_month_smaller_font = rl_by_month_smaller_font
        self.definitions = definitions
class ComponentBag():

    '''Represents a collection of components.'''

    formatter : Formatter
    converter : Converter
    file_path_manager : FilePathManager
    file_manager : FileManager
    logging_function : Callable[[str], None]
    markdown_helper : MarkdownHelper

    def __init__(
            self, 
            formatter : Formatter = Formatter(), 
            converter : Converter = Converter(), 
            file_path_manager : FilePathManager = FilePathManager(),
            file_manager : FileManager = FileManager(file_path_manager = FilePathManager()),
            logging_function : Callable[[str], None] = LambdaProvider().get_default_logging_function(),
            markdown_helper : MarkdownHelper = MarkdownHelper(formatter = Formatter())) -> None:

        self.formatter = formatter
        self.converter = converter
        self.file_path_manager = file_path_manager
        self.file_manager = file_manager
        self.logging_function = logging_function
        self.markdown_helper = markdown_helper
@dataclass(frozen = True)
class RLSummary():

    '''Collects all the dataframes created by RLManager'''

    rl_df : DataFrame
    rl_asrt_df : DataFrame
    rl_by_kbsize_df : DataFrame
    rl_by_kbsize_box_plot: Callable[[Any], None]
    rl_by_books_year_box_plot : Callable[[Any], None]
    sas_by_month_tpl : Tuple[DataFrame, DataFrame]
    sas_by_year_street_price_df : DataFrame
    sas_by_topic_df : DataFrame
    sas_by_publisher_tpl : Tuple[DataFrame, DataFrame]
    sas_by_rating_df : DataFrame
    trend_by_year_topic_df : DataFrame
@dataclass(frozen = True)
class MDSummary():

    '''Collects all the dataframes created by MDManager'''

    rl_md : str
    rl_asrt_md : str    
    rl_by_month_md : str
    rl_by_publisher_md : str
    rl_by_rating_md : str
    rl_by_topic_md : str
    rl_by_topic_trend_md : str # rename

class SettingBagNew():

    '''Represents a collection of settings.'''

    options_rl : list[Literal["show"]]
    options_rl_asrt : list[Literal["show"]]
    options_rl_by_kbsize : list[Literal["show"]]
    options_sas_by_month : list[Literal["show"]]
    options_sas_by_year_street_price : list[Literal["show"]]
    options_sas_by_topic : list[Literal["show"]]
    options_sas_by_publisher : list[Literal["show"]]
    options_sas_by_rating : list[Literal["show"]]
    read_years : list[int]
    excel_path : str
    excel_books_nrows : int

    working_folder_path : str    
    excel_books_skiprows : int
    excel_books_tabname : str
    excel_null_value : str
    now : datetime
    n_generic : int
    n_by_month : int
    n_by_kbsize : int
    rounding_digits : int
    is_worth_min_books : int
    is_worth_min_avgrating : float
    is_worth_criteria : str
    kbsize_ascending : bool
    kbsize_remove_if_zero : bool
    formatted_rating : bool
    enable_sparklines_maximum : bool
    rl_file_name : str    
    rl_by_month_file_name : str
    rl_by_publisher_file_name : str
    rl_by_rating_file_name : str
    rl_by_topic_file_name : str
    rl_topic_trend_file_name : str
    rl_last_update : datetime
    rl_smaller_font : bool
    rl_by_month_smaller_font : bool
    definitions : dict

    def __init__(
            self,
            options_rl : list[Literal["show"]],
            options_rl_asrt : list[Literal["show"]],
            options_rl_by_kbsize : list[Literal["show"]],
            options_sas_by_month : list[Literal["show"]],
            options_sas_by_year_street_price : list[Literal["show"]],
            options_sas_by_topic : list[Literal["show"]],
            options_sas_by_publisher : list[Literal["show"]],
            options_sas_by_rating : list[Literal["show"]],
            read_years : list[int],
            excel_path : str,
            excel_books_nrows : int,
            working_folder_path : str = "/home/nwreadinglist/",        
            excel_books_skiprows : int = 0,
            excel_books_tabname : str = "Books",
            excel_null_value : str = "-",
            now : datetime  = datetime.now(),
            n_generic : int = 5,
            n_by_month : int = 12,
            n_by_kbsize : int = 10,
            rounding_digits : int = 2,
            is_worth_min_books : int = 8,
            is_worth_min_avgrating : float = 2.50,
            is_worth_criteria : str = "Yes",
            kbsize_ascending : bool = False,
            kbsize_remove_if_zero : bool = True,      
            formatted_rating : bool = True,
            enable_sparklines_maximum : bool = True,
            rl_last_update : datetime = datetime.now(),
            rl_smaller_font : bool = False,
            rl_by_month_smaller_font : bool = False,
            file_names : dict[str, str] = {
                "rl" : "READINGLIST.md",
                "rl_by_month" : "READINGLISTBYMONTH.md",
                "rl_by_publisher" : "READINGLISTBYPUBLISHER.md",
                "rl_by_rating" : "READINGLISTBYRATING.md",
                "rl_by_topic" : "READINGLISTBYTOPIC.md",
                "rl_topic_trend" : "READINGLISTTOPICTREND.md"
            },
            definitions : dict[str, str] = {
                "RL": "Reading List",
                "KBSize": "This metric is the word count of the notes I took about a given book.",
                "SAS": "Studying Activity Summary."
                }            
            ) -> None:

        self.options_rl = options_rl
        self.options_rl_asrt = options_rl_asrt
        self.options_rl_by_kbsize = options_rl_by_kbsize
        self.options_sas_by_month = options_sas_by_month
        self.options_sas_by_year_street_price = options_sas_by_year_street_price
        self.options_sas_by_topic = options_sas_by_topic
        self.options_sas_by_publisher = options_sas_by_publisher
        self.options_sas_by_rating = options_sas_by_rating
        self.read_years = read_years
        self.excel_path = excel_path
        self.excel_books_nrows = excel_books_nrows

        self.working_folder_path = working_folder_path
        self.excel_books_skiprows = excel_books_skiprows
        self.excel_books_tabname = excel_books_tabname
        self.excel_null_value = excel_null_value
        self.now = now
        self.n_generic = n_generic
        self.n_by_month = n_by_month
        self.n_by_kbsize = n_by_kbsize
        self.rounding_digits = rounding_digits
        self.is_worth_min_books = is_worth_min_books
        self.is_worth_min_avgrating = is_worth_min_avgrating
        self.is_worth_criteria = is_worth_criteria
        self.kbsize_ascending = kbsize_ascending
        self.kbsize_remove_if_zero = kbsize_remove_if_zero
        self.formatted_rating = formatted_rating
        self.enable_sparklines_maximum = enable_sparklines_maximum
        self.rl_last_update = rl_last_update
        self.rl_smaller_font = rl_smaller_font
        self.rl_by_month_smaller_font = rl_by_month_smaller_font
        self.file_names = file_names
        self.definitions = definitions


        

# STATIC CLASSES
# CLASSES
class DefaultPathProvider():

    '''Responsible for proviving the default path to the dataset.'''

    def get_default_reading_list_path(self)-> str:

        r'''
            "c:\...\nwreadinglistmanager\data\Reading List.xlsx"
        '''
        
        path : str = os.getcwd().replace("src", "data")
        path = os.path.join(path, "Reading List.xlsx")

        return path
class YearProvider():

    '''Collects all the logic related to the retrieval of year-related information.'''

    def get_all_years(self) -> list[int]:

        '''Returns a list of years.'''

        years : list[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

        return years
class ReadingListManager():

    '''Collects all the logic related to the management of "Reading List.xlsx".'''

    __component_bag : ComponentBag
    __setting_bag : SettingBag

    def __init__(self, component_bag : ComponentBag, setting_bag : SettingBag) -> None:

        self.__component_bag = component_bag
        self.__setting_bag = setting_bag

    def __enforce_dataframe_definition_for_rl_df(self, rl_df : DataFrame, excel_null_value : str) -> DataFrame:

        '''Enforces definition for the provided dataframe.'''

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

        rl_df = rl_df[column_names]
        rl_df = rl_df.replace(to_replace = excel_null_value, value = np.nan)
    
        rl_df = rl_df.astype({column_names[0]: str})  
        rl_df = rl_df.astype({column_names[1]: int})
        rl_df = rl_df.astype({column_names[2]: str})
        rl_df = rl_df.astype({column_names[3]: str})
        rl_df = rl_df.astype({column_names[4]: str})
        rl_df = rl_df.astype({column_names[5]: int})

        rl_df[column_names[6]] = pd.to_datetime(rl_df[column_names[6]], format="%Y-%m-%d") 
        rl_df[column_names[6]] = rl_df[column_names[6]].apply(lambda x: x.date())

        rl_df = rl_df.astype({column_names[7]: int})
        rl_df = rl_df.astype({column_names[8]: int})
        rl_df = rl_df.astype({column_names[9]: str})
        rl_df = rl_df.astype({column_names[10]: str})
        rl_df = rl_df.astype({column_names[11]: str})
        rl_df = rl_df.astype({column_names[12]: int})
        rl_df = rl_df.astype({column_names[13]: float})    
        rl_df = rl_df.astype({column_names[14]: str})
        rl_df = rl_df.astype({column_names[15]: str})
        rl_df = rl_df.astype({column_names[16]: str})
        rl_df = rl_df.astype({column_names[17]: str})
        rl_df = rl_df.astype({column_names[18]: int})
        rl_df = rl_df.astype({column_names[19]: int})

        return rl_df
    def __format_reading_status(self, books : int, pages : int) -> str:

        '''
            13, 5157 => "13 (5157)"
        '''
        
        reading_status : str = f"{books} ({pages})"
        
        return reading_status
    def __get_default_sa_by_year(self, read_year : int) -> DataFrame:

        '''

            default_df:

                    Month	2017
                0	1	    0 (0)
                1	2	    0 (0)
                ... ...     ...    
        
        '''

        cn_month : str = "Month"    
        default_df : DataFrame = pd.DataFrame(
            {
                f"{cn_month}": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                f"{str(read_year)}": ["0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)"]
            },
            index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        )

        default_df = default_df.astype({cn_month: int})
        default_df = default_df.astype({str(read_year): str})

        return default_df
    def __try_complete_sa_by_year(self, sa_by_year_df : DataFrame, read_year : int) -> DataFrame:

        '''

            We expect sa_by_year_df to have 12 months: 
            
                - if that's the case, we are done with it and we return it;
                - if it's not the case, we generate a default_df and we use it to fill the missing values.

                sa_by_year_df
            
                        Month	2016
                    0	5	    1 (288)
                    1	6	    8 (1734)
                    2	7	    4 (1758)
                    3	8	    2 (334)
                    4	9	    4 (881)
                    5	10	    2 (275)
                    6	11	    11 (4033)
                    7	12	    11 (3019)
            
                default_df:

                        Month	2016
                    0	1	    0 (0)
                    1	2	    0 (0)
                    2	3	    0 (0)
                    3	4	    0 (0)                
                    ... ...     ...
                    11	12	    0 (0)

                missing_df:

                        Month	2016
                    0	1	    0 (0)
                    1	2	    0 (0)
                    2	3	    0 (0)
                    3	4	    0 (0)                  

                completed_df
            
                        Month	2016
                    0	1	    0 (0)
                    1	2	    0 (0)
                    2	3	    0 (0)
                    3	4	    0 (0)                                                  
                    4	5	    1 (288)
                    ... ...     ...
                    11	12	    11 (3019)
        
        '''

        cn_month : str = "Month"

        if sa_by_year_df[cn_month].count() != 12:

            default_df : DataFrame = self.__get_default_sa_by_year(read_year = read_year)
            missing_df : DataFrame = default_df.loc[~default_df[cn_month].astype(str).isin(sa_by_year_df[cn_month].astype(str))]

            completed_df : DataFrame = pd.concat([sa_by_year_df, missing_df], ignore_index = True)
            completed_df = completed_df.sort_values(by = cn_month, ascending = [True])
            completed_df = completed_df.reset_index(drop = True)

            return completed_df

        return sa_by_year_df
    def __get_sa_by_year(self, rl_df : DataFrame, read_year : int) -> DataFrame:
        
        '''

            filtered_df:
                
                Filter book_df by read_year

            by_books_df:

                    ReadMonth	Books
                0	1	        13
                1	2	        1
                ... ...         ...

            by_pages_df:

                    ReadMonth	Pages
                0	1	        5157
                1	2	        106
                ... ...         ...        
            
            sa_by_year_df:

                    ReadMonth	Pages	Books
                0	1	        5157	13
                1	2	        106 	1
                ... ...         ...     ...

                    ReadMonth	Books	Pages	2017
                0	1	        13	    5157	13 (5157)
                1	2	        1	    106	    1 (106)
                ... ...         ...     ...     ...
                
                    Month	2017
                0	1	    13 (5157)
                1	2	    1 (106)
                ... ...     ...

        '''

        cn_readyear : str = "ReadYear"
        condition : Series = (rl_df[cn_readyear] == read_year)
        filtered_df : DataFrame = rl_df.loc[condition]

        cn_readmonth : str = "ReadMonth" 
        cn_title : str = "Title"
        cn_books : str = "Books"
        by_books_df : DataFrame = filtered_df.groupby([cn_readmonth])[cn_title].size().sort_values(ascending = [False]).reset_index(name = cn_books)
        by_books_df = by_books_df.sort_values(by = cn_readmonth).reset_index(drop = True)   
    
        cn_pages : str = "Pages"
        by_pages_df : DataFrame = filtered_df.groupby([cn_readmonth])[cn_pages].sum().sort_values(ascending = [False]).reset_index(name = cn_pages)
        by_pages_df = by_pages_df.sort_values(by = cn_readmonth).reset_index(drop = True)

        sa_by_year_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_pages_df, 
            how = "inner", 
            left_on = cn_readmonth, 
            right_on = cn_readmonth)
        sa_by_year_df[read_year] = sa_by_year_df.apply(lambda x : self.__format_reading_status(books = x[cn_books], pages = x[cn_pages]), axis = 1) 

        cn_month : str = "Month"
        sa_by_year_df[cn_month] = sa_by_year_df[cn_readmonth]
        sa_by_year_df = sa_by_year_df[[cn_month, read_year]]
        sa_by_year_df = sa_by_year_df.astype({cn_month: int})
        sa_by_year_df = sa_by_year_df.astype({read_year: str})    
        sa_by_year_df.columns = sa_by_year_df.columns.astype(str) # 2016 => "2016"

        sa_by_year_df = self.__try_complete_sa_by_year(sa_by_year_df = sa_by_year_df, read_year = read_year)

        return sa_by_year_df
    def __extract_books_from_trend(self, trend : str) -> int:

        '''
            "13 (5157)" => ["13", "(5157)"] => "13" => 13
        '''

        tokens : list = trend.split(" ")

        return int(tokens[0])
    def __get_trend(self, value_1 : int, value_2 : int) -> str:

        '''
            13, 16 => "↑"
            16, 13 => "↓"
            0, 0 => "="
        '''
        trend : str = ""

        if value_1 < value_2:
            trend = "↑"
        elif value_1 > value_2:
            trend = "↓"
        else:
            trend = "="

        return trend
    def __get_trend_by_books(self, trend_1 : str, trend_2 : str) -> str:

        '''
            "13 (5157)", "16 (3816)" => "↑"
            "16 (3816)", "13 (5157)" => "↓"
            "0 (0)", "0 (0)" => "="   
        '''

        books_1 : int = self.__extract_books_from_trend(trend = trend_1)
        books_2 : int = self.__extract_books_from_trend(trend = trend_2)

        trend : str = self.__get_trend(value_1 = books_1, value_2 = books_2)

        return trend
    def __expand_sa_by_year(self, rl_df : DataFrame, read_years : list, sas_by_month_df : DataFrame, i : int, add_trend : bool) -> DataFrame:

        '''    
            sa_summary_df:

                    Month	2016
                0	1	    0 (0)
                1	2	    0 (0)
                ...

            sa_by_year_df:

                    Month	2017
                0	1	    13 (5157)
                1	2	    1 (106)
                ...            

            expansion_df:

                    Month	2016	2017
                0	1	    0 (0)	13 (5157)
                1	2	    0 (0)	1 (106)
                ...

            expansion_df:        

                    Month	2016	2017	    ↕1
                0	1	    0 (0)	13 (5157)	↑
                1	2	    0 (0)	1 (106)	    ↑
                ...

            expansion_df:

                    Month	2016	↕1	2017
                0	1	    0 (0)	↑	13 (5157)
                1	2	    0 (0)	↑	1 (106)
                ...

            Now that we have the expansion_df, we append it to the right of sa_summary_df:

            sa_summary_df:

                    Month	2016	↕1	2017
                0	1	    0 (0)	↑	13 (5157)
                1	2	    0 (0)	↑	1 (106)
                ...
        '''
        
        actual_df : DataFrame = sas_by_month_df.copy(deep = True)
        sa_by_year_df : DataFrame = self.__get_sa_by_year(rl_df = rl_df, read_year = read_years[i])

        cn_month : str = "Month"      
        expansion_df = pd.merge(
            left = actual_df, 
            right = sa_by_year_df, 
            how = "inner", 
            left_on = cn_month, 
            right_on = cn_month)

        if add_trend == True:

            cn_trend : str = f"↕{i}"
            cn_trend_1 : str = str(read_years[i-1])   # for ex. "2016"
            cn_trend_2 : str = str(read_years[i])     # for ex. "2017"
            
            expansion_df[cn_trend] = expansion_df.apply(lambda x : self.__get_trend_by_books(trend_1 = x[cn_trend_1], trend_2 = x[cn_trend_2]), axis = 1) 

            new_column_names : list = [cn_month, cn_trend_1, cn_trend, cn_trend_2]   # for ex. ["Month", "2016", "↕", "2017"]
            expansion_df = expansion_df.reindex(columns = new_column_names)

            shared_columns : list = [cn_month, str(read_years[i-1])] # ["Month", "2016"]
            actual_df = pd.merge(
                left = actual_df, 
                right = expansion_df, 
                how = "inner", 
                left_on = shared_columns, 
                right_on = shared_columns)

        else:
            actual_df = expansion_df

        return actual_df
    def __try_consolidate_trend_column_name(self, column_name : str) -> str:

        '''
            "2016"  => "2016"
            "↕1"    => "↕"
        '''

        cn_trend : str = "↕"

        if column_name.startswith(cn_trend):
            return cn_trend
        
        return column_name
    def __extract_pages_from_trend(self, trend : str) -> int:

        '''
            "13 (5157)" => ["13", "(5157)"] => "5157" => 5157
        '''

        tokens : list = trend.split(" ")
        token : str = tokens[1].replace("(", "").replace(")", "")

        return int(token)
    def __format_year_books_column_name(self, year_cn : str) -> str:

        '''
            "2016" => "2016_Books"
        '''

        column_name : str = f"{year_cn}_Books"

        return column_name
    def __format_year_pages_column_name(self, year_cn : str) -> str:

        '''
            "2016" => "2016_Pages"
        '''

        column_name : str = f"{year_cn}_Pages"

        return column_name
    def __extract_year_from_column_name(self, column_name : str) -> str:

        '''
            "2016_Books" => "2016"
            "2016_Pages" => "2016"        
        '''

        tokens : list = column_name.split("_")

        return tokens[0]
    def __add_trend_to_sas_by_year(self, sas_by_year_df : DataFrame, yeatrend : list) -> DataFrame:

        '''
            expanded_df:

                    2016	    2017	    2018	    2019	    2020	    2021	    2022	2023
                0	43 (12322)	63 (18726)	48 (12646)	42 (9952)	23 (6602)	13 (1901)	1 (360)	1 (139)

            new_column_names:
            
                ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]

            i == 0, sas_by_year_df:

                    2016	    2017	    2018	    2019	    2020	    2021	    2022	2023	↕0
                0	43 (12322)	63 (18726)	48 (12646)	42 (9952)	23 (6602)	13 (1901)	1 (360)	1 (139)	↑ 

            i == 0, new_column_names:
                
                ["2016", "↕0", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]

            [...]

            expanded_df:        

                2016	    ↕0	2017	    ↕1	2018	    ↕2	2019	    ↕3	2020	    ↕4	2021	    ↕5	2022	↕6	2023
            0	43 (12322)	↑	63 (18726)	↓	48 (12646)	↓	42 (9952)	↓	23 (6602)	↓	13 (1901)	↓	1 (360)	=	1 (139)        

        '''  

        expanded_df : DataFrame = sas_by_year_df.copy(deep=True)
        new_column_names : list = copy.deepcopy(x = yeatrend)

        for i in range(len(yeatrend)):

            if i != (len(yeatrend) - 1):

                cn_trend : str = f"↕{i}"
                cn_trend_1 : str = str(yeatrend[i])       # 2016 => "2016"
                cn_trend_2 : str = str(yeatrend[i+1])     # 2017 => "2017"
                
                expanded_df[cn_trend] = expanded_df.apply(lambda x : self.__get_trend_by_books(trend_1 = x[cn_trend_1], trend_2 = x[cn_trend_2]), axis = 1) 
                
                new_item_position : int = (new_column_names.index(cn_trend_1) + 1)
                new_column_names.insert(new_item_position, cn_trend)

                expanded_df = expanded_df.reindex(columns = new_column_names)
                
        return expanded_df
    def __get_trend_when_float64(self, value_1 : float64, value_2 : float64) -> str:

        '''
            1447.14, 2123.36 => "↑"
            2123.36, 1447.14 => "↓"
            0, 0 => "="
        '''

        trend : str = ""

        if value_1 < value_2:
            trend = "↑"
        elif value_1 > value_2:
            trend = "↓"
        else:
            trend = "="

        return trend
    def __add_trend_to_sas_by_street_price(self, sas_by_street_price_df : DataFrame, yeatrend : list) -> DataFrame:

        '''
            [...]

            expanded_df:

                2016	↕0	2017	↕1	2018	↕2	2019	↕3	2020	↕4	2021	↕5	2022	↕6	2023
            0	1447.14	↑	2123.36	↓	1249.15	↓	748.7	↓	538.75	↓	169.92	↓	49.99	↓	5.0
        '''  

        expanded_df : DataFrame = sas_by_street_price_df.copy(deep=True)
        new_column_names : list = copy.deepcopy(x = yeatrend)
        new_column_names = [str(x) for x in new_column_names]

        for i in range(len(yeatrend)):

            if i != (len(yeatrend) - 1):

                cn_trend : str = f"↕{i}"
                cn_value_1 : str = str(yeatrend[i])       # 2016 => "2016"
                cn_value_2 : str = str(yeatrend[i+1])     # 2017 => "2017"
                
                expanded_df[cn_trend] = expanded_df.apply(lambda x : self.__get_trend_when_float64(value_1 = x[cn_value_1], value_2 = x[cn_value_2]), axis = 1) 
                
                new_item_position : int = (new_column_names.index(cn_value_1) + 1)
                new_column_names.insert(new_item_position, cn_trend)

                expanded_df = expanded_df.reindex(columns = new_column_names)
                
        return expanded_df
    def __group_books_by_single_column(self, rl_df : DataFrame, column_name : str) -> DataFrame:

        '''Groups books according to the provided column name. The book titles act as unique identifiers.'''

        cn_uniqueitemidentifier : str = "Title"
        cn_items : str = "Books"

        grouped_df : DataFrame = rl_df.groupby([column_name])[cn_uniqueitemidentifier].size().sort_values(ascending = [False]).reset_index(name = cn_items)
        
        return grouped_df
    def __group_books_by_multiple_columns(self, rl_df : DataFrame, column_names : list[str]) -> DataFrame:

        '''Groups books according to the provided column names (note: order matters). The book titles act as unique identifiers.'''

        cn_uniqueitemidentifier : str = "Title"
        cn_items : str = "Books"

        grouped_df : DataFrame = rl_df.groupby(by = column_names)[cn_uniqueitemidentifier].count().reset_index(name = cn_items)
        grouped_df = grouped_df.sort_values(by = column_names, ascending = [True, True])

        return grouped_df
    def __slice_by_kbsize(self, rl_df : DataFrame, ascending : bool, remove_if_zero : bool) -> DataFrame:

        '''
                Title	                                        ReadYear	Topic	                        Publisher	Rating	KBSize  A4Sheets
            0	Machine Learning For Dummies	                2017	    Data Analysis, Data Science, ML	Wiley	    4	    3732    8
            1	Machine Learning Projects for .NET Developers	2017	    Data Analysis, Data Science, ML	Apress	    4	    3272    7
            2	Producing Open Source Software	                2016	    Software Engineering	        O'Reilly	1	    2332    5
            ...
        '''

        sliced_df : DataFrame = rl_df.copy(deep=True)

        cn_title : str = "Title"
        cn_readyear : str = "ReadYear"
        cn_topic : str = "Topic"
        cn_publisher : str = "Publisher"
        cn_rating : str = "Rating"
        cn_kbsize : str = "KBSize"
        cn_a4sheets : str = "A4Sheets"

        sliced_df = sliced_df[[cn_title, cn_readyear, cn_topic, cn_publisher, cn_rating, cn_kbsize]]

        if remove_if_zero:
            condition : Series = (sliced_df[cn_kbsize] != 0)
            sliced_df = sliced_df.loc[condition]

        sliced_df = sliced_df.sort_values(by = cn_kbsize, ascending = ascending).reset_index(drop = True)   
        sliced_df[cn_a4sheets] = sliced_df[cn_kbsize].apply(
            lambda x : self.__component_bag.converter.convert_word_count_to_A4_sheets(word_count = x))

        return sliced_df    
    def __create_read_years_dataframe(self, read_years : list[int]) -> DataFrame:

        '''Create a dataframe out of the provided list of Read Years.'''

        cn_read_year : str = "ReadYear"
        read_years_df : DataFrame = pd.DataFrame(data = read_years, columns = [cn_read_year])

        return read_years_df
    def __get_topics_dataframe(self, df : DataFrame) -> DataFrame:

        '''Creates a dataframe of unique topics out of the provided dataframe.'''

        cn_topic : str = "Topic"
        topics_df : DataFrame = pd.DataFrame(data = df[cn_topic].unique(), columns = [cn_topic])
        
        return topics_df
    def __get_default_topic_read_year_dataframe(self, topics_df : DataFrame, read_years_df : DataFrame) -> DataFrame:

        '''
                Topic	                ReadYear
            0	Software Engineering	2016
            1	Software Engineering	2017
            ...
        '''

        default_df : DataFrame = pd.merge(left = topics_df, right = read_years_df, how='cross')

        return default_df
    def __get_books_by_topic_read_year(self, rl_df : DataFrame, read_years : list[int]) -> DataFrame:

        '''
            [0] - Groups rl_df by Topic_ReadYear:

                Topic	                        ReadYear	Books
            0	BI, Data Warehousing, PowerBI	2017	    1
            1	BI, Data Warehousing, PowerBI	2018	    9
            2	BI, Data Warehousing, PowerBI	2019	    11
            ...

            [1] - Add the missing values thru a default dataframe:

                Topic	                        ReadYear	Books
            0	BI, Data Warehousing, PowerBI	2016	    0
            1	BI, Data Warehousing, PowerBI	2017	    1
            2	BI, Data Warehousing, PowerBI	2018	    9
            3	BI, Data Warehousing, PowerBI	2019	    11
            4	BI, Data Warehousing, PowerBI	2020	    0
            ...

            The outer merge creates NaN values and converts the datatype of the original column 
            from "int" to "float" in order to host it. Casting it back to "int" is therefore necessary.
        '''

        cn_topic : str = "Topic"
        cn_read_year : str = "ReadYear"
        cn_books : str = "Books"    

        books_by_topic_read_year_df : DataFrame = self.__group_books_by_multiple_columns(rl_df = rl_df, column_names = [cn_topic, cn_read_year])

        topics_df : DataFrame = self.__get_topics_dataframe(df = rl_df)
        read_years_df : DataFrame = self.__create_read_years_dataframe(read_years = read_years)
        default_df : DataFrame = self.__get_default_topic_read_year_dataframe(topics_df = topics_df, read_years_df = read_years_df)

        completed_df : DataFrame = pd.merge(
            left = books_by_topic_read_year_df, 
            right = default_df,
            how = "outer")

        completed_df.sort_values(by = [cn_topic, cn_read_year], ascending = [True, True], inplace = True)
        completed_df.reset_index(inplace = True, drop = True)
        completed_df.fillna(value = 0, inplace = True)
        completed_df = completed_df.astype({cn_books: int})

        return completed_df
    def __pivot_column_values_to_cell(self, df : DataFrame, cn_index : str, cn_values : str) -> DataFrame:

        '''
            Before:

                    Topic	                        ReadYear	Books
                0	BI, Data Warehousing, PowerBI	2016	    0
                1	BI, Data Warehousing, PowerBI	2017	    1
                2	BI, Data Warehousing, PowerBI	2018	    9
                ...

            After:

                        Topic	                        Books
                0	    BI, Data Warehousing, PowerBI	[0, 1, 9, 11, 0, 0, 0, 0]
                1	    C#	                            [10, 14, 4, 17, 8, 3, 0, 0]
                ...
        '''

        pivoted_df : DataFrame = pd.pivot_table(data = df, index = [cn_index], values = [cn_values], aggfunc = lambda x : list(x))
        pivoted_df.sort_values(by = cn_index, inplace = True)
        pivoted_df.reset_index(inplace = True)

        return pivoted_df
    def __add_sparklines(self, df : DataFrame, cn_values : str, cn_sparklines : str, maximum : Optional[int] = None) -> DataFrame:

        '''
            Adds a column with sparklines to the provided DataFrame.

            "cn_values" is the name of the column containing a list of numbers.
            "cn_sparklines" is the name of the column that will host the sparklines.
        '''

        sparklined_df : DataFrame = df.copy(deep = True)
        sparklined_df[cn_sparklines] = sparklined_df[cn_values].apply(lambda numbers : sparklines(numbers = numbers, maximum = maximum)[0])

        return sparklined_df
    def __update_future_rs_to_empty(self, sas_by_month_df : DataFrame, now : datetime) -> DataFrame:

        '''	
            If now is 2023-08-09:

                Month	2022	↕	2023
                ...
                8	    0 (0)	=	0 (0)
                9	    1 (360)	↓	0 (0)
                10	    0 (0)	=	0 (0)
                11	    0 (0)	=	0 (0)
                12	    0 (0)	=	0 (0)		            

                Month	2022	↕	2023
                ...
                8	    0 (0)	=	0 (0)
                9	    1 (360)		
                10	    0 (0)		
                11	    0 (0)		
                12	    0 (0)
        '''

        sas_by_month_upd_df : DataFrame = sas_by_month_df.copy(deep = True)

        now_year : int = now.year
        now_month : int = now.month	
        cn_year : str = str(now_year)
        cn_month : str = "Month"
        new_value : str = ""

        condition : Series = (sas_by_month_upd_df[cn_month] > now_month)
        sas_by_month_upd_df[cn_year] = np.where(condition, new_value, sas_by_month_upd_df[cn_year])
            
        idx_year : int = sas_by_month_upd_df.columns.get_loc(cn_year)
        idx_trend : int = (idx_year - 1)
        sas_by_month_upd_df.iloc[:, idx_trend] = np.where(condition, new_value, sas_by_month_upd_df.iloc[:, idx_trend])

        return sas_by_month_upd_df       
    def __get_sas_by_year(self, sas_by_month_df : DataFrame) -> DataFrame:

        '''
            sas_by_year_df:

                    Month	2016	↕	2017	    ...	2022	↕	2023
                0	1	    0 (0)	↑	13 (5157)	    0 (0)	=	0 (0)	
                ...

                    2016	2017	    ...	2022	2023
                0	0 (0)	13 (5157)	...	0 (0)	0 (0)
                ...

                    2016	2017	    ... 2016_Books	2016_Pages	...	
                0	0 (0)	13 (5157)	    0	        0	        ...
                ...

                    2016_Books	2016_Pages	2017_Books	2017_Pages ...
                0	0	        0	        13	        5157
                ...

                    2016_Books	2016_Pages	2017_Books	2017_Pages	...
                0	43	        12322	    63	        18726           

                    2016_Books	2016_Pages	... 2016	    ...
                0	43	        12322	        43 (12322)	

                    2016	    2017	    2018	    2019	    2020	    2021	    2022	2023
                0	43 (12322)	63 (18726)	48 (12646)	42 (9952)	23 (6602)	13 (1901)	1 (360)	1 (139)

                [...]

                    2016	    ↕	2017	    ↕	2018	    ↕	2019	    ↕	2020	    ↕	2021	    ↕	2022	↕	2023
                0	43 (12322)	↑	63 (18726)	↓	48 (12646)	↓	42 (9952)	↓	23 (6602)	↓	13 (1901)	↓	1 (360)	=	1 (139)
        '''

        sas_by_year_df : DataFrame = sas_by_month_df.copy(deep = True)

        cn_month : str = "Month"
        cn_trend : str = "↕"
        sas_by_year_df.drop(labels = cn_month, inplace = True, axis = 1)
        sas_by_year_df.drop(labels = cn_trend, inplace = True, axis = 1)

        yeatrend : list = sas_by_year_df.columns.to_list()
        for year in yeatrend:

            cn_year_books : str = self.__format_year_books_column_name(year_cn = year)
            cn_year_pages : str = self.__format_year_pages_column_name(year_cn = year)

            sas_by_year_df[cn_year_books] = sas_by_year_df[year].apply(lambda x : self.__extract_books_from_trend(trend = x))
            sas_by_year_df[cn_year_pages] = sas_by_year_df[year].apply(lambda x : self.__extract_pages_from_trend(trend = x))

            sas_by_year_df.drop(labels = year, inplace = True, axis = 1)

        sas_by_year_df = sas_by_year_df.sum().to_frame().transpose()

        for year in yeatrend:

            cn_year_books = self.__format_year_books_column_name(year_cn = year)
            cn_year_pages = self.__format_year_pages_column_name(year_cn = year)

            sas_by_year_df[year] = sas_by_year_df.apply(lambda x : self.__format_reading_status(books = x[cn_year_books], pages = x[cn_year_pages]), axis = 1) 

            sas_by_year_df.drop(labels = [cn_year_books, cn_year_pages], inplace = True, axis = 1)

        sas_by_year_df = self.__add_trend_to_sas_by_year(sas_by_year_df = sas_by_year_df, yeatrend = yeatrend)
        sas_by_year_df.rename(columns = (lambda x : self.__try_consolidate_trend_column_name(column_name = x)), inplace = True)

        return sas_by_year_df
    def __get_sas_by_street_price(self, rl_df : DataFrame, read_years : list, rounding_digits : int) -> DataFrame:

        '''
            [...]
        
                ReadYear	StreetPrice
            0	2016	    34.95
            1	2016	    34.99
            ...

                ReadYear	StreetPrice
            0	2016	    1447.14
            1	2017	    2123.36
            ...

                2016	2017	2018	2019	2020	2021	2022	2023
            0	1447.14	2123.36	1249.15	748.7	538.75	169.92	49.99	5.0

                2016	↕0	2017	↕1	2018	↕2	2019	↕3	2020	↕4	2021	↕5	2022	↕6	2023
            0	1447.14	↑	2123.36	↓	1249.15	↓	748.7	↓	538.75	↓	169.92	↓	49.99	↓	5.0

                2016	↕	2017	↕	2018	↕	2019	↕	2020	↕	2021	↕	2022	↕	2023
            0	1447.14	↑	2123.36	↓	1249.15	↓	748.7	↓	538.75	↓	169.92	↓	49.99	↓	5.0        

                2016	    ↕	2017	    ↕	2018	    ↕	2019	↕	2020	↕	2021	↕	2022	↕	2023
            0	$1447.14	↑	$2123.36	↓	$1249.15	↓	$748.70	↓	$538.75	↓	$169.92	↓	$49.99	↓	$5.00
        '''

        sas_by_street_price_df : DataFrame = rl_df.copy(deep=True)

        cn_readyear : str = "ReadYear"
        cn_streetprice : str = "StreetPrice"

        condition : Series = (sas_by_street_price_df[cn_readyear].isin(read_years))
        sas_by_street_price_df = sas_by_street_price_df.loc[condition]
        sas_by_street_price_df = sas_by_street_price_df[[cn_readyear, cn_streetprice]]

        sas_by_street_price_df = sas_by_street_price_df.groupby([cn_readyear])[cn_streetprice].sum().sort_values(ascending = [False]).reset_index(name = cn_streetprice)
        sas_by_street_price_df = sas_by_street_price_df.sort_values(by = cn_readyear, ascending = [True])
        sas_by_street_price_df = sas_by_street_price_df.reset_index(drop = True)

        sas_by_street_price_df = sas_by_street_price_df.set_index(cn_readyear).transpose()
        sas_by_street_price_df.reset_index(drop = True, inplace = True)
        sas_by_street_price_df.rename_axis(None, axis = 1, inplace = True)
        sas_by_street_price_df.columns = sas_by_street_price_df.columns.astype(str)
        
        sas_by_street_price_df = self.__add_trend_to_sas_by_street_price(sas_by_street_price_df = sas_by_street_price_df, yeatrend = read_years)
        sas_by_street_price_df.rename(columns = (lambda x : self.__try_consolidate_trend_column_name(column_name = x)), inplace = True)

        new_column_names : list = [str(x) for x in read_years]
        for column_name in new_column_names:
            sas_by_street_price_df[column_name] = sas_by_street_price_df[column_name].apply(
                lambda x : self.__component_bag.formatter.format_usd_amount(
                    amount = float64(x), rounding_digits = rounding_digits))

        return sas_by_street_price_df
    def __filter_by_is_worth(self, sas_by_publisher_df : DataFrame) -> DataFrame:

        '''
                Publisher	Books	AvgRating	IsWorth
            0	Syncfusion	38	    2.55	    Yes
            1	Wiley	    9	    2.78	    Yes
            ... ...         ...     ...
        '''

        filtered_df : DataFrame = sas_by_publisher_df.copy(deep = True)

        cn_isworth : str = "IsWorth"
        condition : Series = (filtered_df[cn_isworth] == self.__setting_bag.is_worth_criteria)
        filtered_df = filtered_df.loc[condition]
        
        filtered_df.reset_index(drop = True, inplace = True)

        return filtered_df

    def get_rl(self) -> DataFrame:
        
        '''Retrieves the content of the "Books" tab and returns it as a Dataframe.'''

        rl_df = pd.read_excel(
            io = self.__setting_bag.excel_path, 	
            skiprows = self.__setting_bag.excel_books_skiprows,
            nrows = self.__setting_bag.excel_books_nrows,
            sheet_name = self.__setting_bag.excel_books_tabname, 
            engine = 'openpyxl'
            )
        
        rl_df = self.__enforce_dataframe_definition_for_rl_df(
            rl_df = rl_df, 
            excel_null_value = self.__setting_bag.excel_null_value)

        return rl_df
    def get_rl_asrt(self, rl_df : DataFrame) -> DataFrame:

        '''
                Years	Books	Pages	TotalSpend  LastUpdate
            0	8	    234	    62648	$6332.01    2023-09-23
        '''

        cn_read_year : str = "ReadYear"
        count_years : int = rl_df[cn_read_year].unique().size

        cn_title : str = "Title"
        count_books : int = rl_df[cn_title].size

        cn_pages : str = "Pages"
        sum_pages : int = rl_df[cn_pages].sum()

        cn_street_price : str = "StreetPrice"
        sum_street_price : float64 = rl_df[cn_street_price].sum()

        cn_years : str = "Years"
        cn_books : str = "Books"
        cn_total_spend : str = "TotalSpend"
        cn_last_update : str = "LastUpdate"

        total_spend_str : str = self.__component_bag.formatter.format_usd_amount(
            amount = sum_street_price, 
            rounding_digits = self.__setting_bag.rounding_digits)
        
        last_update_str : str = self.__component_bag.formatter.format_to_iso_8601(dt = self.__setting_bag.now)

        rl_asrt_dict : dict = {
            f"{cn_years}": f"{str(count_years)}",
            f"{cn_books}": f"{str(count_books)}",
            f"{cn_pages}": f"{str(sum_pages)}",
            f"{cn_total_spend}": f"{total_spend_str}",
            f"{cn_last_update}": f"{last_update_str}"
            }

        rl_asrt_df : DataFrame = pd.DataFrame(rl_asrt_dict, index=[0])
        
        return rl_asrt_df        
    def get_rl_by_kbsize(self, rl_df : DataFrame) -> DataFrame:
        
        '''
            Title	ReadYear	                                    Topic	Publisher	                            Rating	KBSize	A4Sheets
            1	    Machine Learning For Dummies	                2017	Data Analysis, Data Science, ML	Wiley	4	    3732	8
            2	    Machine Learning Projects for .NET Developers	2017	Data Analysis, Data Science, ML	Apress	4	    3272	7        
            ...
        '''

        rl_by_kbsize_df : DataFrame = self.__slice_by_kbsize(
            rl_df = rl_df, 
            ascending = self.__setting_bag.kbsize_ascending, 
            remove_if_zero = self.__setting_bag.kbsize_remove_if_zero)
        
        rl_by_kbsize_df = self.__component_bag.converter.convert_index_to_one_based(df = rl_by_kbsize_df)
        rl_by_kbsize_df = rl_by_kbsize_df.head(n = self.__setting_bag.n_by_kbsize)

        return rl_by_kbsize_df   
    def get_sas_by_month_tpl(self, rl_df : DataFrame) -> Tuple[DataFrame, DataFrame]:

        '''
            The method returns a tuple of dataframes (sas_by_month_df, sas_by_month_upd_df), 
            where the first item contains the pristine dataset while the second one has all 
            the future reading statuses replaced with empty strings ("0 (0)" => "") according 
            to setting_bag.now.

            Example:

                    Month	2016	↕1	2017	    ↕2	2018
                0	1	    0 (0)	↑	13 (5157)	↓	0 (0)
                1	2	    0 (0)	↑	1 (106)	    ↓	0 (0)
                ...

                    Month	2016	↕   2017	    ↕	2018
                0	1	    0 (0)	↑	13 (5157)	↓	0 (0)
                1	2	    0 (0)	↑	1 (106)	    ↓	0 (0)
                ...
        '''

        sas_by_month_df : DataFrame = pd.DataFrame()
        read_years : list[int] = self.__setting_bag.read_years
        add_trend : bool = True

        for i in range(len(read_years)):

            if i == 0:
                sas_by_month_df = self.__get_sa_by_year(rl_df = rl_df, read_year = read_years[i])
            else:
                sas_by_month_df = self.__expand_sa_by_year(
                    rl_df = rl_df, 
                    read_years = read_years, 
                    sas_by_month_df = sas_by_month_df, 
                    i = i, 
                    add_trend = add_trend)

        sas_by_month_df.rename(
            columns = (lambda x : self.__try_consolidate_trend_column_name(column_name = x)), 
            inplace = True)
        
        sas_by_month_upd_df : DataFrame = self.__update_future_rs_to_empty(
            sas_by_month_df = sas_by_month_df, 
            now = self.__setting_bag.now)

        return (sas_by_month_df, sas_by_month_upd_df)
    def get_sas_by_year_street_price(self, sas_by_month_tpl : Tuple[DataFrame, DataFrame], rl_df : DataFrame) -> DataFrame:

        '''
                2016	    ↕	2017	    ↕	2018	    ↕	2019	    ↕	2020	    ↕	2021	    ↕	2022	↕	2023
            0	43 (12322)	↑	63 (18726)	↓	48 (12646)	↓	42 (9952)	↓	23 (6602)	↓	13 (1901)	↓	1 (360)	=	1 (139)
            1	$1447.14	↑	$2123.36	↓	$1249.15	↓	$748.70	    ↓	$538.75	    ↓	$169.92	    ↓	$49.99	↓	$5.00
        '''

        sas_by_year_df : DataFrame = self.__get_sas_by_year(sas_by_month_df = sas_by_month_tpl[0])
        sas_by_street_price_df : DataFrame = self.__get_sas_by_street_price(
            rl_df = rl_df, 
            read_years = self.__setting_bag.read_years,
            rounding_digits = self.__setting_bag.rounding_digits)

        sas_by_year_street_price_df : DataFrame = pd.concat(objs = [sas_by_year_df, sas_by_street_price_df])
        sas_by_year_street_price_df.reset_index(drop = True, inplace = True)

        return sas_by_year_street_price_df      
    def get_sas_by_topic(self, rl_df : DataFrame) -> DataFrame:

        """
            by_books_df:

                    Topic	                Books
                0   Software Engineering	61
                1   C#	                    50
                ... ...                     ...

            by_pages_df:

                    Topic	                Pages
                0	Software Engineering	16776
                1	C#	                    15772
                ... ...                     ...

            sas_by_topic_df:
            
                    Topic	                Books	Pages
                0	Software Engineering	61	    16776
                1	C#	                    50	    15772
                ... ...                     ...     ...     
        """

        cn_topic : str = "Topic"  
        cn_books : str = "Books"
        by_books_df : DataFrame = rl_df.groupby([cn_topic]).size().sort_values(ascending = False).reset_index(name = cn_books)

        cn_pages = "Pages"
        by_pages_df : DataFrame = rl_df.groupby([cn_topic])[cn_pages].sum().sort_values(ascending = False).reset_index(name = cn_pages)

        sas_by_topic_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_pages_df, 
            how = "inner", 
            left_on = cn_topic, 
            right_on = cn_topic)

        return sas_by_topic_df
    def get_sas_by_publisher_tpl(self, rl_df : DataFrame) -> Tuple[DataFrame, DataFrame]:
        
        """
            The method returns a tuple of dataframes (sas_by_publisher_df, sas_by_publisher_flt_df), 
            where the first item contains the full dataset while the second one only the rows filtered 
            by setting_bag.is_worth_criteria.

            Example:

                by_books_df:

                        Publisher	Books
                    0	Syncfusion	38
                    1	O'Reilly	34
                    ... ...         ...

                by_avgrating_df:

                        Publisher	        AvgRating
                    0	Maker Media, Inc	4.00
                    1	Manning	            3.11
                    ... ...                 ...

                sas_by_publisher_df:

                        Publisher	Books	AvgRating	IsWorth
                    0	Syncfusion	38	    2.55	    Yes
                    1	O'Reilly	34	    2.18	    No
                    ... ...         ...     ...         ...

            IsWorth criteria example: "Yes" if AvgRating >= 2.50 && Books >= 8
        """

        cn_publisher : str = "Publisher"
        cn_title : str = "Title"    
        cn_books : str = "Books"
        by_books_df : DataFrame = rl_df.groupby([cn_publisher])[cn_title].size().sort_values(ascending = [False]).reset_index(name = cn_books)
        
        cn_rating : str = "Rating"   
        cn_avgrating : str = "AvgRating"
        by_avgrating_df : DataFrame = rl_df.groupby([cn_publisher])[cn_rating].mean().sort_values(ascending = [False]).reset_index(name = cn_avgrating)
        by_avgrating_df[cn_avgrating] = by_avgrating_df[cn_avgrating].apply(
            lambda x : round(number = x, ndigits = self.__setting_bag.rounding_digits)) # 2.5671 => 2.57

        sas_by_publisher_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_avgrating_df, 
            how = "inner", 
            left_on = cn_publisher, 
            right_on = cn_publisher)

        cn_isworth : str = "IsWorth"
        sas_by_publisher_df[cn_isworth] = np.where(
            (sas_by_publisher_df[cn_books] >= self.__setting_bag.is_worth_min_books) & 
            (sas_by_publisher_df[cn_avgrating] >= self.__setting_bag.is_worth_min_avgrating), 
            "Yes", "No")

        sas_by_publisher_flt_df : DataFrame = self.__filter_by_is_worth(sas_by_publisher_df = sas_by_publisher_df)

        return (sas_by_publisher_df, sas_by_publisher_flt_df)       
    def get_sas_by_rating(self, rl_df : DataFrame) -> DataFrame:

        '''
                Rating  Books
            0	★★★★★  9
            1	★★★★☆  18
            ...
        '''

        cn_rating : str = "Rating"

        sas_by_rating_df : DataFrame = self.__group_books_by_single_column(rl_df = rl_df, column_name = cn_rating)
        sas_by_rating_df.sort_values(by = cn_rating, ascending = False, inplace = True)
        sas_by_rating_df.reset_index(drop = True, inplace = True)

        if self.__setting_bag.formatted_rating:
            sas_by_rating_df[cn_rating] = sas_by_rating_df[cn_rating].apply(
                lambda x : self.__component_bag.formatter.format_rating(rating = x))

        return sas_by_rating_df    
    def get_trend_by_year_topic(self, rl_df : DataFrame) -> DataFrame:

        '''
            Get trend by year and topic as numbers and sparklines.

                Topic	                        Books	                    Trend
            0	BI, Data Warehousing, PowerBI	[0, 1, 9, 11, 0, 0, 0, 0]	▁▂▇█▁▁▁▁
            1	C#	                            [10, 14, 4, 17, 8, 3, 0, 0]	▅▇▃█▄▂▁▁ 
            ...          
        '''

        cn_topic : str = "Topic"
        cn_books : str = "Books"
        cn_trend : str = "Trend"

        by_topic_read_year_df : DataFrame = self.__get_books_by_topic_read_year(
            rl_df = rl_df, 
            read_years = self.__setting_bag.read_years)
        
        pivoted_df : DataFrame = self.__pivot_column_values_to_cell(
            df = by_topic_read_year_df, 
            cn_index = cn_topic, 
            cn_values = cn_books)

        if self.__setting_bag.enable_sparklines_maximum:
            maximum : int = by_topic_read_year_df[cn_books].max()
            return self.__add_sparklines(df = pivoted_df, cn_values = cn_books, cn_sparklines = cn_trend, maximum = maximum)
        else: 
            return self.__add_sparklines(df = pivoted_df, cn_values = cn_books, cn_sparklines = cn_trend)
class MarkdownProcessor():

    '''Collects all the logic related to the processing of Markdown content.'''

    __component_bag : ComponentBag
    __setting_bag : SettingBag    

    def __init__(self, component_bag : ComponentBag, setting_bag : SettingBag) -> None:

        self.__component_bag = component_bag
        self.__setting_bag = setting_bag

    def __get_rl_asrt_md(self, rl_asrt_df : DataFrame) -> str:

        '''Creates the Markdown content for a README file out of the provided dataframe.'''

        rl_asrt_md : str = rl_asrt_df.to_markdown(index = False)

        md_content : str = rl_asrt_md
        md_content += "\n"

        return md_content
    def __get_rl_by_month_md(self, last_update : datetime, sas_by_month_df : DataFrame, sas_by_year_street_price_df : DataFrame, use_smaller_font : bool) -> str:

        '''Creates the Markdown content for a "Reading List By Month" file out of the provided dataframes.'''

        copy_of_sas_by_month_df : DataFrame = sas_by_month_df.copy(deep=True)
        copy_of_sas_by_year_street_price_df : DataFrame = sas_by_year_street_price_df.copy(deep=True)

        if use_smaller_font:
            copy_of_sas_by_month_df = self.__component_bag.markdown_helper.add_subscript_tags_to_dataframe(df = copy_of_sas_by_month_df)
            copy_of_sas_by_year_street_price_df = self.__component_bag.markdown_helper.add_subscript_tags_to_dataframe(df = copy_of_sas_by_year_street_price_df)

        md_paragraph_title : str = "Reading List By Month"

        markdown_header : str = self.__component_bag.markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        sas_by_month_md : str = copy_of_sas_by_month_df.to_markdown(index = False)
        sas_by_year_street_price_md  : str = copy_of_sas_by_year_street_price_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += sas_by_month_md
        md_content += "\n"
        md_content += ""
        md_content += "\n"
        md_content += sas_by_year_street_price_md
        md_content += "\n"
        md_content += ""

        return md_content
    def __get_rl_by_publisher_md(self, last_update : datetime, sas_by_publisher_tpl : Tuple[DataFrame, DataFrame]) -> str:

        '''Creates the Markdown content for a "Reading List By Publisher" file out of the provided dataframes.'''

        md_paragraph_title : str = "Reading List By Publisher"

        markdown_header : str = self.__component_bag.markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        sas_by_publisher_flt_md : str = sas_by_publisher_tpl[1].to_markdown(index = False)
        sas_by_publisher_md : str = sas_by_publisher_tpl[0].to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += sas_by_publisher_flt_md
        md_content += "\n"
        md_content += ""
        md_content += "\n"
        md_content += sas_by_publisher_md
        md_content += "\n"
        md_content += ""

        return md_content
    def __get_rl_by_rating_md(self, last_update : datetime, sas_by_rating_df : DataFrame) -> str:

        '''Creates the Markdown content for a "Reading List By Rating" file out of the provided dataframe.'''

        md_paragraph_title : str = "Reading List By Rating"

        markdown_header : str = self.__component_bag.markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        sas_by_rating_md : str = sas_by_rating_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += sas_by_rating_md
        md_content += "\n"

        return md_content
    def __get_rl_by_topic_md(self, last_update : datetime, sas_by_topic_df : DataFrame) -> str:

        '''Creates the Markdown content for a "Reading List By Topic" file out of the provided dataframe.'''

        md_paragraph_title : str = "Reading List By Topic"

        markdown_header : str = self.__component_bag.markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        sas_by_topic_md : str = sas_by_topic_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += sas_by_topic_md
        md_content += "\n"

        return md_content
    def __get_rl_md(self, last_update : datetime, rl_df : DataFrame, use_smaller_font : bool) -> str:

        '''Creates the Markdown content for a "Reading List" file out of the provided dataframe.'''

        md_paragraph_title : str = "Reading List"

        markdown_header : str = self.__component_bag.markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        formatted_rl_df : DataFrame = self.__get_formatted_rl(rl_df = rl_df)

        if use_smaller_font:
            formatted_rl_df = self.__component_bag.markdown_helper.add_subscript_tags_to_dataframe(df = formatted_rl_df)    

        formatted_rl_md : str = formatted_rl_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += formatted_rl_md
        md_content += "\n"

        return md_content
    def __get_rl_topic_trend_md(self, last_update : datetime, yt_by_topic_df : DataFrame) -> str:

        '''Creates the Markdown content for a "Reading List Topic Trend" file out of the provided dataframe.'''

        md_paragraph_title : str = "Reading List Topic Trend"

        markdown_header : str = self.__component_bag.markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        yt_by_topic_md : str = yt_by_topic_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += yt_by_topic_md
        md_content += "\n"

        return md_content
    def __get_formatted_rl(self, rl_df : DataFrame) -> DataFrame:

        '''
                Id	    Title	            Year	Pages	ReadDate	Publisher	    Rating    Topic
            0	0	    Writing Solid Code	1993	288	    2016-05-28	Microsoft Press	★★☆☆☆  Software Engineering
            1	1	    Git Essentials	    2015	168	    2016-06-05	Packt	        ★★☆☆☆  Git
            ...    
        '''

        formatted_rl_df : DataFrame = pd.DataFrame()

        cn_id : str = "Id"
        cn_title : str = "Title"
        cn_year : str = "Year"
        cn_language : str = "Language"
        cn_pages : str = "Pages"
        cn_read_date : str = "ReadDate"
        cn_publisher : str = "Publisher"
        cn_rating : str = "Rating"
        cn_topic : str = "Topic"

        formatted_rl_df[cn_id] = rl_df.index + 1
        formatted_rl_df[cn_title] = rl_df[cn_title]
        formatted_rl_df[cn_year] = rl_df[cn_year]
        formatted_rl_df[cn_language] = rl_df[cn_language]
        formatted_rl_df[cn_pages] = rl_df[cn_pages]
        formatted_rl_df[cn_read_date] = rl_df[cn_read_date]   
        formatted_rl_df[cn_publisher] = rl_df[cn_publisher]   
        formatted_rl_df[cn_rating] = rl_df[cn_rating].apply(lambda x : self.__component_bag.formatter.format_rating(rating = x))
        formatted_rl_df[cn_topic] = rl_df[cn_topic]   

        return formatted_rl_df

    def process_rl_asrt_md(self, rl_asrt_df : DataFrame) -> None:

        '''Performs all the tasks related to the README file.'''

        content : str = self.__get_rl_asrt_md(rl_asrt_df = rl_asrt_df)

        if self.__setting_bag.show_rl_asrt_md:
            self.__component_bag.logging_function(content)
    def process_rl_by_month_md(self, sas_by_month_tpl : Tuple[DataFrame, DataFrame], sas_by_year_street_price_df : DataFrame) -> None:

        '''Performs all the tasks related to the "Reading List By Month" file.''' 

        content : str = self.__get_rl_by_month_md(      
            last_update = self.__setting_bag.rl_last_update, 
            sas_by_month_df = sas_by_month_tpl[0], 
            sas_by_year_street_price_df = sas_by_year_street_price_df,
            use_smaller_font = self.__setting_bag.rl_by_month_smaller_font)

        if self.__setting_bag.show_rl_by_month_md:
            file_name_content : str = self.__component_bag.markdown_helper.format_file_name_as_content(file_name = self.__setting_bag.rl_by_month_file_name)
            self.__component_bag.logging_function(file_name_content)    
            self.__component_bag.logging_function(content)

        if self.__setting_bag.save_rl_by_month_md:
            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = self.__setting_bag.working_folder_path,
                file_name = self.__setting_bag.rl_by_month_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_rl_by_publisher_md(self, sas_by_publisher_tpl : Tuple[DataFrame, DataFrame]) -> None:

        '''Performs all the tasks related to the "Reading List By Publisher" file.'''

        content : str = self.__get_rl_by_publisher_md(      
            last_update = self.__setting_bag.rl_last_update, 
            sas_by_publisher_tpl = sas_by_publisher_tpl)

        if self.__setting_bag.show_rl_by_publisher_md:
            file_name_content : str = self.__component_bag.markdown_helper.format_file_name_as_content(file_name = self.__setting_bag.rl_by_publisher_file_name)
            self.__component_bag.logging_function(file_name_content)        
            self.__component_bag.logging_function(content)

        if self.__setting_bag.save_rl_by_publisher_md:
            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = self.__setting_bag.working_folder_path,
                file_name = self.__setting_bag.rl_by_publisher_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_rl_by_rating_md(self, sas_by_rating_df : DataFrame) -> None:

        '''Performs all the tasks related to the "Reading List By Rating" file.'''

        content : str = self.__get_rl_by_rating_md(       
            last_update = self.__setting_bag.rl_last_update, 
            sas_by_rating_df = sas_by_rating_df)

        if self.__setting_bag.show_rl_by_rating_md:
            file_name_content : str = self.__component_bag.markdown_helper.format_file_name_as_content(file_name = self.__setting_bag.rl_by_rating_file_name)
            self.__component_bag.logging_function(file_name_content)
            self.__component_bag.logging_function(content)

        if self.__setting_bag.save_rl_by_rating_md:            
            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = self.__setting_bag.working_folder_path,
                file_name = self.__setting_bag.rl_by_rating_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_rl_by_topic_md(self, sas_by_topic_df : DataFrame) -> None:

        '''Performs all the tasks related to the "Reading List By Topic" file.'''

        content : str = self.__get_rl_by_topic_md( 
            last_update = self.__setting_bag.rl_last_update, 
            sas_by_topic_df = sas_by_topic_df)

        if self.__setting_bag.show_rl_by_topic_md:
            file_name_content : str = self.__component_bag.markdown_helper.format_file_name_as_content(file_name = self.__setting_bag.rl_by_topic_file_name)
            self.__component_bag.logging_function(file_name_content)
            self.__component_bag.logging_function(content)

        if self.__setting_bag.save_rl_by_topic_md:
            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = self.__setting_bag.working_folder_path,
                file_name = self.__setting_bag.rl_by_topic_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_rl_by_topic_trend_md(self, yt_by_topic_df : DataFrame) -> None:

        '''Performs all the tasks related to the "Reading List Topic Trend" file.'''

        content : str = self.__get_rl_topic_trend_md(
            last_update = self.__setting_bag.rl_last_update, 
            yt_by_topic_df = yt_by_topic_df)

        if self.__setting_bag.show_rl_topic_trend_md:
            file_name_content : str = self.__component_bag.markdown_helper.format_file_name_as_content(file_name = self.__setting_bag.rl_topic_trend_file_name)           
            self.__component_bag.logging_function(file_name_content)
            self.__component_bag.logging_function(content)

        if self.__setting_bag.save_rl_topic_trend_md:           
            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = self.__setting_bag.working_folder_path,
                file_name = self.__setting_bag.rl_topic_trend_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_rl_md(self, rl_df : DataFrame) -> None:

        '''Performs all the tasks related to the "Reading List" file.'''

        content : str = self.__get_rl_md(
            last_update = self.__setting_bag.rl_last_update, 
            rl_df = rl_df,
            use_smaller_font = self.__setting_bag.rl_smaller_font)

        if self.__setting_bag.show_rl_md:
            file_name_content : str = self.__component_bag.markdown_helper.format_file_name_as_content(file_name = self.__setting_bag.rl_file_name)
            self.__component_bag.logging_function(file_name_content)
            self.__component_bag.logging_function(content)

        if self.__setting_bag.save_rl_md:
            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = self.__setting_bag.working_folder_path,
                file_name = self.__setting_bag.rl_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)

# MAIN
if __name__ == "__main__":
    pass