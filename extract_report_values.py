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

import sys

def load_report(this_file):
    """
    Opens file specified by user & performs some simple quality checks.

    Args:
        this_file - string; the file name provided by user through the command line.

    Returns:
        result - 2-tuple; if the report was loaded successfully (True, "Success") else (False, <error_message>)

    """

    this_file_dict = {} #dictionary of dictionaries representing this_file; keys = line_num, values = dictionary

    with open(this_file) as infile:
        HEADER = next(infile)
        HEADER_split = HEADER.split(",")
        line_num = 1 #start counting at first row of data
        for line in infile:
            line_split = line.split(",")
            #get values for line, combine with header & zip together into line_dict
            line_dict = dict(zip(HEADER_split, line_split))
            this_file_dict[line_num] = line_dict
            line_num += 1

    #get subset of columns in this_file_dict

    #spot check this_file_dict

    #clean up values in this_file_dict (e.g. enforce data types)

if __name__ == "__main__":

    if len(sys.argv) == 2:
        try:
            load_report(sys.argv[1])
        except Exception as e:
            print(e)
    else:
        print("Please enter a file name for processing.")
