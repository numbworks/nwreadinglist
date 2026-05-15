'''
A library that can run several automated data analysis tasks on a reading list and save the results as a PDF report.

Alias: nwread
'''

# GLOBAL MODULES
import base64
import copy
import numpy as np
import os
import pandas as pd
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum, auto
from io import BytesIO
from numpy import float64
from pandas import DataFrame, Series, Index
from pandas.io.formats.style import Styler
from pathlib import Path
from re import Match
from sparklines import sparklines
from typing import Any, Callable, Literal, Optional, Tuple, Union

# LOCAL/NW MODULES
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
    UNDERLINES = "Underlines"
    AVGUNDERLINES = "AvgUnderlines"
    UPERC = "U%"
    ID = "Id"
class DEFINITIONSTR(StrEnum):
    
    '''Collects all the column names used by definitions.'''

    TERM = "Term"
    DEFINITION = "Definition"
    RL = "rl"
    RLS = "rls"
    READINGLIST = "Reading List"
    READINGSTATUS = "Reading Status"
class OPTION(StrEnum):

    '''Represents a collection of options.'''

    display = auto()
    log = auto()
    plot = auto()
    save_html = auto()
    save_pdf = auto()
class REPORTSTR(StrEnum):
    
    '''Collects all the strings related to RLReportManager.'''

    RL = "Full Reading List"
    RLRATINGFIVE = "Rating Five"
    RLMOSTUNDERLINES = "Most Underlines"
    RLSBYMONTH = "By Month"
    RLSBYYEAR = "By Year"
    RLSBYRANGE = "By Range"
    RLSBYTOPIC = "By Topic"
    RLSBYTOPICTREND = "By Topic Trend"
    RLSBYPUBLISHER = "By Publisher"
    RLSBYRATING = "By Rating"
    RLSBYUNDERLINES = "By Underlines"
    DEFINITIONS = "Definitions"
class RSMODE(StrEnum):

    '''Represents a collection of modes for RSHighlighter.'''

    top_one_per_row = auto()
    top_three = auto()
class PlotKind(StrEnum):

    '''All the kinds of plot supported by df.plot().'''

    LINE = "line"
    BAR = "bar"
    BARH = "barh"
    HIST = "hist"
    KDE = "kde"
    DENSITY = "density"
    AREA = "area"
    PIE = "pie"
    SCATTER = "scatter"
    HEXBIN = "hexbin"
    # BOX = "box"

# STATIC CLASSES
class _MessageCollection():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def please_run_initialize_first() -> str:
        return "Please run the 'initialize' method first."

    @staticmethod
    def provided_mode_not_supported(mode : RSMODE):
        return f"The provided mode is not supported: '{mode}'."

# CLASSES
class Formatter():

    '''Collects all the logic related to formatting tasks.'''

    def format_to_iso_8601(self, dt : datetime, include_time : bool = False) -> str:

        '''
            "2023-08-03"
            "2023-08-03 17:22:15"
        '''

        if include_time == False:
            return dt.strftime(format = "%Y-%m-%d")
        else:
            return dt.strftime(format = "%Y-%m-%d %H:%M:%S")
    def format_usd_amount(self, amount : float64, rounding_digits : int) -> str:

        '''
            748.7 => 748.70 => "$748.70"
        '''

        rounded : float64 = amount.round(decimals = rounding_digits)
        formatted : str = f"${rounded:.2f}"

        return formatted
    def format_rating(self, rating : int) -> str:

        '''"★★★★★", "★★★★☆", ...'''

        black_star : str = "★"
        white_star : str = "☆"

        if rating == 1:
            return f"{black_star}{white_star*4}"
        elif rating == 2:
            return f"{black_star*2}{white_star*3}"
        elif rating == 3:
            return f"{black_star*3}{white_star*2}"
        elif rating == 4:
            return f"{black_star*4}{white_star*1}"
        elif rating == 5:
            return f"{black_star*5}"            
        else:
            return str(rating)
class Converter():

    '''Collects all the logic related to converting tasks.'''

    def convert_index_to_blanks(self, df : DataFrame) -> DataFrame:

        '''Converts the index of the provided DataFrame to blanks.'''

        blank_idx : list[str] = [''] * len(df)
        df.index = Index(blank_idx)

        return df
    def convert_index_to_one_based(self, df : DataFrame) -> DataFrame:

        '''Converts the index of the provided DataFrame from zero-based to one-based.'''

        df.index += 1

        return df
    def convert_date_to_datetime(self, dt : date) -> datetime:

        '''Converts provided date to datetime.'''

        return datetime(year = dt.year, month = dt.month, day = dt.day)
    def convert_word_count_to_A4_sheets(self, word_count : int) -> int:

        '''
            "[...], a typical page which has 1-inch margines and is typed with a 12-point font 
            with standard spacing elements will be approximately 500 words when typed single spaced."
        '''

        if word_count == 0:
            return 0

        A4_sheets : int = int(word_count / 500)
        A4_sheets += 1

        return A4_sheets
class FilePathManager():
    
    '''Collects all the logic related to the file path management.'''

    def create_file_path(self, folder_path : str, file_name : str) -> str:

        '''Creates a file path.'''

        return os.path.join(folder_path, file_name) 
    def create_numbered_file_path(self, folder_path : str, number : int, extension : str) -> str:

        r'''Creates a numbered file path. Example: ("C:\\", 1, "html") => "C:\\1.html"'''

        file_name : str = f"{number}.{extension}"
        file_path : str = self.create_file_path(folder_path = folder_path, file_name = file_name)    

        return file_path
    def create_numbered_file_paths(self, folder_path : str, range_start : int, range_end : int, extension : str) -> list[str]:

        '''
            Creates a collection of numbered file paths.

            If range_start = 1 and range_end = 3, only two items will be created (range_end is excluded).
        '''

        file_paths : list[str] = []
        for i in range(range_start, range_end):
            file_path : str = self.create_numbered_file_path(folder_path = folder_path, number = i, extension = extension)
            file_paths.append(file_path)

        return file_paths
class FileManager():
    
    '''Collects all the logic related to the file management.'''

    __file_path_manager : FilePathManager

    def __init__(self, file_path_manager : FilePathManager) -> None:
        
        self.__file_path_manager = file_path_manager
    def __create_file_paths(self, working_folder_path : str, extension : str) -> list[str]:

        '''Creates file paths.'''

        if not extension.startswith("."):
            extension = f".{extension}"

        file_paths : list[str] = []
        for file_name in os.listdir(path = working_folder_path):
            if file_name.endswith(extension):
                file_path : str = self.__file_path_manager.create_file_path(folder_path = working_folder_path, file_name = file_name)   
                file_paths.append(file_path)

        return file_paths
    def __convert_contents_to_lines(self, contents : list[str]) -> list[str]:

        '''Converts contents to lines.'''

        lines : list[str] = []
        for i in range(len(contents)):
            lines.append(contents[i])
            lines.append('\n')

        return lines

    def remove_files(self, extensions : list[str], working_folder_path : str) -> None:

        '''Delete all the files of the provided extensions from the provided folder.'''    

        for file_name in os.listdir(path = working_folder_path):
            for extension in extensions:
                if file_name.endswith(extension):
                    os.remove(os.path.join(working_folder_path, file_name))
    def load_content(self, file_path : str) -> str:
        
        '''Reads the content of the provided text file and returns it as string.'''

        content : str = ""
        with open(file_path, 'r', encoding = 'utf-8') as file:
            content = file.read()

        return content
    def load_contents(self, working_folder_path : str, extension : str) -> list[str]:

        '''Reads the contents of all the text files in the provided folder and returns them as a collection of strings.'''

        file_paths : list[str] = self.__create_file_paths(working_folder_path = working_folder_path, extension = extension)

        contents : list[str] = []
        for file_path in file_paths:
            content : str = self.load_content(file_path = file_path)
            contents.append(content)

        return contents
    def save_content(self, content : str, file_path : str) -> None:    

        '''Writes the provided content to the provided file path.'''

        with open(file_path, 'w', encoding = 'utf-8') as new_file:
            new_file.write(content)
    def save_contents(self, contents : list[str], file_paths : list[str]) -> None: 

        '''Writes the provided contents to the provided file paths.'''

        for i in range(len(contents)):
            self.save_content(content = str(contents[i]), file_path = file_paths[i]) # without str() it returns 'bytes' (?)
    def save_log(self, contents : list[str], working_folder_path : str, file_name : str) -> None:

        '''Writes the provided collection of strings as newline-separated lines into the provided file.'''

        file_path : str = self.__file_path_manager.create_file_path(folder_path = working_folder_path, file_name  = file_name)
        lines : list[str] = self.__convert_contents_to_lines(contents = contents)

        with open(file_path, 'w', encoding = 'utf-8') as new_file:
            new_file.writelines(lines)
