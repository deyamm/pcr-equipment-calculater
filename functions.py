import pandas as pd
import numpy as np
import MySQLdb as sql
import json
import math

# 判断材料key是否在res集中，存在则其基础上加value，不存在则在res中添加该key及其value
def add_equip(res, key, value):
    if key in res.keys():
        res[key] = res[key] + value
    else:
        res[key] = value


def get_equip_num(unit_id, **kwargs):
    """
    根据角色代码及相关关键字得出装备的需求量
    :param unit_id: str     角色代码
    :param kwargs:  dict    关键字集，主要有当前rank及装备，目标rank及装备
    :return: res    dict    用于存储一共需要的装备
    """
    # print(kwargs)
    unit_id = unit_id[:4] + '0' + unit_id[5]
    cur_rank = kwargs.get('cur_rank', 1)  # 当前rank
    target_rank = kwargs.get('target_rank', 2)  # 目标rank
    cur_equip = kwargs.get('cur_equip', '000000')  # 当前装备 0：无  1：有 位置表示装备
    target_equip = kwargs.get('target_equip', '000000')  # 目标装备

    con = sql.connect(host='localhost', port=3306, user='root', passwd='qq16281091', db='pcr', charset='utf8')
    cur = con.cursor()

    query = 'select * from pcr.unit_equip where unit_id=%s' % unit_id
    cur.execute(query)
    columns = [col[0] for col in cur.description]
    # print(columns)
    tmp = np.array(cur.fetchall())
    # print(tmp)
    rank_equip = pd.DataFrame(tmp, columns=columns)
    rank_equip['promotion_level'] = rank_equip['promotion_level'].astype(int)
    # print(rank_equip)

    res = dict()

    for i in range(cur_rank, target_rank):
        if i == cur_rank:
            equip_slots = cur_equip
        else:
            equip_slots = '000000'
        for j in range(0, len(equip_slots)):
            if equip_slots[j] == '0':
                # print(rank_equip[rank_equip['promotion_level'] == i]['equip_slot_' + str(j+1)].values)
                equip_code = rank_equip[rank_equip['promotion_level'] == i]['equip_slot_' + str(j + 1)].values[0]
                add_equip(res, equip_code, 1)

    if cur_rank == target_rank:
        equip_slots = cur_equip
    else:
        equip_slots = '000000'

    for i in range(0, len(equip_slots)):
        if equip_slots[i] != target_equip[i]:
            equip_code = rank_equip[rank_equip['promotion_level'] == target_rank]['equip_slot_' + str(i + 1)].values[0]
            add_equip(res, equip_code, 1)

    cur.close()
    con.close()

    return res


def cal_craft(equip_craft, equip_id, need_num, crafts):
    """
    计算生成指定数量的目标装备所需要的材料
    :param equip_craft: DataFrame   各个装备对应的材料
    :param equip_id:    str         生成的目标装备代码
    :param need_num:    int         需要生成装备的数量
    :param crafts:      dict        用于存储所需要的材料
    :return:
    """
    line = equip_craft.loc[equip_id]
    for i in range(1, int(len(equip_craft.columns) / 2 + 1)):
        if str(line['cost' + str(i)]) == '0':
            continue
        elif str(line['craft' + str(i)]) == '0':
            continue
        else:
            craft_id = line['craft' + str(i)]
            if craft_id in equip_craft.index:
                cal_craft(equip_craft, craft_id, (int)(line['cost' + str(i)]) * need_num, crafts)
            else:
                add_equip(crafts, craft_id, need_num * (int)(line['cost' + str(i)]))


