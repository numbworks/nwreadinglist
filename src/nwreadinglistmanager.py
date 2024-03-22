'''
A collection of components to handle "Reading List.xlsx".

Alias: nwrlm
'''

# INFORMATION
MODULE_ALIAS : str = "nwrlm"
MODULE_NAME : str = "nwreadinglistmanager"
MODULE_VERSION : str = "3.0.0"

# GLOBAL MODULES
import copy
import numpy as np
import openpyxl
import os
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from datetime import date
from numpy import float64
from pandas import DataFrame
from pandas import Series
from sparklines import sparklines
from typing import Callable

# LOCAL MODULES
from nwshared import Formatter, Converter, FilePathManager, FileManager
from nwshared import LambdaProvider

# CONSTANTS
# DTOs
@dataclass(frozen=True)
class SettingBag():

    '''Represents a collection of settings.'''

    read_years : list[int]
    excel_path : str
    excel_books_skiprows : int
    excel_books_nrows : int
    excel_books_tabname : str
    excel_null_value : str
    is_worth_min_books : int
    is_worth_min_avgrating : float
    n_generic : int
    n_by_month : int
    n_by_kbsize : int
    show_books_df : bool
    show_sas_by_month_upd_df : bool
    show_sas_by_year_street_price_df : bool
    show_cumulative_df : bool
    show_sas_by_topic_df : bool
    show_sas_by_publisher_df : bool
    show_sas_by_publisher_flt_df : bool
    show_sas_by_rating_df : bool
    last_update : datetime
    show_readme_md : bool
    show_reading_list_by_month_md : bool
    show_reading_list_by_publisher_md : bool
    show_reading_list_by_rating_md : bool
    show_reading_list_by_topic_md : bool
    show_reading_list_md : bool
    show_reading_list_topic_trend_md : bool
    formatted_rating : bool
    now : datetime
    working_folder_path : str
    reading_list_by_month_file_name : str
    reading_list_by_publisher_file_name : str
    reading_list_by_rating_file_name : str
    reading_list_by_topic_file_name : str
    reading_list_file_name : str
    reading_list_topic_trend_file_name : str
    save_reading_lists_to_file : bool
    definitions : dict
    enable_sparklines_maximum : bool
    show_books_by_year_box_plot : bool
    show_reading_list_by_kbsize_box_plot : bool
    show_reading_list_by_kbsize_df : bool
    show_sliced_by_kbsize_asc_df : bool
    show_yearly_trend_by_topic_df : bool
    use_smaller_font_for_reading_list_md : bool = True
    use_smaller_font_for_reading_list_by_month_md : bool = True

# STATIC CLASSES
# CLASSES
class ComponentBag():

    '''
        Represents a collection of components.
    
        Dependencies: nwshared  
    '''

    formatter : Formatter
    converter : Converter
    file_path_manager : FilePathManager
    file_manager : FileManager
    lambda_provider : LambdaProvider 
    logging_lambda : Callable[[str], None]

    def __init__(
            self, 
            formatter : Formatter, 
            converter : Converter, 
            file_path_manager : FilePathManager,
            file_manager : FileManager,
            lambda_provider : LambdaProvider,
            logging_lambda : Callable[[str], None]) -> None:

        self.formatter = formatter
        self.converter = converter
        self.file_path_manager = file_path_manager
        self.file_manager = file_manager
        self.lambda_provider = lambda_provider
        self.logging_lambda = logging_lambda
    def __init__(self) -> None:
        
        self.formatter = Formatter()
        self.converter = Converter()
        self.file_path_manager = FilePathManager()
        self.file_manager = FileManager(file_path_manager = FilePathManager())
        self.lambda_provider = LambdaProvider()
        self.logging_lambda = LambdaProvider().get_default_logging_lambda()