class LambdaProvider():

    '''Provides useful lambda functions.'''

    def get_default_logging_function(self) -> Callable[[str], None]:

        '''
            An adapter around print().
            Prints something like: "Some message"
        '''

        return lambda msg : print(msg)
    def get_timestamped_logging_function(self, now_function : Callable[[], datetime] = lambda : datetime.now()) -> Callable[[str], None]:

        '''
            An adapter around print(). 
            Prints something like: "[2023-08-03 17:22:15] Some message"
        '''

        dt_str : str = Formatter().format_to_iso_8601(dt = now_function(), include_time = True)

        return lambda msg : print(f"[{dt_str}] {msg}")
class Displayer():

    '''Adapter around IPython.core.display.display().'''

    def __display(self, obj: Any) -> None:

        '''Safely calls IPython display() or do nothing.'''
        
        try:
            from IPython.core.display import display
            display(obj)
        except ImportError:
            pass
    def __display_df(self, df : DataFrame, hide_index : bool = True, formatters : Optional[dict] = None) -> None:

        '''Displays df in Jupyter Notebook according to provided arguments.'''

        styler : Styler = df.style.format()

        if formatters:
            styler = df.style.format(formatters)

        if hide_index:
            styler.hide()

        self.__display(styler)
    def __display_styler(self, styler : Styler, hide_index : bool = True, formatters : Optional[dict] = None) -> None:

        '''Displays styler in Jupyter Notebook according to provided arguments.'''

        new_styler : Styler = copy.deepcopy(styler)

        if formatters:
            new_styler.format(formatters)

        if hide_index:
            new_styler.hide()

        self.__display(new_styler)
    
    def display(self, obj : Union[DataFrame, Styler], hide_index : bool = True, formatters : Optional[dict] = None) -> None:

        '''
            Displays obj in Jupyter Notebook according to provided arguments.

            Example for 'formatters':

                formatters : dict = { "Price" : "{:.2f}" }
        '''

        if isinstance(obj, DataFrame):
            self.__display_df(df = obj, hide_index = hide_index, formatters = formatters)

        if isinstance(obj, Styler):
            self.__display_styler(styler = obj, hide_index = hide_index, formatters = formatters)
    def display_cascade(self, objs : list[Union[DataFrame, Styler]], hide_index : bool = True, formatters : Optional[dict] = None) -> None:

        '''
            Displays objects as a cascade in a Jupyter Notebook based on the provided arguments.

            Example for 'formatters':

                formatters : dict = { "Price" : "{:.2f}" }
        '''

        for obj in objs:
            self.display(obj = obj, hide_index = hide_index, formatters = formatters)
class PlotManager():
    
    '''Collects all the logic related to the plot management.'''

    def __get_plt(self):

        '''Safely returns matplotlib.pyplot or does nothing.'''
        
        try:
            from matplotlib import pyplot as plt
            return plt
        except ImportError:
            return None

    def show_plot(self, df : DataFrame, plot_kind : PlotKind, x_name : str, y_name : str, figsize : Tuple[int, int] = (5, 5)) -> None:

        '''Shows a plot created with df.plot().'''

        title = f"{y_name} by {x_name}"
        df.plot(x = x_name, y = y_name, legend = True, kind = plot_kind.value, title = title, figsize = figsize)
    def create_plot_function(self, df : DataFrame, plot_kind : PlotKind, x_name : str, y_name : str = "items", figsize : Tuple[int, int] = (5, 5)) -> Callable[[], None]:

        '''
            Returns a function that visualizes a plot.

            Example:
            >>> func = PlotManager().create_plot_function(df = df , x_name = "seller_alias")
            >>> func()
        '''

        func : Callable[[], None] = lambda : self.show_plot(df = df, plot_kind = plot_kind, x_name = x_name, y_name = y_name, figsize = figsize)

        return func    
    def create_plot_as_base64(self, df : DataFrame, plot_kind : PlotKind, x_name : str, y_name : str = "items", figsize : Tuple[int, int] = (5, 5)) -> Optional[str]:

        '''
            Returns a plot as a base64 string or returns None.

            Example:            
            >>> plot_manager : PlotManager = PlotManager()
            >>> image_string : str = plot_manager.create_plot_as_base64(df = df, x_name = "seller_alias")
            >>> image_string = plot_manager.create_html_image_tag(image_string = image_string)
            >>> HTML(image_string)
        '''

        plt : Any = self.__get_plt()
        if not plt:
            return None

        buffer : BytesIO = BytesIO()

        title = f"{y_name} by {x_name}"
        fig : Optional[Any] = df.plot(x = x_name, y = y_name, legend = True, kind = plot_kind.value, title = title, figsize = figsize).get_figure()
        
        image_string : Optional[str] = None

        if fig:
            fig.savefig(buffer, format = "png", bbox_inches = 'tight')
            plt.close(fig)
            image_string = base64.b64encode(buffer.getbuffer()).decode("ascii")
            
        return image_string
   
    def show_box_plot(self, df : DataFrame, x_name : str, figsize : Tuple[int, int] = (5, 5)) -> None:

        '''Shows a box plot created with plt.boxplot() or does nothing.'''

        plt : Any = self.__get_plt()
        if not plt:
            return None

        plt.figure(figsize = figsize)
        plt.boxplot(x = df[x_name], vert = False, tick_labels = [x_name])
        plt.show()
    def create_box_plot_function(self, df : DataFrame, x_name : str, figsize : Tuple[int, int] = (5, 5)) -> Callable[[], None]:

        '''
            Returns a function that visualizes a box plot.

            Example:
            >>> func = PlotManager().create_box_plot_function(df = df , x_name = "seller_alias")
            >>> func()
        '''

        func : Callable[[], None] = lambda : self.show_box_plot(df = df, x_name = x_name, figsize = figsize)

        return func
    def create_box_plot_as_base64(self, df : DataFrame, x_name : str, figsize : Tuple[int, int] = (5, 5)) -> Optional[str]:

        '''
            Returns a box plot as a base64 string or returns None.

            Example:            
            >>> plot_manager : PlotManager = PlotManager()
            >>> image_string : str = plot_manager.create_box_plot_as_base64(df = df, x_name = "seller_alias")
            >>> image_string = plot_manager.create_html_image_tag(image_string = image_string)
            >>> HTML(image_string)
        '''

        plt : Any = self.__get_plt()
        if not plt:
            return None

        buffer : BytesIO = BytesIO()

        plt.figure(figsize = figsize)
        plt.boxplot(x = df[x_name], vert = False, tick_labels = [x_name])
        plt.savefig(buffer, format = "png", bbox_inches = 'tight')
        plt.close()

        image_string : str = base64.b64encode(buffer.getbuffer()).decode("ascii")

        return image_string

    def create_html_image_tag(self, image_string : str) -> str:

        '''Creates a <img /> HTML tag to display an image from the provided base64 string.'''

        return f'<img src="data:image/png;base64,{image_string}" />'
    def describe_dataframe(self, df : DataFrame, column_names : list[str]) -> DataFrame:
        
        '''Describes the provided dataframe according to the provided column names.'''

        describe_df = df[column_names].describe().apply(lambda s: s.apply(lambda x: format(x, 'g')))

        return describe_df
