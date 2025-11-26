#!/usr/bin/env python3
"""
Web 界面
提供可视化的 PDF 翻译服务
"""
import os
import sys
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, send_file
from werkzeug.utils import secure_filename

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.pdf_translator.pipeline import TranslationPipeline
from scripts.pdf_translator.config import OUTPUT_DIR, DEFAULT_MODEL

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF 技术文档翻译器</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .upload-area {
            border: 2px dashed #ddd;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .upload-area:hover, .upload-area.dragover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        .upload-area input { display: none; }
        .upload-icon { font-size: 48px; margin-bottom: 10px; }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #333;
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        .checkbox-group {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .checkbox-group label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: normal;
            cursor: pointer;
        }
        button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .progress {
            display: none;
            margin-top: 20px;
        }
        .progress-bar {
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .status {
            margin-top: 10px;
            color: #666;
            font-size: 14px;
        }
        .results {
            display: none;
            margin-top: 30px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 12px;
        }
        .results h3 {
            margin-bottom: 15px;
            color: #333;
        }
        .file-list {
            list-style: none;
        }
        .file-list li {
            padding: 12px;
            background: white;
            border-radius: 8px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-list a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        .error {
            color: #e74c3c;
            background: #fdf0f0;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }
        .file-name {
            margin-top: 10px;
            color: #333;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 PDF 技术文档翻译器</h1>
        <p class="subtitle">中文技术文档 → 英文 Datasheet / User Manual</p>
        
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📁</div>
            <p>点击或拖拽 PDF 文件到这里</p>
            <input type="file" id="fileInput" accept=".pdf">
            <p class="file-name" id="fileName"></p>
        </div>
        
        <div class="form-group">
            <label>OpenRouter API Key</label>
            <input type="text" id="apiKey" placeholder="sk-or-..." value="">
        </div>
        
        <div class="form-group">
            <label>AI 模型</label>
            <select id="model">
                <option value="google/gemini-2.5-flash">Gemini 2.5 Flash (推荐)</option>
                <option value="google/gemini-2.0-flash-exp">Gemini 2.0 Flash</option>
                <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
                <option value="openai/gpt-4o">GPT-4o</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>输出格式</label>
            <div class="checkbox-group">
                <label><input type="checkbox" name="format" value="datasheet" checked> Datasheet</label>
                <label><input type="checkbox" name="format" value="manual" checked> User Manual</label>
                <label><input type="checkbox" name="format" value="markdown" checked> Markdown 源文件</label>
            </div>
        </div>
        
        <button id="submitBtn" onclick="processFile()">🚀 开始翻译</button>
        
        <div class="progress" id="progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <p class="status" id="status">准备中...</p>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="results" id="results">
            <h3>✅ 生成完成</h3>
            <ul class="file-list" id="fileList"></ul>
        </div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        let selectedFile = null;
        
        uploadArea.onclick = () => fileInput.click();
        
        uploadArea.ondragover = (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        };
        
        uploadArea.ondragleave = () => uploadArea.classList.remove('dragover');
        
        uploadArea.ondrop = (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files[0]) {
                selectedFile = e.dataTransfer.files[0];
                fileName.textContent = selectedFile.name;
            }
        };
        
        fileInput.onchange = () => {
            if (fileInput.files[0]) {
                selectedFile = fileInput.files[0];
                fileName.textContent = selectedFile.name;
            }
        };
        
        async function processFile() {
            const apiKey = document.getElementById('apiKey').value;
            const model = document.getElementById('model').value;
            const formats = [...document.querySelectorAll('input[name="format"]:checked')].map(c => c.value);
            
            if (!selectedFile) {
                showError('请选择 PDF 文件');
                return;
            }
            if (!apiKey) {
                showError('请输入 OpenRouter API Key');
                return;
            }
            if (formats.length === 0) {
                showError('请至少选择一种输出格式');
                return;
            }
            
            document.getElementById('submitBtn').disabled = true;
            document.getElementById('progress').style.display = 'block';
            document.getElementById('error').style.display = 'none';
            document.getElementById('results').style.display = 'none';
            
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('api_key', apiKey);
            formData.append('model', model);
            formData.append('formats', JSON.stringify(formats));
            
            try {
                updateStatus('上传文件...', 10);
                
                const response = await fetch('/api/translate', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showError(result.error);
                } else {
                    showResults(result);
                }
            } catch (e) {
                showError('处理失败: ' + e.message);
            }
            
            document.getElementById('submitBtn').disabled = false;
        }
        
        function updateStatus(text, percent) {
            document.getElementById('status').textContent = text;
            document.getElementById('progressFill').style.width = percent + '%';
        }
        
        function showError(msg) {
            document.getElementById('error').textContent = msg;
            document.getElementById('error').style.display = 'block';
            document.getElementById('progress').style.display = 'none';
        }
        
        function showResults(result) {
            document.getElementById('progress').style.display = 'none';
            document.getElementById('results').style.display = 'block';
            
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '';
            
            for (const [name, path] of Object.entries(result.files || {})) {
                const li = document.createElement('li');
                const displayName = path.split('/').pop();
                li.innerHTML = `
                    <span>${displayName}</span>
                    <a href="/api/download?path=${encodeURIComponent(path)}" download>下载</a>
                `;
                fileList.appendChild(li);
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        api_key = request.form.get('api_key')
        model = request.form.get('model', DEFAULT_MODEL)
        formats = request.form.get('formats', '["datasheet", "manual", "markdown"]')
        
        import json
        formats = json.loads(formats)
        
        if not api_key:
            return jsonify({'error': '请提供 API Key'}), 400
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        filepath = UPLOAD_DIR / filename
        file.save(str(filepath))
        
        # 处理文件
        pipeline = TranslationPipeline(api_key=api_key, model=model)
        results = pipeline.process(str(filepath), output_formats=formats)
        
        return jsonify(results)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/download')
def download():
    path = request.args.get('path')
    if not path or not Path(path).exists():
        return jsonify({'error': '文件不存在'}), 404
    return send_file(path, as_attachment=True)


def run_server(host='0.0.0.0', port=8889):
    print(f"🚀 启动 PDF 翻译服务: http://localhost:{port}")
    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    run_server()