def get_equip_craft(equip_list, is_new=True):
    """
    根据所需要的装备，得出生成这些装备需要的材料，用于递归
    :param equip_list:  dict    用于存储所需要的装备及其数量
    :param is_new:      bool    用于标示装备材料数量的版本，False表示旧版本，True表示新版本
    :return: res        dict    存储得出的材料及其数量
    """
    con = sql.connect(host='localhost', port=3306, user='root', passwd='qq16281091', db='pcr', charset='utf8')
    cur = con.cursor()

    cur.execute('select * from pcr.equip_craft')
    columns = [col[0] for col in cur.description]
    equip_craft = pd.DataFrame(np.array(cur.fetchall()), columns=columns)
    equip_craft.set_index('equip_id', inplace=True)
    # print(equip_craft.dtypes)

    res = dict()  # 用于存储最终结果
    # tmp_crafts = dict()  # 用于存储中间装备材料

    for equip in equip_list.keys():
        if equip in equip_craft.index:
            # print(equip_craft.loc[equip])
            crafts = dict()
            cal_craft(equip_craft, equip, equip_list[equip], crafts)
            for key in crafts.keys():
                add_equip(res, key, crafts[key])
        else:
            # print(str(equip) + ' False')
            add_equip(res, equip, equip_list[equip])

    cur.close()
    con.close()
    return res


def get_unit_list():
    """
    获取角色列表
    :return: dict key为角色代码，value为角色名称
    """
    con = sql.connect(host='localhost', port=3306, user='root', passwd='qq16281091', db='pcr', charset='utf8')
    cur = con.cursor()

    cur.execute('select * from pcr.unit_map')
    columns = [col[0] for col in cur.description]
    array = np.array(cur.fetchall())
    unit_list = pd.DataFrame(array, columns=columns)

    res = dict()
    for i in range(len(unit_list)):
        res[unit_list[columns[0]][i]] = unit_list[columns[1]][i]

    cur.close()
    con.close()
    return res


def get_equip_scheme(crafts, max_map):
    """
    根据所提供的材料种类及数量，获取方案
    :param crafts: dict key为材料代码，value为对应材料所需数量
    :param max_map: str 当前推图进度，获取的文案不会超出该进度
    :return: list dict数组，每个元素都为地图编号及次数
    """
    if max_map is None or max_map == '':
        max_map = '110250011'
    # craft2map为dict变量，key为材料代码，value为掉落该材料的地图list
    with open('./data/craft2map.json') as f:
        craft2map = json.load(f)

    # 根据max_map删除超出的地图，先获取需要删除的地图，再从craft2map的value中删除得到的地图
    for key in craft2map.keys():
        areas = craft2map[key]
        need2delete = []
        for area in areas:
            if list(area.keys())[0] > max_map:
                need2delete.append(area)
        for t in need2delete:
            areas.remove(t)
        # print(key)
        # print(craft2map[key])

    # print(craft2map)

    '''
    con = sql.connect(host='localhost', port=3306, user='root', passwd='qq16281091', db='pcr', charset='utf8')
    cur = con.cursor()
    
    cur.execute("select * from pcr.craft_drop")
    columns = [col[0] for col in cur.description]
    craft_drop = pd.DataFrame(np.array(cur.fetchall()), columns=columns)
    craft_drop.set_index('quest_id', inplace=True)
    
    cur.close()
    con.close()
    print(craft_drop)
    '''

    tmp_crafts = crafts.copy()
    scheme = []
    # 在剩余材料为0前不断循环，每次循环中根据当前所剩材料获取最合适的地图及次数
    while len(tmp_crafts.keys()) > 0:
        sorted_craft = deter_area(tmp_crafts, craft2map, scheme)
        # print(scheme)

    return scheme

# 获取材料代码与掉落该材料地图及掉落概率的字典变量并生成文件
# key为材料代码，value为dict数组，每个dict表示地图编号及该材料在该地图的掉落概率
def craft_map_dict():
    con = sql.connect(host='localhost', port=3306, user='root', passwd='qq16281091', db='pcr', charset='utf8')
    cur = con.cursor()

    craft2map = dict()

    cur.execute("select * from pcr.craft_drop")
    columns = [col[0] for col in cur.description]
    craft_drop = pd.DataFrame(np.array(cur.fetchall()), columns=columns)

    for line in craft_drop.values:
        for i in range(2, len(line)):
            if line[i] not in craft2map:
                craft2map[line[i]] = [{line[1]: get_drop_rate(line[0], i-2)}]
            else:
                craft2map[line[i]].append({line[1]: get_drop_rate(line[0], i-2)})
    res = json.dumps(craft2map, indent=1, ensure_ascii=False)
    # print(res)

    with open('./data/craft2map.json', 'w') as f:
        f.write(res)

    cur.close()
    con.close()

