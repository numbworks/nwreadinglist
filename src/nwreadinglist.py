'''
A collection of components to handle "Reading List.xlsx".

Alias: nwrl
'''

# GLOBAL MODULES
import copy
import numpy as np
import os
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum, auto
from numpy import float64
from pandas import DataFrame
from pandas import Series
from sparklines import sparklines
from typing import Any, Callable, Literal, Optional, Tuple

# LOCAL/NW MODULES
from nwshared import Formatter, Converter, FilePathManager, FileManager
from nwshared import LambdaProvider, MarkdownHelper, Displayer, PlotManager

# CONSTANTS
class RLCN(StrEnum):
    
    '''Collects all the column names used by RLDataFrameFactory.'''
    
    TITLE = "Title"
    YEAR = "Year"
    TYPE = "Type"
    FORMAT = "Format"
    LANGUAGE = "Language"
    PAGES = "Pages"
    READDATE = "ReadDate"
    READYEAR = "ReadYear"
    READMONTH = "ReadMonth"
    WORTHBUYING = "WorthBuying"
    WORTHREADINGAGAIN = "WorthReadingAgain"
    PUBLISHER = "Publisher"
    RATING = "Rating"
    STREETPRICE = "StreetPrice"
    CURRENCY = "Currency"
    COMMENT = "Comment"
    TOPIC = "Topic"
    ONGOODREADS = "OnGoodreads"
    COMMENTLENGHT = "CommentLenght"
    KBSIZE = "KBSize"
    BOOKS = "Books"
    A4SHEETS = "A4Sheets"
    ABPERC = "AB%"
    AVGRATING = "AvgRating"
    ISWORTH = "IsWorth"
    YEARS = "Years"
    TOTALSPEND = "TotalSpend"
    LASTUPDATE = "LastUpdate"
    MONTH = "Month"
    TREND = "Trend"
    TRENDSYMBOL = "↕"    
class RLID(StrEnum):
    
    '''Collects all the ids that identify the dataframes created by RLDataFrameFactory.'''

    RL = "rl"
    RLSBYMONTH = "rls_by_month"
    RLSBYPUBLISHER = "rls_by_publisher"
    RLSBYRATING = "rls_by_rating"
    RLSBYTOPIC = "rls_by_topic"
class OPTION(StrEnum):

    '''Represents a collection of options.'''

    display = auto()
    display_c = auto()
    save = auto()
    plot = auto()
    logdef = auto()
    logterm = auto()
    logset = auto()

# STATIC CLASSES
class _MessageCollection():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def no_mdinfo_found(id : RLID) -> str:
        return f"No MDInfo object found for id='{id}'."
    @staticmethod
    def please_run_initialize_first() -> str:
        return "Please run the 'initialize' method first."

    @staticmethod
    def this_content_successfully_saved_as(id : RLID, file_path : str) -> str:
        return f"This content (id: '{id}') has been successfully saved as '{file_path}'."

# DTOs
@dataclass(frozen=True)
class MDInfo():

    '''Represents a collection of information related to a Markdown file.'''

    id : RLID
    file_name : str
    paragraph_title : str
