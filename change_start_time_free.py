import DaVinciResolveScript as dvr_script
import sys
import time
import os

# 最大使用次数
max_usage_count = 3

# 记录当前使用次数的文件路径
usage_file = os.path.expanduser("~/.usagelog")

# 读取当前使用次数
try:
    with open(usage_file, "r") as f:
        usage_count = int(f.read())
except FileNotFoundError:
    # 如果文件不存在，则初始化为 0
    usage_count = 0

# 判断是否达到使用次数上限
if usage_count >= max_usage_count:
    print("已达到使用次数上限，无法继续运行,请联系微信abinxe。")
    sys.exit()

# 更新使用次数
usage_count += 1

# 保存当前使用次数
with open(usage_file, "w") as f:
    f.write(str(usage_count))

# Get Resolve object
resolve = dvr_script.scriptapp("Resolve")

# Get project manager and current project
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()

# Get media pool and root folder
mediaPool = project.GetMediaPool()
rootFolder = mediaPool.GetRootFolder()

# Get all media pool items in root folder
clips = rootFolder.GetClipList()

# Loop through each clip and change start timecode to 00:00:00:00
for clip in clips:
    # Get clip name and current start timecode
    clipName = clip.GetName()
    startTimecode = clip.GetClipProperty("Start TC")
    print(f"Clip name: {clipName}, Start TC: {startTimecode}")

    # Set new start timecode to 00:00:00:00
    newStartTimecode = "00:00:00:00"
    clip.SetClipProperty("Start TC", newStartTimecode)
    print(f"New start TC: {newStartTimecode}")

# Save project
#print(type(mediaPool))
#print(dir(mediaPool))
#mediaPool.SaveProject()
print("恭喜修改成功，天天接大单")

# 暂停一段时间（例如 2 秒）
time.sleep(2)

# 关闭终端窗口
if sys.platform.startswith('win'):
    import subprocess
    subprocess.call('taskkill /F /PID {}'.format(sys.pid), shell=True)
else:
    sys.exit()

