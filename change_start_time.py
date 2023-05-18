import DaVinciResolveScript as dvr_script
import sys
import time

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
print("尔斯麻制作,联系微信Ismaili_yang")

# 暂停一段时间（例如 2 秒）

time.sleep(2)

# 关闭终端窗口
if sys.platform.startswith('win'):
    import subprocess
    subprocess.call('taskkill /F /PID {}'.format(sys.pid), shell=True)
else:
    sys.exit()

