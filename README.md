# report-md-cleaner
A lightweight tool to sanitise, format, and denoise research report Markdown files.
# Report Markdown Cleaner 📄✨

一个专为行业研报 Markdown 文件设计的清洗工具，自动化解决 OCR 噪点、异常换行和表格破损等问题。

## 解决的痛点 (Features)
- **排版修复**：修复 OCR 导致的段内硬换行（Hard Wrap）、修复被破坏的 Markdown 表格。
- **图片与链接清洗**：清理失效引用、规范化本地或网络图片路径。
- **元数据提取**：支持从标题/前言提取研报日期、机构、分析师等前置信息。

## 🔍 清洗效果对比 (Before vs After)

| 原始研报 Markdown (Before) | 清洗后 Markdown (After) |
| :--- | :--- |
| `第 12 页 共 45 页` <br>`证券研究报告·行业深度` <br>`本报告仅供内部参考...` <br><br> 这是一段被硬换行的<br>文本内容。 | 这是一段被硬换行的文本内容。 |

## 🚀 快速上手 (Quick Start)

### 安装依赖
\`\`\`bash
git clone https://github.com/your-username/report-cleaner.git
cd report-cleaner
pip install -r requirements.txt
\`\`\`

### 使用方法
\`\`\`bash
# 清洗单个文件
python src/cleaner.py -i examples/raw_report.md -o output.md

# 批量清洗目录
python src/cleaner.py --batch-dir ./reports/
\`\`\`

## 技术实现
- Markdown 结构解析
