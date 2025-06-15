import re
import os
import sys
import glob
import json
import pandas
import geopandas
from shapely.geometry import Polygon
sys
with open('args.json', 'r', encoding='utf-8') as file:  # getting args from json
    config = json.load(file)

PREFS = {
    1: '北海道', 2: '青森県', 3: '岩手県', 4: '宮城県', 5: '秋田県', 6: '山形県', 7: '福島県',
    8: '茨城県', 9: '栃木県', 10: '群馬県', 11: '埼玉県', 12: '千葉県', 13: '東京都', 14: '神奈川県', 15: '新潟県',
    16: '富山県', 17: '石川県', 18: '福井県', 19: '山梨県', 20: '長野県', 21: '岐阜県', 22: '静岡県', 23: '愛知県',
    24: '三重県', 25: '滋賀県', 26: '京都府', 27: '大阪府', 28: '兵庫県', 29: '奈良県', 30: '和歌山県', 31: '鳥取県',
    32: '島根県', 33: '岡山県', 34: '広島県', 35: '山口県', 36: '徳島県', 37: '香川県', 38: '愛媛県', 39: '高知県',
    40: '福岡県', 41: '佐賀県', 42: '長崎県', 43: '熊本県', 44: '大分県', 45: '宮崎県', 46: '鹿児島県', 47: '沖縄県'
}

def arabic_to_chinese(input_string):
    """
    Finds sequences of full‐width Arabic numerals immediately preceding the character "丁"
    and converts them into their Chinese numeral representation.

    For example, "遠里小野町１丁" will become "遠里小野町一丁".
    """

    # Mapping for individual Chinese digits.
    chinese_digits = "零一二三四五六七八九"

    def int_to_chinese(num):
        """
        Convert an integer to its Chinese numeral representation.
        This implementation handles numbers up to 9999.
        """
        if num == 0:
            return "零"

        # The units corresponding to each digit position
        units = ["", "十", "百", "千"]
        result = ""
        num_str = str(num)
        length = len(num_str)

        for i, char in enumerate(num_str):
            digit = int(char)
            pos = length - i - 1  # Determine the position from the right

            if digit != 0:
                # Special handling for numbers between 10 and 19:
                # e.g., 10 -> "十", 11 -> "十一" (not "一十一")
                if pos == 1 and digit == 1 and length == 2:
                    result += "十"
                else:
                    result += chinese_digits[digit] + units[pos]
            else:
                # Only add "零" if the previous character is not already "零"
                # and if we are not at the last digit.
                if not result.endswith("零") and i != length - 1:
                    result += "零"

        # Remove any trailing "零"
        if result.endswith("零"):
            result = result[:-1]
        return result

    def convert(match):
        """
        Convert a matched full-width Arabic numeral string to its Chinese numeral equivalent.
        """
        fullwidth_num = match.group(0)
        # Convert full-width digits to ASCII digits using str.translate.
        ascii_num = fullwidth_num.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        num = int(ascii_num)
        return int_to_chinese(num)

    # The regex pattern finds one or more full-width digits that are immediately followed by "丁".
    pattern = r'([０-９]+)(?=丁)'
    # Replace each found match with its Chinese numeral conversion.
    result_string = re.sub(pattern, lambda m: convert(m), input_string)

    return result_string

def special_replace(address): # full width is not a int it is a char string
    dictt =  {
    '１': '一',
    '２': '二',
    '３': '三',
    '４': '四',
    '５': '五',
    '６': '六',
    '７': '七',
    '８': '八',
    '９': '九',
    '１０': '十'
}
    for key in sorted(dictt.keys(), reverse=True):
        address = address.replace(str(key), dictt[key])
    return address

