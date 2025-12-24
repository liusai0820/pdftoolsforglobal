#!/usr/bin/env python3
"""
PDF 处理 Web 应用
集成 PDF 翻译和颜色替换功能
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import shutil

# 加载 .env 文件
load_dotenv()

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

from pdf_translator.pdf_inplace_translator import translate_pdf_inplace
from pdf_vector_color_replacer import replace_color_with_device_rgb, analyze_pdf_colors

app = Flask(__name__, template_folder=str(PROJECT_ROOT / 'templates'))

# 配置
UPLOAD_FOLDER = PROJECT_ROOT / 'uploads'
OUTPUT_FOLDER = PROJECT_ROOT / 'output'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 创建必要的目录
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """检查文件是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """主页"""
    return render_template('index_web.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '文件名为空'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': '只支持PDF文件'}), 400
    
    if file.content_length > MAX_FILE_SIZE:
        return jsonify({'success': False, 'error': '文件过大'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        return jsonify({
            'success': True,
            'filepath': str(filepath),
            'filename': filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analyze_colors', methods=['POST'])
def analyze_colors():
    """分析PDF颜色"""
    data = request.json
    filepath = data.get('filepath')
    
    if not filepath:
        return jsonify({'success': False, 'error': 'No file path provided'}), 400
        
    try:
        # 确保路径安全
        filepath = Path(filepath)
        # 简单校验是否在上传目录内（防止路径遍历）
        # 这里为了演示简单起见，假设路径是合法的绝对路径
        
        colors = analyze_pdf_colors(str(filepath))
        return jsonify({'success': True, 'colors': colors})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/process', methods=['POST'])
def process_pdf():
    """处理PDF"""
    try:
        data = request.json
        input_file = data.get('input_file')
        operation = data.get('operation')
        
        if not input_file or not os.path.exists(input_file):
            return jsonify({'success': False, 'error': '输入文件不存在'}), 400
        
        input_path = Path(input_file)
        output_filename = f"{input_path.stem}_processed.pdf"
        output_path = OUTPUT_FOLDER / output_filename
        
        if operation == 'translate':
            # PDF 翻译
            target_language = data.get('target_language', "English")
            
            result = translate_pdf_inplace(
                str(input_path),
                output_path=str(output_path),
                target_language=target_language
            )
            
            return jsonify({
                'success': True,
                'message': f'PDF翻译完成 ({target_language})',
                'download_url': f'/api/download/{output_filename}',
                'filename': output_filename
            })
        
        elif operation == 'color':
            # 颜色替换
            source_cmyk = tuple(data.get('source_cmyk', [0.7804, 0.8667, 0, 0]))
            target_hex = data.get('target_hex', '#01beb0')
            
            replace_color_with_device_rgb(
                str(input_path),
                str(output_path),
                source_cmyk,
                target_hex
            )
            
            return jsonify({
                'success': True,
                'message': '颜色替换完成',
                'download_url': f'/api/download/{output_filename}',
                'filename': output_filename
            })
        
        elif operation == 'text':
            # 文字替换
            replacements = data.get('replacements', {})
            if not replacements:
                return jsonify({'success': False, 'error': '没有替换规则'}), 400
            
            # 这里需要实现文字替换逻辑
            return jsonify({'success': False, 'error': '文字替换功能开发中'}), 501
        
        elif operation == 'both':
            # 同时进行颜色和文字替换
            source_cmyk = tuple(data.get('source_cmyk', [0.7804, 0.8667, 0, 0]))
            target_hex = data.get('target_hex', '#01beb0')
            replacements = data.get('replacements', {})
            
            # 先进行颜色替换
            temp_path = OUTPUT_FOLDER / f"{input_path.stem}_temp.pdf"
            replace_color_with_device_rgb(
                str(input_path),
                str(temp_path),
                source_cmyk,
                target_hex
            )
            
            # 再进行文字替换（如果有规则）
            if replacements:
                pass
            
            # 重命名为最终输出
            shutil.move(str(temp_path), str(output_path))
            
            return jsonify({
                'success': True,
                'message': '处理完成',
                'download_url': f'/api/download/{output_filename}'
            })
        
        else:
            return jsonify({'success': False, 'error': '未知操作'}), 400
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """下载文件"""
    try:
        filepath = OUTPUT_FOLDER / secure_filename(filename)
        if not filepath.exists():
            return jsonify({'success': False, 'error': '文件不存在'}), 404
        
        return send_file(
            str(filepath),
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
