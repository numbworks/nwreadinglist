# GLOBAL MODULES
import unittest
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
from numpy import int32
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from parameterized import parameterized
from unittest.mock import patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
import nwreadinglistmanager as nwrlm
import nwcorecomponents as nwcc
from nwreadinglistmanager import SettingBag

# SUPPORT METHODS
class SupportMethodProvider():

    '''Collection of generic purpose test-aiding methods.'''
class ObjectMother():

    '''Collects all the DTOs required by the unit tests.'''

    @staticmethod
    def create_setting_bag() -> SettingBag:
        pass

# TEST CLASSES
class GetDefaultReadingListPathTestCase(unittest.TestCase):

    def test_getdefaultreadinglistpath_shouldreturnexpectedpath_wheninvoked(self):
        
        '''"C:/project_dir/src/" => "C:/project_dir/data/Reading List.xlsx"'''

        # Arrange
        expected : str = "C:/project_dir/data/Reading List.xlsx"

        # Act
        with patch.object(os, 'getcwd', return_value="C:/project_dir/src/") as mocked_context:
            actual : str = nwrlm.get_default_reading_list_path()

        # Assert
        self.assertEqual(expected, actual)