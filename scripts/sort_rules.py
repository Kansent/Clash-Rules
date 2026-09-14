#!/usr/bin/env python3

import glob
import os
import sys

def sort_list_file_content(content: str, bottom_category_name: str = "Unknown issue") -> str:
    lines = [line.strip() for line in content.strip().splitlines() if line.strip()]
    if not lines:
        return ""

    has_categories = any(line.startswith('#') for line in lines)

    if not has_categories:
        unique_sorted_lines = sorted(list(set(lines)))
        return "\n".join(unique_sorted_lines) + "\n"

    categories = {}
    current_cat = None
    bottom_cat_header = f"# {bottom_category_name}".lower()
    bottom_cat_key = None
    uncategorized = []

    for line in lines:
        if line.startswith('#'):
            current_cat = line
            if current_cat not in categories:
                categories[current_cat] = []
            if line.lower() == bottom_cat_header:
                bottom_cat_key = current_cat
        else:
            if current_cat is not None:
                categories[current_cat].append(line)
            else:
                uncategorized.append(line)

    normal_categories = []
    bottom_category = None

    for cat_header, domains in categories.items():
        unique_sorted_domains = sorted(list(set(domains)))
        if cat_header == bottom_cat_key:
            bottom_category = (cat_header, unique_sorted_domains)
        else:
            normal_categories.append((cat_header, unique_sorted_domains))

    normal_categories.sort(key=lambda x: x[0].lower())

    output_lines = []

    if uncategorized:
        output_lines.extend(sorted(list(set(uncategorized))))
        output_lines.append("")

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
    patterns = [os.path.join(target_dir, "**", "*.txt"), os.path.join(target_dir, "**", "*.list")]
    files = []
    for p in patterns:
        files.extend(glob.glob(p, recursive=True))

    for file_path in files:
        if "scripts/" in file_path.replace("\\", "/"):
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        if not raw_content.strip():
            continue

        sorted_content = sort_list_file_content(raw_content, bottom_category_name="Unknown issue")

        if raw_content.strip() != sorted_content.strip():
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(sorted_content)

if __name__ == "__main__":
    target_directory = sys.argv[1] if len(sys.argv) > 1 else "."
    process_all_lists(target_directory)