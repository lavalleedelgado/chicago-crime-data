'''
Diagnostic: Crime in Chicago
Assignment no. 1
Machine Learning for Public Policy

Patrick Lavallee Delgado
University of Chicago, CS & Harris MSCAPP '20
Tuesday April 9, 2019

Notes:
1. Fix SettingWithCopyWarning in join_crime_with_block_groups().

'''

import json
import re
import requests
import sys
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Point, shape
from shapely.ops import unary_union
import shapely.wkt
from tabulate import tabulate

COMMUNITY_AREAS_API = "https://data.cityofchicago.org/resource/igwz-8jzy.json"
CENSUS_BLOCKS_API = "https://data.cityofchicago.org/resource/bt9m-d2mf.json"
CRIME_DATA_API = "https://data.cityofchicago.org/resource/6zsd-86xi.json"
ACS_API = "https://api.census.gov/data/2017/acs/acs5"

ACS_RACE = {
    "B03002_001E": "race_respondents", # total population
    "B03002_003E": "race_white", # non-Hispanic white
    "B03002_004E": "race_black", # non-Hispanic black
    "B03002_006E": "race_asian", # non-Hispanic Asian
    "B03002_012E": "race_hispanic"} # any Hispanic

ACS_EDUCATION = {
    "B15003_001E": "educ_respondents",
    "B15003_017E": "educ_highschool",
    "B15003_018E": "educ_GED",
    "B15003_021E": "educ_associates",
    "B15003_022E": "educ_bachelors",
    "B15003_023E": "educ_masters",
    "B15003_024E": "educ_professional",
    "B15003_025E": "educ_doctorate"}

ACS_HOUSEHOLD_INCOME = {
    "B19001_001E": "hhinc_respondents",
    "B19001_002E": "hhinc_00_10K",
    "B19001_003E": "hhinc_10_15K",
    "B19001_004E": "hhinc_15_20K",
    "B19001_005E": "hhinc_20_25K",
    "B19001_006E": "hhinc_25_30K",
    "B19001_007E": "hhinc_30_35K",
    "B19001_008E": "hhinc_35_40K",
    "B19001_009E": "hhinc_40_45K",
    "B19001_010E": "hhinc_45_50K",
    "B19001_011E": "hhinc_50_60K",
    "B19001_012E": "hhinc_60_75K",
    "B19001_013E": "hhinc_75_100K",
    "B19001_014E": "hhinc_100_125K",
    "B19001_015E": "hhinc_125_150K",
    "B19001_016E": "hhinc_150_200K"}

ACS_VARIABLES = [ACS_RACE, ACS_EDUCATION, ACS_HOUSEHOLD_INCOME]

COMMUNITY_AREAS_CSV = "chicago-community-areas.csv"
CENSUS_BLOCK_GROUPS_CSV = "chicago-block-groups.csv"
CHICAGO_CRIME_CSV = "chicago-crime.csv"
CENSUS_DATA_CSV = "cook-county-acs5-2017.csv"

def summarize_crime(year_min, year_max, crimes, k_most, demo_from_csv=False):

    communities = compile_community_areas()
    blocks = compile_block_groups(demo_from_csv)
    crime_data = compile_crime_data(year_min, year_max, communities, blocks, demo_from_csv)
    census_data = compile_census_data(ACS_VARIABLES, demo_from_csv)

    # Calculate summary statistics with interesting variables.
    describe_change_overall(crime_data, year_min, year_max)
    print("\n")
    interesting_variables = ["primary_type", "community"]
    for variable in interesting_variables:
        describe_change_in_variable(crime_data, variable, year_min, year_max)
        print("\n")

    # Plot incidence trends of interesting crimes.
    for crime in crimes:
        plot_trend_of_crime_incidence(crime_data, crime)
        print("\n")

    # Identify the k blocks with highest incidence of interesting crimes.
    for crime in crimes:
        print(
            "#### " + crime.upper() + "\n")
        for k in range(k_most):
            describe_block_with_kth_most_crime(crime_data, census_data, \
                year_min, year_max, crime, k)
            print("\n")

    # Refuting Jacob Ringer
    for_ringer = crime_data[crime_data["date"] \
        .map(lambda date: date.month) == 6]
    describe_change_overall(for_ringer, year_min, year_max)
    print("\n")
    
    # Probability of a crime type at 2111 S. Michigan Avenue
    S_MICHIGAN_BLOCK = Point(-87.623565, 41.854015)
    prob_block = gpd \
        .GeoDataFrame([S_MICHIGAN_BLOCK], columns=["the_geom"]) \
        .set_geometry("the_geom")
    prob_block = gpd \
        .sjoin(prob_block, blocks) \
        .drop(columns="index_right")
    prob_block = prob_block["block_group"].iloc[0]
    calculate_probability_by_variable_value(crime_data, "block_group", \
        prob_block, "primary_type")

    # Probability for theft in a community.
    calculate_probability_by_variable_value(crime_data, "primary_type", \
        "THEFT", "community")


