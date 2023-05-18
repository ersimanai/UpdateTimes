from flask import Flask, request, jsonify
import random
import string
from datetime import datetime

app = Flask(__name__)

# 生成的激活码集合
generated_codes = {}

# 激活码使用的字典
activation_codes = {}

# 激活码使用的上限次数
usage_limit = 2

# 时间戳文件路径
timestamp_file = 'custom_timestamp.txt'

def load_activation_codes():
    try:
        with open('generated_activation_codes.txt', 'r') as file:
            for line in file:
                code, user, timestamp = line.strip().split(',')
                generated_codes[code] = {'user': user, 'timestamp': timestamp}
    except FileNotFoundError:
        pass

def save_generated_codes():
    with open('generated_activation_codes.txt', 'w') as file:
        for code, info in generated_codes.items():
            user = info['user']
            timestamp = info['timestamp']
            file.write(f"{code},{user},{timestamp}\n")

def load_activation_usage():
    try:
        with open('activation_usage.txt', 'r') as file:
            for line in file:
                code, usage_count, timestamp, mac_address, mac_name = line.strip().split(',')
                usage_records = activation_codes.get(code, {}).get('usage_records', [])
                if code in activation_codes:
                    if int(usage_count) > activation_codes[code]['usage_count']:
                        activation_codes[code]['usage_count'] = int(usage_count)
                        activation_codes[code]['timestamp'] = timestamp
                        activation_codes[code]['mac_address'] = mac_address
                        activation_codes[code]['mac_name'] = mac_name
                        if not usage_records:
                            usage_records = load_activation_records(code)
                            activation_codes[code]['usage_records'] = usage_records
                else:
                    activation_codes[code] = {'usage_count': int(usage_count), 'timestamp': timestamp, 'mac_address': mac_address, 'mac_name': mac_name, 'usage_records': usage_records}
    except FileNotFoundError:
        pass

def save_activation_usage(code, usage_count, timestamp, mac_address, mac_name):
    with open('activation_usage.txt', 'a') as file:
        file.write(f"{code},{usage_count},{timestamp},{mac_address},{mac_name}\n")

def load_activation_records(code):
    usage_records = []
    try:
        with open('activation_usage.txt', 'r') as file:
            for line in file:
                record_code, usage_count, timestamp, mac_address, mac_name = line.strip().split(',')
                if record_code == code:
                    usage_records.append({'usage_count': int(usage_count), 'timestamp': timestamp, 'mac_address': mac_address, 'mac_name': mac_name})
    except FileNotFoundError:
        pass
    return usage_records

def generate_activation_code(code_type):
    code_length = 6
    while True:
        code = f"{code_type}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length))}"
        if code not in activation_codes and code not in generated_codes:
            return code

def load_custom_timestamp():
    try:
        with open(timestamp_file, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def save_custom_timestamp(timestamp):
    with open(timestamp_file, 'w') as file:
        file.write(timestamp)

@app.route('/check_activation', methods=['POST'])
def check_activation():
    activation_code = request.form.get('code')
    mac_address = request.form.get('mac')
    mac_name = request.form.get('mac_name')

    if activation_code in generated_codes:
        activation_info = activation_codes.get(activation_code, {})
        usage_count = activation_info.get('usage_count', 0)
        usage_records = activation_info.get('usage_records', [])
        if not usage_records:
            usage_records = load_activation_records(activation_code)
            activation_info['usage_records'] = usage_records
        if usage_count >= usage_limit:
            return jsonify({'result': -2, 'usage_count': usage_count,  'usage_records': usage_records})
        else:
            usage_count += 1
            activation_info['usage_count'] = usage_count
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            activation_records = {'usage_count': usage_count, 'timestamp': timestamp, 'mac_address': mac_address, 'mac_name': mac_name}
            usage_records.append(activation_records)
            activation_codes[activation_code] = {'usage_count': int(usage_count), 'timestamp': timestamp, 'mac_address': mac_address, 'mac_name': mac_name, 'usage_records': usage_records}
            save_activation_usage(activation_code, usage_count, timestamp, mac_address, mac_name)
            return jsonify({'result': 0, 'usage_count': usage_count})
    else:
        return jsonify({'result': -1})

@app.route('/generate_activation_codes', methods=['GET'])
def generate_activation_codes():
    name = request.args.get('name')
    num_codes = int(request.args.get('num_codes', 100))
    code_type = request.args.get('type', 'resetTimes')

    if name == 'gulisu':
        codes = []
        for _ in range(num_codes):
            code = generate_activation_code(code_type)
            codes.append(code)
            generated_codes[code] = {'user': name, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        save_generated_codes()
        return '<br>'.join(codes)
    else:
        return "不是爸爸滚开"

@app.route('/get_unused_activation_codes', methods=['GET'])
def get_unused_activation_codes():
    code_type = request.args.get('type', 'resetTimes')
    
    unused_codes = []
    for code in generated_codes:
        if code.startswith(code_type) and code not in activation_codes:
            unused_codes.append(code)
    
    return jsonify({'unused_codes': unused_codes})

@app.route('/get_timestamp', methods=['GET'])
def get_timestamp():
    custom_timestamp = load_custom_timestamp()
    if custom_timestamp:
        return jsonify({'timestamp': custom_timestamp})
    else:
        return jsonify({'timestamp': datetime.timestamp(datetime.now())})

@app.route('/set_timestamp', methods=['GET'])
def set_timestamp():
    new_timestamp = request.args.get('timestamp')
    if new_timestamp:
        save_custom_timestamp(datetime.timestamp(datetime.strptime(new_timestamp, '%Y-%m-%d %H:%M:%S')))
    else:
        save_custom_timestamp(datetime.timestamp(datetime.now()))
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    load_activation_codes()
    load_activation_usage()
    app.run(host='0.0.0.0', port=8008)
