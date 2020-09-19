######################################################################################
# This file is used to extract ammonia, temperature, & pH values from a given report.#
#                                                                                    #
# It can be run by opening a Python terminal & entering:                             #
# "extract_report_values.py <file_name.csv>"                                         #
#                                                                                    #
# without the double quotes & where <file_name.csv> is the file you want to extract  # 
# values from. Results will be saved in a new .csv file with the name:               #
# <datetime>_VALUES_FOR-<file_name>.csv                                              #
#                                                                                    #   
######################################################################################

import sys
import csv
import collections
import datetime
import copy

def check_clean(this_dict):
    """
    Spot check a dictionary representing a report file & update values for processing.

    Args:
        this_dict - dictionary; to be spot checked & values updated.

    Returns:
        this_dict_updated - dictionary; edited version of this_dict.
    """
    this_dict_updated = copy.deepcopy(this_dict)

    #enforce data types
    for values_dict in this_dict_updated.values():

        #string values
        for entry in [
            "sample point description",
            "dmr parameter description abbrv.",
            "concentrated average stat base",
            "concentration maximum stat base"
        ]:

            if (values_dict[entry].isspace()) or (len(values_dict[entry]) == 0):
                values_dict[entry] = None
                continue

            values_dict[entry] = values_dict[entry].strip().lower()

        #date values
        for entry in ["mon. period start date"]:
            if len(values_dict[entry]) == 0:
                values_dict[entry] = None
            else:
                try:
                    values_dict[entry] = datetime.datetime.strptime(values_dict[entry], "%m/%d/%Y %H:%M")
                except:
                    try:
                        values_dict[entry] = datetime.datetime.strptime(values_dict[entry], "%m/%d/%Y") #* try without hours, mins
                    except:
                        raise ValueError("\nERROR: Cannot process value in Mon. Period Start Date.\nCheck source file.\n")
        
    return this_dict_updated

def load_report(this_file):
    """
    Opens file specified by user & performs some simple quality checks.

    Args:
        this_file - string; the file name provided by user through the command line.

    Returns:
        this_file_dict - dictionary; a cleaned, updated, & shortened dictionary based on this_file.
    """

    this_file_dict = {} #dictionary of dictionaries representing this_file; keys = line_num, values = dictionary

    #columns we'll use during processing
    THESE_KEYS = [
        "Sample Point Description",         #string
        "DMR Parameter Description Abbrv.", #string
        "Concentrated Average Stat Base",   #string
        "Concentration Maximum Stat Base",  #string
        "Mon. Period Start Date",           #date
        "Reported Value Concentration Avg", #float
        "Reported Value Concentration Max"  #float
    ]

    with open(this_file, "r") as infile:
        HEADER = next(infile)
        HEADER_split = [i.lower() for i in HEADER.split(",")]

        #* verify all keys are in header
        for entry in THESE_KEYS:
            if entry.lower() in HEADER_split:
                continue
            else:
                raise ValueError(f"{entry} not found in {this_file}")

        line_num = 2 #* to keep numbering consistent w csv file
        reader = csv.reader(infile)
        for row in reader:
            line_dict = dict(zip(HEADER_split, row))
            line_dict_sub = {key:value for key,value in line_dict.items() if key in [entry.lower() for entry in THESE_KEYS]} #* only keep k-v if k is in THESE_COLS
            this_file_dict[line_num] = line_dict_sub
            line_num += 1

        #* verify each col has at least one value in it
        c = collections.Counter()
        for row, entry in this_file_dict.items():
            for k, v in entry.items():
                if len(v)>0:
                    c.update([k])
        for entry in THESE_KEYS:
            if c[entry.lower()]==0:
                raise ValueError(f"No values found in '{entry}' column.")

    return this_file_dict

