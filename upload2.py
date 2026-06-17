import json, urllib.request, sys

wang_data = {
    "file_key": "temp/u144115261961536905/import_861963d3619611cc735af98462ffcf21.docx",
    "task_id": "drivetask_f8416c44e8514c29937aeb7b66369053",
    "upload_url": "https://docs-import-export-1251316161.cos.ap-guangzhou.myqcloud.com/temp/u144115261961536905/import_861963d3619611cc735af98462ffcf21.docx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=YOUR_TENCENT_CLOUD_SECRET_ID%2F20260615%2Fap-guangzhou%2Fs3%2Faws4_request&X-Amz-Date=20260615T145706Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=6af5e327a940f41cc89f41c9a771864634f0b2c53cf0a88a4a88b8ea82d0492a"
}
dai_data = {
    "file_key": "temp/u144115261961536905/import_7b498a2aea3603c66c95620977b17ec5.docx",
    "task_id": "drivetask_c411b686f21042a881070090d7280ff1",
    "upload_url": "https://docs-import-export-1251316161.cos.ap-guangzhou.myqcloud.com/temp/u144115261961536905/import_7b498a2aea3603c66c95620977b17ec5.docx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=YOUR_TENCENT_CLOUD_SECRET_ID%2F20260615%2Fap-guangzhou%2Fs3%2Faws4_request&X-Amz-Date=20260615T145706Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=7445afda2b739f1dfdb8f67195d74962a75e3a4c4d28082874254b7c058dc0af"
}

files = [
    (wang_data, "E:/shixun/zy/文档/王正滔_智能零售用户行为分析系统_实训报告.docx"),
    (dai_data, "E:/shixun/zy/文档/戴天笑_智能零售用户行为分析系统_实训报告.docx"),
]

for data, fpath in files:
    name = fpath.split("/")[-1]
    print(f"Uploading {name} ...")
    url = data["upload_url"]
    with open(fpath, "rb") as f:
        body = f.read()
    print(f"  File size: {len(body)} bytes")
    print(f"  URL starts: {url[:80]}")
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Content-Type", "application/octet-stream")
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        print(f"  PUT status: {resp.status}")
        print(f"  Response: {resp.read().decode()[:200]}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP error {e.code}: {e.reason}")
        body_text = e.read().decode("utf-8", errors="replace")[:500]
        print(f"  Body: {body_text}")
        sys.exit(1)
    except Exception as e:
        print(f"  Error: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)

print("\nDone uploading both files.")
print("Data for async_import:")
for data, fpath in files:
    name = fpath.split("/")[-1]
    print(f"  {name}: task_id={data['task_id']}, file_key={data['file_key']}")
