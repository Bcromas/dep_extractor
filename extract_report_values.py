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
import csv
import datetime
import json #* for testing/writing out dict to file; can remove later
import copy

def check_clean(this_dict):
    """
    Spot check a dictionary representing a report file & update values for processing.

    Args:
        this_dict - dictionary; to be spot checked & values updated.

    Returns:
        result - dictionary; edited version of this_dict.
    """
    result = copy.deepcopy(this_dict)

    if len(result.items()) <= 0:
        raise ValueError("\nERROR: Cannot find rows for processing. Please inspect the file for possible issues.\n")

    #enforce data types
    edit_count = 0
    for line_num, values_dict in result.items():

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
            # if not values_dict[entry].isalnum(): #? not necessary
            #     #attempt to remove all non alphanumeric values
            #     values_dict[entry] = values_dict[entry].replace('"',"").replace("!","").replace("#","").replace("%","").replace("&","").replace("?","") #! don't remove commas they're expected content
            #     edit_count += 1

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
            # print(f"Before:{entry}#{values_dict[entry]}#")
            if (values_dict[entry] == "CODE=N") or (values_dict[entry] == "(empty)") or (len(values_dict[entry]) == 0):
                values_dict[entry] = None
                edit_count += 1
            else:
                try:
                    values_dict[entry] = float(values_dict[entry])
                except Exception as e: #! how to handle conversion of exceptions? '<5', 'PA682', or errors like '15..5'?
                    print(entry, e)
                    print("*"*8)

            # print(f"After:{entry}#{values_dict[entry]}#")

    # print(f"edit_count: {edit_count}")

    return result

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

    # with open(this_file, "r") as infile:
    #     HEADER = next(infile)
    #     HEADER_split = [i.lower() for i in HEADER.split(",")]
    #     line_num = 2 #to keep numbering consistent w csv file
    #     for line in infile:
    #         #get values for line, combine with header & zip together into line_dict
    #         line_split = line.split(",")
    #         line_dict = dict(zip(HEADER_split, line_split))
    #         line_dict_sub = {key:value for key,value in line_dict.items() if key in [entry.lower() for entry in THESE_KEYS]} #only keep k-v if k is in THESE_COLS
    #         this_file_dict[line_num] = line_dict_sub
    #         line_num += 1
    with open(this_file, "r") as infile:
        HEADER = next(infile)
        HEADER_split = [i.lower() for i in HEADER.split(",")]
        line_num = 2 #to keep numbering consistent w csv file
        reader = csv.reader(infile) #load rest of lines with reader
        for row in reader:
            line_dict = dict(zip(HEADER_split, row))
            line_dict_sub = {key:value for key,value in line_dict.items() if key in [entry.lower() for entry in THESE_KEYS]} #only keep k-v if k is in THESE_COLS
            this_file_dict[line_num] = line_dict_sub
            line_num += 1

    #spot check this_file_dict & clean up values in this_file_dict (e.g. enforce data types)
    check_clean(this_file_dict)

    # with open("this_file_dict.txt", "w") as outfile:
    #     outfile.write(json.dumps(this_file_dict, indent=4, sort_keys=True)) #* used for spot checking loading of file


if __name__ == "__main__":

    if len(sys.argv) == 2:
        try:
            load_report(sys.argv[1])
        except Exception as e:
            print(e)
    else:
        print("\nERROR: Please enter a file name for processing.\n")