def get_values(dict_clean):
    """
    Retrieve the values for ammonia, temperature, and pH.

    Args:
        dict_clean - dictionary; contains a cleaned & updated subset of values from original input file.

    Returns:
        extracted_vals - dictionary; the values retrieved from dict_clean.
    """

    dates_used = [] # To hold the dates for all temp. & pH data points used

    dict_clean_sub = {}
    for main_key, main_value in dict_clean.items():
        if main_value["sample point description"] == "effluent gross value":
            dict_clean_sub[main_key] = main_value

    ######################## 
    ## Temperature Values ##

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
    dates_used.extend([i["mon. period start date"] for i in temp_summer_list_sort][:20]) # collect the dates related to the values captured
    temp_winter_values = [i["reported value concentration avg"] for i in temp_winter_list_sort][:10]
    dates_used.extend([i["mon. period start date"] for i in temp_winter_list_sort][:10])
    
    ###############
    ## pH Values ##

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
    dates_used.extend([i["mon. period start date"] for i in ph_summer_list_sort][:30]) # collect the dates related to the values captured
    ph_winter_values = [i["reported value concentration max"] for i in ph_winter_list_sort][:30]
    dates_used.extend([i["mon. period start date"] for i in ph_winter_list_sort][:30])

    ####################
    ## Ammonia Values ##
    #TODO streamline code below, if user can understand simplified version

    #chronic values
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
    
    n_summer_chronic_nums = []
    for i in n_summer_chronic_values:
        try:
            n_summer_chronic_nums.append(float(i))
        except:
            n_summer_chronic_nums.append(0.0)

    n_winter_chronic_nums = []
    for i in n_winter_chronic_values:
        try:
            n_winter_chronic_nums.append(float(i))
        except:
            n_winter_chronic_nums.append(0.0)
    
    try:
        n_summer_chronic_max = max(n_summer_chronic_nums)
        n_winter_chronic_max = max(n_winter_chronic_nums)
    except:
        raise ValueError("Cannot find values for summer or winter chronic Ammonia.")

    #acute values
    n_summer_acute_list = [] #May to Oct; max 18 values
    n_winter_acute_list = [] #Nov to Apr; max 18 values
    for main_key, main_value in dict_clean_sub.items():
        if (main_value["dmr parameter description abbrv."] == "nitrogen, ammonia total (as n)") & (main_value["concentration maximum stat base"] == "01damx"): #max = "acute"
            if 5 <= main_value["mon. period start date"].month <= 10:
                n_summer_acute_list.append(main_value)
            elif (11 <= main_value["mon. period start date"].month <= 12) or (1 <= main_value["mon. period start date"].month <= 4):
                n_winter_acute_list.append(main_value)

    n_summer_acute_list_sort = sorted(n_summer_acute_list, key=lambda x: x["mon. period start date"], reverse=True)
    n_winter_acute_list_sort = sorted(n_winter_acute_list, key=lambda x: x["mon. period start date"], reverse=True)
    n_summer_acute_values = [i["reported value concentration max"] for i in n_summer_acute_list_sort][:18] #* can capture more dict values here to validate results
    n_winter_acute_values = [i["reported value concentration max"] for i in n_winter_acute_list_sort][:18]
    
    n_summer_acute_nums = []
    for i in n_summer_acute_values:
        try:
            n_summer_acute_nums.append(float(i))
        except:
            n_summer_acute_nums.append(0.0)

    n_winter_acute_nums = []
    for i in n_winter_acute_values:
        try:
            n_winter_acute_nums.append(float(i))
        except:
            n_winter_acute_nums.append(0.0)
    
    n_summer_acute_max = max(n_summer_acute_nums)
    n_winter_acute_max = max(n_winter_acute_nums)

    min_date = min(dates_used).date()
    max_date = max(dates_used).date()

    extracted_vals = {
        "Earliest date": str(min_date),
        "Most recent date": str(max_date),
        "pH summer values": ph_summer_values,
        "pH winter values": ph_winter_values,
        "Temperature summer values": temp_summer_values,
        "Temperature winter values": temp_winter_values,
        "Ammonia summer acute max": n_summer_acute_max,
        "Ammonia summer acute values": n_summer_acute_values,
        "Ammonia summer chronic max": n_summer_chronic_max,
        "Ammonia summer chronic values": n_summer_chronic_values,
        "Ammonia winter acute max": n_winter_acute_max,
        "Ammonia winter acute values": n_winter_acute_values,
        "Ammonia winter chronic max": n_winter_chronic_max,
        "Ammonia winter chronic values": n_winter_chronic_values
    }

    return extracted_vals

def export_values(found_values, orig_fname):
    """
    Format & export the results to a .csv file.

    Args:
        found_values - dictionary; values found & extracted from original input file.
        orig_fname - string; name of the original input file.

    Returns:
        N/A - a file is created in the current working directory.
    """
    now = datetime.datetime.now()
    stamp = f"{now.year}_{now.month}_{now.day}_{now.hour}{now.minute}"

    with open(f"{stamp}_VALUES_FOR-{orig_fname}", "w") as outfile:
        outfile.write(f"Export of values from: {orig_fname}\n")
        outfile.write(f"Dates used: {found_values['Earliest date']} to {found_values['Most recent date']}")
        outfile.write("\n\n")

        outfile.write("pH summer values")
        counter = 1
        for i in found_values["pH summer values"]:
            outfile.write(f"\n,{counter}:,{i}")
            counter += 1
        outfile.write("\nn")

        outfile.write("pH winter values")
        counter = 1
        for i in found_values["pH winter values"]:
            outfile.write(f"\n,{counter}:,{i}")
            counter += 1
        outfile.write("\n\n")

        outfile.write("Temperature summer values")
        counter = 1
        for i in found_values["Temperature summer values"]:
            outfile.write(f"\n,{counter}:,{i}")
            counter += 1
        outfile.write("\n\n")

        outfile.write("Temperature winter values")
        counter = 1
        for i in found_values["Temperature winter values"]:
            outfile.write(f"\n,{counter}:,{i}")
            counter += 1
        outfile.write("\n\n")

        outfile.write("Ammonia summer acute max,Ammonia summer chronic max,Ammonia winter acute max,Ammonia winter chronic max\n") #the four titles in a row
        outfile.write(f"{found_values['Ammonia summer acute max']},{found_values['Ammonia summer chronic max']},{found_values['Ammonia winter acute max']},{found_values['Ammonia winter chronic max']}")
        outfile.write("\n\n")

        for i in range(18):
            outfile.write(f"{found_values['Ammonia summer acute values'][i]},{found_values['Ammonia summer chronic values'][i]},{found_values['Ammonia winter acute values'][i]},{found_values['Ammonia winter chronic values'][i]}")
            outfile.write("\n")
        

if __name__ == "__main__":

    if len(sys.argv) == 2:
        try:
            fname = sys.argv[1]
            export_values(get_values(check_clean(load_report(fname))), orig_fname=fname)
        except Exception as e:
            print(e)
    else:
        print("\nERROR: Please enter a file name for processing.\n")

#TODO create test cases to check for scenarios where windows cannot find enough values & where values are blank
#TODO fix floats with double decimals