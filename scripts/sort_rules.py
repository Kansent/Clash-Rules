#!/usr/bin/env python3

import glob
import ipaddress
import os
import sys

def normalize_header(line: str) -> str:
    if line.startswith('#'):
        header_text = line.lstrip('#').strip()
        return f"# {header_text}" if header_text else "#"
    return line

def domain_sort_key(domain: str):
    clean_domain = domain.lstrip("+.*")
    parts = clean_domain.lower().split('.')
    return (parts[::-1], domain.lower())

def is_ip_or_cidr(line: str) -> bool:
    clean_line = line.strip()
    try:
        ipaddress.ip_network(clean_line, strict=False)
        return True
    except ValueError:
        return False

def ip_sort_key(line: str):
    clean_line = line.strip()
    try:
        net = ipaddress.ip_network(clean_line, strict=False)
        return (net.version, net.network_address, net.prefixlen)
    except ValueError:
        return (99, 0, 0)

def sort_lines(lines: list) -> list:
    unique_lines = list(set(lines))
    if not unique_lines:
        return []
    
    ip_count = sum(1 for line in unique_lines if is_ip_or_cidr(line))
    if ip_count / len(unique_lines) > 0.5:
        return sorted(unique_lines, key=ip_sort_key)
    else:
        return sorted(unique_lines, key=domain_sort_key)

def sort_list_file_content(content: str, bottom_category_name: str = "Unknown") -> str:
    lines = [normalize_header(line.strip()) for line in content.strip().splitlines() if line.strip()]
    if not lines:
        return ""

    has_categories = any(line.startswith('#') for line in lines)

    if not has_categories:
        unique_sorted_lines = sort_lines(lines)
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

    for cat_header, item_lines in categories.items():
        unique_sorted_items = sort_lines(item_lines)
        if cat_header == bottom_cat_key:
            bottom_category = (cat_header, unique_sorted_items)
        else:
            normal_categories.append((cat_header, unique_sorted_items))

    normal_categories.sort(key=lambda x: x[0].lower())

    output_lines = []

    if uncategorized:
        output_lines.extend(sort_lines(uncategorized))
        output_lines.append("")

    for cat_header, item_lines in normal_categories:
        output_lines.append(cat_header)
        output_lines.extend(item_lines)
        output_lines.append("")

    if bottom_category:
        cat_header, item_lines = bottom_category
        output_lines.append(cat_header)
        output_lines.extend(item_lines)

    return "\n".join(output_lines).strip() + "\n"

def process_all_lists(target_dir: str):
    patterns = [os.path.join(target_dir, "**", "*.txt"), os.path.join(target_dir, "**", "*.list")]
    files = []
    for p in patterns:
        files.extend(glob.glob(p, recursive=True))

    for file_path in files:
        if "scripts/" in file_path.replace("\\", "/"):
            continue
            
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            raw_content = f.read()

        if not raw_content.strip():
            continue

        has_crlf = "\r\n" in raw_content

        sorted_content = sort_list_file_content(raw_content, bottom_category_name="Unknown")

        raw_lines_count = len(raw_content.strip().splitlines())
        sorted_lines_count = len(sorted_content.strip().splitlines())
        if raw_lines_count > 5 and sorted_lines_count < raw_lines_count * 0.7:
            continue

        if has_crlf or raw_content.strip() != sorted_content.strip():
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(sorted_content)

if __name__ == "__main__":
    target_directory = sys.argv[1] if len(sys.argv) > 1 else "."
    process_all_lists(target_directory)