import os
import re
import html
import unicodedata

TARGET_DIR = "."

def convert_html_table_to_markdown(text: str) -> str:
    """将 HTML table 标签解析并展开合并单元格，转换为标准 Markdown 表格"""
    table_pattern = re.compile(r'<table>(.*?)</table>', re.DOTALL | re.IGNORECASE)

    def replace_table(match):
        table_html = match.group(1)
        rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
        if not rows:
            return match.group(0)

        grid = []
        pending_spans = {}

        for row_html in rows:
            current_row = []
            cells = re.findall(r'<td([^>]*)>(.*?)</td>', row_html, re.DOTALL | re.IGNORECASE)
            cell_iter = iter(cells)
            c_idx = 0

            while True:
                if c_idx in pending_spans:
                    rem_span, val = pending_spans[c_idx]
                    current_row.append(val)
                    if rem_span - 1 > 0:
                        pending_spans[c_idx] = (rem_span - 1, val)
                    else:
                        del pending_spans[c_idx]
                    c_idx += 1
                    continue

                try:
                    attrs, content = next(cell_iter)
                except StopIteration:
                    break

                cell_text = content.strip().replace('\n', ' ')
                rowspan_match = re.search(r'rowspan=["\']?(\d+)["\']?', attrs, re.IGNORECASE)
                if rowspan_match:
                    span_count = int(rowspan_match.group(1))
                    if span_count > 1:
                        pending_spans[c_idx] = (span_count - 1, cell_text)

                current_row.append(cell_text)
                c_idx += 1

            if current_row:
                grid.append(current_row)

        if not grid:
            return match.group(0)

        max_cols = max(len(r) for r in grid)
        for r in grid:
            r.extend([''] * (max_cols - len(r)))

        md_lines = []
        header = grid[0]
        md_lines.append("| " + " | ".join(header) + " |")
        md_lines.append("| " + " | ".join(["---"] * max_cols) + " |")
        for data_row in grid[1:]:
            md_lines.append("| " + " | ".join(data_row) + " |")

        return "\n\n" + "\n".join(md_lines) + "\n\n"

    return table_pattern.sub(replace_table, text)

def clean_garbled_text(text: str) -> str:
    # 1. 解码常见的 HTML 转义字符
    text = html.unescape(text)

    # 2. Unicode 标准化归一
    text = unicodedata.normalize("NFKC", text)

    # 3. 剔除 UTF-8 BOM 标记与菱形替换乱码
    text = text.replace('\ufeff', '').replace('\ufffd', '')

    # 4. 剔除零宽字符与特殊空格
    zero_width_chars = ['\u200b', '\u200c', '\u200d', '\u200e', '\u200f', '\u2060']
    for char in zero_width_chars:
        text = text.replace(char, '')
    text = text.replace('\xa0', ' ')

    # 5. 剔除私有使用区字符（图标字体乱码）
    text = re.sub(r'[\ue000-\uf8ff]', '', text)

    # 6. 剔除底层控制字符（保留换行、回车、制表符）
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # 6.1 将 HTML 上标注脚转换为标准括号引用格式（如 <sup>4</sup> -> [4]）
    text = re.sub(r'<sup>(\d+)</sup>', r'[\1]', text)

    # 6.2 将 HTML 复杂表格自动转换为标准 Markdown 表格
    text = convert_html_table_to_markdown(text)

    # 7. 修复常见西欧编码混乱
    mojibake_map = {
        'â€”': '—',
        'â€“': '–',
        'â€™': "'",
        'â€˜': "'",
        'â€œ': '"',
        'â€': '"',
        'Â': '',
    }
    for bad, good in mojibake_map.items():
        text = text.replace(bad, good)

    # 8. 彻底清理所有 Markdown 图片标签（包括本地 images/xxx.jpg 和网络在线图床）
    text = re.sub(r'!\[.*?\]\([^\)]+\)', '', text)

    # 9. 修复中文单字间断空格
    text = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', text)
    text = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', text)

    # 10. 规范空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip() + '\n'

def process_all_markdown(directory):
    md_files = [f for f in os.listdir(directory) if f.endswith('.md')]
    print(f"找到 {len(md_files)} 个 Markdown 文件，开始全量清洗...\n")
    for filename in md_files:
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='surrogateescape') as f:
                content = f.read()
        except Exception:
            with open(filepath, 'r', encoding='gb18030', errors='ignore') as f:
                content = f.read()
        cleaned_content = clean_garbled_text(content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"[已清洗图片与乱码] {filename}")
    print("\n✅ 所有本地与在线图片噪点清洗完成！")

if __name__ == "__main__":
    process_all_markdown(TARGET_DIR)