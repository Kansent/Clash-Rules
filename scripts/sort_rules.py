#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import sys

def sort_list_file_content(content: str, bottom_category_name: str = "Unknown issue") -> str:
    categories = {}
    current_cat = None
    bottom_cat_header = f"# {bottom_category_name}".lower()
    bottom_cat_key = None

    lines = content.strip().splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        if stripped.startswith('#'):
            current_cat = stripped
            if current_cat not in categories:
                categories[current_cat] = []
            if stripped.lower() == bottom_cat_header:
                bottom_cat_key = current_cat
        else:
            if current_cat is not None:
                categories[current_cat].append(stripped)

    normal_categories = []
    bottom_category = None

    for cat_header, domains in categories.items():
        # 去重并排序该分类下的域名
        unique_sorted_domains = sorted(list(set(domains)))
        if cat_header == bottom_cat_key:
            bottom_category = (cat_header, unique_sorted_domains)
        else:
            normal_categories.append((cat_header, unique_sorted_domains))

    # 对分类名按 A-Z 升序
    normal_categories.sort(key=lambda x: x[0].lower())

    output_lines = []
    for cat_header, domains in normal_categories:
        output_lines.append(cat_header)
        output_lines.extend(domains)
        output_lines.append("")

    if bottom_category:
        cat_header, domains = bottom_category
        output_lines.append(cat_header)
        output_lines.extend(domains)

    return "\n".join(output_lines).strip() + "\n"

def process_all_lists(target_dir: str):
    # 匹配目标目录下所有的 .txt 和 .list 文件（包括子目录）
    patterns = [os.path.join(target_dir, "**", "*.txt"), os.path.join(target_dir, "**", "*.list")]
    files = []
    for p in patterns:
        files.extend(glob.glob(p, recursive=True))

    print(f"找到 {len(files)} 个待处理的文件...")

    for file_path in files:
        # 跳过脚本所在目录
        if "scripts/" in file_path.replace("\\", "/"):
            continue
            
        print(f"正在处理: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        if not raw_content.strip():
            continue

        sorted_content = sort_list_file_content(raw_content, bottom_category_name="Unknown issue")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(sorted_content)

if __name__ == "__main__":
    # 默认扫描整个仓库根目录，如需指定目录可传参，例如 python sort_rules.py ./rules
    target_directory = sys.argv[1] if len(sys.argv) > 1 else "."
    process_all_lists(target_directory)