import json

data = json.load(
    open(
        "/Users/jimjiang/Downloads/bookmarks_sync/step2safaribookmarks/safari_bookmarks_20250608_141532.json"
    )
)
url_bookmarks = [item for item in data if item["type"] == "url"]
print(f"Safari书签统计: {len(url_bookmarks)} 个书签")
print("Safari书签路径分布:")
paths = {}
[paths.update({item["path"]: paths.get(item["path"], 0) + 1}) for item in url_bookmarks]
[print(f"{path}: {count} 个书签") for path, count in paths.items()]