# 漢数字(例: 一、二、三)をアラビア数字(例: 1、2、3)に変換するための関数
def chinese_to_arabic(input_string):
    # 漢数字をアラビア数字に対応付けるマッピング
    numeral_map = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10, '百': 100, '千': 1000, '万': 10000
    }

    def convert_chinese_number(cn_number):
        total = 0
        current_unit = 1  # 現在の単位(漢数字の位)
        current_value = 0  # 現在の数値の積み上げ

        for char in reversed(cn_number):
            value = numeral_map.get(char, None)

            if value >= 10:
                if current_value == 0:
                    current_value = 1
                current_unit = value
                total += current_value * current_unit
                current_value = 0
            else:
                current_value += value * current_unit

        total += current_value
        return str(total)

    # 全ての漢数字をアラビア数字に置き換える
    regex_pattern = r'([零一二三四五六七八九十百千万]+)(?=丁目)'
    arabic_string = re.sub(regex_pattern, lambda m: convert_chinese_number(m.group(0)), input_string)

    return arabic_string

def fullWidthToHalfWidth(s):
    return "".join(
        [chr(ord(char) - 0xFEE0) if '！' <= char <= '～' else char for char in s]
    ).replace('　', ' ')

def halfWidthToFullWidth(s):
    return "".join(
        [chr(ord(char) + 0xFEE0) if '!' <= char <= '~' else char for char in s]
    ).replace(' ', '　')  # Replace half-width space with full-width space

# Function to convert a GeoPandas geometry object (polygon) to a JSON format string
def get_geometry_string(geometry, offset_x = 0, offset_y = 0):
    geo_str = ''
    if isinstance(geometry, Polygon):
        polygon_for_output = []
        for point in geometry.exterior.coords:
            polygon_for_output.append([round(point[0] + offset_x, 6), round(point[1] + offset_y, 6)])
        geo_str = '{"type":"MultiPolygon","coordinates":[[' + json.dumps(polygon_for_output, separators=(',', ':')) + ']]}'
    else:
        multi_polygons_output = []
        for polygon in geometry.geoms:  # Iterate through each Polygon in the MultiPolygon
            polygon_output = []
            for point in polygon.exterior.coords:  # Iterate through the exterior coordinates of the polygon
                polygon_output.append([round(point[0] + offset_x, 6), round(point[1] + offset_y, 6)])  # Round the coordinates and add to list
            if polygon.interiors:  # Check for interior coordinates (holes)
                interiors_output = []
                for interior in polygon.interiors:
                    interior_output = []
                    for point in interior.coords:
                        interior_output.append([round(point[0] + offset_x, 6), round(point[1] + offset_y, 6)])
                    interiors_output.append(interior_output)
                multi_polygons_output.append([polygon_output] + interiors_output)  # Add exterior and interior coords
            else:
                multi_polygons_output.append([polygon_output])  # Add only exterior if no interiors

        geo_str = json.dumps({
            "type": "MultiPolygon",
            "coordinates": multi_polygons_output
        }, separators=(',', ':'))

    return geo_str

def unify(str):
    str = str.replace("ヰ", "井")
    str = str.replace(" ", "")
    str = str.replace("　", "")
    str = str.replace("の", "ノ")
    str = str.replace("之", "ノ")
    str = str.replace("ヶ", "ケ")
    str = str.replace("檜", "桧")
    str = str.replace("藪", "薮")
    str = str.replace("ﾖ", "ョ")
    str = str.replace("ッ", "ツ")
    str = str.replace("ヵ", "カ")
    str = str.replace('瀧','滝')
    str = str.replace("２０丁目", "二十丁目")
    str = str.replace("１９丁目", "十九丁目")
    str = str.replace("１８丁目", "十八丁目")
    str = str.replace("１７丁目", "十七丁目")
    str = str.replace("１６丁目", "十六丁目")
    str = str.replace("１５丁目", "十五丁目")
    str = str.replace("１４丁目", "十四丁目")
    str = str.replace("１３丁目", "十三丁目")
    str = str.replace("１２丁目", "十二丁目")
    str = str.replace("１１丁目", "十一丁目")
    str = str.replace("１０丁目", "十丁目")
    str = str.replace("９丁目", "九丁目")
    str = str.replace("８丁目", "八丁目")
    str = str.replace("７丁目", "七丁目")
    str = str.replace("６丁目", "六丁目")
    str = str.replace("５丁目", "五丁目")
    str = str.replace("４丁目", "四丁目")
    str = str.replace("３丁目", "三丁目")
    str = str.replace("２丁目", "二丁目")
    str = str.replace("１丁目", "一丁目")
    str = str.replace("20丁目", "二十丁目")
    str = str.replace("19丁目", "十九丁目")
    str = str.replace("18丁目", "十八丁目")
    str = str.replace("17丁目", "十七丁目")
    str = str.replace("16丁目", "十六丁目")
    str = str.replace("15丁目", "十五丁目")
    str = str.replace("14丁目", "十四丁目")
    str = str.replace("13丁目", "十三丁目")
    str = str.replace("12丁目", "十二丁目")
    str = str.replace("11丁目", "十一丁目")
    str = str.replace("10丁目", "十丁目")
    str = str.replace("9丁目", "九丁目")
    str = str.replace("8丁目", "八丁目")
    str = str.replace("7丁目", "七丁目")
    str = str.replace("6丁目", "六丁目")
    str = str.replace("5丁目", "五丁目")
    str = str.replace("4丁目", "四丁目")
    str = str.replace("3丁目", "三丁目")
    str = str.replace("2丁目", "二丁目")
    str = str.replace("1丁目", "一丁目")
    replacements = str.maketrans({"ェ": "エ", "工":"エ"})
    str = str.translate(replacements)
    return str

