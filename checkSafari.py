import json
import glob
import os

# 模糊搜索safari书签文件
safari_files = glob.glob("/Users/jimjiang/Downloads/bookmarks_sync/step2safaribookmarks/safari_bookmarks_*.json")
if not safari_files:
    print("未找到Safari书签文件")
    exit(1)

# 使用最新的文件
safari_file = max(safari_files, key=os.path.getctime)
print(f"使用文件: {safari_file}")

data = json.load(open(safari_file))
url_bookmarks = [item for item in data if item["type"] == "url"]
print(f"Safari书签统计: {len(url_bookmarks)} 个书签")
print("Safari书签路径分布:")
paths = {}
[paths.update({item["path"]: paths.get(item["path"], 0) + 1}) for item in url_bookmarks]
[print(f"{path}: {count} 个书签") for path, count in paths.items()]
