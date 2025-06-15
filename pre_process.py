import json
import sys
from constant import PREFS
from util import PREFS, combining_shp_files

SHP_FILE_FOLDER = 'C:/workspace/shp_to_txt/input/'
AREA_DICTS_PATH = 'C:/workspace/shp_to_txt/area_dicts/'
MASTER_DATA_FOLDER = 'C:/workspace/shp_to_txt/masterdata/'
input_dir_combine_shp = r'C:\workspace\shp_to_txt\input\SHP_combine_file'


# GEOMETRY_DETERMINER = 'ronald\masterdata\神之川_寺脇_20250305.txt'

# charsets: utf-8-sig, Shift_JIS, utf-8
""" NOTES
py pattern_***.py [pref_name] [city_name]
[shp_file_path] [shp_file_charset] [aza_header]
 [branch_header] [coord_sys] [coord_sys_no]
[master_data_path]
use: not all headers need to be inputted just need to have # to seperate them ### note K10037 found in masterdata
py pattern_columns_runner.py 富山県 滑川市 福島県相馬市_s.joined.shp UTF-8 字名 地番＿po#地番＿pt JGD2011 7 福島県相馬市_masterdata.txt
py cols_2_converter.py 埼玉県 日高市 固定資産土地.shp 大字コード#小字コード 本番#枝番#枝1#枝2#枝3 JGD2011 9 none


"""


def pre_processing():
    config = {}
    with open('args.json', 'r', encoding='utf-8') as file:  # getting args from json
        jsn = json.load(file)
    config = jsn
    for key, value in jsn.items(): # clears leading or trailing spaces
        if isinstance(value, str):
            jsn[key] = value.replace(" ","")

    # def find_space_in_strings(config): # true or false
    #     if isinstance(config, str):
    #         return " " in config
    #         # returns a is a true or false
    #     elif isinstance(config, dict):
    #         # Check in each value recursively.
    #         return any(find_space_in_strings(value) for value in config.values())
    #     elif isinstance(config, list):
    #         # Check each item in the list.
    #         return any(find_space_in_strings(item) for item in config)
    #     return False
    #         # For any other types that are not string/dict/list.

    # if find_space_in_strings(jsn):
    #     print("There is a space in one of the values")
    #     sys.exit(0)


    config['shp_file_path'] = SHP_FILE_FOLDER + jsn["shp_file_path"]
    master_data_path = jsn["master_data_path"]
    master_data_path1 = jsn["master_data_path1"]
    master_data_charset = jsn["master_data_charset"]
    coord_sys = jsn["coord_sys"]
    coord_sys_no = jsn["coord_sys_no"]
    pref_name = jsn['pref_name']
    config['shp_combine'] = jsn['shp_combine']
    config['aza_header_arr'] = jsn['COLUMNS_ARGUMENTS']['aza_header_arr']
    config['aza_delimiter'] = jsn['aza_delimiter']
    config['branch_header_arr'] = jsn['COLUMNS_ARGUMENTS']['branch_header_arr']
    config['linkkey_header_arr'] = jsn['LINKKEY_ARGUMENTS']['linkkey_header_arr']
    config['linkkey_delimiter'] = jsn['LINKKEY_ARGUMENTS']['linkkey_delimiter']
    config['data_format'] = jsn['data_format']
    # config['length'] = jsn['linkkey_column_length']
    # config['action'] = jsn['linkkey_column']
    config['koaza'] = jsn['koaza']
    with open('epsg_dic.json', 'r', encoding='utf-8') as f:
        epsg_dic = json.load(f)
    config['epsg'] = epsg_dic[coord_sys][int(coord_sys_no)]
    pref_code = [code for code, name in PREFS.items() if name == pref_name][0]
    pref_code = f"{pref_code:02d}"
    area_dic_file = open(f'{AREA_DICTS_PATH}{pref_code}.json', 'r', encoding='utf-8-sig')
    config['area_dic_json'] = json.load(area_dic_file)

    if master_data_path == '':
        config['masterdata'] = None
    else:
        config['masterdata'] = {}
        with open(f'{MASTER_DATA_FOLDER}{master_data_path}', 'r', encoding= master_data_charset) as file:
            for line in file:
                line_arr = line.strip().split("\t")
                config['masterdata'][line_arr[0]] = {'aza_name': line_arr[1]}

    if master_data_path1 == '':
        config['masterdata1'] = None
    else:
        config['masterdata1'] = {}
        with open(f'{MASTER_DATA_FOLDER}{master_data_path1}', 'r', encoding= master_data_charset) as file:
            for line in file:
                line_arr = line.strip().split("\t")
                config['masterdata'][line_arr[0]] = {'branch': line_arr[1]}
    # def masterdata_addon(aza_origin):
    #     config['masterdata'].append(aza_origin)
    #     config['masterdata'][line_arr[0]] = line_arr[1]
    #     {'aza_name': line_arr[1]}
    #     return config['masterdata']
# pref_code, area_dic_json, shp_file_path, shp_file_charset, \
#         aza_header_arr, branch_header_arr, coord_sys, coord_sys_no, epsg, masterdata, aza_delimiter, branch_delimiter
    return config