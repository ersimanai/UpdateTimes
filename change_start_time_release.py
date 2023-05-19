import DaVinciResolveScript as dvr_script
import sys
import time
import os
import requests
import subprocess
import getpass

#体验机会
def free():
    # 最大使用次数
    max_usage_count = 3
    # 记录当前使用次数的文件路径
    usage_file = os.path.expanduser("~/.usagelog")
    
    # 检查文件是否存在
    if os.path.exists(usage_file):
        # 读取当前使用次数
        try:
            with open(usage_file, "r") as f:
                usage_count = int(f.read())
        except ValueError:
            # 如果文件内容无法转换为整数，则使用默认值 0
            usage_count = 0
    else:
        # 文件不存在时，初始化为 0
        usage_count = 0
    
    # 判断是否达到使用次数上限
    if usage_count >= max_usage_count:
        #print("免费次数用完了。")
        return False
    
    # 更新使用次数
    usage_count += 1
    
    # 保存当前使用次数
    with open(usage_file, "w") as f:
        f.write(str(usage_count))
    
    return True



# 获取本机 MAC 地址和用户名
mac_id = None
def get_mac_serial_number():
    output = subprocess.check_output(['system_profiler', 'SPHardwareDataType'])
    lines = output.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith(b"Serial Number (system):"):
            return line.split(b":")[1].strip().decode("utf-8")

mac_id = get_mac_serial_number()

# 检查标志，记录是否已经输入正确的激活码
activation_done = False

# 检查系统目录下的隐藏文件是否存在
activation_file = os.path.expanduser('~/.activation_flag')
if os.path.exists(activation_file):
    activation_done = True

# 获取截止时间戳
def get_deadline():
    # 获取当前时间戳
    current_time = int(time.time())
    response = requests.get("http://101.35.227.215:8008/get_timestamp")
    if response.status_code == 200:
        deadline =  response.json().get('timestamp')
    else:
        # 如果无法连接到服务器或获取失败，返回默认的deadline值
        deadline = current_time
    if current_time < deadline:
        return True
    return False

#根据macId查看是否已经绑定了激活码
def get_bind_mac(mac_id):
    data = {
        'mac_id' : mac_id
    }
    response = requests.post("http://101.35.227.215:8008/get_bind_mac", data=data)
    if response.status_code == 200:
        result = response.json().get('result')
        return result
    return False;

isFree = free()

#设备绑定了激活码或者免激活码期间activation_done为true
if not activation_done:
    deadline = get_deadline()
    bindmac = get_bind_mac(mac_id)
    if deadline or bindmac:
        activation_done = True
        with open(activation_file, "w") as f:
                f.write("activation done")


if not activation_done and not isFree:
    activation_code = input("免费次数用完了，请输入激活码: ")
    # 构建请求数据
    data = {
        'code': activation_code,
        'mac_id': mac_id
    }

    # 向服务器发送 POST 请求验证激活码使用信息
    response = requests.post("http://101.35.227.215:8008/check_activation", data=data)

    if response.status_code == 200:
        result = response.json().get('result')
        if result == 0:
            activation_done = True
            with open(activation_file, "w") as f:
                f.write("activation done")
            usage_count = response.json().get('usage_count')
            print(f"激活码使用次数: ({usage_count}次)")
        elif result == -1:
            print("无效的激活码")
            sys.exit()
        elif result == -2:
            usage_count = response.json().get('usage_count')
            print(f"激活码使用次数已达到上限 ({usage_count}次)")
            usage_records = response.json().get('usage_records')
            print("激活码已使用的电脑信息:")
            for record in usage_records:
                usage_count = record['usage_count']
                timestamp = record['timestamp']
                mac_name = record['mac_id']
                print(f"使用激活码时间: {timestamp}, MAC 序列号: {mac_name}")
            sys.exit()
        else:
            print("未知错误")
            sys.exit()
    else:
        print("无法连接到服务器")
        sys.exit()

# Get Resolve object
resolve = dvr_script.scriptapp("Resolve")

# Get project manager and current project
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()

# Get media pool and root folder
mediaPool = project.GetMediaPool()
rootFolder = mediaPool.GetRootFolder()

# Function to recursively traverse the media pool folder structure
def process_folder(folder):
    clips = folder.GetClipList()

    # Loop through each clip in the folder and change start timecode to 00:00:00:00
    for clip in clips:
        # Get clip name and current start timecode
        clipName = clip.GetName()
        startTimecode = clip.GetClipProperty("Start TC")
        print(f"Clip name: {clipName}, Start TC: {startTimecode}")

        # Set new start timecode to 00:00:00:00
        newStartTimecode = "00:00:00:00"
        clip.SetClipProperty("Start TC", newStartTimecode)
        print(f"New start TC: {newStartTimecode}")

    subfolders = folder.GetSubFolderList()

    # Recursively process subfolders
    for subfolder in subfolders:
        process_folder(subfolder)

# Call the function to process the root folder and its subfolders
process_folder(rootFolder)

# Save project
# mediaPool.SaveProject()
print("恭喜修改成功，天天接大单")
print("尔斯麻制作,联系微信Ismaili_yang")

# 暂停一段时间（例如 1 秒）
time.sleep(1)

# 关闭终端窗口
if sys.platform.startswith('win'):
    subprocess.call('taskkill /F /PID {}'.format(os.getpid()), shell=True)
else:
    sys.exit()