def compile_community_areas():

    communities = pd.DataFrame(requests.get(COMMUNITY_AREAS_API).json())
    communities["the_geom"] = communities["the_geom"] \
        .apply(shape)
    communities = gpd.GeoDataFrame(communities) \
        .set_geometry("the_geom") \
        .drop(columns=["area_numbe", "comarea", "comarea_id"])
    return communities


def compile_block_groups(demo_from_csv=False):

    if demo_from_csv:
        blocks = pd.read_csv(CENSUS_BLOCK_GROUPS_CSV, dtype=str)
        blocks["the_geom"] = blocks["the_geom"] \
            .apply(shapely.wkt.loads)
    else:
        blocks = request_census_blocks()
        blocks["block_group"] = blocks["geoid10"] \
            .apply(lambda block: block[:12])
        blocks["the_geom"] = blocks["the_geom"] \
            .apply(shape) \
            .apply(unary_union)
    blocks = gpd.GeoDataFrame(blocks) \
        .set_geometry("the_geom") \
        .drop(columns=blocks.columns.difference(["block_group", "the_geom"]))
    if not demo_from_csv:
        blocks.to_csv(CENSUS_BLOCK_GROUPS_CSV, index=False)
    return blocks


def request_census_blocks(max_records=1000):

    census_blocks = []
    keep_requesting = True
    while keep_requesting:
        request = requests.get(
            CENSUS_BLOCKS_API,
            params=set_census_blocks_params(max_records, len(census_blocks)))
        new_census_blocks = request.json()
        if len(new_census_blocks) < max_records:
            keep_requesting = False
        census_blocks.extend(new_census_blocks)
    return pd.DataFrame(census_blocks)


def set_census_blocks_params(max_records, num_records):

    parameters = {
        "$limit": max_records,
        "$offset": num_records}
    return parameters


def compile_crime_data(year_min, year_max, communities, blocks, demo_from_csv=False):

    if demo_from_csv:
        crime_data = pd.read_csv(CHICAGO_CRIME_CSV, dtype=str)
    else:
        crime_data = request_crime_data(year_min)
        for y in range(1, year_max - year_min + 1):
            crime_data = crime_data.append(request_crime_data(year_min + y))
        crime_data.to_csv(CHICAGO_CRIME_CSV, index=False)
    crime_data["date"] = pd.DatetimeIndex(crime_data["date"]) \
        .normalize()
    crime_data = join_crime_with_community_areas(crime_data, communities)
    crime_data = join_crime_with_block_groups(crime_data, blocks)
    return crime_data


def request_crime_data(year, max_records=1000):

    crime_data = []
    keep_requesting = True
    while keep_requesting:
        request = requests.get(
            CRIME_DATA_API,
            params=set_crime_data_params(year, max_records, len(crime_data)))
        new_crime_data = request.json()
        if len(new_crime_data) < max_records:
            keep_requesting = False
        crime_data.extend(new_crime_data)
    return pd.DataFrame(crime_data)


def set_crime_data_params(year, max_records, num_records):

    parameters = {
        "year": year,
        "$limit": max_records,
        "$offset": num_records}
    return parameters