# 获取每个地图中每个材料的掉落概率
def get_drop_rate(area_id, drop_order):
    drop_rate = {'1': [0.54, 0.54, 0.54, 0.20, 0.20, 0.20, 0.20, 0.20],
                 '2': [0.36, 0.36, 0.24, 0.20, 0.20, 0.20, 0.20, 0.20],
                 '22': [0.36, 0.36, 0.24, 0.24, 0.24, 0.20, 0.17, 0.15]}
    area_num = int(area_id[3:])
    keys = list(drop_rate.keys())
    for i in range(len(keys)):
        if area_num < int(keys[i]):
            return drop_rate[keys[i-1]][drop_order]
        else:
            continue
    return drop_rate[keys[len(keys)-1]][drop_order]


def deter_area(crafts, area_drop, scheme):
    """
    根据当前所需要的材料种类及数量、各个地图材料的掉落概率获取一个最佳目标地图及刷图次数
    :param crafts: dict 当前所需要的材料种类及其数量，key为材料代码，value为数量
    :param area_drop: dict 各个材料对应的掉落该材料的地图及概率
    :param scheme: list 存储目标地图及刷图次数
    :return: crafts 表示经过指定次数的后，还需要获得的剩余材料
    """
    # print(json.dumps(area_drop, indent=1))
    # print(json.dumps(crafts, indent=1))

    # 一个地图可以获取所需材料的概率及所需个数
    # key地图编号，value为可以获取的各个材料及其掉落概率
    area2craft = {}
    max_num_area = ''
    for key in crafts.keys():
        areas = area_drop[key]
        for single in areas:
            area = list(single.keys())[0]
            if area in area2craft.keys():
                area2craft[area].append({key: [single[area], crafts[key]]})
            else:
                area2craft[area] = [{key: [single[area], crafts[key]]}]
            # 选出可以获得所需材料种类最多的地图作为目标地图
            if max_num_area == '':
                max_num_area = area
            elif len(area2craft[area]) > len(area2craft[max_num_area]):
                max_num_area = area

    # 根据所选的地图，计算刷图次数的期望值，并得到满足的装备
    # 刷图次数为刷完某一种材料所需要最小次数
    expected_num = 1e9
    selected_craft = ''
    for craft in area2craft[max_num_area]:
        info = list(craft.values())[0]
        cur_need_num = math.ceil(info[1] / info[0])
        if expected_num > cur_need_num:
            expected_num = cur_need_num
            selected_craft = list(craft.keys())[0]
    # print(json.dumps(area2craft, indent=1))
    # print(area2craft[max_num_area])
    # print(selected_craft)
    # print(max_num_area)

    # 将地图编号及刷图次数添加到scheme变量中
    scheme.append([max_num_area[3:5]+'-'+max_num_area[8:10], expected_num])
    # 根据次数，从所有需要的材料中减去获得的材料数量的期望值
    for craft in area2craft[max_num_area]:
        craft_code = list(craft.keys())[0]
        if craft_code not in crafts.keys():
            continue
        crafts[craft_code] = crafts[craft_code] - math.floor(expected_num * list(craft.values())[0][0])
        if crafts[craft_code] <= 0:
            crafts.pop(craft_code)
    '''
        canditated_area = []
        # 一个地图最多可以获得2种碎片,待改进
        for i in range(1, len(sorted_craft)):
            single_area = [val for val in needed_area[0] if dict_is_in_list(val, needed_area[i])]
            if len(single_area) > 0:

    '''
    return crafts

# 查找dict是否在一个list中
def dict_is_in_list(d, d_list):
    for v in d_list:
        if d.keys() == v.keys():
            return True
    return False

if __name__ == '__main__':
    # print(get_unit_list())
    craft_map_dict()