def match_address(district_master_json, city_name, aza_str):
    # level2
    koaza_name = ''
    koaza_child = ''
    v = {key: value for key, value in district_master_json.items() if key.startswith(city_name)}

    oaza_list = district_master_json[next(iter(v))]
    is_matched = False
    addon = {}
    for k2, v2 in sorted(oaza_list.items(), key=lambda x: len(x[0]), reverse=True):
        place_str = aza_str
        oaza_name = k2.split('_')[0]  # 大字名
        place_u = unify(place_str)
        oaza_u = unify(oaza_name)
        # if oaza_u.startswith('鹿央町' + place_u[0]) and ('鹿央町' + place_u).startswith(oaza_u):
        #     place_str = '鹿央町'+ place_str
        if oaza_u.startswith('大字' + place_u[0]) and ('大字' + place_u).startswith(oaza_u):
            place_str = '大字'+ place_str

        if oaza_u.startswith('字' + place_u[0]) and ('字' + place_u).startswith(oaza_u):
            place_str = '字'+ place_str
            # print("  sample matched" + place_str)

        # if oaza_u.startswith('浪岡大字' + place_u[0]) and ('浪岡大字' + place_u).startswith(oaza_u):
        #     place_str = '浪岡大字'+ place_str
        #     prefix = '浪岡大字'

        place_u = unify(place_str)
        if oaza_u.startswith(place_u[0]) and place_u.startswith(oaza_u):
            addon[oaza_name] = v2
            place2_str = place_u.replace(oaza_u, '', 1)
            if place2_str == '':
                is_matched = True
                break

            for k3, v3 in sorted(v2.items(), key=lambda x: len(x[0]), reverse=True):
                koaza_name = k3.split('_')[0]  # 小字名
                # koaza_name = halfWidthToFullWidth(koaza_name) # next layer, use corresponding values
                if not v3:
                    if unify(place2_str) == unify(koaza_name):
                        is_matched = True
                        break
                    else:
                        continue
                place2_u = unify(place2_str)
                koaza_u = unify(koaza_name)
                if koaza_u.startswith(place2_u[0]) and place2_u.startswith(koaza_u):
                    place3_str = place2_u.replace(koaza_u, '', 1)
                    if place3_str == '':
                        is_matched = True
                        break
                    else:
                        for k4, v4 in sorted(v3.items(), key=lambda x: len(x[0]), reverse=True):
                            koaza_child = k4.split('_')[0]
                            if not v4:
                                trash1 = place3_str.replace(koaza_child, '', 1)
                                if trash1 == '':
                                    is_matched = True
                                    break



            if is_matched:
                break

    if not is_matched:
        for k2, v2 in sorted(addon.items(), key=lambda x: len(x[0]), reverse=True):
            place_str = aza_str
            if k2.startswith('大字' + place_str[0]) and ('大字' + place_str).startswith(k2):
                place_str = '大字'+ place_str
            if k2.startswith(place_str[0]) and place_str.startswith(k2):
                koaza_name = place_str.replace(k2, '', 1)
                if len(v2) < 1 and koaza_name != '':
                    is_matched = True
                    aza_str = k2
    if koaza_child == '':
        return is_matched, oaza_name, koaza_name, ''
    else:
        return is_matched, oaza_name, koaza_name, koaza_child