def compile_census_data(variable_dicts, demo_from_csv=False):

    if demo_from_csv:
        crime_data = pd.read_csv(CENSUS_DATA_CSV, dtype=str)
        return crime_data
    LOCATION_VARIABLES = ["state", "county", "tract", "block group"]
    census_data = request_census_data(variable_dicts.pop())
    for variable_dict in variable_dicts:
        census_data = census_data \
            .merge(
                request_census_data(variable_dict),
                how="outer",
                on=LOCATION_VARIABLES)
    census_data["block_group"] = census_data \
        .apply(
            lambda row: "".join(str(row[var]) for var in LOCATION_VARIABLES),
            axis=1)
    census_data = census_data \
        .drop(columns=LOCATION_VARIABLES)
    if not demo_from_csv:
        census_data.to_csv(CENSUS_DATA_CSV, index=False)
    return census_data


def request_census_data(variable_dict):

    request = requests.get(
        ACS_API,
        params=set_census_data_params(variable_dict))
    census_data = request.json()
    labels = [variable_dict.get(var, var) for var in census_data.pop(0)]
    census_data = pd.DataFrame(census_data, columns=labels)
    census_data = normalize_census_data_variables(census_data, variable_dict)
    return census_data


def set_census_data_params(variable_dict):

    parameters = {
        "get": ",".join(var for var in variable_dict.keys()),
        "for": "block group:*",
        "in": "state:17 county:031"} # Cook County, Illinois
    return parameters


def normalize_census_data_variables(census_data, variable_dict):

    columns, exclude = isolate_respondents_label(variable_dict.values())
    normalized = census_data[columns] \
        .astype(float) \
        .div(census_data[exclude].astype(float), axis=0)
    census_data = census_data.drop(columns=columns)
    census_data = pd.concat([census_data, normalized], axis=1)
    return census_data


def isolate_respondents_label(labels):

    regex = re.compile(r".*_respondents")
    respondents = list(filter(regex.match, labels))[0]
    columns = [col for col in labels if col != respondents]
    return columns, respondents


def join_crime_with_community_areas(crime_data, communities):

    joined_data = crime_data.merge(
        communities[["area_num_1", "community"]],
        left_on="community_area",
        right_on="area_num_1")
    return joined_data


def join_crime_with_block_groups(crime_data, blocks):

    crime_data = crime_data \
        .dropna(subset=["longitude", "latitude"])
    crime_data["the_geom"] = crime_data \
        .apply(
            lambda row: Point(float(row["longitude"]), float(row["latitude"])),
            axis=1)
    crime_data = gpd.GeoDataFrame(crime_data) \
        .set_geometry("the_geom")
    joined_data = gpd \
        .sjoin(crime_data, blocks[["block_group", "the_geom"]]) \
        .drop(columns="index_right")
    return joined_data


def describe_change_overall(crime_data, year_min, year_max):

    crime_data = crime_data \
        .groupby("year") \
        .size()
    crime_data = crime_data.append(
        pd.Series(
            [(crime_data[str(year_max)] - crime_data[str(year_min)]) \
                / crime_data[str(year_min)]], index=["change"]))
    crime_data = crime_data \
        .reset_index()
    crime_data.columns = ["year", "incidents"]
    print(
        tabulate(crime_data, headers="keys", tablefmt="simple", showindex="never"))


def describe_change_in_variable(crime_data, variable, year_min, year_max):

    crime_data = crime_data \
        .groupby(["year", variable]) \
        .size() \
        .unstack(0) \
        .reset_index()
    crime_data["change"] = crime_data \
        .apply(
            lambda row: (row[str(year_max)] - row[str(year_min)]) / row[str(year_min)],
            axis=1)
    crime_data = crime_data \
        .fillna(0) \
        .sort_values(by="change", ascending=False)
    print(
        tabulate(crime_data, headers="keys", tablefmt="simple", showindex="never"))


def plot_trend_of_crime_incidence(crime_data, crime):

    figure, axes = plt.subplots()
    crime_data = crime_data[crime_data["primary_type"] == crime.upper()] \
        .groupby(pd.Grouper(key="date", freq="W-MON"))["primary_type"] \
        .size()
    try:
        crime_data.plot()
        axes.set(
            xlabel="Date",
            ylabel="Incidence",
            title=crime.title())
        plt.show()
    except:
        pass # skip this visualization if there is nothing to plot.


