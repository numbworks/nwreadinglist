'''
    A CLI application that can run several automated data analysis tasks on a reading list and save the results as a PDF report.
'''

# GLOBAL MODULES
import os
from argparse import _SubParsersAction, ArgumentParser, Namespace
from typing import Any, Final

# LOCAL/NW MODULES
from nwreadinglist import ReadingListProcessor, RLSummary, ComponentBag, SettingBag
from setupinfo import PROJECT_VERSION, PROJECT_ALIAS, CLI_DESCRIPTION

# CONSTANTS
class CLISTRING:

    '''Collects all the CLI-related strings.'''

    COMMAND_DEST : Final[str] = "command"
    COMMAND_REQUIRED : Final[bool] = True
    COMMAND_ARGS : dict[str, Any] = { "dest": COMMAND_DEST, "required": COMMAND_REQUIRED }

    COMMAND_SAVE_NAME : Final[str] = "save"
    COMMAND_SAVE_HELP : Final[str] = "Runs all the data analysis tasks against the reading list and save the outcome as PDF report."

    OPTION_INPUTPATH_FLAGS : Final[list[str]] = ["--input_path"]
    OPTION_INPUTPATH_DEST : Final[str] = "input_path"
    OPTION_INPUTPATH_REQUIRED : Final[bool] = True
    OPTION_INPUTPATH_HELP : Final[str] = "The path to the reading list file in Excel format."

    OPTION_OUTPUTPATH_FLAGS : Final[list[str]] = ["--output_path"]
    OPTION_OUTPUTPATH_DEST : Final[str] = "output_path"
    OPTION_OUTPUTPATH_REQUIRED : Final[bool] = False
    OPTION_OUTPUTPATH_HELP : Final[str] = "The path to the outcome report in PDF format."

# STATIC CLASSES
class _MessageCollectionAsciiBannerManager:

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def provided_version_empty_whitespace() -> str:
        return "The provided 'version' is empty or whitespace."
class _MessageCollectionValidator:

    '''Collects all the messages used for logging and for the exceptions used by Validator.'''

    @staticmethod
    def provided_file_path_doesnt_exist(file_path : str) -> str:
        return f"The provided 'file_path' doesn't exist: '{file_path}'."
class _MessageCollection(
        _MessageCollectionAsciiBannerManager,
        _MessageCollectionValidator):

    '''Collects all the messages used for logging and for the exceptions.'''

# CLASSES
class AsciiBannerManager:

    """Creates the ASCII banner for the provided library's version."""

    def __validate(self, version: str) -> None:
        
        """Validates the provided 'version'."""

        if not version or not version.strip():
            raise ValueError(_MessageCollection.provided_version_empty_whitespace())
    def __create_figlet(self) -> tuple:
        
        """Returns a tuple containing the figlet and its width."""
        
        lines : list[str] = [
            "'##::: ##:'##:::::'##:'########::'########::::'###::::'########::",
            " ###:: ##: ##:'##: ##: ##.... ##: ##.....::::'## ##::: ##.... ##:",
            " ####: ##: ##: ##: ##: ##:::: ##: ##::::::::'##:. ##:: ##:::: ##:",
            " ## ## ##: ##: ##: ##: ########:: ######:::'##:::. ##: ##:::: ##:",
            " ##. ####: ##: ##: ##: ##.. ##::: ##...:::: #########: ##:::: ##:",
            " ##:. ###: ##: ##: ##: ##::. ##:: ##::::::: ##.... ##: ##:::: ##:",
            " ##::. ##:. ###. ###:: ##:::. ##: ########: ##:::: ##: ########::",
            "..::::..:::...::...:::..:::::..::........::..:::::..::........:::"
        ]

        return (os.linesep.join(lines), len(lines[0]))
    def __create_frame(self, version: str, max_length: int) -> tuple:
        
        """Returns a tuple containing the frame of the figlet."""
        
        version_token : str = f"Version: {version}"
        
        margin_length : int = 5
        total_length : int = max_length - len(version_token) - margin_length

        top_line : str = "*" * max_length
        bottom_line : str = f"{top_line[:total_length]}{version_token}{'*' * margin_length}"

        return (top_line, bottom_line)

    def create(self, version: str) -> str:
        
        """Creates the formatted ASCII banner with a versioned frame."""
        
        self.__validate(version)

        figlet, max_length = self.__create_figlet()
        top_line, bottom_line = self.__create_frame(version, max_length)

        ascii_banner : str = os.linesep.join([
            top_line,
            figlet,
            bottom_line,
            ""
        ])

        return ascii_banner
class Validator:

    '''Collects all validation methods.'''

    @staticmethod
    def validate_file_path(file_path : str) -> None:

        '''Returns file_path or raises Exception.'''
        
        if not os.path.isfile(file_path):
            raise Exception(_MessageCollection.provided_file_path_doesnt_exist(file_path))
class CLIValidator:

    '''Handles CLI argument validation.'''

    def validate_file_path(self, file_path: str) -> str:

        '''Returns file_path or raises Exception.'''

        Validator().validate_file_path(file_path)

        return file_path
class APFactory():

    '''Encapsulates all the logic related to the creation of a custom instance of argparse.ArgumentParser.'''

    __cli_validator : CLIValidator

    def __init__(self, cli_validator : CLIValidator = CLIValidator()) -> None:
        self.__cli_validator = cli_validator

    def __add_option_input_path(self, argument_parser : ArgumentParser) -> None:
        
        '''Adds the option mentioned in the method name.'''
        
        argument_parser.add_argument(
            *CLISTRING.OPTION_INPUTPATH_FLAGS,
            dest = CLISTRING.OPTION_INPUTPATH_DEST,
            required = CLISTRING.OPTION_INPUTPATH_REQUIRED,
            help = CLISTRING.OPTION_INPUTPATH_HELP,
            type = self.__cli_validator.validate_file_path
        )
    def __add_option_output_path(self, argument_parser : ArgumentParser) -> None:
        
        '''Adds the option mentioned in the method name.'''
        
        argument_parser.add_argument(
            *CLISTRING.OPTION_OUTPUTPATH_FLAGS,
            dest = CLISTRING.OPTION_OUTPUTPATH_DEST,
            required = CLISTRING.OPTION_OUTPUTPATH_REQUIRED,
            help = CLISTRING.OPTION_OUTPUTPATH_HELP,
            type = self.__cli_validator.validate_file_path
        )

    def create(self) -> ArgumentParser:

        '''
            Creates a custom instance of argparse.ArgumentParser.

            The "prog" argument is not provided in order to make the "usage" statement dynamic:

                usage: nwreadinglistcli.py [-h] ...
        '''

        argument_parser : ArgumentParser = ArgumentParser(description = CLI_DESCRIPTION)
        root : _SubParsersAction[ArgumentParser] = argument_parser.add_subparsers(**CLISTRING.COMMAND_ARGS)

        savefetcher : ArgumentParser = root.add_parser(
            name = CLISTRING.COMMAND_SAVE_NAME, 
            help = CLISTRING.COMMAND_SAVE_HELP
        )

        self.__add_option_input_path(savefetcher)
        self.__add_option_output_path(savefetcher)

        return argument_parser


# MAIN
def main(): pass

if __name__ == "__main__":
    main()