@dataclass(frozen=True)
class RLSummary():

    '''Collects all the dataframes and markdowns.'''

    rl_df : DataFrame
    rls_asrt_df : DataFrame
    rls_by_month_tpl : Tuple[DataFrame, DataFrame]
    rls_by_kbsize_df : DataFrame
    rls_by_publisher_tpl : Tuple[DataFrame, DataFrame, str]
    rls_by_rating_df : DataFrame
    rls_by_topic_df : DataFrame
    rls_by_topic_bt_df : DataFrame
    rls_by_year_street_price_df : DataFrame
    definitions_df : DataFrame

    rl_md : str
    rls_asrt_md : str
    rls_by_month_md : str
    rls_by_publisher_md : str
    rls_by_rating_md : str
    rls_by_topic_md : str

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

        years : list[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

        return years
class MDInfoProvider():

    '''Collects all the logic related to the retrieval of MDInfo objects.'''

    def get_all(self) -> list[MDInfo]:

        '''Returns a list of MDInfo objects.'''

        md_infos : list[MDInfo] = [
                MDInfo(id = RLID.RL, file_name = "READINGLIST.md", paragraph_title = "Reading List"),
                MDInfo(id = RLID.RLSBYMONTH, file_name = "READINGLISTBYMONTH.md", paragraph_title = "Reading List By Month"),
                MDInfo(id = RLID.RLSBYPUBLISHER, file_name = "READINGLISTBYPUBLISHER.md", paragraph_title = "Reading List By Publisher"),
                MDInfo(id = RLID.RLSBYRATING, file_name = "READINGLISTBYRATING.md", paragraph_title = "Reading List By Rating"),
                MDInfo(id = RLID.RLSBYTOPIC, file_name = "READINGLISTBYTOPIC.md", paragraph_title = "Reading List By Topic")
            ]
        
        return md_infos
@dataclass(frozen=True)
class SettingBag():

    '''Represents a collection of settings.'''

	# Without Defaults
    options_rl : list[Literal[OPTION.display, OPTION.save]]
    options_rls_asrt : list[Literal[OPTION.display, OPTION.logset]]
    options_rls_by_books_year : list[Literal[OPTION.plot]]
    options_rls_by_kbsize : list[Literal[OPTION.display, OPTION.plot]]
    options_rls_by_month : list[Literal[OPTION.display, OPTION.save]]
    options_rls_by_publisher : list[Literal[OPTION.display, OPTION.logset, OPTION.save]]
    options_rls_by_rating : list[Literal[OPTION.display, OPTION.save]]
    options_rls_by_topic : list[Literal[OPTION.display, OPTION.save]]
    options_rls_by_topic_bt : list[Literal[OPTION.display, OPTION.save]]
    options_definitions : list[Literal[OPTION.display]]
    read_years : list[int]
    excel_path : str
    excel_nrows : int
	
	# With Defaults
    excel_skiprows : int = field(default = 0)
    excel_tabname : str = field(default = "Books")
    excel_null_value : str = field(default = "-")
    working_folder_path : str = field(default = "/home/nwreadinglist/")
    rounding_digits : int = field(default = 2)
    now : datetime = field(default = datetime.now())
    rls_by_kbsize_n : int = field(default = 10)
    rls_by_kbsize_ascending : bool = field(default = False)
    rls_by_kbsize_remove_if_zero : bool = field(default = True)
    rls_by_publisher_n : int = field(default = 10)
    rls_by_publisher_formatters : dict = field(default_factory = lambda : { "AvgRating" : "{:.2f}", "AB%" : "{:.2f}" })
    rls_by_publisher_min_books : int = field(default = 8)
    rls_by_publisher_min_ab_perc : float = field(default = 100)
    rls_by_publisher_min_avgrating : float = field(default = 2.50)
    rls_by_publisher_criteria : Literal["Yes", "No"] = field(default = "Yes")    
    rls_by_rating_number_as_stars : bool = field(default = True)
    rls_by_topic_bt_sparklines_maximum : bool = field(default = False)    
    md_last_update : datetime = field(default = datetime.now())
    md_infos : list[MDInfo] = field(default_factory = lambda : MDInfoProvider().get_all())
class RLDataFrameHelper():

    '''Collects helper functions for RLDataFrameFactory.'''

    def format_reading_status(self, books : int, pages : int) -> str:

        '''
            13, 5157 => "13 (5157)"
        '''
        
        reading_status : str = f"{books} ({pages})"
        
        return reading_status
    def get_default_sa_by_year(self, read_year : int) -> DataFrame:

        '''
            default_df:

                    Month	2017
                0	1	    0 (0)
                1	2	    0 (0)
                ... ...     ...    
        '''
  
        default_df : DataFrame = pd.DataFrame(
            {
                f"{RLCN.MONTH}": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                f"{str(read_year)}": ["0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)"]
            },
            index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        )

        default_df = default_df.astype({RLCN.MONTH: int})
        default_df = default_df.astype({str(read_year): str})

        return default_df
    def extract_books_from_trend(self, trend : str) -> int:

        '''
            "13 (5157)" => ["13", "(5157)"] => "13" => 13
        '''

        tokens : list = trend.split(" ")

        return int(tokens[0])
    def get_trend(self, value_1 : int, value_2 : int) -> str:

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
    def get_trend_by_books(self, trend_1 : str, trend_2 : str) -> str:

        '''
            "13 (5157)", "16 (3816)" => "↑"
            "16 (3816)", "13 (5157)" => "↓"
            "0 (0)", "0 (0)" => "="   
        '''

        books_1 : int = self.extract_books_from_trend(trend = trend_1)
        books_2 : int = self.extract_books_from_trend(trend = trend_2)

        trend : str = self.get_trend(value_1 = books_1, value_2 = books_2)

        return trend
    def try_consolidate_trend_column_name(self, column_name : str) -> str:

        '''
            "2016"  => "2016"
            "↕1"    => "↕"
        '''

        if column_name.startswith(RLCN.TRENDSYMBOL):
            return RLCN.TRENDSYMBOL
        
        return column_name
    def extract_pages_from_trend(self, trend : str) -> int:

        '''
            "13 (5157)" => ["13", "(5157)"] => "5157" => 5157
        '''

        tokens : list = trend.split(" ")
        token : str = tokens[1].replace("(", "").replace(")", "")

        return int(token)
    def format_year_books_column_name(self, year_cn : str) -> str:

        '''
            "2016" => "2016_Books"
        '''

        column_name : str = f"{year_cn}_Books"

        return column_name
    def format_year_pages_column_name(self, year_cn : str) -> str:

        '''
            "2016" => "2016_Pages"
        '''

        column_name : str = f"{year_cn}_Pages"

        return column_name
    def extract_year_from_column_name(self, column_name : str) -> str:

        '''
            "2016_Books" => "2016"
            "2016_Pages" => "2016"        
        '''

        tokens : list = column_name.split("_")

        return tokens[0]
    def get_trend_when_float64(self, value_1 : float64, value_2 : float64) -> str:

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
    def create_read_years_dataframe(self, read_years : list[int]) -> DataFrame:

        '''Create a dataframe out of the provided list of Read Years.'''

        read_years_df : DataFrame = pd.DataFrame(data = read_years, columns = [RLCN.READYEAR])

        return read_years_df
class RLDataFrameFactory():

    '''Collects all the logic related to dataframe creation out of "Reading List.xlsx".'''

    __converter : Converter
    __formatter : Formatter
    __df_helper : RLDataFrameHelper

    def __init__(
            self,
            converter : Converter,
            formatter : Formatter,
            df_helper : RLDataFrameHelper
        ) -> None:
        
        self.__converter = converter
        self.__formatter = formatter
        self.__df_helper = df_helper

    def __enforce_dataframe_definition_for_rl_df(self, rl_df : DataFrame, excel_null_value : str) -> DataFrame:

        '''Enforces definition for the provided dataframe.'''

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

        if sa_by_year_df[RLCN.MONTH].count() != 12:

            default_df : DataFrame = self.__df_helper.get_default_sa_by_year(read_year = read_year)
            missing_df : DataFrame = default_df.loc[~default_df[RLCN.MONTH].astype(str).isin(sa_by_year_df[RLCN.MONTH].astype(str))]

            completed_df : DataFrame = pd.concat([sa_by_year_df, missing_df], ignore_index = True)
            completed_df = completed_df.sort_values(by = RLCN.MONTH, ascending = [True])
            completed_df = completed_df.reset_index(drop = True)

            return completed_df

        return sa_by_year_df
    def __create_sa_by_year(self, rl_df : DataFrame, read_year : int) -> DataFrame:
        
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

        condition : Series = (rl_df[RLCN.READYEAR] == read_year)
        filtered_df : DataFrame = rl_df.loc[condition]

        by_books_df : DataFrame = filtered_df.groupby([RLCN.READMONTH])[RLCN.TITLE].size().sort_values(ascending = [False]).reset_index(name = RLCN.BOOKS)
        by_books_df = by_books_df.sort_values(by = RLCN.READMONTH).reset_index(drop = True)   
    
        by_pages_df : DataFrame = filtered_df.groupby([RLCN.READMONTH])[RLCN.PAGES].sum().sort_values(ascending = [False]).reset_index(name = RLCN.PAGES)
        by_pages_df = by_pages_df.sort_values(by = RLCN.READMONTH).reset_index(drop = True)

        sa_by_year_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_pages_df, 
            how = "inner", 
            left_on = RLCN.READMONTH, 
            right_on = RLCN.READMONTH)
        sa_by_year_df[read_year] = sa_by_year_df.apply(lambda x : self.__df_helper.format_reading_status(books = x[RLCN.BOOKS], pages = x[RLCN.PAGES]), axis = 1) 

        sa_by_year_df[RLCN.MONTH] = sa_by_year_df[RLCN.READMONTH]
        sa_by_year_df = sa_by_year_df[[RLCN.MONTH, read_year]]
        sa_by_year_df = sa_by_year_df.astype({RLCN.MONTH: int})
        sa_by_year_df = sa_by_year_df.astype({read_year: str})    
        sa_by_year_df.columns = sa_by_year_df.columns.astype(str) # 2016 => "2016"

        sa_by_year_df = self.__try_complete_sa_by_year(sa_by_year_df = sa_by_year_df, read_year = read_year)

        return sa_by_year_df
    def __expand_sa_by_year(self, rl_df : DataFrame, read_years : list, rls_by_month_df : DataFrame, i : int, add_trend : bool) -> DataFrame:

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
        
        actual_df : DataFrame = rls_by_month_df.copy(deep = True)
        sa_by_year_df : DataFrame = self.__create_sa_by_year(rl_df = rl_df, read_year = read_years[i])
    
        expansion_df = pd.merge(
            left = actual_df, 
            right = sa_by_year_df, 
            how = "inner", 
            left_on = RLCN.MONTH, 
            right_on = RLCN.MONTH)

        if add_trend == True:

            cn_trend : str = f"↕{i}"
            cn_trend_1 : str = str(read_years[i-1])   # for ex. "2016"
            cn_trend_2 : str = str(read_years[i])     # for ex. "2017"
            
            expansion_df[cn_trend] = expansion_df.apply(lambda x : self.__df_helper.get_trend_by_books(trend_1 = x[cn_trend_1], trend_2 = x[cn_trend_2]), axis = 1) 

            new_column_names : list = [RLCN.MONTH, cn_trend_1, cn_trend, cn_trend_2]   # for ex. ["Month", "2016", "↕", "2017"]
            expansion_df = expansion_df.reindex(columns = new_column_names)

            shared_columns : list = [RLCN.MONTH, str(read_years[i-1])] # ["Month", "2016"]
            actual_df = pd.merge(
                left = actual_df, 
                right = expansion_df, 
                how = "inner", 
                left_on = shared_columns, 
                right_on = shared_columns)

        else:
            actual_df = expansion_df

        return actual_df
    def __add_trend_to_rls_by_year(self, rls_by_year_df : DataFrame, yeatrend : list) -> DataFrame:

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

        expanded_df : DataFrame = rls_by_year_df.copy(deep=True)
        new_column_names : list = copy.deepcopy(x = yeatrend)

        for i in range(len(yeatrend)):

            if i != (len(yeatrend) - 1):

                cn_trend : str = f"↕{i}"
                cn_trend_1 : str = str(yeatrend[i])       # 2016 => "2016"
                cn_trend_2 : str = str(yeatrend[i+1])     # 2017 => "2017"
                
                expanded_df[cn_trend] = expanded_df.apply(lambda x : self.__df_helper.get_trend_by_books(trend_1 = x[cn_trend_1], trend_2 = x[cn_trend_2]), axis = 1) 
                
                new_item_position : int = (new_column_names.index(cn_trend_1) + 1)
                new_column_names.insert(new_item_position, cn_trend)

                expanded_df = expanded_df.reindex(columns = new_column_names)
                
        return expanded_df
    def __add_trend_to_rls_by_street_price(self, rls_by_street_price_df : DataFrame, yeatrend : list) -> DataFrame:

        '''
            [...]

            expanded_df:

                2016	↕0	2017	↕1	2018	↕2	2019	↕3	2020	↕4	2021	↕5	2022	↕6	2023
            0	1447.14	↑	2123.36	↓	1249.15	↓	748.7	↓	538.75	↓	169.92	↓	49.99	↓	5.0
        '''  

        expanded_df : DataFrame = rls_by_street_price_df.copy(deep=True)
        new_column_names : list = copy.deepcopy(x = yeatrend)
        new_column_names = [str(x) for x in new_column_names]

        for i in range(len(yeatrend)):

            if i != (len(yeatrend) - 1):

                cn_trend : str = f"↕{i}"
                cn_value_1 : str = str(yeatrend[i])       # 2016 => "2016"
                cn_value_2 : str = str(yeatrend[i+1])     # 2017 => "2017"
                
                expanded_df[cn_trend] = expanded_df.apply(lambda x : self.__df_helper.get_trend_when_float64(value_1 = x[cn_value_1], value_2 = x[cn_value_2]), axis = 1) 
                
                new_item_position : int = (new_column_names.index(cn_value_1) + 1)
                new_column_names.insert(new_item_position, cn_trend)

                expanded_df = expanded_df.reindex(columns = new_column_names)
                
        return expanded_df
    def __group_books_by_single_column(self, rl_df : DataFrame, column_name : str) -> DataFrame:

        '''Groups books according to the provided column name. The book titles act as unique identifiers.'''

        grouped_df : DataFrame = rl_df.groupby([column_name])[RLCN.TITLE].size().sort_values(ascending = [False]).reset_index(name = RLCN.BOOKS)
        
        return grouped_df
    def __group_books_by_multiple_columns(self, rl_df : DataFrame, column_names : list[str]) -> DataFrame:

        '''Groups books according to the provided column names (note: order matters). The book titles act as unique identifiers.'''

        grouped_df : DataFrame = rl_df.groupby(by = column_names)[RLCN.TITLE].count().reset_index(name = RLCN.BOOKS)
        grouped_df = grouped_df.sort_values(by = column_names, ascending = [True, True])

        return grouped_df
    def __add_a4sheets_column(self, df : DataFrame) -> DataFrame:

        '''
            ... KBSize
            ... 3732
            ... ...           

            ... KBSize  A4Sheets
            ... 3732    8
            ... ...     ...
        '''

        copied_df : DataFrame = df.copy(deep = True)

        copied_df[RLCN.A4SHEETS] = copied_df[RLCN.KBSIZE].apply(
            lambda x : self.__converter.convert_word_count_to_A4_sheets(word_count = x))

        return copied_df
    def __slice_by_kbsize(self, rl_df : DataFrame, ascending : bool, remove_if_zero : bool) -> DataFrame:

        '''
                Title	                                        ReadYear	Topic	                        Publisher	Rating	KBSize  A4Sheets
            0	Machine Learning For Dummies	                2017	    Data Analysis, Data Science, ML	Wiley	    4	    3732    8
            1	Machine Learning Projects for .NET Developers	2017	    Data Analysis, Data Science, ML	Apress	    4	    3272    7
            2	Producing Open Source Software	                2016	    Software Engineering	        O'Reilly	1	    2332    5
            ...
        '''

        sliced_df : DataFrame = rl_df.copy(deep=True)
        sliced_df = sliced_df[[RLCN.TITLE, RLCN.READYEAR, RLCN.TOPIC, RLCN.PUBLISHER, RLCN.RATING, RLCN.KBSIZE]]

        if remove_if_zero:
            condition : Series = (sliced_df[RLCN.KBSIZE] != 0)
            sliced_df = sliced_df.loc[condition]

        sliced_df = sliced_df.sort_values(by = RLCN.KBSIZE, ascending = ascending).reset_index(drop = True)   
        sliced_df = self.__add_a4sheets_column(df = sliced_df)

        return sliced_df    
    def __create_topics_dataframe(self, df : DataFrame) -> DataFrame:

        '''Creates a dataframe of unique topics out of the provided dataframe.'''

        topics_df : DataFrame = pd.DataFrame(data = df[RLCN.TOPIC].unique(), columns = [RLCN.TOPIC])
        
        return topics_df
    def __create_default_topic_read_year_dataframe(self, topics_df : DataFrame, read_years_df : DataFrame) -> DataFrame:

        '''
                Topic	                ReadYear
            0	Software Engineering	2016
            1	Software Engineering	2017
            ...
        '''

        default_df : DataFrame = pd.merge(left = topics_df, right = read_years_df, how='cross')

        return default_df
    def __create_books_by_topic_read_year(self, rl_df : DataFrame, read_years : list[int]) -> DataFrame:

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

        books_by_topic_read_year_df : DataFrame = self.__group_books_by_multiple_columns(rl_df = rl_df, column_names = [RLCN.TOPIC, RLCN.READYEAR])

        topics_df : DataFrame = self.__create_topics_dataframe(df = rl_df)
        read_years_df : DataFrame = self.__df_helper.create_read_years_dataframe(read_years = read_years)
        default_df : DataFrame = self.__create_default_topic_read_year_dataframe(topics_df = topics_df, read_years_df = read_years_df)

        completed_df : DataFrame = pd.merge(
            left = books_by_topic_read_year_df, 
            right = default_df,
            how = "outer")

        completed_df.sort_values(by = [RLCN.TOPIC, RLCN.READYEAR], ascending = [True, True], inplace = True)
        completed_df.reset_index(inplace = True, drop = True)
        completed_df.fillna(value = 0, inplace = True)
        completed_df = completed_df.astype({RLCN.BOOKS: int})

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
    def __update_future_rs_to_empty(self, rls_by_month_df : DataFrame, now : datetime) -> DataFrame:

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

        rls_by_month_upd_df : DataFrame = rls_by_month_df.copy(deep = True)

        now_year : int = now.year
        now_month : int = now.month	
        cn_year : str = str(now_year)
        new_value : str = ""

        condition : Series = (rls_by_month_upd_df[RLCN.MONTH] > now_month)
        rls_by_month_upd_df[cn_year] = np.where(condition, new_value, rls_by_month_upd_df[cn_year])
            
        idx_year : Any = rls_by_month_upd_df.columns.get_loc(cn_year)
        idx_trend : int = (idx_year - 1)
        rls_by_month_upd_df.iloc[:, idx_trend] = np.where(condition, new_value, rls_by_month_upd_df.iloc[:, idx_trend])

        return rls_by_month_upd_df       
    def __create_rls_by_year_df(self, rls_by_month_df : DataFrame) -> DataFrame:

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

        rls_by_year_df : DataFrame = rls_by_month_df.copy(deep = True)

        cn_month : str = "Month"
        cn_trend : str = "↕"
        rls_by_year_df.drop(labels = cn_month, inplace = True, axis = 1)
        rls_by_year_df.drop(labels = cn_trend, inplace = True, axis = 1)

        yeatrend : list = rls_by_year_df.columns.to_list()
        for year in yeatrend:

            cn_year_books : str = self.__df_helper.format_year_books_column_name(year_cn = year)
            cn_year_pages : str = self.__df_helper.format_year_pages_column_name(year_cn = year)

            rls_by_year_df[cn_year_books] = rls_by_year_df[year].apply(lambda x : self.__df_helper.extract_books_from_trend(trend = x))
            rls_by_year_df[cn_year_pages] = rls_by_year_df[year].apply(lambda x : self.__df_helper.extract_pages_from_trend(trend = x))

            rls_by_year_df.drop(labels = year, inplace = True, axis = 1)

        rls_by_year_df = rls_by_year_df.sum().to_frame().transpose()

        for year in yeatrend:

            cn_year_books = self.__df_helper.format_year_books_column_name(year_cn = year)
            cn_year_pages = self.__df_helper.format_year_pages_column_name(year_cn = year)

            rls_by_year_df[year] = rls_by_year_df.apply(lambda x : self.__df_helper.format_reading_status(books = x[cn_year_books], pages = x[cn_year_pages]), axis = 1) 

            rls_by_year_df.drop(labels = [cn_year_books, cn_year_pages], inplace = True, axis = 1)

        rls_by_year_df = self.__add_trend_to_rls_by_year(rls_by_year_df = rls_by_year_df, yeatrend = yeatrend)
        rls_by_year_df.rename(columns = (lambda x : self.__df_helper.try_consolidate_trend_column_name(column_name = x)), inplace = True)

        return rls_by_year_df
    def __create_rls_by_street_price_df(self, rl_df : DataFrame, read_years : list, rounding_digits : int) -> DataFrame:

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

            In the case there is a mismatch bewtween the actual and expected column, we create the missing ones with "0" as value.
        '''

        rls_by_street_price_df : DataFrame = rl_df.copy(deep=True)

        condition : Series = (rls_by_street_price_df[RLCN.READYEAR].isin(read_years))
        rls_by_street_price_df = rls_by_street_price_df.loc[condition]
        rls_by_street_price_df = rls_by_street_price_df[[RLCN.READYEAR, RLCN.STREETPRICE]]

        rls_by_street_price_df = rls_by_street_price_df.groupby([RLCN.READYEAR])[RLCN.STREETPRICE].sum().sort_values(ascending = [False]).reset_index(name = RLCN.STREETPRICE)
        rls_by_street_price_df = rls_by_street_price_df.sort_values(by = RLCN.READYEAR, ascending = [True])
        rls_by_street_price_df = rls_by_street_price_df.reset_index(drop = True)

        rls_by_street_price_df = rls_by_street_price_df.set_index(RLCN.READYEAR).transpose()
        rls_by_street_price_df.reset_index(drop = True, inplace = True)
        rls_by_street_price_df.rename_axis(None, axis = 1, inplace = True)
        rls_by_street_price_df.columns = rls_by_street_price_df.columns.astype(str)
        
        new_column_names : list = [str(x) for x in read_years]

        if rls_by_street_price_df.shape[1] != len(read_years):
            for column_name in new_column_names:
                if column_name not in rls_by_street_price_df.columns:
                    rls_by_street_price_df[column_name] = 0
            rls_by_street_price_df = rls_by_street_price_df[new_column_names]

        if rls_by_street_price_df.shape[1] > 1:
            rls_by_street_price_df = self.__add_trend_to_rls_by_street_price(rls_by_street_price_df = rls_by_street_price_df, yeatrend = read_years)
            rls_by_street_price_df.rename(columns = (lambda x : self.__df_helper.try_consolidate_trend_column_name(column_name = x)), inplace = True)

        for column_name in new_column_names:
            if column_name in rls_by_street_price_df.columns:
                rls_by_street_price_df[column_name] = rls_by_street_price_df[column_name].apply(
                    lambda x : self.__formatter.format_usd_amount(
                        amount = float64(x), rounding_digits = rounding_digits))

        return rls_by_street_price_df
    def __create_rls_by_publisher_footer(self, publisher_min_books : int, publisher_min_ab_perc : float, publisher_min_avgrating : float) -> str:
        
        '''Creates a footer message for sas_by_publisher.'''

        rls_by_publisher_footer : str = str(
            f"'Yes' if "
            f"'{RLCN.BOOKS}' >= '{publisher_min_books}' & "
            f"('{RLCN.AVGRATING}' >= '{publisher_min_avgrating}' | '{RLCN.ABPERC}' >= '{publisher_min_ab_perc}')"
            )

        return rls_by_publisher_footer
    def __filter_by_is_worth(self, rls_by_publisher_df : DataFrame, publisher_criteria : str) -> DataFrame:

        '''
                Publisher	Books	AvgRating	IsWorth
            0	Syncfusion	38	    2.55	    Yes
            1	Wiley	    9	    2.78	    Yes
            ... ...         ...     ...
        '''

        filtered_df : DataFrame = rls_by_publisher_df.copy(deep = True)

        condition : Series = (filtered_df[RLCN.ISWORTH] == publisher_criteria)
        filtered_df = filtered_df.loc[condition]
        
        filtered_df.reset_index(drop = True, inplace = True)

        return filtered_df

    def create_rl_df(self, excel_path : str, excel_skiprows : int, excel_nrows : int, excel_tabname : str, excel_null_value : str) -> DataFrame:
        
        '''Retrieves the content of the "Books" tab and returns it as a Dataframe.'''

        rl_df = pd.read_excel(
            io = excel_path, 	
            skiprows = excel_skiprows,
            nrows = excel_nrows,
            sheet_name = excel_tabname, 
            engine = 'openpyxl'
            )
        
        rl_df = self.__enforce_dataframe_definition_for_rl_df(
            rl_df = rl_df, 
            excel_null_value = excel_null_value)

        return rl_df
    def create_rls_asrt_df(self, rl_df : DataFrame, rounding_digits : int, now : datetime) -> DataFrame:

        '''
                Years	Books	Pages	TotalSpend  LastUpdate
            0	8	    234	    62648	$6332.01    2023-09-23
        '''

        count_years : int = rl_df[RLCN.READYEAR].unique().size
        count_books : int = rl_df[RLCN.TITLE].size
        sum_pages : int = rl_df[RLCN.PAGES].sum()
        sum_street_price : float64 = rl_df[RLCN.STREETPRICE].sum()

        total_spend_str : str = self.__formatter.format_usd_amount(
            amount = sum_street_price, 
            rounding_digits = rounding_digits)
        
        last_update_str : str = self.__formatter.format_to_iso_8601(dt = now)

        rl_asrt_dict : dict = {
            f"{RLCN.YEARS}": f"{str(count_years)}",
            f"{RLCN.BOOKS}": f"{str(count_books)}",
            f"{RLCN.PAGES}": f"{str(sum_pages)}",
            f"{RLCN.TOTALSPEND}": f"{total_spend_str}",
            f"{RLCN.LASTUPDATE}": f"{last_update_str}"
            }

        rl_asrt_df : DataFrame = pd.DataFrame(rl_asrt_dict, index=[0])
        
        return rl_asrt_df        
    def create_rls_by_kbsize_df(self, rl_df : DataFrame, ascending : bool, remove_if_zero : bool, n : int) -> DataFrame:
        
        '''
            Title	ReadYear	                                    Topic	Publisher	                            Rating	KBSize	A4Sheets
            1	    Machine Learning For Dummies	                2017	Data Analysis, Data Science, ML	Wiley	4	    3732	8
            2	    Machine Learning Projects for .NET Developers	2017	Data Analysis, Data Science, ML	Apress	4	    3272	7        
            ...
        '''

        rl_by_kbsize_df : DataFrame = self.__slice_by_kbsize(
            rl_df = rl_df, 
            ascending = ascending, 
            remove_if_zero = remove_if_zero)
        
        rl_by_kbsize_df = self.__converter.convert_index_to_one_based(df = rl_by_kbsize_df)
        rl_by_kbsize_df = rl_by_kbsize_df.head(n = n)

        return rl_by_kbsize_df   
    def create_rls_by_month_tpl(self, rl_df : DataFrame, read_years : list[int], now : datetime) -> Tuple[DataFrame, DataFrame]:

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
        add_trend : bool = True

        for i in range(len(read_years)):

            if i == 0:
                sas_by_month_df = self.__create_sa_by_year(rl_df = rl_df, read_year = read_years[i])
            else:
                sas_by_month_df = self.__expand_sa_by_year(
                    rl_df = rl_df, 
                    read_years = read_years, 
                    rls_by_month_df = sas_by_month_df, 
                    i = i, 
                    add_trend = add_trend)

        sas_by_month_df.rename(
            columns = (lambda x : self.__df_helper.try_consolidate_trend_column_name(column_name = x)), 
            inplace = True)
        
        sas_by_month_upd_df : DataFrame = self.__update_future_rs_to_empty(
            rls_by_month_df = sas_by_month_df, 
            now = now)

        return (sas_by_month_df, sas_by_month_upd_df)
    def create_rls_by_year_street_price_df(self, rls_by_month_tpl : Tuple[DataFrame, DataFrame], rl_df : DataFrame, read_years : list[int], rounding_digits : int) -> DataFrame:

        '''
                2016	    ↕	2017	    ↕	2018	    ↕	2019	    ↕	2020	    ↕	2021	    ↕	2022	↕	2023
            0	43 (12322)	↑	63 (18726)	↓	48 (12646)	↓	42 (9952)	↓	23 (6602)	↓	13 (1901)	↓	1 (360)	=	1 (139)
            1	$1447.14	↑	$2123.36	↓	$1249.15	↓	$748.70	    ↓	$538.75	    ↓	$169.92	    ↓	$49.99	↓	$5.00
        '''

        sas_by_year_df : DataFrame = self.__create_rls_by_year_df(rls_by_month_df = rls_by_month_tpl[0])
        sas_by_street_price_df : DataFrame = self.__create_rls_by_street_price_df(
            rl_df = rl_df, 
            read_years = read_years,
            rounding_digits = rounding_digits)

        sas_by_year_street_price_df : DataFrame = pd.concat(objs = [sas_by_year_df, sas_by_street_price_df])
        sas_by_year_street_price_df.reset_index(drop = True, inplace = True)

        return sas_by_year_street_price_df      
    def create_rls_by_topic_df(self, rl_df : DataFrame) -> DataFrame:

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

            by_kbsize_df:

                    Topic	                KBSize
                0	Software Engineering	32169
                1	C#	                    23141
                ... ...                     ...  

            sas_by_topic_df:
            
                    Topic	                Books	Pages   KBSize  A4Sheets
                0	Software Engineering	61	    16776   32169   65
                1	C#	                    50	    15772   23141   47
                ... ...                     ...     ...     ...     ...

                    Topic	                Books	Pages   A4Sheets
                0	Software Engineering	61	    16776   65
                1	C#	                    50	    15772   47
                ... ...                     ...     ...     ...
        """

        by_books_df : DataFrame = rl_df.groupby([RLCN.TOPIC])[RLCN.TITLE].size().sort_values(ascending = False).reset_index(name = RLCN.BOOKS)
        by_pages_df : DataFrame = rl_df.groupby([RLCN.TOPIC])[RLCN.PAGES].sum().sort_values(ascending = False).reset_index(name = RLCN.PAGES)

        sas_by_topic_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_pages_df, 
            how = "inner", 
            left_on = RLCN.TOPIC, 
            right_on = RLCN.TOPIC)

        by_kbsize_df : DataFrame = rl_df.groupby([RLCN.TOPIC])[RLCN.KBSIZE].sum().sort_values(ascending = False).reset_index(name = RLCN.KBSIZE)

        sas_by_topic_df = pd.merge(
            left = sas_by_topic_df, 
            right = by_kbsize_df, 
            how = "inner", 
            left_on = RLCN.TOPIC, 
            right_on = RLCN.TOPIC)
        
        sas_by_topic_df = self.__add_a4sheets_column(df = sas_by_topic_df)
        sas_by_topic_df = sas_by_topic_df[[RLCN.TOPIC, RLCN.BOOKS, RLCN.PAGES, RLCN.A4SHEETS]]

        return sas_by_topic_df
    def create_rls_by_publisher_tpl(
            self, 
            rl_df : DataFrame, 
            rounding_digits : int, 
            min_books : int, 
            min_ab_perc : float, 
            min_avgrating : float, 
            criteria : str) -> Tuple[DataFrame, DataFrame, str]:
        
        """
            The method returns (sas_by_publisher_df, sas_by_publisher_flt_df, sas_by_publisher_footer).

            Data Pipeline:

                by_books_df:

                        Publisher	Books
                    0	Syncfusion	38
                    1	O'Reilly	34
                    ... ...         ...

                by_kbsize_df:

                        Publisher	KBSize
                    0	Syncfusion	1254
                    1	O'Reilly	987
                    ... ...         ...

                sas_by_publisher_df:

                        Publisher	Books	KBSize	A4Sheets
                    0	Syncfusion	38	    1254	7
                    1	O'Reilly	34	    987	    4
                    ... ...         ...     ...     ...

                        Publisher	Books	A4Sheets
                    0	Syncfusion	38	    7
                    1	O'Reilly	34	    4
                    ... ...         ...     ...

                        Publisher	Books	A4Sheets    AB%
                    0	Syncfusion	38	    7           34.00
                    1	O'Reilly	34	    4           9.43
                    ... ...         ...     ...         ...

                by_avgrating_df:

                        Publisher	        AvgRating
                    0	Maker Media, Inc	4.00
                    1	Manning	            3.11
                    ... ...                 ...

                sas_by_publisher_df:

                        Publisher	Books	A4Sheets    AB%     AvgRating	IsWorth
                    0	Syncfusion	38	    7           34.00   2.55	    Yes
                    1	O'Reilly	34	    4           9.43    2.18	    No
                    ... ...         ...     ...         ...     ...         ...
        """
  
        by_books_df : DataFrame = rl_df.groupby([RLCN.PUBLISHER])[RLCN.TITLE].size().sort_values(ascending = [False]).reset_index(name = RLCN.BOOKS)
        by_kbsize_df : DataFrame = rl_df.groupby([RLCN.PUBLISHER])[RLCN.KBSIZE].sum().sort_values(ascending = False).reset_index(name = RLCN.KBSIZE)

        sas_by_publisher_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_kbsize_df, 
            how = "inner", 
            left_on = RLCN.PUBLISHER, 
            right_on = RLCN.PUBLISHER)
        sas_by_publisher_df = self.__add_a4sheets_column(df = sas_by_publisher_df)
        
        sas_by_publisher_df = sas_by_publisher_df[[RLCN.PUBLISHER, RLCN.BOOKS, RLCN.A4SHEETS]]
        sas_by_publisher_df[RLCN.ABPERC] = round(((sas_by_publisher_df[RLCN.A4SHEETS] / sas_by_publisher_df[RLCN.BOOKS]) * 100), rounding_digits)
  
        by_avgrating_df : DataFrame = rl_df.groupby([RLCN.PUBLISHER])[RLCN.RATING].mean().sort_values(ascending = [False]).reset_index(name = RLCN.AVGRATING)
        by_avgrating_df[RLCN.AVGRATING] = by_avgrating_df[RLCN.AVGRATING].apply(
            lambda x : round(number = x, ndigits = rounding_digits)) # 2.5671 => 2.57

        sas_by_publisher_df = pd.merge(
            left = sas_by_publisher_df, 
            right = by_avgrating_df, 
            how = "inner", 
            left_on = RLCN.PUBLISHER, 
            right_on = RLCN.PUBLISHER)

        sas_by_publisher_df[RLCN.ISWORTH] = np.where(
            np.logical_and(
                sas_by_publisher_df[RLCN.BOOKS] >= min_books,
                np.logical_or(
                    (sas_by_publisher_df[RLCN.AVGRATING] >= min_avgrating), 
                    (sas_by_publisher_df[RLCN.ABPERC] >= min_ab_perc))
                ), "Yes", "No")
        
        sas_by_publisher_flt_df : DataFrame = self.__filter_by_is_worth(rls_by_publisher_df = sas_by_publisher_df, publisher_criteria = criteria)

        sas_by_publisher_footer : str = self.__create_rls_by_publisher_footer(
            publisher_min_books = min_books,
            publisher_min_ab_perc = min_ab_perc,
            publisher_min_avgrating = min_avgrating
        )

        return (sas_by_publisher_df, sas_by_publisher_flt_df, sas_by_publisher_footer)       
    def create_rls_by_rating_df(self, rl_df : DataFrame, number_as_stars : bool) -> DataFrame:

        '''
                Rating  Books
            0	★★★★★  9
            1	★★★★☆  18
            ...
        '''

        sas_by_rating_df : DataFrame = self.__group_books_by_single_column(rl_df = rl_df, column_name = RLCN.RATING)
        sas_by_rating_df.sort_values(by = RLCN.RATING, ascending = False, inplace = True)
        sas_by_rating_df.reset_index(drop = True, inplace = True)

        if number_as_stars:
            sas_by_rating_df[RLCN.RATING] = sas_by_rating_df[RLCN.RATING].apply(
                lambda x : self.__formatter.format_rating(rating = x))

        return sas_by_rating_df    
    def create_rls_by_topic_bt_df(self, rl_df : DataFrame, read_years : list[int], sparklines_maximum : bool) -> DataFrame:

        '''
            Get trend by year and topic as numbers and sparklines.

                Topic	                        Books	                    Trend
            0	BI, Data Warehousing, PowerBI	[0, 1, 9, 11, 0, 0, 0, 0]	▁▂▇█▁▁▁▁
            1	C#	                            [10, 14, 4, 17, 8, 3, 0, 0]	▅▇▃█▄▂▁▁ 
            ...          
        '''

        by_topic_read_year_df : DataFrame = self.__create_books_by_topic_read_year(rl_df = rl_df, read_years = read_years)
        
        pivoted_df : DataFrame = self.__pivot_column_values_to_cell(
            df = by_topic_read_year_df, 
            cn_index = RLCN.TOPIC, 
            cn_values = RLCN.BOOKS)

        if sparklines_maximum:
            maximum : int = by_topic_read_year_df[RLCN.BOOKS].max()
            return self.__add_sparklines(df = pivoted_df, cn_values = RLCN.BOOKS, cn_sparklines = RLCN.TREND, maximum = maximum)
        else: 
            return self.__add_sparklines(df = pivoted_df, cn_values = RLCN.BOOKS, cn_sparklines = RLCN.TREND)
    def create_definitions_df(self) -> DataFrame:

        '''Creates a dataframe containing all the definitions in use in this application.'''

        columns : list[str] = ["Term", "Definition"]

        definitions : dict[str, str] = {
            "RL": "Reading List",
            "RLS": "Reading List Summary",
            "KBSize": "This metric is the word count of the notes I took about a given book",
            "A4Sheets": "'KBSize' converted into amount of A4 sheets",
            "AB%": "Calculated with the following formula: '(A4Sheets / Books) * 100'"
            }
        
        definitions_df : DataFrame = DataFrame(
            data = definitions.items(), 
            columns = columns
        )

        return definitions_df
class RLMarkdownFactory():

    '''Collects all the logic related to Markdown creation out of Reading List dataframes.'''

    __markdown_helper : MarkdownHelper
    __formatter : Formatter

    def __init__(self, markdown_helper : MarkdownHelper, formatter : Formatter) -> None:

        self.__markdown_helper = markdown_helper
        self.__formatter = formatter

    def __format(self, rl_df : DataFrame) -> DataFrame:

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
        formatted_rl_df[cn_rating] = rl_df[cn_rating].apply(lambda x : self.__formatter.format_rating(rating = x))
        formatted_rl_df[cn_topic] = rl_df[cn_topic]   

        return formatted_rl_df

    def create_rl_md(self, paragraph_title : str, last_update : datetime, rl_df : DataFrame) -> str:

        '''Creates the expected Markdown content for the provided arguments.'''

        markdown_header : str = self.__markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = paragraph_title)
        rl_md : str = self.__format(rl_df = rl_df).to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += rl_md
        md_content += "\n"

        return md_content
    def create_rl_asrt_md(self, rl_asrt_df : DataFrame) -> str:

        '''Creates the expected Markdown content for the provided arguments.'''

        rl_asrt_md : str = rl_asrt_df.to_markdown(index = False)

        md_content : str = rl_asrt_md
        md_content += "\n"

        return md_content
    def create_rls_by_month_md(self, paragraph_title : str, last_update : datetime, rls_by_month_df : DataFrame, rls_by_year_street_price_df : DataFrame) -> str:

        '''Creates the expected Markdown content for the provided arguments.'''

        markdown_header : str = self.__markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = paragraph_title)
        sas_by_month_md : str = rls_by_month_df.to_markdown(index = False)
        sas_by_year_street_price_md  : str = rls_by_year_street_price_df.to_markdown(index = False)

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
    def create_rls_by_publisher_md(self, paragraph_title : str, last_update : datetime, rls_by_publisher_tpl : Tuple[DataFrame, DataFrame, str]) -> str:

        '''Creates the expected Markdown content for the provided arguments.'''

        markdown_header : str = self.__markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = paragraph_title)
        sas_by_publisher_flt_md : str = rls_by_publisher_tpl[1].to_markdown(index = False)
        sas_by_publisher_md : str = rls_by_publisher_tpl[0].to_markdown(index = False)
        sas_by_publisher_footer : str = rls_by_publisher_tpl[2]

        md_content : str = markdown_header
        md_content += "\n"
        md_content += sas_by_publisher_flt_md
        md_content += "\n"
        md_content += ""
        md_content += "\n"
        md_content += sas_by_publisher_md
        md_content += "\n"
        md_content += ""
        md_content += "\n"        
        md_content += sas_by_publisher_footer
        md_content += "\n"
        md_content += ""

        return md_content
    def create_rls_by_rating_md(self, paragraph_title : str, last_update : datetime, rls_by_rating_df : DataFrame) -> str:

        '''Creates the expected Markdown content for the provided arguments.'''

        markdown_header : str = self.__markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = paragraph_title)
        sas_by_rating_md : str = rls_by_rating_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += sas_by_rating_md
        md_content += "\n"

        return md_content
    def create_rls_by_topic_md(self, paragraph_title : str, last_update : datetime, rls_by_topic_df : DataFrame, rls_by_ytt_df : DataFrame) -> str:

        '''Creates the expected Markdown content for the provided arguments.'''

        markdown_header : str = self.__markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = paragraph_title)
        sas_by_topic_md : str = rls_by_topic_df.to_markdown(index = False)
        trend_by_year_topic_md : str = rls_by_ytt_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += sas_by_topic_md
        md_content += "\n"
        md_content += ""
        md_content += "\n"
        md_content += trend_by_year_topic_md
        md_content += "\n"
        md_content += ""        

        return md_content
class RLAdapter():

    '''Adapts SettingBag properties for use in RL*Factory methods.'''

    __df_factory : RLDataFrameFactory
    __md_factory : RLMarkdownFactory

    def __init__(self, df_factory : RLDataFrameFactory, md_factory : RLMarkdownFactory) -> None:
        
        self.__df_factory = df_factory
        self.__md_factory = md_factory

    def extract_file_name_and_paragraph_title(self, id : RLID, setting_bag : SettingBag) -> Tuple[str, str]: 
    
        '''Returns (file_name, paragraph_title) for the provided id or raise an Exception.'''

        for md_info in setting_bag.md_infos:
            if md_info.id == id: 
                return (md_info.file_name, md_info.paragraph_title)

        raise Exception(_MessageCollection.no_mdinfo_found(id = id)) 

    def create_rl_df(self, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag.'''

        rl_df : DataFrame = self.__df_factory.create_rl_df(
            excel_path = setting_bag.excel_path,
            excel_skiprows = setting_bag.excel_skiprows,
            excel_nrows = setting_bag.excel_nrows,
            excel_tabname = setting_bag.excel_tabname,
            excel_null_value = setting_bag.excel_null_value
            )

        return rl_df
    def create_rls_asrt_df(self, rl_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_asrt_df : DataFrame = self.__df_factory.create_rls_asrt_df(
            rl_df = rl_df, 
            rounding_digits = setting_bag.rounding_digits,
            now = setting_bag.now
            )

        return rls_asrt_df  
    def create_rls_by_kbsize_df(self, rl_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_kbsize_df : DataFrame = self.__df_factory.create_rls_by_kbsize_df(
            rl_df = rl_df,
            ascending = setting_bag.rls_by_kbsize_ascending,
            remove_if_zero = setting_bag.rls_by_kbsize_remove_if_zero,
            n = setting_bag.rls_by_kbsize_n
        )

        return rls_by_kbsize_df
    def create_rls_by_month_tpl(self, rl_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_month_tpl : Tuple[DataFrame, DataFrame] = self.__df_factory.create_rls_by_month_tpl(
            rl_df = rl_df,
            read_years = setting_bag.read_years,
            now = setting_bag.now
        )

        return rls_by_month_tpl
    def create_rls_by_year_street_price_df(self, rls_by_month_tpl : Tuple[DataFrame, DataFrame], rl_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_year_street_price_df : DataFrame = self.__df_factory.create_rls_by_year_street_price_df(
            rls_by_month_tpl = rls_by_month_tpl,
            rl_df = rl_df,
            read_years = setting_bag.read_years,
            rounding_digits = setting_bag.rounding_digits
        )

        return rls_by_year_street_price_df
    def create_rls_by_publisher_tpl(self, rl_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame, str]:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_publisher_tpl : Tuple[DataFrame, DataFrame, str] = self.__df_factory.create_rls_by_publisher_tpl(
            rl_df = rl_df,
            rounding_digits = setting_bag.rounding_digits,
            min_books = setting_bag.rls_by_publisher_min_books,
            min_ab_perc = setting_bag.rls_by_publisher_min_ab_perc,
            min_avgrating = setting_bag.rls_by_publisher_min_avgrating,
            criteria = setting_bag.rls_by_publisher_criteria
        )

        return rls_by_publisher_tpl
    def create_rls_by_rating_df(self, rl_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_rating_df : DataFrame = self.__df_factory.create_rls_by_rating_df(
            rl_df = rl_df,
            number_as_stars = setting_bag.rls_by_rating_number_as_stars
        )

        return rls_by_rating_df 
    def create_rls_by_topic_bt_df(self, rl_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_topic_bt_df : DataFrame = self.__df_factory.create_rls_by_topic_bt_df(
            rl_df = rl_df,
            read_years = setting_bag.read_years,
            sparklines_maximum = setting_bag.rls_by_topic_bt_sparklines_maximum
        )

        return rls_by_topic_bt_df
    def create_rl_md(self, rl_df : DataFrame, setting_bag : SettingBag) -> str:

        '''Creates the expected Markdown content using setting_bag and the provided arguments.'''

        rl_md : str = self.__md_factory.create_rl_md(
            paragraph_title = self.extract_file_name_and_paragraph_title(id = RLID.RL, setting_bag = setting_bag)[1],
            last_update = setting_bag.md_last_update,
            rl_df = rl_df
        )

        return rl_md
    def create_rls_by_month_md(self, rls_by_month_tpl : Tuple[DataFrame, DataFrame], rls_by_year_street_price_df : DataFrame, setting_bag : SettingBag) -> str:

        '''Creates the expected Markdown content using setting_bag and the provided arguments.'''

        rls_by_month_md : str = self.__md_factory.create_rls_by_month_md(
            paragraph_title = self.extract_file_name_and_paragraph_title(id = RLID.RLSBYMONTH, setting_bag = setting_bag)[1],
            last_update = setting_bag.md_last_update,
            rls_by_month_df = rls_by_month_tpl[1],
            rls_by_year_street_price_df = rls_by_year_street_price_df
        )

        return rls_by_month_md
    def create_rls_by_topic_md(self, rls_by_topic_df : DataFrame, rls_by_ytt_df : DataFrame, setting_bag : SettingBag) -> str:

        '''Creates the expected Markdown content using setting_bag and the provided arguments.'''

        rls_by_topic_md : str = self.__md_factory.create_rls_by_topic_md(
            paragraph_title = self.extract_file_name_and_paragraph_title(id = RLID.RLSBYTOPIC, setting_bag = setting_bag)[1],
            last_update = setting_bag.md_last_update,
            rls_by_topic_df = rls_by_topic_df,
            rls_by_ytt_df = rls_by_ytt_df
        )

        return rls_by_topic_md
    def create_rls_by_publisher_md(self, rls_by_publisher_tpl : Tuple[DataFrame, DataFrame, str], setting_bag : SettingBag) -> str:

        '''Creates the expected Markdown content using setting_bag and the provided arguments.'''

        rls_by_publisher_md : str = self.__md_factory.create_rls_by_publisher_md(
            paragraph_title = self.extract_file_name_and_paragraph_title(id = RLID.RLSBYPUBLISHER, setting_bag = setting_bag)[1],
            last_update = setting_bag.md_last_update,
            rls_by_publisher_tpl = rls_by_publisher_tpl
        )

        return rls_by_publisher_md
    def create_rls_by_rating_md(self, rls_by_rating_df : DataFrame, setting_bag : SettingBag) -> str:

        '''Creates the expected Markdown content using setting_bag and the provided arguments.'''

        rls_by_rating_md : str = self.__md_factory.create_rls_by_rating_md(
            paragraph_title = self.extract_file_name_and_paragraph_title(id = RLID.RLSBYRATING, setting_bag = setting_bag)[1],
            last_update = setting_bag.md_last_update,
            rls_by_rating_df = rls_by_rating_df
        )

        return rls_by_rating_md
    def create_summary(self, setting_bag : SettingBag) -> RLSummary:

        '''Creates a RLSummary object out of setting_bag.'''

        rl_df : DataFrame = self.create_rl_df(setting_bag = setting_bag)
        rls_asrt_df : DataFrame = self.create_rls_asrt_df(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_kbsize_df : DataFrame = self.create_rls_by_kbsize_df(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_month_tpl : Tuple[DataFrame, DataFrame] = self.create_rls_by_month_tpl(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_publisher_tpl : Tuple[DataFrame, DataFrame, str] = self.create_rls_by_publisher_tpl(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_rating_df : DataFrame = self.create_rls_by_rating_df(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_topic_df : DataFrame = self.__df_factory.create_rls_by_topic_df(rl_df = rl_df)
        rls_by_topic_bt_df : DataFrame = self.create_rls_by_topic_bt_df(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_year_street_price_df : DataFrame = self.create_rls_by_year_street_price_df(rls_by_month_tpl = rls_by_month_tpl, rl_df = rl_df, setting_bag = setting_bag)
        definitions_df : DataFrame = self.__df_factory.create_definitions_df()

        rl_md : str = self.create_rl_md(rl_df = rl_df, setting_bag = setting_bag)
        rls_asrt_md : str = self.__md_factory.create_rl_asrt_md(rl_asrt_df = rls_asrt_df)
        rls_by_month_md : str = self.create_rls_by_month_md(rls_by_month_tpl = rls_by_month_tpl, rls_by_year_street_price_df = rls_by_year_street_price_df, setting_bag = setting_bag)
        rls_by_publisher_md : str = self.create_rls_by_publisher_md(rls_by_publisher_tpl = rls_by_publisher_tpl, setting_bag = setting_bag)
        rls_by_rating_md : str = self.create_rls_by_rating_md(rls_by_rating_df = rls_by_rating_df, setting_bag = setting_bag)
        rls_by_topic_md : str = self.create_rls_by_topic_md(rls_by_topic_df = rls_by_topic_df, rls_by_ytt_df = rls_by_topic_bt_df, setting_bag = setting_bag)

        rl_summary : RLSummary = RLSummary(
            rl_df = rl_df,
            rls_asrt_df = rls_asrt_df,
            rls_by_kbsize_df = rls_by_kbsize_df,
            rls_by_month_tpl = rls_by_month_tpl,
            rls_by_publisher_tpl = rls_by_publisher_tpl,
            rls_by_rating_df = rls_by_rating_df,
            rls_by_topic_df = rls_by_topic_df,
            rls_by_topic_bt_df = rls_by_topic_bt_df,
            rls_by_year_street_price_df = rls_by_year_street_price_df,
            definitions_df = definitions_df,
            rl_md = rl_md,
            rls_asrt_md = rls_asrt_md,
            rls_by_month_md = rls_by_month_md,
            rls_by_publisher_md = rls_by_publisher_md,
            rls_by_rating_md = rls_by_rating_md,
            rls_by_topic_md = rls_by_topic_md
        )

        return rl_summary
@dataclass(frozen=True)
class ComponentBag():

    '''Represents a collection of components.'''

    file_path_manager : FilePathManager = field(default = FilePathManager())
    file_manager : FileManager = field(default = FileManager(file_path_manager = FilePathManager()))
	
    rl_adapter : RLAdapter = field(default = RLAdapter(
        df_factory = RLDataFrameFactory(
                    converter = Converter(),
                    formatter = Formatter(),
                    df_helper = RLDataFrameHelper()
                    ),
        md_factory = RLMarkdownFactory(
                    markdown_helper = MarkdownHelper(formatter = Formatter()),
                    formatter = Formatter()
                )
        ))

    displayer : Displayer = field(default = Displayer())
    plot_manager : PlotManager = field(default = PlotManager())
    logging_function : Callable[[str], None] = field(default = LambdaProvider().get_default_logging_function())
class ReadingListProcessor():

    '''Collects all the logic related to the processing of "Reading List.xlsx".'''

    __component_bag : ComponentBag
    __setting_bag : SettingBag
    __rl_summary : RLSummary

    def __init__(self, component_bag : ComponentBag, setting_bag : SettingBag) -> None:

        self.__component_bag = component_bag
        self.__setting_bag = setting_bag

    def __validate_summary(self) -> None:
        
        '''Raises an exception if __rl_summary is None.'''

        if not hasattr(self, '_ReadingListProcessor__rl_summary'):
            raise Exception(_MessageCollection.please_run_initialize_first())
    def __save_and_log(self, id : RLID, content : str) -> None:

        '''Creates the provided Markdown content using __setting_bag.'''

        file_path : str = self.__component_bag.file_path_manager.create_file_path(
            folder_path = self.__setting_bag.working_folder_path,
            file_name = self.__component_bag.rl_adapter.extract_file_name_and_paragraph_title(id = id, setting_bag = self.__setting_bag)[0]
        )
        
        self.__component_bag.file_manager.save_content(content = content, file_path = file_path)

        message : str = _MessageCollection.this_content_successfully_saved_as(id = id, file_path = file_path)
        self.__component_bag.logging_function(message)

    def initialize(self) -> None:

        '''Creates a RLSummary object and assign it to __rl_summary.'''

        self.__rl_summary = self.__component_bag.rl_adapter.create_summary(setting_bag = self.__setting_bag)
    def process_rl(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rl.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rl
        df : DataFrame = self.__rl_summary.rl_df
        content : str = self.__rl_summary.rl_md
        id : RLID = RLID.RL

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)

        if OPTION.save in options:
            self.__save_and_log(id = id, content = content)
    def process_rls_asrt(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rl_asrt.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_asrt
        df : DataFrame = self.__rl_summary.rls_asrt_df
        content : str = self.__rl_summary.rls_asrt_md

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)

        if OPTION.logset in options:
            self.__component_bag.logging_function(content)
    def process_rls_by_kbsize(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rl_by_kbsize.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_kbsize
        df : DataFrame = self.__rl_summary.rls_by_kbsize_df
        x_name : str = "A4Sheets"

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)

        if OPTION.plot in options:
            self.__component_bag.plot_manager.show_box_plot(df = df, x_name = x_name)            
    def process_rls_by_books_year(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rl_by_books_year.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_books_year
        df : DataFrame = self.__rl_summary.rl_df
        x_name : str = "Year"

        if OPTION.plot in options:
            self.__component_bag.plot_manager.show_box_plot(df = df, x_name = x_name)
    def process_rls_by_month(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_sas.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_month
        df_1 : DataFrame = self.__rl_summary.rls_by_month_tpl[1]
        df_2 : DataFrame = self.__rl_summary.rls_by_year_street_price_df
        content : str = self.__rl_summary.rls_by_month_md     
        id : RLID = RLID.RLSBYMONTH

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df_1)
            self.__component_bag.displayer.display(obj = df_2)

        if OPTION.save in self.__setting_bag.options_rls_by_month:
            self.__save_and_log(id = id, content = content)
    def process_rls_by_publisher(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_sas_by_publisher.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_publisher
        df : DataFrame = self.__rl_summary.rls_by_publisher_tpl[0].head(n = self.__setting_bag.rls_by_publisher_n)
        formatters : dict = self.__setting_bag.rls_by_publisher_formatters
        footer : str = self.__rl_summary.rls_by_publisher_tpl[2] + "\n"
        content : str = self.__rl_summary.rls_by_publisher_md
        id : RLID = RLID.RLSBYPUBLISHER

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df, formatters = formatters)

        if OPTION.logset in options:
            self.__component_bag.logging_function(footer)

        if OPTION.save in options:
            self.__save_and_log(id = id, content = content)
    def process_rls_by_rating(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_sas_by_rating.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_rating
        df : DataFrame = self.__rl_summary.rls_by_rating_df
        content : str = self.__rl_summary.rls_by_rating_md
        id : RLID = RLID.RLSBYRATING      

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)

        if OPTION.save in options:
            self.__save_and_log(id = id, content = content)
    def process_rls_by_topic(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_sas_by_topic.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_topic
        df_1 : DataFrame = self.__rl_summary.rls_by_topic_df
        df_2 : DataFrame = self.__rl_summary.rls_by_topic_bt_df
        content : str = self.__rl_summary.rls_by_topic_md
        id : RLID = RLID.RLSBYTOPIC

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df_1)
            self.__component_bag.displayer.display(obj = df_2)

        if OPTION.save in options:
            self.__save_and_log(id = id, content = content)
    def process_definitions(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_definitions.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_definitions
        df : DataFrame = self.__rl_summary.definitions_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def get_summary(self) -> RLSummary:

        '''Returns __rl_summary.'''

        self.__validate_summary()

        return self.__rl_summary

# MAIN
if __name__ == "__main__":
    pass