#region Arbitrary Code Block
# place filters, add to database
# def readshpfile(file_path, output_file,shp_file_columns1, shp_file_columns2, shp_file_columns3, shp_file_columns4, encode):
#     master_shp_file = geopandas.read_file(file_path, encoding=encode)
#     master_shp_file.crs = "EPSG:4326"
#     # print(readshp); sys.exit(0)

#     f = open(output_file, "w", encoding="utf-8")
#     # required_columns = [shp_file_columns1, shp_file_columns2]
#     for index, line in master_shp_file.iterrows():
#         col1 = str(line[shp_file_columns1])
#         col2 = str(line[shp_file_columns2])
#         col3 = str(line[shp_file_columns3])
#         col4 = str(line[shp_file_columns4])
#         x = str(col1).zfill(4)+ str(col2).zfill(3) #\r
#         f.write(x + "\t" + col3 + col4+ "\n") #\r

#     for index, line in master_shp_file.iterrows():
#         col1 = str(line[shp_file_columns1])
#         col2 = str(line[shp_file_columns2])
#         col3 = str(line[shp_file_columns3])
#         col4 = str(line[shp_file_columns4])
#         for x in range(100):
#             f.write(col1.zfill(4) + str(x).zfill(3) + "\t" + col3 + "小字不明\n") #\r

#     print("shp written to text file successfully!")
#     f.close()

# def gaiji_filter_愛知県_岡崎市(str):


#     if str.startswith('坂左右町字中丁田'):
#         str = '坂左右町字仲丁田'
#     if str.startswith('野畑町字藪下'):
#         str = '野畑町字薮下'
#     if str.startswith('蓑川町1丁目'):
#         str = '蓑川町１丁目'
#     if str.startswith('蓑川町2丁目'):
#         str = '蓑川町２丁目'
#     if str.startswith('蓑川町3丁目'):
#         str = '蓑川町３丁目'
#     if str.startswith('蓑川町字藪下'):
#         str = '蓑川町字薮下'
#     if str.startswith('みはらし台1丁目'):
#         str = 'みはらし台１丁目'
#     if str.startswith('みはらし台2丁目'):
#         str = 'みはらし台２丁目'
#     if str.startswith('みはらし台3丁目'):
#         str = 'みはらし台３丁目'
#     if str.startswith('生平町字葛藪'):
#         str = '生平町字葛薮'
     # if str.startswith('みはらし台2丁目'):
    #     str = 'みはらし台２丁目'
    # return str


# def gaiji_filter_岐阜県_高山市(str):
#     str = str.replace('ッ', 'ツ')
#     str = str.replace('ヶ', 'ケ')
#     str = str.replace('ノ', '之')
#     str = str.replace('澤','沢')
#     str = str.replace('澤','々')
#     if str.startswith('高根町池ケ洞'):
#         str = '高根町池ケ洞'
#     if str.startswith('国府町瓜巣'):
#         str = '国府町瓜巣'
#     if str.startswith('丹生川町板殿'):
#         str = '丹生川町板殿'
#     if str.startswith('丹生川町下保'):
#         str = '丹生川町下保'
#     if str.startswith('丹生川町大萱'):
#         str = '丹生川町大萱'
#     if str.startswith('上宝町鼠餅字津石'):
#         str = '上宝町鼠餅字津石'
#    return str



# def gaiji_filter_青森県_青森市(str):
#     if str.startswith('王余魚沢字五郎左エ門'):
#         str = '王余魚沢字五郎左エ門釜沢'
#     if str.startswith('王余魚沢字水ヶ沢'):
#         str = '王余魚沢字水ケ沢'
#     if str.startswith('五本松字堤ヶ沢'):
#         str = '五本松字堤ケ沢'
#     if str.startswith('前田字前田'):
#         str = '前田字前田山'
#     # if str.startswith('王余魚沢字水ヶ沢'):
#     #     str = '王余魚沢字水ケ沢'
#     return str




