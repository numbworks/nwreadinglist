# GLOBAL MODULES
import os
import sys
import unittest
from argparse import _SubParsersAction, ArgumentParser, Namespace
from io import StringIO
from parameterized import parameterized
from unittest.mock import Mock, patch

# LOCAL/NW MODULES
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwreadinglist import ComponentBag, ReadingListProcessor, SettingBag
from nwreadinglistcli import CLISTRING, APFactory, AsciiBannerManager, _MessageCollection
from nwreadinglistcli import CLIManager, CLIValidator, ReadingListProcessorFactory, Validator

# SUPPORT METHODS
# TEST CLASSES
class AsciiBannerManagerTestCase(unittest.TestCase):

    def test_validate_shouldraisevalueerror_whenversionisnone(self) -> None:

        # Arrange
        # Act, Assert
        with self.assertRaises(ValueError) as context:
            AsciiBannerManager()._AsciiBannerManager__validate(version = None) # type: ignore

        self.assertEqual(_MessageCollection.provided_version_empty_whitespace(), str(context.exception))
    def test_validate_shouldraisevalueerror_whenversioniswhitespace(self) -> None:

        # Arrange
        version : str = " "

        # Act, Assert
        with self.assertRaises(ValueError) as context:
            AsciiBannerManager()._AsciiBannerManager__validate(version = version) # type: ignore

        self.assertEqual(_MessageCollection.provided_version_empty_whitespace(), str(context.exception))
    def test_createfiglet_shouldreturnexpectedmaxlength_wheninvoked(self) -> None:

        # Arrange
        expected : int = 65

        # Act
        _, max_length = AsciiBannerManager()._AsciiBannerManager__create_figlet() # type: ignore

        # Assert
        self.assertEqual(expected, max_length)
    def test_createframe_shouldreturnexpectedtuple_wheninvoked(self) -> None:

        # Arrange
        version : str = "1.0.5"
        max_length : int = 65
        
        expected_top_line : str = "*" * 65
        expected_bottom_line : str = "*" * 46 + "Version: 1.0.5" + "*" * 5

        # Act
        top_line, bottom_line = AsciiBannerManager()._AsciiBannerManager__create_frame(version = version, max_length = max_length) # type: ignore

        # Assert
        self.assertEqual(expected_top_line, top_line)
        self.assertEqual(expected_bottom_line, bottom_line)
    def test_create_shouldcallexpectedprivatemethodsandreturnbanner_wheninvoked(self) -> None:

        # Arrange
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager()
        version : str = "1.0.5"
        max_lenght : int = 65
        
        figlet_tpl : tuple = ("ascii_art", max_lenght)
        frame_tpl : tuple = ("top_border", "bottom_border")

        with patch.object(ascii_banner_manager, "_AsciiBannerManager__validate") as mocked_validate, \
                patch.object(ascii_banner_manager, "_AsciiBannerManager__create_figlet", return_value = figlet_tpl) as mocked_create_figlet, \
                patch.object(ascii_banner_manager, "_AsciiBannerManager__create_frame", return_value = frame_tpl) as mocked_create_frame:

            # Act
            actual : str = ascii_banner_manager.create(version = version)

            # Assert
            mocked_validate.assert_called_once_with(version)
            mocked_create_figlet.assert_called_once()
            mocked_create_frame.assert_called_once_with(version, max_lenght)

            self.assertIn("top_border", actual)
            self.assertIn("ascii_art", actual)
            self.assertIn("bottom_border", actual)
