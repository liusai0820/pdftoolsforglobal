"""
AI 处理器
使用 OpenRouter API 调用 Gemini 进行文档分析和翻译
"""
import json
import httpx
from typing import Optional
from .config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_MODEL


class AIProcessor:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or DEFAULT_MODEL
        self.base_url = OPENROUTER_BASE_URL
        
        if not self.api_key:
            raise ValueError("请设置 OPENROUTER_API_KEY 环境变量")
    
    def _call_api(self, messages: list, max_tokens: int = 8192) -> str:
        """调用 OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pdf-translator",
            "X-Title": "PDF Translator"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def analyze_pdf_pages(self, page_images: list[dict]) -> dict:
        """
        分析 PDF 页面内容，提取结构化信息
        输入: 页面图片列表 (base64)
        输出: 结构化的文档内容
        """
        # 构建多模态消息
        content = [
            {
                "type": "text",
                "text": """你是一个专业的技术文档分析专家。请仔细分析这份中文技术文档的所有页面，提取以下信息：

1. **产品基本信息**: 产品名称、型号、品牌
2. **技术规格**: 所有技术参数（电压、电流、尺寸、工作温度等），以表格形式整理
3. **功能特点**: 产品的主要功能和特点
4. **接线说明**: 接线方式、引脚定义
5. **安装说明**: 安装步骤和注意事项
6. **操作说明**: 使用方法、菜单设置等
7. **安全警告**: 所有安全相关的警告和注意事项
8. **图片描述**: 描述文档中的每张图片（产品图、接线图、尺寸图等）

请用 JSON 格式输出，结构如下：
```json
{
  "product_name": "产品名称",
  "model": "型号",
  "brand": "品牌",
  "specifications": [
    {"name": "参数名", "value": "参数值", "unit": "单位"}
  ],
  "features": ["特点1", "特点2"],
  "wiring": {
    "description": "接线说明",
    "pins": [{"color": "线色", "function": "功能"}]
  },
  "installation": ["步骤1", "步骤2"],
  "operation": ["操作说明1", "操作说明2"],
  "safety_warnings": ["警告1", "警告2"],
  "images": [
    {"type": "product|wiring|dimension|other", "description": "图片描述", "page": 1}
  ]
}
```

请确保提取所有技术参数，不要遗漏任何重要信息。"""
            }
        ]
        
        # 添加所有页面图片
        for page in page_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{page['image_base64']}"
                }
            })
        
        messages = [{"role": "user", "content": content}]
        
        response = self._call_api(messages, max_tokens=8192)
        
        # 解析 JSON 响应
        try:
            # 提取 JSON 部分
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {"raw_response": response}


    def generate_datasheet(self, doc_info: dict, embedded_images: list = None) -> str:
        """
        生成英文 Datasheet (Markdown 格式)
        """
        prompt = f"""你是一个专业的技术文档编写专家。请根据以下产品信息，生成一份专业的英文 Datasheet。

产品信息:
```json
{json.dumps(doc_info, ensure_ascii=False, indent=2)}
```

要求:
1. 使用专业的技术英语，简洁精准
2. 遵循国际通行的 Datasheet 格式:
   - 产品概述 (Overview)
   - 主要特点 (Key Features) - 用 bullet points
   - 技术规格 (Specifications) - 用表格
   - 接线图说明 (Wiring Diagram)
   - 外形尺寸 (Dimensions)
   - 订购信息 (Ordering Information)
3. **重要：Markdown 表格必须使用正确格式，每个参数一行：**
   ```
   | Parameter | Value |
   |-----------|-------|
   | Power Supply | 12-24VDC |
   | Response Time | 200µs |
   ```
4. 保持 1-2 页的篇幅，突出关键信息
5. 不要包含详细的操作说明和安全警告（那些放在 User Manual 里）

输出格式: 纯 Markdown 文本（不要用代码块包裹）

图片占位符:
- 产品图位置: <!-- PRODUCT_IMAGE -->
- 接线图位置: <!-- WIRING_IMAGE -->
- 尺寸图位置: <!-- DIMENSION_IMAGE -->
"""
        
        messages = [{"role": "user", "content": prompt}]
        return self._call_api(messages, max_tokens=8192)
    
    def generate_user_manual(self, doc_info: dict, embedded_images: list = None) -> str:
        """
        生成英文 User Manual (Markdown 格式)
        """
        prompt = f"""你是一个专业的技术文档编写专家。请根据以下产品信息，生成一份完整的英文 User Manual。

产品信息:
```json
{json.dumps(doc_info, ensure_ascii=False, indent=2)}
```

要求:
1. 使用清晰易懂的技术英语
2. 遵循国际通行的 User Manual 格式:
   - 安全须知 (Safety Information) - 包含 Warning 和 Caution 标记
   - 产品介绍 (Product Introduction)
   - 技术规格 (Specifications)
   - 安装指南 (Installation Guide)
   - 接线说明 (Wiring Instructions)
   - 操作说明 (Operation Instructions)
   - 故障排除 (Troubleshooting) - 如果有相关信息
   - 保修条款 (Warranty) - 如果有相关信息
3. 安全警告使用 blockquote 格式:
   > ⚠️ **WARNING**: 警告内容
   > ⚡ **CAUTION**: 注意内容
4. 步骤说明使用编号列表
5. **重要：Markdown 表格必须使用正确格式，每个参数一行：**
   ```
   | Parameter | Value |
   |-----------|-------|
   | Power Supply | 12-24VDC |
   | Response Time | 200µs |
   ```

输出格式: 纯 Markdown 文本（不要用代码块包裹）

图片占位符:
- 产品图位置: <!-- PRODUCT_IMAGE -->
- 接线图位置: <!-- WIRING_IMAGE -->
- 尺寸图位置: <!-- DIMENSION_IMAGE -->
"""
        
        messages = [{"role": "user", "content": prompt}]
        return self._call_api(messages, max_tokens=16384)
    
    def translate_image_annotations(self, image_base64: str, image_type: str = "diagram") -> dict:
        """
        分析图片中的标注文字，生成英文图例
        """
        content = [
            {
                "type": "text",
                "text": f"""请分析这张{image_type}图片中的所有中文标注和文字。

任务:
1. 识别图片中的所有中文文字
2. 将每个中文标注翻译成英文
3. 如果是接线图，识别线色和对应功能

输出 JSON 格式:
```json
{{
  "annotations": [
    {{"chinese": "中文标注", "english": "English annotation", "position": "位置描述"}}
  ],
  "legend": [
    {{"item": "项目", "description": "英文描述"}}
  ],
  "figure_caption": "Figure X. 英文图片标题"
}}
```"""
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            }
        ]
        
        messages = [{"role": "user", "content": content}]
        response = self._call_api(messages, max_tokens=2048)
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {"raw_response": response}