@dataclass(frozen=True)
class RLSummary():

    '''Collects all the dataframes and markdowns.'''

    rl_df : DataFrame
    rl_enriched_df : DataFrame
    rl_rating_five_df : DataFrame
    rl_most_underlines_df : DataFrame
    rls_by_month_tpl : Tuple[DataFrame, DataFrame]
    rls_by_year_df : DataFrame
    rls_by_range_df : DataFrame
    rls_by_topic_df : DataFrame
    rls_by_topic_trend_df : DataFrame
    rls_by_publisher_tpl : Tuple[DataFrame, str]
    rls_by_rating_df : DataFrame
    rls_by_underlines_df : DataFrame
    rld_by_kbsize_df : DataFrame
    definitions_df : DataFrame
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

        years : list[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

        return years
@dataclass(frozen=True)
class SettingBag():

    '''Represents a collection of settings.'''

	# Without Defaults
    options_rl_rating_five : list[Literal[OPTION.display]]
    options_rl_most_underlines : list[Literal[OPTION.display]]
    options_rls_by_month : list[Literal[OPTION.display]]
    options_rls_by_year : list[Literal[OPTION.display]]
    options_rls_by_range : list[Literal[OPTION.display]]
    options_rls_by_topic : list[Literal[OPTION.display]]
    options_rls_by_topic_trend : list[Literal[OPTION.display]]
    options_rls_by_publisher : list[Literal[OPTION.display, OPTION.log]]
    options_rls_by_rating : list[Literal[OPTION.display]]
    options_rls_by_underlines : list[Literal[OPTION.display]]
    options_definitions : list[Literal[OPTION.display]]
    options_report : list[Literal[OPTION.save_html, OPTION.save_pdf]]
    read_years : list[int]
    excel_path : str
    excel_nrows : int
	
	# With Defaults
    options_rl : list[Literal[OPTION.display]] = field(default_factory = list)
    options_rl_enriched : list[Literal[OPTION.display]] = field(default_factory = list)
    options_rld_by_books_year : list[Literal[OPTION.plot]] = field(default_factory = list)
    options_rld_by_kbsize : list[Literal[OPTION.display, OPTION.plot]] = field(default_factory = list)
    excel_skiprows : int = field(default = 0)
    excel_tabname : str = field(default = "Books")
    excel_null_value : str = field(default = "-")
    working_folder_path : str = field(default = "/home/nwreadinglist/")
    rounding_digits : int = field(default = 2)
    now : datetime = field(default = datetime.now())
    enable_rs_highlighting : bool = field(default = True)
    report_last_update : datetime = field(default = datetime.now())
    rl_most_underlines_formatters : dict = field(default_factory = lambda : { RLCN.AVGUNDERLINES : "{:.2f}", RLCN.UPERC : "{:.2f}" })
    rld_by_kbsize_n : int = field(default = 10)
    rld_by_kbsize_ascending : bool = field(default = False)
    rld_by_kbsize_remove_if_zero : bool = field(default = True)
    rls_by_publisher_n : Optional[int] = field(default = 15)
    rls_by_publisher_formatters : dict = field(default_factory = lambda : { RLCN.AVGRATING : "{:.2f}", RLCN.ABPERC : "{:.2f}", RLCN.AVGUNDERLINES : "{:.2f}" })
    rls_by_publisher_min_books : int = field(default = 8)
    rls_by_publisher_min_ab_perc : float = field(default = 100)
    rls_by_publisher_min_avgrating : float = field(default = 2.50)
    rls_by_publisher_criteria : Optional[Literal["Yes", "No"]] = field(default = None)
    rls_by_rating_number_as_stars : bool = field(default = True)
    rls_by_topic_trend_sparklines_maximum : bool = field(default = False)
class RLDataFrameHelper():

    '''Collects helper functions for RLDataFrameFactory.'''

    def box_rs(self, books : int, pages : int) -> str:

        '''
            13, 5157 => "13 (5157)"
        '''
        
        rs : str = f"{books} ({pages})"
        
        return rs
    def unbox_rs(self, rs : str) -> Tuple[int, int]:

        '''
            Books: "13 (5157)" => ["13", "(5157)"] => "13" => 13
            Pages: "13 (5157)" => ["13", "(5157)"] => "5157" => 5157
        '''    

        tokens : list = rs.split(" ")

        books : int = int(tokens[0])
        pages : int = int(tokens[1].replace("(", "").replace(")", ""))

        return (books, pages)
       
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
    def get_trend_by_books(self, rs_1 : str, rs_2 : str) -> str:

        '''
            "13 (5157)", "16 (3816)" => "↑"
            "16 (3816)", "13 (5157)" => "↓"
            "0 (0)", "0 (0)" => "="   
        '''

        books_1 : int = self.unbox_rs(rs = rs_1)[0]
        books_2 : int = self.unbox_rs(rs = rs_2)[0]

        trend : str = self.get_trend(value_1 = books_1, value_2 = books_2)

        return trend
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
    def try_consolidate_trend_column_name(self, column_name : str) -> str:

        '''
            "2016"  => "2016"
            "↕1"    => "↕"
        '''

        if column_name.startswith(RLCN.TRENDSYMBOL):
            return RLCN.TRENDSYMBOL
        
        return column_name
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
        column_names.append(RLCN.UNDERLINES)        # [20], int

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
        rl_df = rl_df.astype({column_names[20]: int})

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
        sa_by_year_df[read_year] = sa_by_year_df.apply(lambda x : self.__df_helper.box_rs(books = x[RLCN.BOOKS], pages = x[RLCN.PAGES]), axis = 1) 

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

            cn_trend : str = f"{RLCN.TRENDSYMBOL}{i}"
            cn_trend_1 : str = str(read_years[i-1])   # for ex. "2016"
            cn_trend_2 : str = str(read_years[i])     # for ex. "2017"
            
            expansion_df[cn_trend] = expansion_df.apply(lambda x : self.__df_helper.get_trend_by_books(rs_1 = x[cn_trend_1], rs_2 = x[cn_trend_2]), axis = 1) 

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

                cn_trend : str = f"{RLCN.TRENDSYMBOL}{i}"
                cn_trend_1 : str = str(yeatrend[i])       # 2016 => "2016"
                cn_trend_2 : str = str(yeatrend[i+1])     # 2017 => "2017"
                
                expanded_df[cn_trend] = expanded_df.apply(lambda x : self.__df_helper.get_trend_by_books(rs_1 = x[cn_trend_1], rs_2 = x[cn_trend_2]), axis = 1) 
                
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

                cn_trend : str = f"{RLCN.TRENDSYMBOL}{i}"
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
            rls_by_year_df:

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

        rls_by_year_df.drop(labels = RLCN.MONTH, inplace = True, axis = 1)
        rls_by_year_df.drop(labels = RLCN.TRENDSYMBOL, inplace = True, axis = 1)

        yeatrend : list = rls_by_year_df.columns.to_list()
        for year in yeatrend:

            cn_year_books : str = self.__df_helper.format_year_books_column_name(year_cn = year)
            cn_year_pages : str = self.__df_helper.format_year_pages_column_name(year_cn = year)

            rls_by_year_df[cn_year_books] = rls_by_year_df[year].apply(lambda x : self.__df_helper.unbox_rs(rs = x)[0])
            rls_by_year_df[cn_year_pages] = rls_by_year_df[year].apply(lambda x : self.__df_helper.unbox_rs(rs = x)[1])

            rls_by_year_df.drop(labels = year, inplace = True, axis = 1)

        rls_by_year_df = rls_by_year_df.sum().to_frame().transpose()

        for year in yeatrend:

            cn_year_books = self.__df_helper.format_year_books_column_name(year_cn = year)
            cn_year_pages = self.__df_helper.format_year_pages_column_name(year_cn = year)

            rls_by_year_df[year] = rls_by_year_df.apply(lambda x : self.__df_helper.box_rs(books = x[cn_year_books], pages = x[cn_year_pages]), axis = 1) 

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
    def __create_rls_by_publisher_step_1(self, rl_df : DataFrame) -> Tuple[DataFrame, DataFrame]:

        """
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
        """

        by_books_df : DataFrame = rl_df.groupby([RLCN.PUBLISHER])[RLCN.TITLE].size().sort_values(ascending = [False]).reset_index(name = RLCN.BOOKS)
        by_kbsize_df : DataFrame = rl_df.groupby([RLCN.PUBLISHER])[RLCN.KBSIZE].sum().sort_values(ascending = False).reset_index(name = RLCN.KBSIZE)

        return (by_books_df, by_kbsize_df)
    def __create_rls_by_publisher_step_2(self, by_books_df : DataFrame, by_kbsize_df : DataFrame, rounding_digits : int) -> DataFrame:

        """
            rls_by_publisher_df:

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
        """
        
        rls_by_publisher_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_kbsize_df, 
            how = "inner", 
            left_on = RLCN.PUBLISHER, 
            right_on = RLCN.PUBLISHER)
        rls_by_publisher_df = self.__add_a4sheets_column(df = rls_by_publisher_df)
        
        rls_by_publisher_df = rls_by_publisher_df[[RLCN.PUBLISHER, RLCN.BOOKS, RLCN.A4SHEETS]]
        rls_by_publisher_df[RLCN.ABPERC] = round(((rls_by_publisher_df[RLCN.A4SHEETS] / rls_by_publisher_df[RLCN.BOOKS]) * 100), rounding_digits)

        return rls_by_publisher_df
    def __create_rls_by_publisher_step_3(self, rl_df : DataFrame, rounding_digits : int) -> DataFrame:

        """
            by_avgrating_df:

                    Publisher	        AvgRating
                0	Maker Media, Inc	4.00
                1	Manning	            3.11
                ... ...     
        """

        by_avgrating_df : DataFrame = rl_df.groupby([RLCN.PUBLISHER])[RLCN.RATING].mean().sort_values(ascending = [False]).reset_index(name = RLCN.AVGRATING)
        
        by_avgrating_df[RLCN.AVGRATING] = by_avgrating_df[RLCN.AVGRATING].apply(
            lambda x : round(number = x, ndigits = rounding_digits))

        return by_avgrating_df
    def __create_rls_by_publisher_step_4(self, rls_by_publisher_df : DataFrame, by_avgrating_df: DataFrame) -> DataFrame:
        
        """
            rls_by_publisher_df:

                    Publisher	Books	A4Sheets    AB%     AvgRating
                0	Syncfusion	38	    7           34.00   2.55
                1	O'Reilly	34	    4           9.43    2.18
                ... ...         ...     ...         ...     ...
        """
        
        rls_by_publisher_df = pd.merge(
            left = rls_by_publisher_df, 
            right = by_avgrating_df, 
            how = "inner", 
            left_on = RLCN.PUBLISHER, 
            right_on = RLCN.PUBLISHER)
            
        return rls_by_publisher_df
    def __create_rls_by_publisher_step_5(self, rl_df : DataFrame, rounding_digits : int) -> DataFrame:

        """
            by_avgunderlines_df:

                    Publisher	        AvgUnderlines
                0	Maker Media, Inc	1.20
                1	Manning	            1.11
                ... ...     
        """

        by_avgunderlines_df : DataFrame = rl_df.groupby([RLCN.PUBLISHER])[RLCN.UNDERLINES].mean().sort_values(ascending = [False]).reset_index(name = RLCN.AVGUNDERLINES)
        by_avgunderlines_df[RLCN.AVGUNDERLINES] = by_avgunderlines_df[RLCN.AVGUNDERLINES].apply(
            lambda x : round(number = x, ndigits = rounding_digits))

        return by_avgunderlines_df
    def __create_rls_by_publisher_step_6(self, rls_by_publisher_df : DataFrame, by_avgunderlines_df : DataFrame) -> DataFrame:
        
        """
            rls_by_publisher_df:

                    Publisher	Books	A4Sheets    AB%     AvgRating   AvgUnderlines
                0	Syncfusion	38	    7           34.00   2.55        1.20
                1	O'Reilly	34	    4           9.43    2.18        1.11
                ... ...         ...     ...         ...     ...
        """
        
        rls_by_publisher_df = pd.merge(
            left = rls_by_publisher_df, 
            right = by_avgunderlines_df, 
            how = "inner", 
            left_on = RLCN.PUBLISHER, 
            right_on = RLCN.PUBLISHER)
            
        return rls_by_publisher_df
    def __create_rls_by_publisher_step_7(self, rls_by_publisher_df : DataFrame, min_books : int, min_ab_perc : float, min_avgrating : float) -> DataFrame:

        """
                Publisher	Books	A4Sheets    AB%     AvgRating	AvgUnderlines   IsWorth
            0	Syncfusion	38	    7           34.00   2.55	    1.20            Yes
            1	O'Reilly	34	    4           9.43    2.18	    1.11            No
            ... ...         ...     ...         ...     ...         ...
        """

        rls_by_publisher_df[RLCN.ISWORTH] = np.where(
            np.logical_and(
                rls_by_publisher_df[RLCN.BOOKS] >= min_books,
                np.logical_or(
                    (rls_by_publisher_df[RLCN.AVGRATING] >= min_avgrating), 
                    (rls_by_publisher_df[RLCN.ABPERC] >= min_ab_perc))
                ), "Yes", "No")
        
        return rls_by_publisher_df
    def __create_rls_by_publisher_step_8(self, rls_by_publisher_df : DataFrame) -> DataFrame:

        """
                Publisher	Books	AvgRating	A4Sheets    AB%     AvgUnderlines   IsWorth
            0	Syncfusion	38	    2.55	    7           34.00   1.20            Yes
            1	O'Reilly	34	    2.18	    4           9.43    1.11            No
            ... ...         ...     ...         ...         ...     ...             ...
        """

        reordered_cns : list[str] = [
            RLCN.PUBLISHER,
            RLCN.BOOKS,
            RLCN.AVGRATING,
            RLCN.A4SHEETS,
            RLCN.ABPERC,
            RLCN.AVGUNDERLINES,
            RLCN.ISWORTH
        ]

        rls_by_publisher_df = rls_by_publisher_df[reordered_cns]
        
        return rls_by_publisher_df  
    def __create_rls_by_publisher_footer(self, publisher_min_books : int, publisher_min_ab_perc : float, publisher_min_avgrating : float) -> str:
        
        '''Creates a footer message for sas_by_publisher.'''

        rls_by_publisher_footer : str = str(
            f"'Yes' if "
            f"'{RLCN.BOOKS}' >= '{publisher_min_books}' & "
            f"('{RLCN.AVGRATING}' >= '{publisher_min_avgrating}' | '{RLCN.ABPERC}' >= '{publisher_min_ab_perc}')"
            )

        return rls_by_publisher_footer
    def __filter_by_is_worth(self, rls_by_publisher_df : DataFrame, criteria : Literal["Yes", "No"]) -> DataFrame:

        '''
                Publisher	Books	AvgRating	IsWorth
            0	Syncfusion	38	    2.55	    Yes
            1	Wiley	    9	    2.78	    Yes
            ... ...         ...     ...
        '''

        filtered_df : DataFrame = rls_by_publisher_df.copy(deep = True)

        condition : Series = (filtered_df[RLCN.ISWORTH] == criteria)
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
    def create_rl_enriched_df(self, rl_df : DataFrame) -> DataFrame:

        '''
                ... A4Sheets    AvgUnderlines   U%
            0   ... 1           1.2             250.00
            1   ... 1           1.2             0.00
            ...            
        '''

        rl_enriched_df : DataFrame = rl_df.copy(deep = True)

        rl_enriched_df[RLCN.A4SHEETS] = rl_enriched_df[RLCN.KBSIZE].apply(
            lambda x : self.__converter.convert_word_count_to_A4_sheets(word_count = x))
        
        avg_underlines : float = rl_df[RLCN.UNDERLINES].mean()

        rl_enriched_df[RLCN.AVGUNDERLINES] = avg_underlines
        rl_enriched_df[RLCN.AVGUNDERLINES] = rl_enriched_df[RLCN.AVGUNDERLINES].round(2)

        rl_enriched_df[RLCN.UPERC] = (rl_enriched_df[RLCN.UNDERLINES] / rl_enriched_df[RLCN.AVGUNDERLINES]) * 100
        rl_enriched_df[RLCN.UPERC] = rl_enriched_df[RLCN.UPERC].round(2)

        return rl_enriched_df
    def create_rl_rating_five_df(self, rl_enriched_df : DataFrame, number_as_stars : bool) -> DataFrame:

        """
                Title	                                    Year	ReadDate	Topic	                Publisher	A4Sheets	Rating
            0   Machine Learning Using CSharp Succinctly	2014	2016-11-19	Data Analysis & ML	    Syncfusion	3	        ★★★★★
            1   Head First Design Patterns	                2004	2017-03-17	Software Engineering	O'Reilly	4	        ★★★★★
            ...
        """

        rl_rating_five_df : DataFrame = rl_enriched_df.copy(deep = True)
        rl_rating_five_df = rl_rating_five_df[rl_rating_five_df[RLCN.RATING] == 5]

        cns : list[str] = [
            RLCN.TITLE,
            RLCN.YEAR,
            RLCN.READDATE,
            RLCN.TOPIC,
            RLCN.PUBLISHER,
            RLCN.A4SHEETS,
            RLCN.RATING
        ]
        rl_rating_five_df = rl_rating_five_df[cns]

        if number_as_stars:
            rl_rating_five_df[RLCN.RATING] = rl_rating_five_df[RLCN.RATING].apply(
                lambda x : self.__formatter.format_rating(rating = x))

        return rl_rating_five_df
    def create_rl_most_underlines_df(self, rl_enriched_df : DataFrame, number_as_stars : bool) -> DataFrame:

        '''
                Title                               Year    ReadDate    Topic                   A4Sheets    Rating  Underlines  AvgUnderlines   U%
            0   A Philosophy of Software Design     2018    2024-07-16  Software Engineering    2           4       15          1.2             1250.00
            1   Microservices in .NET Core          2017    2019-07-24  C#                      4           2       14          1.2             1166.67
            ...        
        '''

        rl_most_underlines_df : DataFrame = rl_enriched_df.copy(deep = True)

        cns : list[str] = [
                RLCN.TITLE,
                RLCN.YEAR,
                RLCN.READDATE,
                RLCN.TOPIC,
                RLCN.A4SHEETS,
                RLCN.RATING,
                RLCN.UNDERLINES,
                RLCN.AVGUNDERLINES,
                RLCN.UPERC
            ]
        rl_most_underlines_df = rl_most_underlines_df[cns]

        rl_most_underlines_df = rl_most_underlines_df.sort_values(by = RLCN.UPERC, ascending = [False])
        rl_most_underlines_df = rl_most_underlines_df.reset_index(drop = True)
        rl_most_underlines_df = rl_most_underlines_df.head(10)

        if number_as_stars:
            rl_most_underlines_df[RLCN.RATING] = rl_most_underlines_df[RLCN.RATING].apply(
                lambda x : self.__formatter.format_rating(rating = x))

        return rl_most_underlines_df
    def create_rls_by_month_tpl(self, rl_df : DataFrame, read_years : list[int], now : datetime) -> Tuple[DataFrame, DataFrame]:

        '''
            The method returns a tuple of dataframes (rls_by_month_df, rls_by_month_upd_df):

            Item 0 (rls_by_month_df) contains the pristine dataset:

                    Month	2016	↕	2017	    ↕	2018
                0	1	    0 (0)	↑	13 (5157)	↓	0 (0)
                1	2	    0 (0)	↑	1 (106)	    ↓	0 (0)
                ...

            Item 1 (rls_by_month_upd_df) contains the same dataset optimized for visual representation:
                
                - Future reading statuses replaced with empty strings ("0 (0)" => "") according to setting_bag.now.
                - The "Month" column is removed.

                    2016	↕   2017	    ↕	2018
                0	0 (0)	↑	13 (5157)	↓	0 (0)
                1	0 (0)	↑	1 (106)	    ↓	
                ...
        '''

        rls_by_month_df : DataFrame = pd.DataFrame()
        add_trend : bool = True

        for i in range(len(read_years)):

            if i == 0:
                rls_by_month_df = self.__create_sa_by_year(rl_df = rl_df, read_year = read_years[i])
            else:
                rls_by_month_df = self.__expand_sa_by_year(
                    rl_df = rl_df, 
                    read_years = read_years, 
                    rls_by_month_df = rls_by_month_df, 
                    i = i, 
                    add_trend = add_trend)

        rls_by_month_df.rename(
            columns = (lambda x : self.__df_helper.try_consolidate_trend_column_name(column_name = x)), 
            inplace = True)
        
        rls_by_month_upd_df : DataFrame = self.__update_future_rs_to_empty(
            rls_by_month_df = rls_by_month_df, 
            now = now)

        rls_by_month_upd_df.drop(columns = [RLCN.MONTH], inplace = True)

        return (rls_by_month_df, rls_by_month_upd_df)    
    def create_rls_by_year_df(self, rls_by_month_tpl : Tuple[DataFrame, DataFrame], rl_df : DataFrame, read_years : list[int], rounding_digits : int) -> DataFrame:

        '''
                2016	    ↕	2017	    ↕	2018	    ↕	2019	    ↕	2020	    ↕	2021	    ↕	2022	↕	2023
            0	43 (12322)	↑	63 (18726)	↓	48 (12646)	↓	42 (9952)	↓	23 (6602)	↓	13 (1901)	↓	1 (360)	=	1 (139)
            1	$1447.14	↑	$2123.36	↓	$1249.15	↓	$748.70	    ↓	$538.75	    ↓	$169.92	    ↓	$49.99	↓	$5.00
        '''

        rls_by_year_df : DataFrame = self.__create_rls_by_year_df(rls_by_month_df = rls_by_month_tpl[0])
        
        rls_by_street_price_df : DataFrame = self.__create_rls_by_street_price_df(
            rl_df = rl_df, 
            read_years = read_years,
            rounding_digits = rounding_digits)

        rls_by_year_df = pd.concat(objs = [rls_by_year_df, rls_by_street_price_df])
        rls_by_year_df.reset_index(drop = True, inplace = True)

        return rls_by_year_df
    def create_rls_by_range_df(self, rl_df : DataFrame, rounding_digits : int) -> DataFrame:

        '''
                8 Years
            0	234 (62648)
            1	$6332.01
        '''

        count_years : int = rl_df[RLCN.READYEAR].nunique()
        count_books : int = rl_df[RLCN.TITLE].size
        sum_pages : int = rl_df[RLCN.PAGES].sum()
        sum_street_price : float64 = rl_df[RLCN.STREETPRICE].sum()

        total_spend_str: str = self.__formatter.format_usd_amount(
            amount = sum_street_price,
            rounding_digits = rounding_digits
        )

        col_name = f"{count_years} {RLCN.YEARS}"
        values = [
            f"{count_books} ({sum_pages})",
            total_spend_str
        ]

        rls_by_range_df : DataFrame = pd.DataFrame(values, columns = [col_name])

        return rls_by_range_df
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

            rls_by_topic_df:
            
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

        rls_by_topic_df : DataFrame = pd.merge(
            left = by_books_df, 
            right = by_pages_df, 
            how = "inner", 
            left_on = RLCN.TOPIC, 
            right_on = RLCN.TOPIC)

        by_kbsize_df : DataFrame = rl_df.groupby([RLCN.TOPIC])[RLCN.KBSIZE].sum().sort_values(ascending = False).reset_index(name = RLCN.KBSIZE)

        rls_by_topic_df = pd.merge(
            left = rls_by_topic_df, 
            right = by_kbsize_df, 
            how = "inner", 
            left_on = RLCN.TOPIC, 
            right_on = RLCN.TOPIC)
        
        rls_by_topic_df = self.__add_a4sheets_column(df = rls_by_topic_df)
        rls_by_topic_df = rls_by_topic_df[[RLCN.TOPIC, RLCN.BOOKS, RLCN.PAGES, RLCN.A4SHEETS]]

        return rls_by_topic_df
    def create_rls_by_topic_trend_df(self, rl_df : DataFrame, read_years : list[int], sparklines_maximum : bool) -> DataFrame:

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
    def create_rls_by_publisher_tpl(
            self, 
            rl_df : DataFrame, 
            rounding_digits : int, 
            min_books : int, 
            min_ab_perc : float, 
            min_avgrating : float,
            n : Optional[int],             
            criteria : Optional[Literal["Yes", "No"]]) -> Tuple[DataFrame, str]:
        
        """The method returns (rls_by_publisher_df, rls_by_publisher_footer)."""
  
        by_books_df, by_kbsize_df = self.__create_rls_by_publisher_step_1(rl_df)
        rls_by_publisher_df : DataFrame = self.__create_rls_by_publisher_step_2(by_books_df, by_kbsize_df, rounding_digits)
  
        by_avgrating_df : DataFrame = self.__create_rls_by_publisher_step_3(rl_df, rounding_digits)
        rls_by_publisher_df = self.__create_rls_by_publisher_step_4(rls_by_publisher_df, by_avgrating_df)

        by_avgunderlines_df : DataFrame = self.__create_rls_by_publisher_step_5(rl_df, rounding_digits)
        rls_by_publisher_df = self.__create_rls_by_publisher_step_6(rls_by_publisher_df, by_avgunderlines_df)

        rls_by_publisher_df = self.__create_rls_by_publisher_step_7(rls_by_publisher_df, min_books, min_ab_perc, min_avgrating)
        rls_by_publisher_df = self.__create_rls_by_publisher_step_8(rls_by_publisher_df)

        if n:
            rls_by_publisher_df = rls_by_publisher_df.head(n = n)

        if criteria:
            rls_by_publisher_df = self.__filter_by_is_worth(rls_by_publisher_df = rls_by_publisher_df, criteria = criteria)

        rls_by_publisher_footer : str = self.__create_rls_by_publisher_footer(
            publisher_min_books = min_books,
            publisher_min_ab_perc = min_ab_perc,
            publisher_min_avgrating = min_avgrating
        )

        return (rls_by_publisher_df, rls_by_publisher_footer)
    def create_rls_by_rating_df(self, rl_df : DataFrame, number_as_stars : bool) -> DataFrame:

        '''
                Rating  Books
            0	★★★★★  9
            1	★★★★☆  18
            ...
        '''

        rls_by_rating_df : DataFrame = self.__group_books_by_single_column(rl_df = rl_df, column_name = RLCN.RATING)
        rls_by_rating_df.sort_values(by = RLCN.RATING, ascending = False, inplace = True)
        rls_by_rating_df.reset_index(drop = True, inplace = True)

        if number_as_stars:
            rls_by_rating_df[RLCN.RATING] = rls_by_rating_df[RLCN.RATING].apply(
                lambda x : self.__formatter.format_rating(rating = x))

        return rls_by_rating_df    
    def create_rls_by_underlines_df(self, rl_enriched_df : DataFrame) -> DataFrame:

        '''
                Underlines  Books
            0   0           208
            1   1-2         108
            2   3-10        51
            3   11-15       4
            4   15+         0        
        '''

        rls_by_underlines_df : DataFrame = rl_enriched_df.copy(deep = True)

        bins : list[float] = [-0.1, 0, 2, 11, 15, float("inf")]
        labels : list[str] = ["0", "1-2", "3-10", "11-15", "15+"]

        rls_by_underlines_df[RLCN.UNDERLINES] = pd.cut(
            rls_by_underlines_df[RLCN.UNDERLINES],
            bins = bins,
            labels = labels,
            include_lowest = True)

        rls_by_underlines_df = (
            rls_by_underlines_df
                .groupby(RLCN.UNDERLINES, observed = False)[RLCN.TITLE]
                .nunique()
                .reset_index(name = RLCN.BOOKS))

        return rls_by_underlines_df
    def create_rld_by_kbsize_df(self, rl_df : DataFrame, ascending : bool, remove_if_zero : bool, n : int) -> DataFrame:
        
        '''
            Title	ReadYear	                                    Topic	Publisher	                            Rating	KBSize	A4Sheets
            1	    Machine Learning For Dummies	                2017	Data Analysis, Data Science, ML	Wiley	4	    3732	8
            2	    Machine Learning Projects for .NET Developers	2017	Data Analysis, Data Science, ML	Apress	4	    3272	7        
            ...
        '''

        rld_by_kbsize_df : DataFrame = self.__slice_by_kbsize(
            rl_df = rl_df, 
            ascending = ascending, 
            remove_if_zero = remove_if_zero)
        
        rld_by_kbsize_df = self.__converter.convert_index_to_one_based(df = rld_by_kbsize_df)
        rld_by_kbsize_df = rld_by_kbsize_df.head(n = n)

        return rld_by_kbsize_df
    def create_definitions_df(self) -> DataFrame:

        '''Creates a dataframe containing all the definitions in use in this application.'''

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
@dataclass(frozen = True)
class RSCell():
    
    '''Collects all the information related to a DataFrame cell that are required by RSHighlighter.'''

    coordinate_pair : Tuple[int, int]
    rs : str 
    books : int
    pages : int