class ValidatorTestCase(unittest.TestCase):

    def test_validatefilepath_shouldraiseexceptionwithexpectedmessage_whenfiledoesnotexist(self):

        # Arrange
        file_path : str = r"C:/NonExistentFile.txt"
        expected : str = _MessageCollection.provided_path_doesnt_exist(file_path)

        # Act, Assert
        with patch("os.path.isfile", return_value = False):
            with self.assertRaises(Exception) as context:
                Validator.validate_file_path(file_path = file_path)
            
            self.assertEqual(str(context.exception), expected)
    def test_validatefilepath_shoulddonothing_whenfileexists(self):

        # Arrange
        file_path : str = r"C:/Exists.txt"

        # Act, Assert
        with patch("os.path.isfile", return_value = True):
            Validator.validate_file_path(file_path = file_path)
    
    def test_validatefolderpath_shouldraiseexceptionwithexpectedmessage_whenfolderdoesnotexist(self):

        # Arrange
        folder_path : str = r"C:/NonExistent/"
        expected : str = _MessageCollection.provided_path_doesnt_exist(folder_path)

        # Act, Assert
        with patch("os.path.isdir", return_value = False):
            with self.assertRaises(Exception) as context:
                Validator.validate_folder_path(folder_path = folder_path)
            
            self.assertEqual(str(context.exception), expected)
    def test_validatefolderpath_shoulddonothing_whenfolderexists(self):

        # Arrange
        folder_path : str = r"C:/Existent/"

        # Act, Assert
        with patch("os.path.isdir", return_value = True):
            Validator.validate_folder_path(folder_path = folder_path)

    def test_validatenrows_shouldraiseexceptionwithexpectedmessage_whennrowsisnotaninteger(self):

        # Arrange
        nrows : str = "abc"
        expected : str = _MessageCollection.provided_nrows_not_valid_integer(nrows)

        # Act, Assert
        with self.assertRaises(Exception) as context:
            Validator.validate_nrows(nrows = nrows)
        
        self.assertEqual(str(context.exception), expected)
    def test_validatenrows_shouldraiseexceptionwithexpectedmessage_whennrowsislessthanone(self):

        # Arrange
        nrows : str = "0"
        expected : str = _MessageCollection.provided_nrows_less_one(nrows)

        # Act, Assert
        with self.assertRaises(Exception) as context:
            Validator.validate_nrows(nrows = nrows)
        
        self.assertEqual(str(context.exception), expected)
    def test_validatenrows_shoulddonothing_whennrowsisvalidinteger(self):

        # Arrange
        nrows : str = "10"

        # Act, Assert
        Validator.validate_nrows(nrows = nrows)
class CLIValidatorTestCase(unittest.TestCase):

    def test_validatefilepath_shouldreturnfilepath_whenvalidfilepath(self) -> None:

        # Arrange
        file_path : str = "valid_file.py"

        # Act
        with patch("nwreadinglistcli.Validator.validate_file_path") as validate_file_path:
            validate_file_path.return_value = None
            actual : str = CLIValidator().validate_file_path(file_path = file_path)

        # Assert
        self.assertEqual(file_path, actual)
    def test_validatefilepath_shouldraiseexception_wheninvalidfilepath(self) -> None:

        # Arrange
        file_path : str = "invalid_file.py"
        message : str = "The provided 'file_path' doesn't exist: 'invalid_file.py'."

        # Act, Assert
        with patch("nwreadinglistcli.Validator") as validator_class:
            validator_instance = validator_class.return_value
            validator_instance.validate_file_path.side_effect = Exception(message)
            
            with self.assertRaises(Exception) as context:
                CLIValidator().validate_file_path(file_path = file_path)
            
            self.assertEqual(message, str(context.exception))

    def test_validatefolderpath_shouldreturnfolderpath_whenvalidfolderpath(self) -> None:

        # Arrange
        folder_path : str = "valid_folder/"

        # Act
        with patch("nwreadinglistcli.Validator.validate_folder_path") as validate_folder_path:
            validate_folder_path.return_value = None
            actual : str = CLIValidator().validate_folder_path(folder_path = folder_path)

        # Assert
        self.assertEqual(folder_path, actual)
    def test_validatefolderpath_shouldraiseexception_wheninvalidfolderpath(self) -> None:

        # Arrange
        folder_path : str = "invalid_folder/"
        message : str = "The provided 'folder_path' doesn't exist: 'invalid_folder/'."

        # Act, Assert
        with patch("nwreadinglistcli.Validator") as validator_class:
            validator_instance = validator_class.return_value
            validator_instance.validate_folder_path.side_effect = Exception(message)
            
            with self.assertRaises(Exception) as context:
                CLIValidator().validate_folder_path(folder_path = folder_path)
            
            self.assertEqual(message, str(context.exception))

    def test_validatenrows_shouldreturnnrows_whenvalidnrows(self) -> None:

        # Arrange
        nrows : str = "10"

        # Act
        with patch("nwreadinglistcli.Validator.validate_nrows") as validate_nrows:
            validate_nrows.return_value = None
            actual : str = CLIValidator().validate_nrows(nrows = nrows)

        # Assert
        self.assertEqual(nrows, actual)
    def test_validatenrows_shouldraiseexception_wheninvalidnrows(self) -> None:

        # Arrange
        nrows : str = "-1"
        message : str = "The provided 'nrows' must be greater than or equal to 1."

        # Act, Assert
        with patch("nwreadinglistcli.Validator") as validator_class:
            validator_instance = validator_class.return_value
            validator_instance.validate_nrows.side_effect = Exception(message)
            
            with self.assertRaises(Exception) as context:
                CLIValidator().validate_nrows(nrows = nrows)
            
            self.assertEqual(message, str(context.exception))