# def gaiji_filter_埼玉県_さいたま市(str):
#     str =  str.replace('新右ェ門新田', '新右衛門新田')
#     str =  str.replace('仲町（浦和）', '仲町')
#     str =  str.replace('大字大谷場字小池下', '大字大谷口')
#     str =  str.replace('弦藩', '玄蕃')
#     str =  str.replace('ケ', 'ヶ')
#     return str

# def gaiji_filter_兵庫県_赤穂郡上郡町(str):
#     str =  str.replace('梨ヶ原', '梨ケ原')
#     str =  str.replace('与井新', '與井新')
#     str =  str.replace('与井', '與井')
#     str =  str.replace('大富', '大冨')
#     return str

# def gaiji_filter_福島県_相馬市(str):
#     str =  str.replace('字大藪', '字大薮')
#     str =  str.replace('霊山道', '霊仙道')
#     str =  str.replace('字与五右エ門屋敷', '字与五右ェ門屋敷')
#     str =  str.replace('字藪内', '字薮内')
#     str =  str.replace('字楢', '字楢這')
#     str =  str.replace('字シﾖガ沢', '字ショガ沢')
#     str =  str.replace('字藪内前', '字薮内前')
#     str =  str.replace('字五郎右エ門橋', '字五郎右ェ門橋')
#     return str

# def aza_filter_北海道_上川郡当麻町(str):
#     str = str.replace('３条東','三条東')
#     str = str.replace('３条西','三条西')
#     str = str.replace('４条西','四条西')
#     str = str.replace('４条東','四条東')
#     str = str.replace('４条南','四条南')
#     str = str.replace('５条西','五条西')
#     str = str.replace('５条東','五条東')
#     str = str.replace('６条西','六条西')
#     str = str.replace('６条東','六条東')

# def aza_filter_福島県_岩瀬郡天栄村(str):
#     str = str.replace('斧切沢','斧伐沢')
#     str = str.replace('橋向山','向山')
#     str = str.replace('長峯','長峰')
#     str = str.replace('アラタ山','あら田山')
#     str = str.replace('宇桶清水','芋桶清水')
#     str = str.replace('姥子壇','姥子檀')
#     str = str.replace('高礼前','高札前')
#     str = str.replace('七曲','七曲り')
#     str = str.replace('鯖綱','鯖網')
#     str = str.replace('七曲りり','七曲り')
#     str = str.replace('田良大向山','田良尾大向山')
#     return str
# def 福島県石川郡古殿町_filter(str):
#     if str:
#         str = str.replace( 'G', '鵰')
#     return str
# def column_filter_県日置市(str):
#     if str:
#         str =  str.replace(' ', '').replace('　', '')
#         return str
#     else:
#         return str
# def aza_filter_上伊那郡南箕輪村(str):
#     if str:
#         str = str.replace( '南箕輪', '上伊那郡南箕輪村')
#     return str
# # data =
# def 余市郡余市町_filter(kensaku, branch): # note: check if both are strings
#     if not branch:
#         pass
#     elif kensaku in branch:
#         kensaku_arr = branch.replace(kensaku,"") # kensaku is now a list
#         kensaku = kensaku_arr[0]
#     else:
#         pass
#     return branch
# def 栃木県塩谷郡高根沢町_filter(str):
#     if str:
#         str = str.replace('挟間田', '狹間田')
#         str = str.replace('文挟', '文挾')
#         str = str.replace('挟間田', '狹間田')
#         str = str.replace('柿ノ木沢', '柿木沢')
#     return str
# # note: 五所川原市大字高野字 not in 青森市
# # note: 駅東区画Ｂ１ not in 岡崎市

# def 奈良県北葛城郡広陵町_filter(str):
#     if str:
#         str = str.replace('赤部','三吉元赤部方')
#         str = str.replace('大垣内','三吉元大垣内方')
#         str = str.replace('斉音寺','三吉元斉音寺方')
#     return str

# def 和歌山県和歌山市_filter(str):
#     if str:
#         str = str.replace('祢宜', '禰宜')
#     return str

# def 秋田県にかほ市_filter(str):
#     if str:
#         str = str.replace('傳蔵田', '傅蔵田')
#         str = str.replace('字兔森', '字兎森')
#     return str

