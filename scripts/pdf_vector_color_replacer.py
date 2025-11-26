#!/usr/bin/env python3
"""
矢量PDF颜色替换工具
将ICC色彩空间的颜色替换为DeviceRGB，保留矢量状态
"""
import pikepdf
import re
import sys
from pathlib import Path

def hex_to_rgb(hex_color: str) -> tuple:
    """将十六进制颜色转换为RGB (0-1范围)"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r / 255.0, g / 255.0, b / 255.0)

def replace_color_with_device_rgb(input_pdf: str, output_pdf: str, 
                                  source_cmyk: tuple, target_hex: str):
    """
    将源CMYK颜色替换为目标RGB颜色，使用DeviceRGB色彩空间
    
    参数:
        input_pdf: 输入PDF文件路径
        output_pdf: 输出PDF文件路径
        source_cmyk: 源颜色的CMYK值 (c, m, y, k)，范围0-1
        target_hex: 目标颜色的十六进制值，如 "#01beb0"
    """
    print(f"打开PDF: {input_pdf}")
    pdf = pikepdf.open(input_pdf)
    
    # 转换目标颜色
    target_r, target_g, target_b = hex_to_rgb(target_hex)
    target_rgb_255 = (int(target_r * 255), int(target_g * 255), int(target_b * 255))
    
    print(f"源颜色 CMYK: {source_cmyk}")
    print(f"目标颜色: RGB{target_rgb_255} = {target_hex}")
    print(f"RGB (0-1): ({target_r:.4f}, {target_g:.4f}, {target_b:.4f})")
    print()
    
    replaced_count = 0
    
    for page_num, page in enumerate(pdf.pages, 1):
        print(f"处理第 {page_num} 页...")
        
        if "/Contents" in page:
            contents = page["/Contents"]
            
            if isinstance(contents, pikepdf.Array):
                for i, content_ref in enumerate(contents):
                    if isinstance(content_ref, pikepdf.Stream):
                        stream_data = content_ref.read_bytes()
                        content = stream_data.decode('latin-1', errors='ignore')
                        
                        # 替换颜色空间和颜色值
                        # 从ICC色彩空间到DeviceRGB
                        c, m, y, k = source_cmyk
                        
                        # 小写 cs/scn (非描边颜色)
                        pattern = rf'/CS\d+\s+cs\s+{c:.4f}\s+{m:.4f}\s+{y:.4f}\s+{k:.4f}\s+scn'
                        replacement = f'/DeviceRGB cs {target_r:.4f} {target_g:.4f} {target_b:.4f} sc'
                        new_content = re.sub(pattern, replacement, content)
                        
                        # 大写 CS/SCN (描边颜色)
                        pattern_CS = rf'/CS\d+\s+CS\s+{c:.4f}\s+{m:.4f}\s+{y:.4f}\s+{k:.4f}\s+SCN'
                        replacement_CS = f'/DeviceRGB CS {target_r:.4f} {target_g:.4f} {target_b:.4f} SC'
                        new_content = re.sub(pattern_CS, replacement_CS, new_content)
                        
                        if new_content != content:
                            content_ref.write(new_content.encode('latin-1', errors='ignore'))
                            replaced_count += 1
                            print(f"  ✓ 流 {i+1} 已更新")
                        else:
                            print(f"  - 流 {i+1} 无变化")
            elif isinstance(contents, pikepdf.Stream):
                stream_data = contents.read_bytes()
                content = stream_data.decode('latin-1', errors='ignore')
                
                c, m, y, k = source_cmyk
                
                pattern = rf'/CS\d+\s+cs\s+{c:.4f}\s+{m:.4f}\s+{y:.4f}\s+{k:.4f}\s+scn'
                replacement = f'/DeviceRGB cs {target_r:.4f} {target_g:.4f} {target_b:.4f} sc'
                new_content = re.sub(pattern, replacement, content)
                
                pattern_CS = rf'/CS\d+\s+CS\s+{c:.4f}\s+{m:.4f}\s+{y:.4f}\s+{k:.4f}\s+SCN'
                replacement_CS = f'/DeviceRGB CS {target_r:.4f} {target_g:.4f} {target_b:.4f} SC'
                new_content = re.sub(pattern_CS, replacement_CS, new_content)
                
                if new_content != content:
                    contents.write(new_content.encode('latin-1', errors='ignore'))
                    replaced_count += 1
                    print(f"  ✓ 内容流已更新")
                else:
                    print(f"  - 内容流无变化")
    
    print()
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