class RSHighlighter():

    '''Encapsulates all the logic related to highlighting cells in dataframes containing reading stasuses.'''

    __df_helper : RLDataFrameHelper

    def __init__(self, df_helper : RLDataFrameHelper) -> None:

        self.__df_helper = df_helper

    def __is_rs(self, cell_content : str) -> bool :

        '''Returns True if content in ["0 (0)", "2 (275)", "13 (5157)", "63 (18578)", ...].'''

        pattern : str = r"^\d+\s*\(\d+\)$"
        match : Optional[Match[str]] = re.fullmatch(pattern = pattern, string = cell_content)

        if match is not None:
            return True
        else:
            return False
    def __append_new_rs_cell(self, rs_cells : list[RSCell], coordinate_pair : Tuple[int, int], cell_content : str) -> None:

        '''Creates and append new RSCell object to rs_cells.'''

        books, pages = self.__df_helper.unbox_rs(rs = cell_content)

        rs_cell : RSCell = RSCell(
            coordinate_pair = coordinate_pair,
            rs = cell_content,
            books = books,
            pages = pages, 
        )
        
        rs_cells.append(rs_cell)
    def __extract_row(self, df : DataFrame, row_idx : int, column_names : list[str]) -> list[RSCell]:

        '''Returns a collection of RSCell objects for provided arguments.'''

        rs_cells : list[RSCell] = []
        col_indices : list = [df.columns.get_loc(column_name) for column_name in column_names if column_name in df.columns]

        for col_idx in col_indices:

            coordinate_pair : Tuple[int, int] = (row_idx, col_idx)
            cell_content : str = str(df.iloc[row_idx, col_idx])

            if self.__is_rs(cell_content = cell_content):
                self.__append_new_rs_cell(rs_cells, coordinate_pair, cell_content)

        return rs_cells
    def __extract_n(self, mode : RSMODE) -> int:

        '''Extracts n from mode.'''

        if mode == RSMODE.top_three:
            return 3
        elif mode == RSMODE.top_one_per_row:
            return 1
        else:
            raise Exception(_MessageCollection.provided_mode_not_supported(mode))
    def __extract_top_n_rs_cells(self, rs_cells : list[RSCell], n : int) -> list[RSCell]:

        '''Extracts the n objects in rs_cells with the highest books.'''

        sorted_cells : list[RSCell] = sorted(rs_cells, key = lambda cell : cell.books, reverse = True)
        top_n : list[RSCell] = sorted_cells[:n]

        return top_n
    def __calculate_rs_cells(self, df : DataFrame, mode : RSMODE, column_names : list[str]) -> list[RSCell]:

        '''Returns a list of RSCell objects according to df and mode.'''

        rs_cells : list[RSCell] = []

        last_row_idx : int = len(df)
        n : int = self.__extract_n(mode = mode)
        current : list[RSCell] = []

        if mode == RSMODE.top_one_per_row:
            for row_idx in range(last_row_idx):

                current = self.__extract_row(df = df, row_idx = row_idx, column_names = column_names)
                current = self.__extract_top_n_rs_cells(rs_cells = current, n = n)
                rs_cells.extend(current)
                
        elif mode == RSMODE.top_three:
            for row_idx in range(last_row_idx):
                
                current = self.__extract_row(df = df, row_idx = row_idx, column_names = column_names)
                rs_cells.extend(current)

            rs_cells = self.__extract_top_n_rs_cells(rs_cells = rs_cells, n = n)

        else:
            raise Exception(_MessageCollection.provided_mode_not_supported(mode))

        return rs_cells
    def __add_tags(self, df : DataFrame, rs_cells : list[RSCell], tags : Tuple[str, str]) -> DataFrame:

        '''Adds two HTML tags around the content of the cells listed in rs_cells.'''

        tagged_df : DataFrame = df.copy(deep = True)

        left_h : str = tags[0]
        right_h : str = tags[1]

        for rs_cell in rs_cells:

            row, col = rs_cell.coordinate_pair

            if row < len(df) and col < len(df.columns):
                tagged_df.iloc[row, col] = f"{left_h}{str(df.iloc[row, col])}{right_h}"
            
        return tagged_df
    def __highlight_dataframe(self, df : DataFrame, mode : RSMODE, column_names : list[str] = []) -> DataFrame:

        '''
            Expects a df containing reading stasuses into cells - i.e. "0 (0)", "2 (275)".
            Returns a df with highlighted cells as per arguments.

            Note: column names are converted to string to aid column search when the dataframe has mixed type column names.
        '''

        highlighted_df : DataFrame = df.copy(deep = True)
        highlighted_df.columns = highlighted_df.columns.map(str)

        if len(column_names) == 0:
            column_names = highlighted_df.columns.to_list()

        rs_cells : list[RSCell] = self.__calculate_rs_cells(
            df = highlighted_df, 
            mode = mode,
            column_names = column_names
        )

        tags : Tuple[str, str] = (f"<mark style='background-color: pink'>", "</mark>")
        highlighted_df = self.__add_tags(df = highlighted_df, rs_cells = rs_cells, tags = tags)

        return highlighted_df

    def highlight_rls_by_month(self, rls_by_month_df : DataFrame) -> DataFrame:
        
        '''Returns the provided dataframe with adequate highlights.'''

        mode : RSMODE = RSMODE.top_three

        highlighted_df : DataFrame = self.__highlight_dataframe(
            df = rls_by_month_df,
            mode = mode
        )
        
        return highlighted_df
    def highlight_rls_by_year(self, rls_by_year_df : DataFrame) -> DataFrame:
        
        '''Returns the provided dataframe with adequate highlights.'''

        mode : RSMODE = RSMODE.top_three

        highlighted_df : DataFrame = self.__highlight_dataframe(
            df = rls_by_year_df,
            mode = mode
        )
        
        return highlighted_df
