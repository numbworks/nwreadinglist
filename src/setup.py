'''Contains packaging information about nwreadinglist.py.'''

# GLOBAL MODULES
from setuptools import setup

# INFORMATION
MODULE_ALIAS : str = "nwrl"
MODULE_NAME : str = "nwreadinglist"
MODULE_VERSION : str = "4.3.0"

# SETUP
if __name__ == "__main__":
    setup(
        name = MODULE_NAME,
        version = MODULE_VERSION,
        description = "An application designed to run automated data analysis tasks on 'Reading List.xlsx'.",
        author = "numbworks",
        url = f"https://github.com/numbworks/{MODULE_NAME}",
        py_modules = [ MODULE_NAME ],
        install_requires = [
            "numpy>=2.1.2",
            "pyarrow>=17.0.0",
            "openpyxl>=3.1.5",
            "pandas>=2.2.3",
            "requests>=2.32.3",
            "matplotlib>=3.9.2",        
            "tabulate>=0.9.0",
            "sparklines>=0.5.0",
            "nwshared @ git+https://github.com/numbworks/nwshared.git@v1.8.1#egg=nwshared&subdirectory=src"
        ],
        python_requires = ">=3.12",
        license = "MIT"
    )