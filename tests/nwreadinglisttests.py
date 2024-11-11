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
from nwreadinglist import RLID, DefaultPathProvider, MDInfo, YearProvider, SettingBag, ComponentBag
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


# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)