class RLAdapter():

    '''Adapts SettingBag properties for use in RL*Factory methods.'''

    __df_factory : RLDataFrameFactory
    __rs_highlighter : RSHighlighter

    def __init__(self, df_factory : RLDataFrameFactory, rs_highlighter : RSHighlighter) -> None:
        
        self.__df_factory = df_factory
        self.__rs_highlighter = rs_highlighter

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
    def create_rl_enriched_df(self, rl_df : DataFrame) -> DataFrame:

        '''Creates the expected dataframe.'''

        rl_enriched_df : DataFrame = self.__df_factory.create_rl_enriched_df(rl_df = rl_df)

        return rl_enriched_df     
    def create_rl_rating_five_df(self, rl_enriched_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rl_rating_five_df : DataFrame = self.__df_factory.create_rl_rating_five_df(
            rl_enriched_df = rl_enriched_df,
            number_as_stars = setting_bag.rls_by_rating_number_as_stars
        )

        return rl_rating_five_df 
    def create_rl_most_underlines_df(self, rl_enriched_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rl_most_underlines_df : DataFrame = self.__df_factory.create_rl_most_underlines_df(
            rl_enriched_df = rl_enriched_df,
            number_as_stars = setting_bag.rls_by_rating_number_as_stars
        )

        return rl_most_underlines_df 
    def create_rls_by_month_tpl(self, rl_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_month_tpl : Tuple[DataFrame, DataFrame] = self.__df_factory.create_rls_by_month_tpl(
            rl_df = rl_df,
            read_years = setting_bag.read_years,
            now = setting_bag.now
        )

        return rls_by_month_tpl    
    def create_rls_by_year_df(self, rls_by_month_tpl : Tuple[DataFrame, DataFrame], rl_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_year_df : DataFrame = self.__df_factory.create_rls_by_year_df(
            rls_by_month_tpl = rls_by_month_tpl,
            rl_df = rl_df,
            read_years = setting_bag.read_years,
            rounding_digits = setting_bag.rounding_digits
        )

        return rls_by_year_df    
    def create_rls_by_range_df(self, rl_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_range_df : DataFrame = self.__df_factory.create_rls_by_range_df(
            rl_df = rl_df, 
            rounding_digits = setting_bag.rounding_digits
            )

        return rls_by_range_df  
    def create_rls_by_topic_trend_df(self, rl_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_topic_trend_df : DataFrame = self.__df_factory.create_rls_by_topic_trend_df(
            rl_df = rl_df,
            read_years = setting_bag.read_years,
            sparklines_maximum = setting_bag.rls_by_topic_trend_sparklines_maximum
        )

        return rls_by_topic_trend_df    
    def create_rls_by_publisher_tpl(self, rl_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, str]:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rls_by_publisher_tpl : Tuple[DataFrame, str] = self.__df_factory.create_rls_by_publisher_tpl(
            rl_df = rl_df,
            rounding_digits = setting_bag.rounding_digits,
            min_books = setting_bag.rls_by_publisher_min_books,
            min_ab_perc = setting_bag.rls_by_publisher_min_ab_perc,
            min_avgrating = setting_bag.rls_by_publisher_min_avgrating,
            n = setting_bag.rls_by_publisher_n,
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
    def create_rld_by_kbsize_df(self, rl_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe using setting_bag and the provided arguments.'''

        rld_by_kbsize_df : DataFrame = self.__df_factory.create_rld_by_kbsize_df(
            rl_df = rl_df,
            ascending = setting_bag.rld_by_kbsize_ascending,
            remove_if_zero = setting_bag.rld_by_kbsize_remove_if_zero,
            n = setting_bag.rld_by_kbsize_n
        )

        return rld_by_kbsize_df

    def create_summary(self, setting_bag : SettingBag) -> RLSummary:

        '''Creates a RLSummary object out of setting_bag.'''

        rl_df : DataFrame = self.create_rl_df(setting_bag = setting_bag)
        rl_enriched_df : DataFrame = self.create_rl_enriched_df(rl_df = rl_df)
        rl_rating_five_df : DataFrame = self.create_rl_rating_five_df(rl_enriched_df = rl_enriched_df, setting_bag = setting_bag)
        rl_most_underlines_df : DataFrame = self.create_rl_most_underlines_df(rl_enriched_df = rl_enriched_df, setting_bag = setting_bag)
        rls_by_month_tpl : Tuple[DataFrame, DataFrame] = self.create_rls_by_month_tpl(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_year_df : DataFrame = self.create_rls_by_year_df(rls_by_month_tpl = rls_by_month_tpl, rl_df = rl_df, setting_bag = setting_bag)
        rls_by_range_df : DataFrame = self.create_rls_by_range_df(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_topic_df : DataFrame = self.__df_factory.create_rls_by_topic_df(rl_df = rl_df)
        rls_by_topic_trend_df : DataFrame = self.create_rls_by_topic_trend_df(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_publisher_tpl : Tuple[DataFrame, str] = self.create_rls_by_publisher_tpl(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_rating_df : DataFrame = self.create_rls_by_rating_df(rl_df = rl_df, setting_bag = setting_bag)
        rls_by_underlines_df : DataFrame = self.__df_factory.create_rls_by_underlines_df(rl_enriched_df = rl_enriched_df)
        rld_by_kbsize_df : DataFrame = self.create_rld_by_kbsize_df(rl_df = rl_df, setting_bag = setting_bag)
        definitions_df : DataFrame = self.__df_factory.create_definitions_df()

        if setting_bag.enable_rs_highlighting:
            rls_by_month_tpl = (
                self.__rs_highlighter.highlight_rls_by_month(rls_by_month_df = rls_by_month_tpl[0]),
                self.__rs_highlighter.highlight_rls_by_month(rls_by_month_df = rls_by_month_tpl[1]))
            rls_by_year_df = self.__rs_highlighter.highlight_rls_by_year(rls_by_year_df = rls_by_year_df)

        rl_summary : RLSummary = RLSummary(
            rl_df = rl_df,
            rl_enriched_df = rl_enriched_df,
            rl_rating_five_df = rl_rating_five_df,
            rl_most_underlines_df = rl_most_underlines_df,
            rls_by_month_tpl = rls_by_month_tpl,
            rls_by_year_df = rls_by_year_df,
            rls_by_range_df = rls_by_range_df,
            rls_by_topic_df = rls_by_topic_df,
            rls_by_topic_trend_df = rls_by_topic_trend_df,
            rls_by_publisher_tpl = rls_by_publisher_tpl,
            rls_by_rating_df = rls_by_rating_df,
            rls_by_underlines_df = rls_by_underlines_df,
            rld_by_kbsize_df = rld_by_kbsize_df,
            definitions_df = definitions_df
        )

        return rl_summary
class RLReportManager():

    '''Collects all the logic related to the creation of reports out of RLSummary objects.'''

    __formatter : Formatter

    def __init__(self, formatter : Formatter) -> None:
        
        self.__formatter = formatter

    def __format_for_file_name(self, last_update : datetime) ->  str:

        '''Example: "20251222".'''

        return last_update.strftime("%Y%m%d")
    def __format_for_title(self, last_update : datetime) ->  str:

        '''Example: "2025-12-22".'''

        return last_update.strftime("%Y-%m-%d")
    def __reportify_rl(self, rl_enriched_df : DataFrame) -> DataFrame:

        '''Re-arranges rl_enriched_df in a report-compliant format.'''

        rl_reportified_df : DataFrame = rl_enriched_df.copy(deep = True)
        rl_reportified_df[RLCN.ID] = rl_reportified_df.index + 1
        
        rl_reportified_df = rl_reportified_df[[
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
        ]]
        
        rl_reportified_df[RLCN.RATING] = rl_reportified_df[RLCN.RATING].apply(lambda x : self.__formatter.format_rating(rating = x))

        return rl_reportified_df    
    def __create_report_file_paths(self, folder_path: str, last_update : datetime) -> Tuple[Path, Path]:

        '''
            Example: 
                - /home/nwreadinglist/READINGLISTREPORT20251222.html
                - /home/nwreadinglist/READINGLISTREPORT20251222.pdf
        '''

        file_name : str = f"READINGLISTREPORT{self.__format_for_file_name(last_update)}"
        base_path : Path = Path(folder_path) / file_name

        html_path : Path = base_path.with_suffix(".html")
        pdf_path : Path = base_path.with_suffix(".pdf")

        return (html_path, pdf_path)
    def __create_html(self, df : DataFrame, title : str, formatters : Optional[dict], footer : Optional[str] = None) -> str:

        """Converts the provided DataFrame into a styled HTML table using a layout similar to Jupyter Notebook."""

        styled = (
            df.style
            .format(formatters)
            .hide(axis="index")
            .set_table_styles(
                [
                    {
                        "selector": "thead th", 
                        "props": "background-color: #eeeeee; color: #333; font-weight: bold; padding: 8px 10px; text-align: left; border: none;"
                    },
                    {
                        "selector": "tbody td", 
                        "props": "padding: 8px 10px; text-align: left; border: none; white-space: nowrap;"
                    },
                    {
                        "selector": "tbody tr:nth-child(even)", 
                        "props": "background-color: #f5f5f5;"
                    },
                    {
                        "selector": "", 
                        "props": "border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 12px; color: #444;"
                    }
                ]
            )
        )

        footer_html : str = (
                f"<br/><div style='margin-top: 6px; font-size: 14px; color: #666;'>{footer}</div>"
                if footer
                else ""
            )
    
        return (
            "<div style='margin-bottom: 20px;'>"
            f"<h2>{title}</h2>\n"
            f"{styled.to_html()}\n"
            f"{footer_html}"
            "</div>"
            )
    def __create_html_sections(self, rl_summary : RLSummary, formatters : Optional[dict]) -> list[str]:

        '''Converts summary to a collection of HTML code blocks.'''

        html_sections: list[str] = []
        
        html_sections.append(self.__create_html(rl_summary.rls_by_month_tpl[1], REPORTSTR.RLSBYMONTH, formatters))
        html_sections.append(self.__create_html(rl_summary.rls_by_year_df, REPORTSTR.RLSBYYEAR, formatters))
        html_sections.append(self.__create_html(rl_summary.rls_by_range_df, REPORTSTR.RLSBYRANGE, formatters))
        html_sections.append(self.__create_html(rl_summary.rls_by_topic_df, REPORTSTR.RLSBYTOPIC, formatters))
        html_sections.append(self.__create_html(rl_summary.rls_by_topic_trend_df, REPORTSTR.RLSBYTOPICTREND, formatters))
        html_sections.append(self.__create_html(rl_summary.rls_by_publisher_tpl[0], REPORTSTR.RLSBYPUBLISHER, formatters, rl_summary.rls_by_publisher_tpl[1]))
        html_sections.append(self.__create_html(rl_summary.rls_by_rating_df, REPORTSTR.RLSBYRATING, formatters))
        html_sections.append(self.__create_html(rl_summary.rl_rating_five_df, REPORTSTR.RLRATINGFIVE, formatters))
        html_sections.append(self.__create_html(rl_summary.rls_by_underlines_df, REPORTSTR.RLSBYUNDERLINES, formatters))
        html_sections.append(self.__create_html(rl_summary.rl_most_underlines_df, REPORTSTR.RLMOSTUNDERLINES, formatters))
        html_sections.append(self.__create_html(rl_summary.definitions_df, REPORTSTR.DEFINITIONS, formatters))

        html_sections.append(self.__create_html(self.__reportify_rl(rl_summary.rl_enriched_df), REPORTSTR.RL, formatters))

        return html_sections
    def __create_html_template(self, html_sections : list[str], last_update : datetime) -> str:

        '''Creates HTML template.'''

        report_title : str = "Reading List Report"
        app_name : str = "nwreadinglist"

        full_html: str = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>{report_title} | {self.__format_for_title(last_update)}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }}
                h1 {{
                    text-align: left;
                    margin-bottom: 40px;
                }}
                h2 {{
                    margin-top: 40px;
                    border-bottom: 2px solid #ddd;
                    padding-bottom: 5px;
                }}
                p {{
                    margin-top: 10px;
                    margin-bottom: 10px;
                    line-height: 1.5;
                    font-size: 12px;
                }}                
            </style>
        </head>
        <body>
            <img src='https://avatars.githubusercontent.com/u/10279234' alt='NW logo' style='width:120px; height:120px; margin-bottom:10px;'>
            <h1>{report_title} | {self.__format_for_title(last_update)}</h1>
            {''.join(html_sections)}
            <br/><p>© numbworks. This report is generated by '{app_name}' and licensed under the MIT License. Additional information: <a href="https://github.com/numbworks">github.com/numbworks</a>.</p>
        </body>
        </html>
        """
        
        return full_html
    
    def save_as_report(
        self, 
        rl_summary: RLSummary, 
        folder_path : str, 
        last_update : datetime, 
        save_html : bool, 
        save_pdf : bool, 
        formatters : Optional[dict] = None) -> None:
        
        '''Builds an HTML report from selected DataFrames in RLSummary and saves it as both HTML and PDF.'''

        if save_html == False and save_pdf == False:
            return

        html_path, pdf_path = self.__create_report_file_paths(folder_path = folder_path, last_update = last_update)
        html_sections : list[str] = self.__create_html_sections(rl_summary = rl_summary, formatters = formatters)
        full_html : str = self.__create_html_template(html_sections = html_sections, last_update = last_update)

        if save_html:
            html_path.write_text(data = full_html, encoding = "utf-8")
        
        if save_pdf:
            from weasyprint import CSS, HTML
            stylesheet : CSS = CSS(string = "@page { size: A3 landscape; margin: 20mm; }")
            HTML(string = full_html).write_pdf(target = str(pdf_path), stylesheets = [stylesheet])
@dataclass(frozen=True)
class ComponentBag():

    '''Represents a collection of components.'''

    file_path_manager : FilePathManager = field(default = FilePathManager())
    file_manager : FileManager = field(default = FileManager(file_path_manager = FilePathManager()))
    displayer : Displayer = field(default = Displayer())
    plot_manager : PlotManager = field(default = PlotManager())
    logging_function : Callable[[str], None] = field(default = LambdaProvider().get_default_logging_function())
    rlr_manager : RLReportManager = field(default = RLReportManager(formatter = Formatter()))
    rl_adapter : RLAdapter = field(default = RLAdapter(
        df_factory = RLDataFrameFactory(
            converter = Converter(),
            formatter = Formatter(),
            df_helper = RLDataFrameHelper()),
        rs_highlighter = RSHighlighter(df_helper = RLDataFrameHelper())))
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
    def __merge_formatters(self) -> dict:

        '''Merges all formatters in one dict'''

        formatters : dict = (
            self.__setting_bag.rl_most_underlines_formatters | 
            self.__setting_bag.rls_by_publisher_formatters
        )
            
        return formatters

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

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)    
    def process_rl_enriched(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rl.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rl_enriched
        df : DataFrame = self.__rl_summary.rl_enriched_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)       
    def process_rl_rating_five(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rl_rating_five.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rl_rating_five
        df : DataFrame = self.__rl_summary.rl_rating_five_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_rl_most_underlines(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rl_most_underlines.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rl_most_underlines
        df : DataFrame = self.__rl_summary.rl_most_underlines_df
        formatters : dict = self.__setting_bag.rl_most_underlines_formatters

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df, formatters = formatters)
    def process_rls_by_month(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rls_by_month.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_month
        df : DataFrame = self.__rl_summary.rls_by_month_tpl[1]

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_rls_by_year(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rls_by_year.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_month
        df : DataFrame = self.__rl_summary.rls_by_year_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_rls_by_range(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rl_asrt.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_range
        df : DataFrame = self.__rl_summary.rls_by_range_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_rls_by_topic(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rls_by_topic.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_topic
        df : DataFrame = self.__rl_summary.rls_by_topic_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_rls_by_topic_trend(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rls_by_topic_trend.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_topic_trend
        df : DataFrame = self.__rl_summary.rls_by_topic_trend_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_rls_by_publisher(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rls_by_publisher.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_publisher
        df : DataFrame = self.__rl_summary.rls_by_publisher_tpl[0]
        formatters : dict = self.__setting_bag.rls_by_publisher_formatters
        footer : str = self.__rl_summary.rls_by_publisher_tpl[1] + "\n"

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df, formatters = formatters)

        if OPTION.log in options:
            self.__component_bag.logging_function(footer)
    def process_rls_by_rating(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rls_by_rating.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_rating
        df : DataFrame = self.__rl_summary.rls_by_rating_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_rls_by_underlines(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rls_by_underlines.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rls_by_underlines
        df : DataFrame = self.__rl_summary.rls_by_underlines_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_rld_by_kbsize(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rld_by_kbsize.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rld_by_kbsize
        df : DataFrame = self.__rl_summary.rld_by_kbsize_df
        x_name : str = RLCN.A4SHEETS

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)

        if OPTION.plot in options:
            self.__component_bag.plot_manager.show_box_plot(df = df, x_name = x_name)
    def process_rld_by_books_year(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_rld_by_books_year.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_rld_by_books_year
        df : DataFrame = self.__rl_summary.rl_df
        x_name : str = RLCN.YEAR

        if OPTION.plot in options:
            self.__component_bag.plot_manager.show_box_plot(df = df, x_name = x_name)
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
    def save_as_report(self) -> None:

        '''Builds an HTML report from selected DataFrames in RLSummary and saves it as both HTML and PDF.'''

        self.__validate_summary()

        options : list = self.__setting_bag.options_report
        formatters :dict = self.__merge_formatters()
        save_html : bool = False
        save_pdf : bool = False

        if OPTION.save_html in options:
            save_html = True

        if OPTION.save_pdf in options:
            save_pdf = True

        self.__component_bag.rlr_manager.save_as_report(
            rl_summary = self.__rl_summary,
            folder_path = self.__setting_bag.working_folder_path,
            last_update = self.__setting_bag.now,
            save_html = save_html,
            save_pdf = save_pdf,
            formatters = formatters)

# MAIN
if __name__ == "__main__":
    pass