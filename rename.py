import os
import re

def extract_title_from_content(filepath):
    """读取 Markdown 前 20 行，抓取一级标题 (# 标题) 或机构、年份信息"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [f.readline() for _ in range(20)]

    title = None
    year = None

    # 1. 尝试寻找 Markdown 一级或二级标题 (# 报告名称)
    for line in lines:
        line = line.strip()
        if line.startswith("# ") and len(line) > 4:
            title = line.replace("# ", "").strip()
            break

    # 2. 如果没写标准 markdown 标题，抓取前几行最长的一句有意义文字
    if not title:
        for line in lines:
            line = line.strip()
            if len(line) > 6 and not line.startswith("!") and not line.startswith("<"):
                title = line
                break

    # 3. 从前文扫描年份
    content_header = "".join(lines)
    year_match = re.search(r'(202[0-9])', content_header)
    if year_match:
        year = year_match.group(1)

    if title:
        # 去除文件名非法字符
        clean_title = re.sub(r'[\/\\:\*\?"<>\|]', '', title)[:40].strip()
        prefix = f"{year}_" if year else ""
        return f"{prefix}{clean_title}.md"
    
    return None

def batch_rename():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for filename in os.listdir(current_dir):
        # 仅处理 MinerU 开头的 Markdown 文件，避免修改自身或其他脚本
        if filename.startswith("MinerU_markdown_") and filename.endswith(".md"):
            old_path = os.path.join(current_dir, filename)
            new_name = extract_title_from_content(old_path)
            
            if new_name and new_name != filename:
                new_path = os.path.join(current_dir, new_name)
                
                # 防止同名覆盖冲突
                counter = 1
                base_name, ext = os.path.splitext(new_name)
                while os.path.exists(new_path):
                    new_name = f"{base_name}_{counter}{ext}"
                    new_path = os.path.join(current_dir, new_name)
                    counter += 1
                
                os.rename(old_path, new_path)
                print(f"重命名: {filename} -> {new_name}")
            else:
                print(f"跳过（未提取到有效标题）: {filename}")

if __name__ == "__main__":
    batch_rename()