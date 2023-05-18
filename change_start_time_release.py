import DaVinciResolveScript as dvr_script
import sys
import time
import os
import requests
import subprocess
import getpass

# 检查标志，记录是否已经输入正确的激活码
activation_done = False

# 检查系统目录下的隐藏文件是否存在
activation_file = os.path.expanduser('~/.activation_flag')
if os.path.exists(activation_file):
    activation_done = True

# 获取当前时间戳
current_time = int(time.time())

# 获取截止时间戳
def get_deadline():
    response = requests.get("http://101.35.227.215:8008/get_timestamp")
    if response.status_code == 200:
        return response.json().get('timestamp')
    else:
        # 如果无法连接到服务器或获取失败，返回默认的deadline值
        return current_time
if not activation_done:
    deadline = get_deadline()
    # 判断是否在指定时间截止之前
    if current_time < deadline:
        activation_done = True
        with open(activation_file, "w") as f:
                f.write("activation done")
                
if not activation_done:
    activation_code = input("请输入激活码: ")

    # 获取本机 MAC 地址和用户名
    mac_address = None
    username = None

    if sys.platform.startswith('win'):
        output = subprocess.getoutput('ipconfig /all')
        for line in output.splitlines():
            if 'Physical Address' in line:
                mac_address = line.split(':')[1].strip()
                break
    else:
        output = subprocess.getoutput('ifconfig')
        for line in output.splitlines():
            if 'ether' in line:
                mac_address = line.split()[1]
                break

    if mac_address:
        try:
            username = getpass.getuser()
        except Exception:
            pass

    if not mac_address or not username:
        print("无法获取 MAC 地址或用户名")
        sys.exit()

    # 构建请求数据
    data = {
        'code': activation_code,
        'mac': mac_address,
        'mac_name': username
    }

    # 向服务器发送 POST 请求验证激活码使用信息
    response = requests.post("http://101.35.227.215:8008/check_activation", data=data)

    if response.status_code == 200:
        result = response.json().get('result')
        if result == 0:
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
                mac_name = record['mac_name']
                print(f"使用次数: {usage_count}, 时间: {timestamp}, MAC 名称: {mac_name}")
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