class ReadingListManager():

    '''Collects all the logic related to the management of "Reading List.xlsx".'''

    __component_bag : ComponentBag

    def __init__(self, component_bag : ComponentBag) -> None:

        self.__component_bag = component_bag

    def __enforce_dataframe_definition_for_books_df(self, books_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

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

        books_df = books_df[column_names]

        books_df = books_df.replace(
            to_replace = setting_bag.excel_null_value, 
            value = np.nan
        )
    
        books_df = books_df.astype({column_names[0]: str})  
        books_df = books_df.astype({column_names[1]: int})
        books_df = books_df.astype({column_names[2]: str})
        books_df = books_df.astype({column_names[3]: str})
        books_df = books_df.astype({column_names[4]: str})
        books_df = books_df.astype({column_names[5]: int})

        books_df[column_names[6]] = pd.to_datetime(books_df[column_names[6]], format="%Y-%m-%d") 
        books_df[column_names[6]] = books_df[column_names[6]].apply(lambda x: x.date())

        books_df = books_df.astype({column_names[7]: int})
        books_df = books_df.astype({column_names[8]: int})
        books_df = books_df.astype({column_names[9]: str})
        books_df = books_df.astype({column_names[10]: str})
        books_df = books_df.astype({column_names[11]: str})
        books_df = books_df.astype({column_names[12]: int})
        books_df = books_df.astype({column_names[13]: float})    
        books_df = books_df.astype({column_names[14]: str})
        books_df = books_df.astype({column_names[15]: str})
        books_df = books_df.astype({column_names[16]: str})
        books_df = books_df.astype({column_names[17]: str})
        books_df = books_df.astype({column_names[18]: int})
        books_df = books_df.astype({column_names[19]: int})

        return books_df
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
    def __get_sa_by_year(self, books_df : DataFrame, read_year : int) -> DataFrame:
        
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
        condition : Series = (books_df[cn_readyear] == read_year)
        filtered_df : DataFrame = books_df.loc[condition]

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
        trend : str = None

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
    def __expand_sa_by_year(self, books_df : DataFrame, read_years : list, sas_by_month_df : DataFrame, i : int, add_trend : bool) -> DataFrame:

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
        sa_by_year_df : DataFrame = self.__get_sa_by_year(books_df = books_df, read_year = read_years[i])

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

        trend : str = None

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
    def __group_books_by_single_column(self, books_df : DataFrame, column_name : str) -> DataFrame:

        '''Groups books according to the provided column name. The book titles act as unique identifiers.'''

        cn_uniqueitemidentifier : str = "Title"
        cn_items : str = "Books"

        grouped_df : DataFrame = books_df.groupby([column_name])[cn_uniqueitemidentifier].size().sort_values(ascending = [False]).reset_index(name = cn_items)
        
        return grouped_df
    def __group_books_by_multiple_columns(self, books_df : DataFrame, column_names : list[str]) -> DataFrame:

        '''Groups books according to the provided column names (note: order matters). The book titles act as unique identifiers.'''

        cn_uniqueitemidentifier : str = "Title"
        cn_items : str = "Books"

        grouped_df : DataFrame = books_df.groupby(by = column_names)[cn_uniqueitemidentifier].count().reset_index(name = cn_items)
        grouped_df = grouped_df.sort_values(by = column_names, ascending = [True, True])

        return grouped_df
    def __slice_by_kbsize(self, books_df : DataFrame, ascending : bool, remove_if_zero : bool) -> DataFrame:

        '''
                Title	                                        ReadYear	Topic	                        Publisher	Rating	KBSize  A4Sheets
            0	Machine Learning For Dummies	                2017	    Data Analysis, Data Science, ML	Wiley	    4	    3732    8
            1	Machine Learning Projects for .NET Developers	2017	    Data Analysis, Data Science, ML	Apress	    4	    3272    7
            2	Producing Open Source Software	                2016	    Software Engineering	        O'Reilly	1	    2332    5
            ...
        '''

        sliced_df : DataFrame = books_df.copy(deep=True)

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
    def __get_books_by_topic_read_year(self, books_df : DataFrame, read_years : list[int]) -> DataFrame:

        '''
            [0] - Groups by books_df by Topic_ReadYear:

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

        books_by_topic_read_year_df : DataFrame = self.__group_books_by_multiple_columns(books_df = books_df, column_names = [cn_topic, cn_read_year])

        topics_df : DataFrame = self.__get_topics_dataframe(df = books_df)
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
    def __add_sparklines(self, df : DataFrame, cn_values : str, cn_sparklines : str, maximum : int = None) -> DataFrame:

        '''
            Adds a column with sparklines to the provided DataFrame.

            "cn_values" is the name of the column containing a list of numbers.
            "cn_sparklines" is the name of the column that will host the sparklines.
        '''

        sparklined_df : DataFrame = df.copy(deep = True)
        sparklined_df[cn_sparklines] = sparklined_df[cn_values].apply(lambda numbers : sparklines(numbers = numbers, maximum = maximum)[0])

        return sparklined_df

    def get_default_reading_list_path(self)-> str:

        r'''
            "c:\...\nwreadinglistmanager\data\Reading List.xlsx"
        '''
        
        path : str = os.getcwd().replace("src", "data")
        path = os.path.join(path, "Reading List.xlsx")

        return path
    def get_books_dataset(self, setting_bag : SettingBag) -> DataFrame:
        
        '''Retrieves the content of the "Books" tab and returns it as a Dataframe.'''

        books_df = pd.read_excel(
            io = setting_bag.excel_path, 	
            skiprows = setting_bag.excel_books_skiprows,
            nrows = setting_bag.excel_books_nrows,
            sheet_name = setting_bag.excel_books_tabname, 
            engine = 'openpyxl'
            )
        
        books_df = self.__enforce_dataframe_definition_for_books_df(books_df = books_df, setting_bag = setting_bag)

        return books_df
    def get_sas_by_month(self, books_df : DataFrame, read_years : list) -> DataFrame:

        '''
                Month	2016	↕1	2017	    ↕2	2018
            0	1	    0 (0)	↑	13 (5157)	↓	0 (0)
            1	2	    0 (0)	↑	1 (106)	    ↓	0 (0)
            ...

                Month	2016	↕   2017	    ↕	2018
            0	1	    0 (0)	↑	13 (5157)	↓	0 (0)
            1	2	    0 (0)	↑	1 (106)	    ↓	0 (0)
            ...
        '''

        sas_by_month_df : DataFrame = None
        for i in range(len(read_years)):

            if i == 0:
                sas_by_month_df = self.__get_sa_by_year(books_df = books_df, read_year = read_years[i])
            else:
                sas_by_month_df = self.__expand_sa_by_year(
                    books_df = books_df, 
                    read_years = read_years, 
                    sas_by_month_df = sas_by_month_df, 
                    i = i, 
                    add_trend = True)

        sas_by_month_df.rename(columns = (lambda x : self.__try_consolidate_trend_column_name(column_name = x)), inplace = True)

        return sas_by_month_df
    def update_future_rs_to_empty(self, sas_by_month_df : DataFrame, now : datetime) -> DataFrame:

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
    def get_cumulative(self, books_df : DataFrame, last_update : date, rounding_digits : bool = 2) -> DataFrame:

        '''
                Years	Books	Pages	TotalSpend  LastUpdate
            0	8	    234	    62648	$6332.01    2023-09-23
        '''

        cn_read_year : str = "ReadYear"
        count_years : int = books_df[cn_read_year].unique().size

        cn_title : str = "Title"
        count_books : int = books_df[cn_title].size

        cn_pages : str = "Pages"
        sum_pages : int = books_df[cn_pages].sum()

        cn_street_price : str = "StreetPrice"
        sum_street_price : float64 = books_df[cn_street_price].sum()

        cn_years : str = "Years"
        cn_books : str = "Books"
        cn_pages : str = "Pages"
        cn_total_spend : str = "TotalSpend"
        cn_last_update : str = "LastUpdate"

        cumulative_dict : dict = {
            f"{cn_years}": f"{str(count_years)}",
            f"{cn_books}": f"{str(count_books)}",
            f"{cn_pages}": f"{str(sum_pages)}",
            f"{cn_total_spend}": f"{self.__component_bag.formatter.format_usd_amount(amount = sum_street_price, rounding_digits = rounding_digits)}",
            f"{cn_last_update}": f"{self.__component_bag.formatter.format_to_iso_8601(dt = self.__component_bag.converter.convert_date_to_datetime(dt = last_update))}"
            }

        cumulative_df : DataFrame = pd.DataFrame(cumulative_dict, index=[0])

        return cumulative_df    
    def get_sas_by_year(self, sas_by_month_df : DataFrame) -> DataFrame:

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

            cn_year_books : str = self.__format_year_books_column_name(year_cn = year)
            cn_year_pages : str = self.__format_year_pages_column_name(year_cn = year)

            sas_by_year_df[year] = sas_by_year_df.apply(lambda x : self.__format_reading_status(books = x[cn_year_books], pages = x[cn_year_pages]), axis = 1) 

            sas_by_year_df.drop(labels = [cn_year_books, cn_year_pages], inplace = True, axis = 1)

        sas_by_year_df = self.__add_trend_to_sas_by_year(sas_by_year_df = sas_by_year_df, yeatrend = yeatrend)
        sas_by_year_df.rename(columns = (lambda x : self.__try_consolidate_trend_column_name(column_name = x)), inplace = True)

        return sas_by_year_df
    def get_sas_by_street_price(self, books_df : DataFrame, read_years : list, rounding_digits : int = 2) -> DataFrame:

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

        sas_by_street_price_df : DataFrame = books_df.copy(deep=True)

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
                lambda x : self.__component_bag.formatter.formatter.format_usd_amount(
                    amount = float64(x), rounding_digits = rounding_digits))

        return sas_by_street_price_df
    def get_sas_by_year_street_price(self, sas_by_month_df : DataFrame, books_df : DataFrame, read_years : list) -> DataFrame:

        '''
                2016	    ↕	2017	    ↕	2018	    ↕	2019	    ↕	2020	    ↕	2021	    ↕	2022	↕	2023
            0	43 (12322)	↑	63 (18726)	↓	48 (12646)	↓	42 (9952)	↓	23 (6602)	↓	13 (1901)	↓	1 (360)	=	1 (139)
            1	$1447.14	↑	$2123.36	↓	$1249.15	↓	$748.70	    ↓	$538.75	    ↓	$169.92	    ↓	$49.99	↓	$5.00
        '''

        sas_by_year_df : DataFrame = self.get_sas_by_year(sas_by_month_df = sas_by_month_df)
        sas_by_street_price_df : DataFrame = self.get_sas_by_street_price(books_df = books_df, read_years = read_years)

        sas_by_year_street_price_df : DataFrame = pd.concat(objs = [sas_by_year_df, sas_by_street_price_df])
        sas_by_year_street_price_df.reset_index(drop = True, inplace = True)

        return sas_by_year_street_price_df
    def get_sas_by_topic(self, books_df : DataFrame) -> DataFrame:

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
        by_books_df : DataFrame = books_df.groupby([cn_topic]).size().sort_values(ascending = [False]).reset_index(name = cn_books)

        cn_pages = "Pages"
        by_pages_df : DataFrame = books_df.groupby([cn_topic])[cn_pages].sum().sort_values(ascending = [False]).reset_index(name = cn_pages)

        sas_by_topic_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_pages_df, 
            how = "inner", 
            left_on = cn_topic, 
            right_on = cn_topic)

        return sas_by_topic_df
    def get_sas_by_publisher(self, books_df : DataFrame, setting_bag : SettingBag) -> DataFrame:
        
        """
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
        by_books_df : DataFrame = books_df.groupby([cn_publisher])[cn_title].size().sort_values(ascending = [False]).reset_index(name = cn_books)
        
        cn_rating : str = "Rating"   
        cn_avgrating : str = "AvgRating"
        by_avgrating_df : DataFrame = books_df.groupby([cn_publisher])[cn_rating].mean().sort_values(ascending = [False]).reset_index(name = cn_avgrating)
        by_avgrating_df[cn_avgrating] = by_avgrating_df[cn_avgrating].apply(lambda x : round(number = x, ndigits = 2)) # 2.5671 => 2.57

        sas_by_publisher_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_avgrating_df, 
            how = "inner", 
            left_on = cn_publisher, 
            right_on = cn_publisher)

        cn_isworth : str = "IsWorth"
        sas_by_publisher_df[cn_isworth] = np.where(
            (sas_by_publisher_df[cn_books] >= setting_bag.is_worth_min_books) & 
            (sas_by_publisher_df[cn_avgrating] >= setting_bag.is_worth_min_avgrating), 
            "Yes", "No")

        return sas_by_publisher_df
    def filter_by_is_worth(self, sas_by_publisher_df : DataFrame, is_worth : str = "Yes") -> DataFrame:

        '''
                Publisher	Books	AvgRating	IsWorth
            0	Syncfusion	38	    2.55	    Yes
            1	Wiley	    9	    2.78	    Yes
            ... ...         ...     ...
        '''

        filtered_df : DataFrame = sas_by_publisher_df.copy(deep = True)

        cn_isworth : str = "IsWorth"
        condition : Series = (filtered_df[cn_isworth] == is_worth)
        filtered_df = filtered_df.loc[condition]
        
        filtered_df.reset_index(drop = True, inplace = True)

        return filtered_df
    def get_sas_by_rating(self, books_df : DataFrame, formatted_rating : bool) -> DataFrame:

        '''
                Rating  Books
            0	★★★★★  9
            1	★★★★☆  18
            ...
        '''

        cn_rating : str = "Rating"

        sas_by_rating_df : DataFrame = self.__group_books_by_single_column(books_df = books_df, column_name = cn_rating)
        sas_by_rating_df.sort_values(by = cn_rating, ascending = False, inplace = True)
        sas_by_rating_df.reset_index(drop = True, inplace = True)

        if formatted_rating:
            sas_by_rating_df[cn_rating] = sas_by_rating_df[cn_rating].apply(lambda x : __format_rating(rating = x))

        return sas_by_rating_df
    def get_reading_list_by_kbsize(self, books_df : DataFrame, n_by_kbsize : int) -> DataFrame:
        
        '''
            Title	ReadYear	                                    Topic	Publisher	                            Rating	KBSize	A4Sheets
            1	    Machine Learning For Dummies	                2017	Data Analysis, Data Science, ML	Wiley	4	    3732	8
            2	    Machine Learning Projects for .NET Developers	2017	Data Analysis, Data Science, ML	Apress	4	    3272	7        
            ...
        '''

        ascending : bool = False
        remove_if_zero : bool = True

        rl_by_kbsize_df : DataFrame = self.__slice_by_kbsize(books_df = books_df, ascending = ascending, remove_if_zero = remove_if_zero)
        rl_by_kbsize_df = self.__component_bag.converter.convert_index_to_one_based(df = rl_by_kbsize_df)
        rl_by_kbsize_df = rl_by_kbsize_df.head(n = n_by_kbsize)

        return rl_by_kbsize_df
    def get_yearly_trend_by_topic(self, books_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''
            Get yearly trend by topic as numbers and sparklines.

                Topic	                        Books	                    Trend
            0	BI, Data Warehousing, PowerBI	[0, 1, 9, 11, 0, 0, 0, 0]	▁▂▇█▁▁▁▁
            1	C#	                            [10, 14, 4, 17, 8, 3, 0, 0]	▅▇▃█▄▂▁▁ 
            ...          
        '''

        cn_topic : str = "Topic"
        cn_books : str = "Books"
        cn_trend : str = "Trend"

        by_topic_read_year_df : DataFrame = self.__get_books_by_topic_read_year(books_df = books_df, read_years = setting_bag.read_years)
        pivoted_df : DataFrame = self.__pivot_column_values_to_cell(df = by_topic_read_year_df, cn_index = cn_topic, cn_values = cn_books)

        if setting_bag.enable_sparklines_maximum:
            maximum : int = by_topic_read_year_df[cn_books].max()
            sparklined_df : DataFrame = self.__add_sparklines(df = pivoted_df, cn_values = cn_books, cn_sparklines = cn_trend, maximum = maximum)
        else: 
            sparklined_df : DataFrame = self.__add_sparklines(df = pivoted_df, cn_values = cn_books, cn_sparklines = cn_trend)

        return sparklined_df
class MarkdownConverter():

    '''Collects all the logic related to the conversion of dataframes to Markdown format.'''

    __component_bag : ComponentBag

    def __init__(self, component_bag : ComponentBag) -> None:

        self.__component_bag = component_bag

    def __get_markdown_header(self, last_update : datetime, paragraph_title : str) -> str:
        
        '''
            ## Revision History

            |Date|Author|Description|
            |---|---|---|
            |2020-12-22|numbworks|Created.|
            |2023-04-28|numbworks|Last update.|

            ## Reading List By Month
        '''

        lines : list[str] = [
            "## Revision History", 
            "", 
            "|Date|Author|Description|", 
            "|---|---|---|",
            "|2020-12-22|numbworks|Created.|",
            f"|{self.__component_bag.formatter.format_to_iso_8601(dt = last_update)}|numbworks|Last update.|",
            "",
            f"## {paragraph_title}",
            ""
            ]

        markdown_header : str = "\n".join(lines)

        return markdown_header
    def __add_subscript_tags_to_value(self, value : str) -> str:

        '''
        "49.99" => "<sub>49.99</sub>"
        '''

        tagged : str = f"<sub>{value}</sub>"

        return tagged
    def __add_subscript_tags_to_dataframe(self, df : DataFrame) -> DataFrame:

        '''Adds subscript tags to every cell and column name of the provided DataFrame.'''

        tagged_df = df.copy(deep=True)
        
        tagged_df = tagged_df.map(func = self.__add_subscript_tags_to_value)
        tagged_df = tagged_df.rename(columns = lambda column_name : self.__add_subscript_tags_to_value(value = column_name))

        return tagged_df
    def __get_readme_md(self, cumulative_df : DataFrame) -> str:

        '''Creates the Markdown content for a README file out of the provided dataframe.'''

        cumulative_md : str = cumulative_df.to_markdown(index = False)

        md_content : str = cumulative_md
        md_content += "\n"

        return md_content
    def __get_reading_list_by_month_md(self, last_update : datetime, sas_by_month_df : DataFrame, sas_by_year_street_price_df : DataFrame, use_smaller_font : bool) -> str:

        '''Creates the Markdown content for a "Reading List By Month" file out of the provided dataframes.'''

        copy_of_sas_by_month_df : DataFrame = sas_by_month_df.copy(deep=True)
        copy_of_sas_by_year_street_price_df : DataFrame = sas_by_year_street_price_df.copy(deep=True)
        if use_smaller_font:
            copy_of_sas_by_month_df = self.__add_subscript_tags_to_dataframe(df = copy_of_sas_by_month_df)
            copy_of_sas_by_year_street_price_df = self.__add_subscript_tags_to_dataframe(df = copy_of_sas_by_year_street_price_df)

        md_paragraph_title : str = "Reading List By Month"

        markdown_header : str = self.__get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
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
    def __get_reading_list_by_publisher_md(self, last_update : datetime, sas_by_publisher_flt_df : DataFrame, sas_by_publisher_df : DataFrame) -> str:

        '''Creates the Markdown content for a "Reading List By Publisher" file out of the provided dataframes.'''

        md_paragraph_title : str = "Reading List By Publisher"

        markdown_header : str = self.__get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        sas_by_publisher_flt_md : str = sas_by_publisher_flt_df.to_markdown(index = False)
        sas_by_publisher_md : str = sas_by_publisher_df.to_markdown(index = False)

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
    def __get_reading_list_by_rating_md(self, last_update : datetime, sas_by_rating_df : DataFrame) -> str:

        '''Creates the Markdown content for a "Reading List By Rating" file out of the provided dataframe.'''

        md_paragraph_title : str = "Reading List By Rating"

        markdown_header : str = self.__get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        sas_by_rating_md : str = sas_by_rating_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += sas_by_rating_md
        md_content += "\n"

        return md_content
    def __get_reading_list_by_topic_md(self, last_update : datetime, sas_by_topic_df : DataFrame) -> str:

        '''Creates the Markdown content for a "Reading List By Topic" file out of the provided dataframe.'''

        md_paragraph_title : str = "Reading List By Topic"

        markdown_header : str = self.__get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        sas_by_topic_md : str = sas_by_topic_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += sas_by_topic_md
        md_content += "\n"

        return md_content
    def __get_reading_list_md(self, last_update : datetime, books_df : DataFrame, use_smaller_font : bool) -> str:

        '''Creates the Markdown content for a "Reading List" file out of the provided dataframe.'''

        md_paragraph_title : str = "Reading List"

        markdown_header : str = self.__get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        formatted_rl_df : DataFrame = self.__get_formatted_reading_list(books_df = books_df)

        if use_smaller_font:
            formatted_rl_df = self.__add_subscript_tags_to_dataframe(df = formatted_rl_df)    

        formatted_rl_md : str = formatted_rl_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += formatted_rl_md
        md_content += "\n"

        return md_content
    def __get_reading_list_topic_trend_md(self, last_update : datetime, yt_by_topic_df : DataFrame) -> str:

        '''Creates the Markdown content for a "Reading List Topic Trend" file out of the provided dataframe.'''

        md_paragraph_title : str = "Reading List Topic Trend"

        markdown_header : str = __get_markdown_header(last_update = last_update, paragraph_title = md_paragraph_title)
        yt_by_topic_md : str = yt_by_topic_df.to_markdown(index = False)

        md_content : str = markdown_header
        md_content += "\n"
        md_content += yt_by_topic_md
        md_content += "\n"

        return md_content
    def __format_file_name(self, file_name : str) -> str:

        '''Formats the provided file_name so that it can be displayed on the screen before the Markdown content.'''

        md_content : str = file_name
        md_content += "\n"
        md_content += ""

        return md_content
    def __get_formatted_reading_list(self, books_df : DataFrame) -> DataFrame:

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

        formatted_rl_df[cn_id] = books_df.index + 1
        formatted_rl_df[cn_title] = books_df[cn_title]
        formatted_rl_df[cn_year] = books_df[cn_year]
        formatted_rl_df[cn_language] = books_df[cn_language]
        formatted_rl_df[cn_pages] = books_df[cn_pages]
        formatted_rl_df[cn_read_date] = books_df[cn_read_date]   
        formatted_rl_df[cn_publisher] = books_df[cn_publisher]   
        formatted_rl_df[cn_rating] = books_df[cn_rating].apply(lambda x : self.__component_bag.formatter.format_rating(rating = x))
        formatted_rl_df[cn_topic] = books_df[cn_topic]   

        return formatted_rl_df

    def process_readme_md(self, cumulative_df : DataFrame, setting_bag : SettingBag) -> None:

        '''Performs all the tasks related to the README file.'''

        content : str = self.__get_readme_md(cumulative_df = cumulative_df)

        if setting_bag.show_readme_md:
            self.__component_bag.logging_lambda(content)
    def process_reading_list_by_month_md(self, sas_by_month_df : DataFrame, sas_by_year_street_price_df : DataFrame, setting_bag : SettingBag) -> None:

        '''Performs all the tasks related to the "Reading List By Month" file.''' 

        content : str = self.__get_reading_list_by_month_md(      
            last_update = setting_bag.last_update, 
            sas_by_month_df = sas_by_month_df, 
            sas_by_year_street_price_df = sas_by_year_street_price_df,
            use_smaller_font = setting_bag.use_smaller_font_for_reading_list_by_month_md)

        if setting_bag.show_reading_list_by_month_md:    
            self.__component_bag.logging_lambda(
                self.__format_file_name(file_name = setting_bag.reading_list_by_month_file_name))    
            self.__component_bag.logging_lambda(content)

        if setting_bag.save_reading_lists_to_file:

            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = setting_bag.working_folder_path,
                file_name = setting_bag.reading_list_by_month_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_reading_list_by_publisher_md(self, sas_by_publisher_flt_df : DataFrame, sas_by_publisher_df : DataFrame, setting_bag : SettingBag) -> None:

        '''Performs all the tasks related to the "Reading List By Publisher" file.'''

        content : str = self.__get_reading_list_by_publisher_md(      
            last_update = setting_bag.last_update, 
            sas_by_publisher_flt_df = sas_by_publisher_flt_df, 
            sas_by_publisher_df = sas_by_publisher_df)

        if setting_bag.show_reading_list_by_publisher_md:
            self.__component_bag.logging_lambda(
                self.__format_file_name(file_name = setting_bag.reading_list_by_publisher_file_name))        
            self.__component_bag.logging_lambda(content)

        if setting_bag.save_reading_lists_to_file:

            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = setting_bag.working_folder_path,
                file_name = setting_bag.reading_list_by_publisher_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_reading_list_by_rating_md(self, sas_by_rating_df : DataFrame, setting_bag : SettingBag) -> None:

        '''Performs all the tasks related to the "Reading List By Rating" file.'''

        content : str = self.__get_reading_list_by_rating_md(       
            last_update = setting_bag.last_update, 
            sas_by_rating_df = sas_by_rating_df)

        if setting_bag.show_reading_list_by_rating_md:
            self.__component_bag.logging_lambda(
                self.__format_file_name(file_name = setting_bag.reading_list_by_rating_file_name))
            self.__component_bag.logging_lambda(content)

        if setting_bag.save_reading_lists_to_file:
            
            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = setting_bag.working_folder_path,
                file_name = setting_bag.reading_list_by_rating_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_reading_list_by_topic_md(self, sas_by_topic_df : DataFrame, setting_bag : SettingBag) -> None:

        '''Performs all the tasks related to the "Reading List By Topic" file.'''

        content : str = self.__get_reading_list_by_topic_md( 
            last_update = setting_bag.last_update, 
            sas_by_topic_df = sas_by_topic_df)

        if setting_bag.show_reading_list_by_topic_md:
            self.__component_bag.logging_lambda(
                self.__format_file_name(file_name = setting_bag.reading_list_by_topic_file_name))
            self.__component_bag.logging_lambda(content)

        if setting_bag.save_reading_lists_to_file:

            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = setting_bag.working_folder_path,
                file_name = setting_bag.reading_list_by_topic_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_reading_list_md(self, books_df : DataFrame, setting_bag : SettingBag) -> None:

        '''Performs all the tasks related to the "Reading List" file.'''

        content : str = self.__get_reading_list_md(
            last_update = setting_bag.last_update, 
            books_df = books_df,
            use_smaller_font = setting_bag.use_smaller_font_for_reading_list_md)

        if setting_bag.show_reading_list_md:
            self.__component_bag.logging_lambda(
                self.__format_file_name(file_name = setting_bag.reading_list_file_name))
            self.__component_bag.logging_lambda(content)

        if setting_bag.save_reading_lists_to_file:

            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = setting_bag.working_folder_path,
                file_name = setting_bag.reading_list_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
    def process_reading_list_topic_trend_md(self, yt_by_topic_df : DataFrame, setting_bag : SettingBag) -> None:

        '''Performs all the tasks related to the "Reading List Topic Trend" file.'''

        content : str = self.__get_reading_list_topic_trend_md(
            last_update = setting_bag.last_update, 
            yt_by_topic_df = yt_by_topic_df)

        if setting_bag.show_reading_list_topic_trend_md:
            self.__component_bag.logging_lambda(
                self.__format_file_name(file_name = setting_bag.reading_list_topic_trend_file_name))
            self.__component_bag.logging_lambda(content)

        if setting_bag.save_reading_lists_to_file:
            
            file_path : str = self.__component_bag.file_path_manager.create_file_path(
                folder_path = setting_bag.working_folder_path,
                file_name = setting_bag.reading_list_topic_trend_file_name)
            
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)

# MAIN
if __name__ == "__main__":
    pass