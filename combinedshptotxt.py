#region Arbitrary Code Block
import geopandas as gpd
import json
from shapely.geometry import Polygon
import sys
from pre_process import pre_processing
from util import get_geometry_string, match_address, combining_shp_files, koaza_existence, dynamic_filtername, fullWidthToHalfWidth
import random

OUTPUT_FOLDER = 'C:/workspace/shp_to_txt/output/'

config = pre_processing()
if config['shp_combine'] == "yes":
    config['shp_file_path'] = combining_shp_files(config['shp_file_path'])

print("Loading the shp_files...")
print(config['shp_file_path'], config['shp_file_charset'])
shp_file = gpd.read_file(config['shp_file_path'], encoding=config['shp_file_charset'])
header_from_shp = shp_file.columns.tolist()
denominator = len(shp_file)
shp_file.crs = f'EPSG:{config['epsg']}'
shp_file = shp_file.to_crs(f"EPSG:4326")  # WGS84

output_txt_path = config['pref_name'] + config['city_name'] + "_" + config['coord_sys'] + "_" + config['coord_sys_no'] + ".txt"
print('Output path...')
print(output_txt_path)
f = open(f'{OUTPUT_FOLDER}{output_txt_path}', 'w', encoding='utf-8-sig', newline='')

count_instances = {}
status = 0
aza_unknown = 0
aza_incorrect = 0
branch_unknown = 0
skip = 0
geometry_null = 0
error_line = 1
renamed_branches = []
printed_errors = {}
if config['data_format'] == "linkkey":pass
elif config['data_format'] == "linkkey_column":pass
elif config['data_format'] == "columns":pass
else:
    print("Your input: '"+ config['data_format']+"' is invalid. Only linkkey, columns and linkkey_column are accepted!")
    sys.exit(0)
#endregion

for index, line in shp_file.iterrows():
    if config['data_format'] == "linkkey":
        linkkey = line[config['linkkey_header_arr'][0]]
        if linkkey is not None:
            debug_count = 0
            linkkey_list = linkkey.split(config['linkkey_delimiter'], 2)
            aza_origin = linkkey_list[0]
            debug_count += 1
            unsplit = linkkey_list[1]
            splt = unsplit.split(config['aza_delimiter'], 2)
            unsplit_list = []
            for x in splt:
                unsplit_list.append(x)
                if len(unsplit_list) >= 2:
                    break
            branch = config['aza_delimiter'].join(unsplit_list)
        else:
            aza_origin = None
            branch = "地番不明"
    elif config['data_format'] == "columns":
        if koaza_existence() == False:
            aza_origin = line[config['COLUMNS_ARGUMENTS']['aza_header_arr'][0]]
        else:
            aza_pt1 = line[config['COLUMNS_ARGUMENTS']['aza_header_arr'][0]]

            if len(config['COLUMNS_ARGUMENTS']['aza_header_arr'][1]) == 0:
                aza_origin = aza_pt1
            else:
                aza_pt2 = line[config['COLUMNS_ARGUMENTS']['aza_header_arr'][1]]
                aza_origin = aza_pt1 + aza_pt2
        aza_origin = dynamic_filtername(aza_origin)
        branch_value_arr = []
        for branch_header in config['branch_header_arr']:
            if not branch_header:
                continue
            if line[branch_header] is not None and line[branch_header] != 0:
                branch_value_arr.append(str(line[branch_header]))
        branch = "-".join(branch_value_arr)
        if branch is not None and branch != '':
            found = branch.find("+")
            if found != -1:
                branch = branch[0:found]
            found = branch.find("--")
            if found != -1:
                branch = branch[0:found]
        # if config['master_data_path1']:
        #     branch = config['masterdata'][aza_origin]['branch']
        else:
            branch = "地番不明"
    elif config['data_format'] == "linkkey_column":
        temp = line[config['COLUMNS_ARGUMENTS']['aza_header_arr'][0]]
        if config['linkkey_column'] == "split":
            if temp:
                aza_list = temp[0:config['length']]
                aza_origin = "".join(aza_list)
            else:
                aza_origin = None
        branch_value_arr = []
        for branch_header in config['branch_header_arr']:
            if not branch_header:
                continue
            if line[branch_header] is not None and line[branch_header] != 0:
                branch_value_arr.append(str(line[branch_header]))
        branch = "-".join(branch_value_arr)
        if branch is not None and branch != '':
            found = branch.find("+")
            if found != -1:
                branch = branch[0:found]
            found = branch.find("--")
            if found != -1:
                branch = branch[0:found]
        # if config['master_data_path1']:
        #     branch = config['masterdata'][aza_origin]['branch']
        else:
            branch = "地番不明"

    branch = fullWidthToHalfWidth(branch)
    if not branch.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9',
                            '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬',
                            '癸','イ', 'ロ', 'ハ', 'ニ', 'ホ', 'ヘ', 'ト')):
        count = count_instances.get(branch, 0)
        new_branch = branch if count == 0 else f"{branch}-{count}"
        renamed_branches.append(new_branch)
        count_instances[branch] = count + 1
        branch = new_branch

    aza_str = None
    if config['masterdata'] and (aza_origin != '') and aza_origin:
        aza_str = config['masterdata'][aza_origin]['aza_name']


    else:
        aza_str = aza_origin


    if config['skip_address_match']:
        aza_str = ''
    elif not aza_str:
        aza_str = "所在不明"
        aza_unknown += 1
        branch_unknown += 1
    else:
        is_matched, oaza_str, koaza_str, koaza_child = match_address(config['area_dic_json'], config['city_name'], aza_str)
        if is_matched:
            aza_str = oaza_str + koaza_str + koaza_child
        else:
            error_line += 1
            aza_str = aza_str + '(仮'
            error_key = aza_origin + aza_str
            if error_key in printed_errors:
                printed_errors[error_key] += 1
            else:
                printed_errors[error_key] = 1

    if status % 10000 == 0:
        fraction = f"{int(status * 100) / denominator:.3f}"
        print(status, "of", denominator, fraction, "%")

    if line['geometry'] is not None:
        centroid = line['geometry'].centroid
        geo_str = get_geometry_string(line['geometry'], config['offset_x'], config['offset_y'])
    else:
        skip += 1
        continue

    lng = str(round(centroid.x + int(config['offset_x']), 6))
    lat = str(round(centroid.y + int(config['offset_y']), 6))

    f.write(aza_str + '|' + branch + '|' + lng + '|' + lat + '|' + geo_str + "\r\n")
    status += 1


if len(printed_errors) > 0:
    output_error_path = config['pref_name'] + config['city_name'] + "_" + config['coord_sys'] + "_" + config['coord_sys_no'] + "_error.txt"
    error_file = open(f'{OUTPUT_FOLDER}{output_error_path}', 'w', encoding='utf-8-sig', newline='')
    for key, values in printed_errors.items():
        error_file.write(key + " " + str(values) + "\r\n")
    error_file.close

f.close()
# print(renamed_branches) #for checking anomalous branches
print("\n")
print("aza_unknown:", aza_unknown, "of", denominator)
print("branch_unknown:", branch_unknown, "of", denominator)
print("geometry_null:", geometry_null, "of", denominator)
print("skip:", skip, "of", denominator)
print("\n")
print("Shape file has been successfully converted to a txt file\nFilepath is: " + output_txt_path)