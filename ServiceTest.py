from flask import Flask, request
import random
import string

app = Flask(__name__)

# 激活码和使用次数的字典
activation_codes = {
    '1001': 0,
    # 如果需要，可以在这里添加更多的激活码
}

# 激活码使用的上限次数
usage_limit = 2

# 生成的激活码集合
generated_codes = set()

def load_activation_codes():
    try:
        with open('activation_codes.txt', 'r') as file:
            for line in file:
                code = line.strip()
                if code:
                    generated_codes.add(code)
    except FileNotFoundError:
        pass

@app.route('/check_activation', methods=['POST'])
def check_activation():
    activation_code = request.form.get('code')
    if activation_code in activation_codes:
        usage_count = activation_codes[activation_code]
        if usage_count >= usage_limit:
            return "-2"  # 激活码使用次数已达到上限
        else:
            activation_codes[activation_code] += 1
            return "0"  # 返回验证成功
    else:
        return "-1"  # 无效的激活码

@app.route('/generate_activation_codes', methods=['GET'])
def generate_activation_codes():
    name = request.args.get('name')
    
    if name == 'gulisu':
        # 生成激活码
        code_length = 6
        num_codes = 1
        codes = []
        
        while len(codes) < num_codes:
            code = "abin"
            
            # 校验激活码是否重复
            if code not in generated_codes:
                generated_codes.add(code)
                codes.append(code)
            else:
                 return "激活码重复"
        
        # 将激活码写入文件
        with open('activation_codes.txt', 'a') as file:
            file.write('\n'.join(codes) + '\n')
        
        return '<br>'.join(codes)
    else:
        return "不是爸爸滚开"

if __name__ == '__main__':
    load_activation_codes()
    app.run(host='0.0.0.0', port=8008)

