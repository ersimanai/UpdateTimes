import DaVinciResolveScript as dvr_script
import sys
import time
import os
import requests
import subprocess
import getpass
import tkinter as tk
from tkinter import simpledialog, messagebox, Scrollbar, Text

# 禁用 Oh My Zsh 更新提示
os.environ["DISABLE_UPDATE_PROMPT"] = "true"

# 检查是否为免费试用
def is_free_trial():
    # 最大使用次数
    max_usage_count = 3
    # 使用次数文件路径
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
        # 如果文件不存在，则初始化为 0
        usage_count = 0

    # 检查是否达到最大使用次数
    if usage_count >= max_usage_count:
        return False

    # 更新使用次数
    usage_count += 1

    # 保存当前使用次数
    with open(usage_file, "w") as f:
        f.write(str(usage_count))

    return True

# 获取当前机器的 MAC 地址和用户名
mac_id = None
def get_mac_serial_number():
    output = subprocess.check_output(['system_profiler', 'SPHardwareDataType'])
    lines = output.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith(b"Serial Number (system):"):
            return line.split(b":")[1].strip().decode("utf-8")

mac_id = get_mac_serial_number()

# 检查是否已正确输入激活码
activation_done = False

# 检查系统目录中是否存在激活标志文件
activation_file = os.path.expanduser('~/.activation_flag')
if os.path.exists(activation_file):
    activation_done = True

# 获取截止时间戳
def get_deadline():
    # 获取当前时间戳
    current_time = int(time.time())
    response = requests.get("http://101.35.227.215:8008/get_timestamp")
    if response.status_code == 200:
        deadline = response.json().get('timestamp')
    else:
        # 如果无法连接到服务器或获取时间戳，则返回默认的截止时间
        deadline = current_time
    if current_time < deadline:
        return True
    return False

# 检查激活码是否绑定到 MAC 地址
def is_activation_bound(mac_id):
    data = {
        'mac_id': mac_id
    }
    response = requests.post("http://101.35.227.215:8008/get_bind_mac", data=data)
    if response.status_code == 200:
        result = response.json().get('result')
        return result
    return False

is_free = is_free_trial()

# 设备已绑定激活码或处于免费试用期（如果 activation_done 为 True）
if not activation_done and not is_free:
    root = tk.Tk()
    root.withdraw()
    activation_code = simpledialog.askstring("激活码", "免费试用次数已用尽，请输入激活码：")
    # 构造请求数据
    data = {
        'code': activation_code,
        'mac_id': mac_id
    }

    # 向服务器发送 POST 请求以验证激活码的使用信息
    response = requests.post("http://101.35.227.215:8008/check_activation", data=data)

    if response.status_code == 200:
        result = response.json().get('result')
        if result == 0:
            activation_done = True
            with open(activation_file, "w") as f:
                f.write("activation done")
            usage_count = response.json().get('usage_count')
            messagebox.showinfo("激活成功", f"激活码使用次数：{usage_count} 次")
        elif result == -1:
            messagebox.showerror("激活失败", "无效的激活码")
            sys.exit()
        elif result == -2:
            usage_count = response.json().get('usage_count')
            usage_records = response.json().get('usage_records')
            usage_info = f"激活码使用次数已达上限（{usage_count} 次）\n\n激活码已在以下计算机上使用过：\n"
            for record in usage_records:
                usage_count = record['usage_count']
                timestamp = record['timestamp']
                mac_name = record['mac_id']
                usage_info += f"激活码使用时间：{timestamp}，MAC 序列号：{mac_name}\n"
            messagebox.showwarning("激活失败", usage_info)
            sys.exit()
        else:
            messagebox.showerror("激活失败", "未知错误")
            sys.exit()
    else:
        messagebox.showerror("激活失败", "无法连接到服务器")
        sys.exit()

# 获取 Resolve 对象
resolve = dvr_script.scriptapp("Resolve")

# 获取项目管理器和当前项目
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()

# 获取媒体池和根文件夹
mediaPool = project.GetMediaPool()
rootFolder = mediaPool.GetRootFolder()

# 创建一个 tkinter 窗口以显示输出
window = tk.Tk()
window.title("时间码修改工具")

# 将窗口位置设置为屏幕中心
window_width = 800
window_height = 400
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

text_box = Text(window, height=10, width=50)
text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 为文本框创建滚动条
scrollbar = Scrollbar(window)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 将滚动条与文本框关联
text_box.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_box.yview)

# 递归遍历媒体池文件夹结构的函数
def process_folder(folder):
    clips = folder.GetClipList()

    # 遍历文件夹中的每个剪辑，并将开始时间码修改为 00:00:00:00
    for clip in clips:
        # 获取剪辑名称和当前开始时间码
        clipName = clip.GetName()
        startTimecode = clip.GetClipProperty("Start TC")
        output_text = f"片段名称：{clipName}，开始时间码：{startTimecode}\n"
        text_box.insert(tk.END, output_text)
        text_box.update()

        # 将新的开始时间码设置为 00:00:00:00
        newStartTimecode = "00:00:00:00"
        clip.SetClipProperty("Start TC", newStartTimecode)
        output_text = f"新的开始时间码：{newStartTimecode}\n\n"
        text_box.insert(tk.END, output_text)
        text_box.update()

    # 递归处理子文件夹
    subfolders = folder.GetSubFolderList()
    for subfolder in subfolders:
        process_folder(subfolder)

# 开始处理根文件夹
process_folder(rootFolder)
output_text = "时间码修改成功。\n\n如需进一步协助，请联系微信：Ismaili_yang。"
text_box.insert(tk.END, output_text)
text_box.update()

# 显示 tkinter 窗口并等待用户交互
messagebox.showinfo("修改成功", "恭喜修改成功，天天接大单\n\n尔斯麻制作，联系微信：Ismaili_yang")
#window.mainloop()
