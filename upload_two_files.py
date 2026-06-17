"""上传两个文件到腾讯文档"""
import json
import urllib.request

# pre_import responses (parsed)
responses = [
    {
        "name": "王正滔_智能零售用户行为分析系统_实训报告.docx",
        "path": "E:/shixun/zy/文档/王正滔_智能零售用户行为分析系统_实训报告.docx",
        "file_key": "temp/u144115261961536905/import_861963d3619611cc735af98462ffcf21.docx",
        "task_id": "drivetask_90dcdc9fdd9140ab832b2ac12110a936",
        "upload_url": "https://docs-import-export-1251316161.cos.ap-guangzhou.myqcloud.com/temp/u144115261961536905/import_861963d3619611cc735af98462ffcf21.docx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=YOUR_TENCENT_CLOUD_SECRET_ID%2F20260615%2Fap-guangzhou%2Fs3%2Faws4_request&X-Amz-Date=20260615T145149Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=da17154c9e3d6dc72a27f366dd3223a66635de42beb189c284e873c9d5101fff9"
    },
    {
        "name": "戴天笑_智能零售用户行为分析系统_实训报告.docx",
        "path": "E:/shixun/zy/文档/戴天笑_智能零售用户行为分析系统_实训报告.docx",
        "file_key": "temp/u144115261961536905/import_7b498a2aea3603c66c95620977b17ec5.docx",
        "task_id": "drivetask_fe705b3067574bbfa5a7209766ea1cb2",
        "upload_url": "https://docs-import-export-1251316161.cos.ap-guangzhou.myqcloud.com/temp/u144115261961536905/import_7b498a2aea3603c66c95620977b17ec5.docx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=YOUR_TENCENT_CLOUD_SECRET_ID%2F20260615%2Fap-guangzhou%2Fs3%2Faws4_request&X-Amz-Date=20260615T145149Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=9de148209549d1af23ea61d53a4876c8bb077fa658ebd73ff5086918d9dd5ee87"
    }
]

for r in responses:
    print(f"上传 {r['name']} ...")
    url = r["upload_url"]
    with open(r["path"], "rb") as f:
        data = f.read()
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Content-Type", "application/octet-stream")
    try:
        resp = urllib.request.urlopen(req)
        print(f"  上传成功，状态码: {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"  上传失败: {e.code} {e.reason}")
        print(f"  响应: {e.read().decode()[:200]}")

print("上传完成")