def describe_block_with_kth_most_crime(crime_data, census_data, year_min, year_max, crime, k):
    
    kth_block = crime_data[crime_data["primary_type"] == crime.upper()] \
        .groupby(["year", "block_group"])["primary_type"] \
        .agg(np.size) \
        .fillna(0) \
        .unstack(0) \
        .reset_index() \
        .merge(
            crime_data[["block_group", "community"]].drop_duplicates(),
            on="block_group", how="inner") \
        .merge(census_data, on="block_group", how="left") \
        .sort_values(by=str(year_max), ascending=False) \
        .iloc[k]
    print(
        "\n" + kth_block["community"].title() + ", block no. " + 
        str(kth_block["block_group"]) + ":\n\n"
        "    Ranked no. " + str(k + 1) + " for most CPD responses to " +
        "incidents of " + crime.lower() + " in " + str(year_max) + ":\n" + 
        "    " + str(year_max) + ": " + str(kth_block[str(year_max)]) + "\n" +
        "    " + str(year_min) + ": " + str(kth_block[str(year_min)]) + "\n\n" +
        "    Groups most represented in ACS statistics for this block:")
    kth_block = kth_block \
        .drop(["block_group", "community"]) \
        .astype(float) \
        .sort_values(ascending=False)
    indicators = get_top_block_census_indicators(kth_block, ACS_VARIABLES)
    for indicator, percent in indicators:
        print(
            "    " + indicator + ": " + str(np.round(percent * 100, 2)) + "%")


def get_top_block_census_indicators(block, variable_dicts):

    indicators = []
    for variable_dict in variable_dicts:
        best_indicator = (None, None)
        columns, _ = isolate_respondents_label(variable_dict.values())
        for variable in columns:
            loc = block.index.get_loc(variable)
            if best_indicator[0] is None or loc < best_indicator[0]:
                best_indicator = loc, variable
        if best_indicator[0]:
            indicators.append([
                best_indicator[1],
                block.iloc[best_indicator[0]]])
    return indicators


def calculate_probability_by_variable_value(crime_data, variable, value, group):

    prob_crime = crime_data[crime_data[variable] == value] \
        .groupby(group) \
        .size() \
        .reset_index()
    prob_crime.columns = [group, "incidents"]
    prob_crime["probability"] = prob_crime \
        .apply(
            lambda crime: crime["incidents"] / prob_crime["incidents"].sum(),
            axis=1)
    prob_crime = prob_crime \
        .sort_values(by="probability", ascending=False)
    print(
        tabulate(prob_crime, headers="keys", tablefmt="simple", showindex="never"))
    
    
def run():

    arguments = sys.argv[1:]
    if len(arguments) < 6:
        print(
            "Expected at least five arguments:\n"
            "  1. inclusive upper bound year,\n"
            "  2. inclusive lower bound year,\n"
            "  3. comma delimited crimes,\n"
            "  4. number of highest-incidence blocks,\n"
            "  5. whether to run in demo mode from existing CSV files.")
        sys.exit()
    try:
        demo = bool(arguments.pop())
    except TypeError:
        print(
            "Expected a truth value for the fifth argument:\n"
            "  5. whether to run in demo mode from existing CSV files.")
    try:
        k_most = int(arguments.pop())
    except TypeError:
        print(
            "Expected an integer for the fourth argument:\n"
            "  4. number of highest-incidence blocks.")
    try:
        year_min = int(arguments.pop(0))
        year_max = int(arguments.pop(0))
    except TypeError:
        print(
            "Expected integers for the first two arguments:\n"
            "  1. inclusive upper bound year,\n"
            "  2. inclusive lower bound year.\n")
    crimes = " ".join(arguments)
    if not crimes:
        print(
            "Expected a string for the third argument:\n"
            "  3. comma delimited crimes.")
    crimes = crimes.split(",")
    crimes = [crime.lstrip() for crime in crimes]
    summarize_crime(year_min, year_max, crimes, k_most, demo)
    print(
        "Finished!")


if __name__ == "__main__":
    run()