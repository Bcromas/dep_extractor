######################################################################################
# This file is used to extract ammonia, temperature, & pH values from a given report.#
#                                                                                    #
# It can be run by opening a Python terminal & entering:                             #
# "get_njpdes_values.py <file_name.csv>"                                             #
#                                                                                    #
# without the double quotes & where <file_name.csv> is the file you want to extract  # 
# values from. Results will be saved in a new .csv file with the name:               #
# <file_name>_values.csv                                                             #
#                                                                                    #   
######################################################################################

def load_report(this_file):
    """
    Opens file specified by user & performs some simple quality checks.

    Args:
        this_file - string; the file name provided by user through the command line.

    Returns:
        result - 2-tuple; if the report was loaded successfully (True, "Success") else (False, <error_message>)

    """
    print("HERE")


if __name__ == "__main__":
    load_report()
