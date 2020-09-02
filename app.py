from flask import Flask, request
from flask import render_template
import json
import functions as fun

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list/info', methods=['GET', 'POST'])
def list_info():
    recv = request.get_data()
    # print(recv)
    if recv:
        recv = json.loads(str(recv, encoding='utf-8'))
        if recv['item'] == 'unit':
            res = fun.get_unit_list()
            res['status'] = 'success'
        elif recv['item'] == 'equip':
            res = fun.get_equip_list()
        else:
            print('type error')
            res = {'status': 'error'}
        return json.dumps(res, indent=1, ensure_ascii=False)
    else:
        print("None received")
        return json.dumps({'status': 'error'})


@app.route('/cal/craft', methods=['GET', 'POST'])
def cal_craft():
    recv = request.get_data()
    if recv:
        recv = json.loads(str(recv, encoding='utf-8'))
        # print(recv)
        equip_num = fun.get_equip_num(recv['unit_id'], cur_rank=recv['cur_rank'], cur_equip=recv['cur_equip'],
                                      target_rank=recv['target_rank'], target_equip=recv['target_equip'])
        equip_craft = fun.get_equip_craft(equip_num)
        equip_craft['status'] = 'success'
        return json.dumps(equip_craft, indent=1, ensure_ascii=False)
    else:
        print("None received")
        return json.dumps({'status': 'error'})


@app.route('/cal/scheme', methods=['GET', 'POST'])
def create_scheme():
    recv = request.get_data()
    if recv:
        recv = json.loads(str(recv, encoding='utf-8'))
        # print(recv)
        res = fun.get_equip_scheme(recv['crafts'], recv['maxMap'])
        return json.dumps({'scheme': res, 'status': 'success'}, indent=1, ensure_ascii=False)
    else:
        return json.dumps({'status': 'fail'}, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    app.run()
