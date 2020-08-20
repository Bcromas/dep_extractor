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

            if (values_dict[entry].isspace()) or (len(values_dict[entry]) == 0):
                values_dict[entry] = None
                edit_count += 1
                continue

            values_dict[entry] = values_dict[entry].strip().lower()

        #date values
        for entry in ["mon. period start date"]:
            if len(values_dict[entry]) == 0:
                values_dict[entry] = None
                edit_count += 1
            else:
                values_dict[entry] = datetime.datetime.strptime(values_dict[entry], "%m/%d/%Y %H:%M")

        #float values
        for entry in ["reported value concentration avg", "reported value concentration max"]:
            # if (values_dict[entry] == "CODE=N") or (values_dict[entry] == "(empty)") or (len(values_dict[entry]) == 0):
            #     values_dict[entry] = None
            #     edit_count += 1
            # else:
            #     try:
            #         values_dict[entry] = float(values_dict[entry])
            #     except Exception as e: #! how to handle conversion of exceptions? '<5', 'PA682', or errors like '15..5'?
            #         print(line_num, entry, e)
            #         print("*"*8)
            values_dict[entry] = values_dict[entry]

    return result

def load_report(this_file):
    """
    Opens file specified by user & performs some simple quality checks.

    Args:
        this_file - string; the file name provided by user through the command line.

    Returns:
        result - dictionary; a cleaned, updated, & shortened dictionary based on this_file.
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

    # with open("this_file_dict.txt", "w") as outfile:
    #     outfile.write(json.dumps(this_file_dict, indent=4, sort_keys=True)) #* used for spot checking loading of file

    #spot check this_file_dict & clean up values in this_file_dict (e.g. enforce data types)
    result = check_clean(this_file_dict)

    # with open("result.txt", "w") as outfile:
    #     outfile.write(json.dumps(result, indent=4, sort_keys=True, default=str)) #* used for spot checking result of check_clean()

    return result

def get_values(dict_clean):
    """
    Retrieve the values for ammonia, temperature, and pH.

    Args:
        dict_clean - dictionary; contains a cleaned & updated subset of values from original input file.

    Returns:
        result - 
    """

    #get subset of entries where 'sample point description' == "effluent gross value"
    dict_clean_sub = {}
    for main_key, main_value in dict_clean.items():
        if main_value["sample point description"] == "effluent gross value":
            dict_clean_sub[main_key] = main_value

    #get temperature values
    temp_summer_list = [] #Jun to Sep; max 20 values
    temp_winter_list = [] #Apr & Nov; max 10 values
    for main_key, main_value in dict_clean_sub.items():
        if (main_value["dmr parameter description abbrv."] == "temperature,  oc") & (main_value["concentrated average stat base"] == "01moav"):
            if 6 <= main_value["mon. period start date"].month <= 9:
                temp_summer_list.append(main_value)
            elif (main_value["mon. period start date"].month == 4) or (main_value["mon. period start date"].month == 11):
                temp_winter_list.append(main_value)
    
    temp_summer_list_sort = sorted(temp_summer_list, key=lambda x: x["mon. period start date"], reverse=True)
    temp_winter_list_sort = sorted(temp_winter_list, key=lambda x: x["mon. period start date"], reverse=True)
    temp_summer_values = [i["reported value concentration avg"] for i in temp_summer_list_sort][:20] #* can capture more dict values here to validate results
    temp_winter_values = [i["reported value concentration avg"] for i in temp_winter_list_sort][:10]

    #get pH values
    ph_summer_list = [] #May to Oct; max 30 values
    ph_winter_list = [] #Nov to Apr; max 30 values
    for main_key, main_value in dict_clean_sub.items():
        if (main_value["dmr parameter description abbrv."] == "ph") & (main_value["concentration maximum stat base"] == "01rpmx"):
            if 5 <= main_value["mon. period start date"].month <= 10:
                ph_summer_list.append(main_value)
            elif (11 <= main_value["mon. period start date"].month <= 12) or (1 <= main_value["mon. period start date"].month <= 4):
                ph_winter_list.append(main_value)

    ph_summer_list_sort = sorted(ph_summer_list, key=lambda x: x["mon. period start date"], reverse=True)
    ph_winter_list_sort = sorted(ph_winter_list, key=lambda x: x["mon. period start date"], reverse=True)
    ph_summer_values = [i["reported value concentration max"] for i in ph_summer_list_sort][:30] #* can capture more dict values here to validate results
    ph_winter_values = [i["reported value concentration max"] for i in ph_winter_list_sort][:30]

    #get ammonia values
    n_summer_chronic_list = [] #May to Oct; max 18 values
    n_winter_chronic_list = [] #Nov to Apr; max 18 values
    for main_key, main_value in dict_clean_sub.items():
        if (main_value["dmr parameter description abbrv."] == "nitrogen, ammonia total (as n)") & (main_value["concentrated average stat base"] == "01moav"): #average = "chronic"
            if 5 <= main_value["mon. period start date"].month <= 10:
                n_summer_chronic_list.append(main_value)
            elif (11 <= main_value["mon. period start date"].month <= 12) or (1 <= main_value["mon. period start date"].month <= 4):
                n_winter_chronic_list.append(main_value)

    n_summer_chronic_list_sort = sorted(n_summer_chronic_list, key=lambda x: x["mon. period start date"], reverse=True)
    n_winter_chronic_list_sort = sorted(n_winter_chronic_list, key=lambda x: x["mon. period start date"], reverse=True)
    n_summer_chronic_values = [i["reported value concentration avg"] for i in n_summer_chronic_list_sort][:18] #* can capture more dict values here to validate results
    n_winter_chronic_values = [i["reported value concentration avg"] for i in n_winter_chronic_list_sort][:18]
    n_summer_chronic_max = max(n_summer_chronic_values) #TODO treat values as numbers, or filter out entries like 'CODE=N'
    n_winter_chronic_max = max(n_winter_chronic_values)
    raise ValueError("Address issue with max value")

    print(n_summer_chronic_values)

    print(n_summer_chronic_max, n_winter_chronic_max)

def export_results(found_values):
    """
    Format & export the results to a .csv file. 
    """
    pass

if __name__ == "__main__":

    if len(sys.argv) == 2:
        try:
            get_values(load_report(sys.argv[1]))
            #TODO call export_results() here
        except Exception as e:
            print(e)
    else:
        print("\nERROR: Please enter a file name for processing.\n")