# def 熊本県上益城郡甲佐町_branch_filter(str):
#     if str:
#         str = str.replace('【','')
#         str = str.replace('】','')
#     return str

# def 神奈川県鎌倉市_azafilter(str):
#     if str:
#         str = str.replace('腰越（未）','腰越')
#         str = str.replace('極楽寺（未）','極楽寺')
#         str = str.replace('大町（未）','大町')
#         str = str.replace('雪ノ下（未）','雪ノ下')
#         str = str.replace('台（未）','台')
#         str = str.replace('今泉（未）','今泉')
#         str = str.replace('小袋谷（未）','小袋谷')
#         str = str.replace('岩瀬（未）','岩瀬')
#     return str

def 北海道厚岸郡浜中町_filter(s):
    if s:
        s = s.replace('浜中西１線', '浜中西一線')
        s = s.replace('浜中西２線', '浜中西二線')
        s = s.replace('浜中西３線', '浜中西三線')
        s = s.replace('円朱別西３線', '円朱別西三線')
        s = s.replace('円朱別西４線', '円朱別西四線')
        s = s.replace('円朱別西５線', '円朱別西五線')
        s = s.replace('円朱別西６線', '円朱別西六線')
        s = s.replace('円朱別西７線', '円朱別西七線')
        s = s.replace('円朱別西８線', '円朱別西八線')
        s = s.replace('円朱別西９線', '円朱別西九線')
        s = s.replace('円朱別西１０線', '円朱別西十線')
        s = s.replace('熊牛西１線', '熊牛西一線')
        s = s.replace('熊牛西２線', '熊牛西二線')
        s = s.replace('熊牛西３線', '熊牛西三線')
        s = s.replace('熊牛東１線', '熊牛東一線')
        s = s.replace('熊牛東２線', '熊牛東二線')
        s = s.replace('熊牛東３線', '熊牛東三線')
        s = s.replace('熊牛東４線', '熊牛東四線')
        s = s.replace('熊牛東５線', '熊牛東五線')
        s = s.replace('熊牛東６線', '熊牛東六線')
        s = s.replace('１番沢', '一番沢')
        s = s.replace('２番沢', '二番沢')
        s = s.replace('３番沢', '三番沢')
        s = s.replace('４番沢', '四番沢')
        s = s.replace('６番沢', '六番沢')
        s = s.replace('西円朱別西１４線', '西円朱別西十四線')
        s = s.replace('西円朱別西１５線', '西円朱別西十五線')
        s = s.replace('西円朱別西１６線', '西円朱別西十六線')
        s = s.replace('西円朱別西１７線', '西円朱別西十七線')
        s = s.replace('西円朱別西１８線', '西円朱別西十八線')
        s = s.replace('西円朱別西１９線', '西円朱別西十九線')
        s = s.replace('西円朱別西２０線', '西円朱別西二十線')
        s = s.replace('西円朱別西２１線', '西円朱別西二十一線')
        s = s.replace('西円朱別西２２線', '西円朱別西二十二線')
        s = s.replace('西円朱別西２３線', '西円朱別西二十三線')
        s = s.replace('西円朱別西２４線', '西円朱別西二十四線')
        s = s.replace('西円朱別西２５線', '西円朱別西二十五線')
        s = s.replace('西円朱別西２６線', '西円朱別西二十六線')
        s = s.replace('西円朱別西２７線', '西円朱別西二十七線')
        s = s.replace('茶内東１線', '茶内東一線')
        s = s.replace('茶内東２線', '茶内東二線')
        s = s.replace('茶内東３線', '茶内東三線')
        s = s.replace('茶内東４線', '茶内東四線')
        s = s.replace('茶内東５線', '茶内東五線')
        s = s.replace('茶内東６線', '茶内東六線')
        s = s.replace('霧多布西１条１丁目', '霧多布西一条１丁目')
        s = s.replace('霧多布西１条２丁目', '霧多布西一条２丁目')
        s = s.replace('霧多布西２条１丁目', '霧多布西二条１丁目')
        s = s.replace('霧多布西２条２丁目', '霧多布西二条２丁目')
        s = s.replace('霧多布西３条１丁目', '霧多布西三条１丁目')
        s = s.replace('霧多布西３条２丁目', '霧多布西三条２丁目')
        s = s.replace('霧多布東１条１丁目', '霧多布東一条１丁目')
        s = s.replace('霧多布東１条２丁目', '霧多布東一条２丁目')
        s = s.replace('霧多布東２条１丁目', '霧多布東二条１丁目')
        s = s.replace('霧多布東２条２丁目', '霧多布東二条２丁目')
        s = s.replace('霧多布東３条１丁目', '霧多布東三条１丁目')
        s = s.replace('霧多布東３条２丁目', '霧多布東三条２丁目')
        s = s.replace('霧多布東４条１丁目', '霧多布東四条１丁目')
        s = s.replace('霧多布西４条１丁目', '霧多布西四条１丁目')

    return s



