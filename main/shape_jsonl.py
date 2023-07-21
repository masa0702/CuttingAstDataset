import json
import os
import re

input_jsonl = "input.jsonl"
output_jsonl = "output.jsonl"

def remove_comments(code):
    # 正規表現を使ってコメントを削除
    code = re.sub(r'\"\"\"(.|\n)*?\"\"\"', '', code)   # """コメント"""
    code = re.sub(r"\'\'\'(.|\n)*?\'\'\'", '', code)   # '''コメント'''
    code = re.sub(r'\#.*', '', code)                  # #コメント
    return code

# JSONL ファイルの内容を読み込んでリストに格納
data_list = []
with open(input_jsonl, "r") as f:
    for line in f:
        data = json.loads(line)
        data_list.append(data)

# 新しい JSONL ファイルに必要な属性のデータを書き込む
with open(output_jsonl, "w") as f:
    for data in data_list:
        file_path = data["path"]
        # ファイル名のみを取得して ".py" で終わる場合はそのまま、そうでない場合は ".py" を追加
        file_name = os.path.basename(file_path)
        if not file_name.endswith(".py"):
            file_name += ".py"

        # コードのコメントを削除
        code = remove_comments(data["code"])

        new_data = {
            "file_path": file_name,
            "code": code
        }
        f.write(json.dumps(new_data) + "\n")
