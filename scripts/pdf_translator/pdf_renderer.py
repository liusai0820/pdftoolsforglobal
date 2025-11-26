"""
PDF 渲染器
将 Markdown 转换为专业排版的 PDF
使用 WeasyPrint 或 Typst
"""
import markdown
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from .config import OUTPUT_DIR, ASSETS_DIR, LOGO_PATH, COMPANY_NAME, COMPANY_WEBSITE


# Datasheet CSS 样式
DATASHEET_CSS = """
@page {
    size: A4;
    margin: 15mm 15mm 20mm 15mm;
    @top-right {
        content: "DATASHEET";
        font-size: 9pt;
        color: #666;
    }
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.4;
    color: #333;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #01beb0;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.header img {
    height: 40px;
}

.header .title {
    font-size: 24pt;
    font-weight: bold;
    color: #01beb0;
}

h1 {
    font-size: 18pt;
    color: #01beb0;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
    margin-top: 15px;
}

h2 {
    font-size: 12pt;
    color: #333;
    margin-top: 12px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 9pt;
}

th {
    background-color: #01beb0;
    color: white;
    padding: 8px;
    text-align: left;
    font-weight: bold;
}

td {
    padding: 6px 8px;
    border-bottom: 1px solid #ddd;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

ul {
    margin: 5px 0;
    padding-left: 20px;
}

li {
    margin: 3px 0;
}

.features {
    column-count: 2;
    column-gap: 20px;
}

img {
    max-width: 100%;
    height: auto;
}

.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 8pt;
    color: #666;
    border-top: 1px solid #ddd;
    padding-top: 5px;
}
"""

# User Manual CSS 样式
MANUAL_CSS = """
@page {
    size: A4;
    margin: 20mm;
    @top-left {
        content: "USER MANUAL";
        font-size: 9pt;
        color: #666;
    }
    @bottom-center {
        content: counter(page);
        font-size: 9pt;
    }
}

body {
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

.header {
    text-align: center;
    border-bottom: 2px solid #01beb0;
    padding-bottom: 15px;
    margin-bottom: 30px;
}

.header img {
    height: 50px;
    margin-bottom: 10px;
}

.header .title {
    font-size: 28pt;
    font-weight: bold;
    color: #333;
}

.header .subtitle {
    font-size: 14pt;
    color: #666;
}

h1 {
    font-size: 16pt;
    color: #01beb0;
    border-bottom: 2px solid #01beb0;
    padding-bottom: 5px;
    margin-top: 25px;
    page-break-after: avoid;
}

h2 {
    font-size: 13pt;
    color: #333;
    margin-top: 15px;
    page-break-after: avoid;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th {
    background-color: #01beb0;
    color: white;
    padding: 10px;
    text-align: left;
}

td {
    padding: 8px 10px;
    border: 1px solid #ddd;
}

blockquote {
    margin: 15px 0;
    padding: 15px;
    border-left: 4px solid #ff9800;
    background-color: #fff8e1;
}

blockquote.danger {
    border-left-color: #f44336;
    background-color: #ffebee;
}

ol, ul {
    margin: 10px 0;
    padding-left: 25px;
}

li {
    margin: 5px 0;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 15px auto;
}

.figure-caption {
    text-align: center;
    font-style: italic;
    color: #666;
    margin-top: 5px;
}
"""


def markdown_to_html(md_content: str) -> str:
    """将 Markdown 转换为 HTML"""
    extensions = [
        'tables',
        'fenced_code',
        'toc',
        'nl2br'
    ]
    return markdown.markdown(md_content, extensions=extensions)


def render_datasheet_pdf(
    md_content: str,
    output_path: str,
    product_name: str = "",
    logo_path: str = None,
    images_dir: str = None
):
    """
    渲染 Datasheet PDF
    """
    html_content = markdown_to_html(md_content)
    
    logo_html = ""
    if logo_path and Path(logo_path).exists():
        logo_html = f'<img src="file://{logo_path}" alt="Logo">'
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <div class="header">
            {logo_html}
            <div class="title">{product_name}</div>
        </div>
        {html_content}
        <div class="footer">
            {COMPANY_NAME} | {COMPANY_WEBSITE}
        </div>
    </body>
    </html>
    """
    
    font_config = FontConfiguration()
    base_url = str(images_dir) if images_dir else "."
    
    HTML(string=full_html, base_url=base_url).write_pdf(
        output_path,
        stylesheets=[CSS(string=DATASHEET_CSS, font_config=font_config)],
        font_config=font_config
    )
    
    return output_path


def render_manual_pdf(
    md_content: str,
    output_path: str,
    product_name: str = "",
    logo_path: str = None,
    images_dir: str = None
):
    """
    渲染 User Manual PDF
    """
    html_content = markdown_to_html(md_content)
    
    logo_html = ""
    if logo_path and Path(logo_path).exists():
        logo_html = f'<img src="file://{logo_path}" alt="Logo">'
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <div class="header">
            {logo_html}
            <div class="title">{product_name}</div>
            <div class="subtitle">User Manual</div>
        </div>
        {html_content}
    </body>
    </html>
    """
    
    font_config = FontConfiguration()
    base_url = str(images_dir) if images_dir else "."
    
    HTML(string=full_html, base_url=base_url).write_pdf(
        output_path,
        stylesheets=[CSS(string=MANUAL_CSS, font_config=font_config)],
        font_config=font_config
    )
    
    return output_path


def save_markdown(md_content: str, output_path: str):
    """保存 Markdown 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    return output_path