class APFactoryTestCase(unittest.TestCase):

    @parameterized.expand([
        ("save", CLISTRING.OPTION_INPUTPATH_FLAGS[0]),
        ("save", CLISTRING.OPTION_NROWS_FLAGS[0]),
        ("save", CLISTRING.OPTION_FOLDERPATH_FLAGS[0])
    ])
    def test_create_shouldreturnexpectedargumentparser_wheninvoked(self, command_name : str, flag : str) -> None:

        # Arrange
        # Act
        argument_parser : ArgumentParser = APFactory().create()

        # Assert
        self.assertIsInstance(argument_parser, ArgumentParser)

        arguments : list[str] = []
        for command in argument_parser._actions:
            if isinstance(command, _SubParsersAction):
                if command_name in command.choices:
                    for action in command._name_parser_map[command_name]._actions:
                        arguments.extend(action.option_strings)

        self.assertIn(flag, arguments)
    
    def test_create_shouldraiseerror_whenrequiredruntimeargumentismissing(self):

        # Arrange
        args_list : list[str] = CLISTRING.OPTION_INPUTPATH_FLAGS
        argument_parser : ArgumentParser = APFactory().create()

        # Act, Assert
        with patch("sys.stderr", new_callable = StringIO):
            with self.assertRaises(SystemExit):
                argument_parser.parse_args(args_list)
class ReadingListProcessorFactoryTestCase(unittest.TestCase):

    def test_create_shouldreturnreadinglistprocessor_wheninvoked(self) -> None:

        # Arrange
        component_bag : Mock = Mock(spec = ComponentBag)
        setting_bag : Mock = Mock(spec = SettingBag)
        factory : ReadingListProcessorFactory = ReadingListProcessorFactory()

        # Act
        actual : ReadingListProcessor = factory.create(
            component_bag = component_bag, 
            setting_bag = setting_bag
        )

        # Assert
        self.assertIsInstance(actual, ReadingListProcessor)
        self.assertEqual(actual._ReadingListProcessor__component_bag, component_bag)  # type: ignore
        self.assertEqual(actual._ReadingListProcessor__setting_bag, setting_bag)      # type: ignore
class CLIManagerTestCase(unittest.TestCase):

    def test_lognamespace_shouldlogallarguments_wheninvoked(self) -> None:

        # Arrange
        namespace : Namespace = Namespace(input_path = "readinglist.xlsx", nrows = 371, folder_path = "/current/directory/")
        logging_function : Mock = Mock()
        cli_manager : CLIManager = CLIManager(logging_function = logging_function)

        # Act
        cli_manager._CLIManager__log_namespace(namespace = namespace) # type: ignore

        # Assert
        self.assertEqual(logging_function.call_count, 4)
        logging_function.assert_any_call("input_path: 'readinglist.xlsx'")
        logging_function.assert_any_call("nrows: '371'")
        logging_function.assert_any_call("folder_path: '/current/directory/'")
        logging_function.assert_any_call("")   
    
    def test_getdefaultoutputpath_shouldreturnexpectedstring_wheninvoked(self) -> None:

        # Arrange
        expected : str = "/current/directory/"
        
        with patch("os.getcwd", return_value = "/current/directory/"):
            
            # Act
            actual : str = CLIManager()._CLIManager__get_cwd_path()  # type: ignore

            # Assert
            self.assertEqual(expected, actual)   

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)