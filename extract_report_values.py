######################################################################################
# This file is used to extract ammonia, temperature, & pH values from a given report.#
#                                                                                    #
# It can be run by opening a Python terminal & entering:                             #
# "extract_report_values.py <file_name.csv>"                                         #
#                                                                                    #
# without the double quotes & where <file_name.csv> is the file you want to extract  # 
# values from. Results will be saved in a new .csv file with the name:               #
# <file_name>_values.csv                                                             #
#                                                                                    #   
######################################################################################

import sys
import datetime

def check_clean(this_dict):
    """
    Spot check a dictionary representing a report file & update values for processing.

    Args:
        this_dict - dictionary; to be spot checked & values updated.

    Returns:
        result - dictionary; updated version of this_dict.
    """

    if len(this_dict.items()) <= 0:
        raise ValueError("ERROR\nCannot find rows for processing. Please inspect the file for possible issues.")

    #enforce data types
    edit_count = 0
    for line_num, values_dict in this_dict.items():

        #string values
        for entry in [
            "sample point description",
            "dmr parameter description abbrv.",
            "concentrated average stat base",
            "concentration maximum stat base"
        ]:
            # print(f"Before:{entry}#{values_dict[entry]}#")
            if (values_dict[entry].isspace()) or (len(values_dict[entry]) == 0):
                values_dict[entry] = None
                edit_count += 1
                continue
            if not values_dict[entry].isalnum():
                #attempt to remove all non alphanumeric values
                values_dict[entry] = values_dict[entry].replace('"',"").replace("!","").replace("#","").replace("%","").replace("&","").replace("?","")
                edit_count += 1

            values_dict[entry] = values_dict[entry].strip().lower()
            # print(f"After:{entry}#{values_dict[entry]}#")

        #date values
        for entry in ["mon. period start date"]:
            # print(f"Before:#{values_dict[entry]}#")
            if len(values_dict[entry]) == 0:
                values_dict[entry] = None
                edit_count += 1
            else:
                values_dict[entry] = datetime.datetime.strptime(values_dict[entry], "%m/%d/%Y %H:%M")
            # print(f"After:#{values_dict[entry]}#")

        #float values
        for entry in ["reported value concentration avg", "reported value concentration max"]:
            print(f"Before:{entry}#{values_dict[entry]}#")
            if (values_dict[entry] == "CODE=N") or (values_dict[entry] == "(empty)") or (len(values_dict[entry]) == 0):
                values_dict[entry] = None
                edit_count += 1
            else:
                try:
                    values_dict[entry] = float(values_dict[entry])
                except Exception as e:
                    print("*"*8)
                    print(line_num, e)
                    print("*"*8)

            print(f"After:{entry}#{values_dict[entry]}#")

    print(edit_count)       

def load_report(this_file):
    """
    Opens file specified by user & performs some simple quality checks.

    Args:
        this_file - string; the file name provided by user through the command line.

    Returns:
        result - 2-tuple; if the report was loaded successfully (True, "Success") else (False, <error_message>)

    """

    this_file_dict = {} #dictionary of dictionaries representing this_file; keys = line_num, values = dictionary

    #columns we'll use during processing
    THESE_KEYS = [
        "Sample Point Description",         #string
        "DMR Parameter Description Abbrv.", #string
        "Concentrated Average Stat Base",   #string
        "Concentration Maximum Stat Base",  #string
        "Mon. Period Start Date",           #date
        "Reported Value Concentration Avg", #float, CODE=N, (empty), <5
        "Reported Value Concentration Max"  #float, CODE=N, (empty), <5
    ]

    with open(this_file) as infile:
        HEADER = next(infile)
        HEADER_split = [i.lower() for i in HEADER.split(",")]
        line_num = 1 #start counting at first row of data
        for line in infile:
            #get values for line, combine with header & zip together into line_dict
            line_split = line.split(",")
            line_dict = dict(zip(HEADER_split, line_split))
            line_dict_sub = {key:value for key,value in line_dict.items() if key in [entry.lower() for entry in THESE_KEYS]} #only keep k-v if k is in THESE_COLS
            this_file_dict[line_num] = line_dict_sub
            line_num += 1

    #spot check this_file_dict & clean up values in this_file_dict (e.g. enforce data types)
    # check_clean(this_file_dict)
    #! Spot check dict entries for completeness (e.g. line_num = 823, 824, 836, 1140, 1141, 1142)

if __name__ == "__main__":

    if len(sys.argv) == 2:
        try:
            load_report(sys.argv[1])
        except Exception as e:
            print(e)
    else:
        print("Please enter a file name for processing.")