def 福岡県行橋市_azafilter(str):
    if str:
        str = str.replace('簑','蓑')
    return str
#endregion

# dynamic_filtername = config["pref_name"] + config["city_name"]
def dynamic_filtername(str):
    if config["filter_keyword"] and config["filtered_keyword"]:
        if config["filter_action"] == "replace":
            str = str.replace(config["filter_keyword"], config["filtered_keyword"])
        elif config["filter_action"] == "startswith":
            if str.startswith(config["filter_keyword"]):
                str = config["filtered_keyword"]
        else:
            pass
    return str

def combining_shp_files(input_dir_combine_shp):
    shp_files = glob.glob(os.path.join(input_dir_combine_shp, '*.shp'))
    gdf_list = []
    encoding = config["shp_file_charset"]
    for shp in shp_files:
        print("Processing:", shp)
        gdf = geopandas.read_file(shp, encoding=encoding)
        gdf_list.append(gdf)
    combined_gdf = geopandas.GeoDataFrame(pandas.concat(gdf_list, ignore_index=True))
    print("Shapefile combined successfully")
    output_path = r'C:\workspace\shp_to_txt\input\combined_shapefile.shp'
    combined_gdf.to_file(output_path)
    # print("Combined shapefile saved to:", output_path)
    shpfile_path = "combined_shapefile.shp"
    return shpfile_path

def koaza_existence(): # instead of making this function a true or false maybe return a string and make sure string is one to one for robustness
    if config['koaza'] == "unused":
        InUse = False
    else:
        InUse = True
    return InUse
# @classmethod

def get_all_coords(geom):
    """
    Recursively extract all coordinate tuples from a geometry.
    """
    if geom.is_empty:
        return []
    geom_type = geom.geom_type
    if geom_type == 'Point':
        return [geom.coords[0]]
    elif geom_type in ['LineString', 'LinearRing']:
        return list(geom.coords)
    elif geom_type == 'Polygon':
        # Get coordinates from exterior and interiors
        coords = list(geom.exterior.coords)
        for interior in geom.interiors:
            coords.extend(list(interior.coords))
        return coords
    elif geom_type.startswith('Multi') or geom_type == 'GeometryCollection':
        coords = []
        for part in geom.geoms:
            coords.extend(get_all_coords(part))
        return coords
    return []

# prototype AUTO header selector
combined_aza_header = []
combined_branch_header = []
header_from_shp = ['大字コード', '小字コード', '本番', '枝番', '枝1', '枝2', '枝3', '枝4', 'geometry']
aza_keywd_DB = {"大字コード","小字コード","大字","小字"}
branch_keywd_DB = {"地番","本番","枝番","枝番1","枝番2","枝番3","枝番4"}
def header_creation(header_from_shp):
    for word in header_from_shp:
        if (word in aza_keywd_DB and header_from_shp) and config['koaza'] == "unused":
            combined_aza_header.append(word)
        elif (word in aza_keywd_DB and header_from_shp) and config['koaza'] == "used":
            combined_aza_header.append(word)
        if word in branch_keywd_DB and header_from_shp:
            combined_branch_header.append(word)
    return combined_aza_header, combined_branch_header

"""
if aza_origin not in config['masterdata']:
    config['masterdata'][aza_origin] = {'aza_name': "所在不明"}
    aza_unknown += 1

code for automatically

"""