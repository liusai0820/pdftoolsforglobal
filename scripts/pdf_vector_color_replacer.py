#!/usr/bin/env python3
"""
矢量PDF颜色替换工具
将ICC色彩空间的颜色替换为DeviceRGB，保留矢量状态
"""
import pikepdf
import re
import sys
import fitz
from pathlib import Path
from collections import Counter

def hex_to_rgb(hex_color: str) -> tuple:
    """将十六进制颜色转换为RGB (0-1范围)"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r / 255.0, g / 255.0, b / 255.0)

def extract_colors_from_page(page):
    """从 PyMuPDF 页面提取矢量颜色"""
    colors = []
    
    # 获取所有的矢量绘图
    paths = page.get_drawings()
    for path in paths:
        # 获取填充颜色
        # color / fill 是 RGB tuple/list (r, g, b) 范围 0-1 或 None
        if path.get("fill") is not None:
             colors.append(tuple(path["fill"]))
             
        # 获取描边颜色
        if path.get("color") is not None:
             colors.append(tuple(path["color"]))
             
    return colors

def analyze_pdf_colors(input_pdf: str, max_pages: int = 5, top_n: int = 10) -> list:
    """
    分析 PDF 中的主要 CMYK 颜色
    返回: [{"c": 0, "m": 0, "y": 0, "k": 0, "hex": "#..."}, ...]
    """
    print(f"[analyze_pdf_colors] 开始分析: {input_pdf}")
    cmyk_colors = []
    
    try:
        pdf = pikepdf.open(input_pdf)
        
        # 多种 CMYK 颜色指令的正则匹配
        # 格式1: /CSx cs C M Y K scn (非描边颜色，使用色彩空间)
        pattern1 = re.compile(r'/CS\d+\s+cs\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+scn', re.IGNORECASE)
        # 格式2: C M Y K k (直接设置 CMYK 填充色)
        pattern2 = re.compile(r'(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+k(?:\s|$)')
        # 格式3: C M Y K K (直接设置 CMYK 描边色)
        pattern3 = re.compile(r'(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+K(?:\s|$)')
        
        for i, page in enumerate(pdf.pages):
            if i >= max_pages:
                break
            
            # 读取所有内容流
            contents_list = []
            if "/Contents" in page:
                contents = page["/Contents"]
                if isinstance(contents, pikepdf.Array):
                    for c_ref in contents:
                        try:
                            contents_list.append(c_ref.read_bytes().decode('latin-1', 'ignore'))
                        except:
                            pass
                elif isinstance(contents, pikepdf.Stream):
                    contents_list.append(contents.read_bytes().decode('latin-1', 'ignore'))
            
            for content in contents_list:
                # 尝试所有模式
                for pattern in [pattern1, pattern2, pattern3]:
                    matches = pattern.findall(content)
                    for m in matches:
                        try:
                            c, m_val, y, k = map(float, m)
                            # 只保留有效的 CMYK 值 (0-1 范围)
                            if 0 <= c <= 1.0 and 0 <= m_val <= 1.0 and 0 <= y <= 1.0 and 0 <= k <= 1.0:
                                # 排除纯黑和纯白，通常不是用户想替换的
                                if not (c == 0 and m_val == 0 and y == 0 and k == 0):  # 白色
                                    if not (c == 0 and m_val == 0 and y == 0 and k == 1):  # 黑色
                                        cmyk_colors.append((round(c, 4), round(m_val, 4), round(y, 4), round(k, 4)))
                        except:
                            pass
        
        pdf.close()
        
        # 统计 Top N
        stats = Counter(cmyk_colors).most_common(top_n)
        print(f"[analyze_pdf_colors] 找到 {len(stats)} 种不同颜色")
        
        result = []
        for (c, m, y, k), freq in stats:
            # CMYK -> RGB 转换 (简单公式)
            r = int(255 * (1 - c) * (1 - k))
            g = int(255 * (1 - m) * (1 - k))
            b = int(255 * (1 - y) * (1 - k))
            
            hex_val = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            
            result.append({
                "c": c, "m": m, "y": y, "k": k,
                "hex": hex_val,
                "freq": freq
            })
            print(f"  颜色: CMYK({c}, {m}, {y}, {k}) -> {hex_val} (出现 {freq} 次)")
            
        return result
        
    except Exception as e:
        print(f"[analyze_pdf_colors] 错误: {e}")
        import traceback
        traceback.print_exc()
        return []

def cmyk_to_rgb(c, m, y, k):
    """CMYK 转 RGB (0-255)"""
    r = int(255 * (1 - c) * (1 - k))
    g = int(255 * (1 - m) * (1 - k))
    b = int(255 * (1 - y) * (1 - k))
    return (r, g, b)

def color_distance(cmyk1, cmyk2):
    """计算两个 CMYK 颜色之间的距离（基于 RGB 空间）"""
    rgb1 = cmyk_to_rgb(*cmyk1)
    rgb2 = cmyk_to_rgb(*cmyk2)
    return ((rgb1[0] - rgb2[0])**2 + (rgb1[1] - rgb2[1])**2 + (rgb1[2] - rgb2[2])**2)**0.5

def replace_color_with_device_rgb(input_pdf: str, output_pdf: str, 
                                  source_cmyk: tuple, target_hex: str,
                                  tolerance: float = 80.0):
    """
    将源CMYK颜色及其相似颜色替换为目标RGB颜色
    
    参数:
        input_pdf: 输入PDF文件路径
        output_pdf: 输出PDF文件路径
        source_cmyk: 源颜色的CMYK值 (c, m, y, k)，范围0-1
        target_hex: 目标颜色的十六进制值，如 "#01beb0"
        tolerance: 颜色容差（RGB 空间距离），默认 80，相似颜色都会被替换
    """
    print(f"打开PDF: {input_pdf}")
    pdf = pikepdf.open(input_pdf)
    
    # 转换目标颜色
    target_r, target_g, target_b = hex_to_rgb(target_hex)
    target_rgb_255 = (int(target_r * 255), int(target_g * 255), int(target_b * 255))
    
    print(f"源颜色 CMYK: {source_cmyk}")
    print(f"目标颜色: RGB{target_rgb_255} = {target_hex}")
    print(f"RGB (0-1): ({target_r:.4f}, {target_g:.4f}, {target_b:.4f})")
    print(f"颜色容差: {tolerance}")
    print()
    
    replaced_count = 0
    colors_replaced = set()  # 记录被替换的颜色
    
    # 正则匹配所有 CMYK 颜色指令
    # 格式: /CSx cs C M Y K scn
    cmyk_pattern = re.compile(r'(/CS\d+\s+cs\s+)(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)(\s+scn)', re.IGNORECASE)
    cmyk_pattern_stroke = re.compile(r'(/CS\d+\s+CS\s+)(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)(\s+SCN)', re.IGNORECASE)
    
    def replace_similar_colors(match, is_stroke=False):
        """替换相似颜色的回调函数"""
        nonlocal colors_replaced
        prefix = match.group(1)
        c = float(match.group(2))
        m = float(match.group(3))
        y = float(match.group(4))
        k = float(match.group(5))
        suffix = match.group(6)
        
        current_cmyk = (c, m, y, k)
        dist = color_distance(source_cmyk, current_cmyk)
        
        if dist <= tolerance:
            colors_replaced.add(current_cmyk)
            if is_stroke:
                return f'/DeviceRGB CS {target_r:.4f} {target_g:.4f} {target_b:.4f} SC'
            else:
                return f'/DeviceRGB cs {target_r:.4f} {target_g:.4f} {target_b:.4f} sc'
        else:
            return match.group(0)  # 保持原样
    
    for page_num, page in enumerate(pdf.pages, 1):
        print(f"处理第 {page_num} 页...")
        
        if "/Contents" in page:
            contents = page["/Contents"]
            
            if isinstance(contents, pikepdf.Array):
                for i, content_ref in enumerate(contents):
                    if isinstance(content_ref, pikepdf.Stream):
                        stream_data = content_ref.read_bytes()
                        content = stream_data.decode('latin-1', errors='ignore')
                        
                        # 使用回调函数替换所有相似颜色
                        new_content = cmyk_pattern.sub(lambda m: replace_similar_colors(m, False), content)
                        new_content = cmyk_pattern_stroke.sub(lambda m: replace_similar_colors(m, True), new_content)
                        
                        if new_content != content:
                            content_ref.write(new_content.encode('latin-1', errors='ignore'))
                            replaced_count += 1
                            print(f"  ✓ 流 {i+1} 已更新")
                        else:
                            print(f"  - 流 {i+1} 无变化")
            elif isinstance(contents, pikepdf.Stream):
                stream_data = contents.read_bytes()
                content = stream_data.decode('latin-1', errors='ignore')
                
                new_content = cmyk_pattern.sub(lambda m: replace_similar_colors(m, False), content)
                new_content = cmyk_pattern_stroke.sub(lambda m: replace_similar_colors(m, True), new_content)
                
                if new_content != content:
                    contents.write(new_content.encode('latin-1', errors='ignore'))
                    replaced_count += 1
                    print(f"  ✓ 内容流已更新")
                else:
                    print(f"  - 内容流无变化")
    
    print()
    if colors_replaced:
        print(f"替换了以下 {len(colors_replaced)} 种颜色:")
        for cmyk in colors_replaced:
            print(f"  - CMYK{cmyk}")
    print(f"保存到: {output_pdf}")
    pdf.save(output_pdf)
    pdf.close()
    print(f"完成！共更新 {replaced_count} 个内容流")
    print("\n✓ 使用DeviceRGB色彩空间，保留矢量状态")

if __name__ == "__main__":
    # 默认配置
    input_file = "materials/平板支架光纤1124.pdf"
    output_file = "output/平板支架光纤1124_colored.pdf"
    
    # 源颜色：深蓝色 CMYK(0.7804, 0.8667, 0.0, 0.0)
    source_cmyk = (0.7804, 0.8667, 0.0000, 0.0000)
    
    # 目标颜色：青绿色 #01beb0
    target_hex = "#01beb0"
    
    # 支持命令行参数
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    if len(sys.argv) >= 4:
        target_hex = sys.argv[3]
    
    Path("output").mkdir(exist_ok=True)
    replace_color_with_device_rgb(input_file, output_file, source_cmyk, target_hex)
