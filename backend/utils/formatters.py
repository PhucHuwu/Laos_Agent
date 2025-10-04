"""
Data formatting utilities for Laos eKYC Agent
"""

from typing import Dict, Any
import re


def format_file_size(bytes_size: int) -> str:
    """Format file size in bytes to human readable format"""
    if bytes_size == 0:
        return "0 Bytes"

    import math
    k = 1024
    sizes = ["Bytes", "KB", "MB", "GB"]
    i = int(math.floor(math.log(bytes_size) / math.log(k)))

    return f"{math.floor((bytes_size / math.pow(k, i)) * 100) / 100} {sizes[i]}"


def format_lao_cccd_result(ocr_result: Dict[str, Any]) -> str:
    """Format OCR result for Lao CCCD to beautiful HTML display"""
    if not ocr_result:
        return "<p>Không có dữ liệu căn cước</p>"

    html = '<div class="lao-cccd-result">'

    # Header với tên tài liệu
    html += '<div class="cccd-header">'
    html += f'<h3><i class="fas fa-id-card"></i> {ocr_result.get("display_name", "Căn cước công dân Lào")}</h3>'
    html += '</div>'

    # Thông tin cá nhân chính
    fields = ocr_result.get('fields', {})
    if fields:
        html += '<div class="cccd-section">'
        html += '<h4><i class="fas fa-user"></i> Thông tin cá nhân</h4>'
        html += '<div class="cccd-info-grid">'

        # Số căn cước
        if fields.get('id_number'):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-hashtag"></i> Số căn cước:</span>'
            html += f'<span class="info-value">{fields["id_number"]}</span>'
            html += '</div>'

        # Họ tên
        if fields.get('fullname'):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-signature"></i> Họ và tên:</span>'
            html += f'<span class="info-value">{fields["fullname"]}</span>'
            html += '</div>'

        # Ngày sinh
        if fields.get('dob'):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-birthday-cake"></i> Ngày sinh:</span>'
            html += f'<span class="info-value">{fields["dob"]}</span>'
            html += '</div>'

        # Quốc tịch
        if fields.get('nationality'):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-flag"></i> Quốc tịch:</span>'
            html += f'<span class="info-value">{fields["nationality"]}</span>'
            html += '</div>'

        # Dân tộc
        if fields.get('ethnicity'):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-users"></i> Dân tộc:</span>'
            html += f'<span class="info-value">{fields["ethnicity"]}</span>'
            html += '</div>'

        html += '</div>'
        html += '</div>'

        # Thông tin địa chỉ
        address = fields.get('address', {})
        if address:
            html += '<div class="cccd-section">'
            html += '<h4><i class="fas fa-map-marker-alt"></i> Địa chỉ</h4>'
            html += '<div class="cccd-info-grid">'

            # Địa chỉ đầy đủ
            if address.get('address'):
                html += '<div class="info-item full-width">'
                html += '<span class="info-label"><i class="fas fa-home"></i> Địa chỉ:</span>'
                html += f'<span class="info-value">{address["address"]}</span>'
                html += '</div>'

            # Chi tiết địa chỉ
            children = address.get('childrent', {})
            if children:
                if children.get('address_village'):
                    html += '<div class="info-item">'
                    html += '<span class="info-label"><i class="fas fa-building"></i> Thôn/Bản:</span>'
                    html += f'<span class="info-value">{children["address_village"]}</span>'
                    html += '</div>'

                if children.get('address_district'):
                    html += '<div class="info-item">'
                    html += '<span class="info-label"><i class="fas fa-map"></i> Huyện:</span>'
                    html += f'<span class="info-value">{children["address_district"]}</span>'
                    html += '</div>'

                if children.get('address_province'):
                    html += '<div class="info-item">'
                    html += '<span class="info-label"><i class="fas fa-city"></i> Tỉnh:</span>'
                    html += f'<span class="info-value">{children["address_province"]}</span>'
                    html += '</div>'

            html += '</div>'
            html += '</div>'

        # Thông tin thời hạn
        html += '<div class="cccd-section">'
        html += '<h4><i class="fas fa-calendar-alt"></i> Thông tin thời hạn</h4>'
        html += '<div class="cccd-info-grid">'

        if fields.get('issue_date'):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-calendar-plus"></i> Ngày cấp:</span>'
            html += f'<span class="info-value">{fields["issue_date"]}</span>'
            html += '</div>'

        if fields.get('expiry_date'):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-calendar-times"></i> Ngày hết hạn:</span>'
            html += f'<span class="info-value">{fields["expiry_date"]}</span>'
            html += '</div>'

        html += '</div>'
        html += '</div>'

    # Hiển thị ảnh nếu có
    if ocr_result.get('img_url'):
        html += '<div class="cccd-section">'
        html += '<h4><i class="fas fa-image"></i> Ảnh căn cước</h4>'
        html += '<div class="cccd-image-container">'
        html += f'<img src="{ocr_result["img_url"]}" alt="Ảnh căn cước công dân" class="cccd-image" />'
        html += '</div>'
        html += '</div>'

    # Văn bản gốc (nếu cần debug)
    if ocr_result.get('text'):
        html += '<div class="cccd-section">'
        html += '<h4><i class="fas fa-file-text"></i> Văn bản trích xuất</h4>'
        html += '<div class="cccd-text-container">'
        # Convert list to string if needed
        text_content = ocr_result["text"]
        if isinstance(text_content, list):
            text_content = "\n".join(text_content)
        html += f'<pre class="cccd-text">{text_content}</pre>'
        html += '</div>'
        html += '</div>'

    html += '</div>'
    return html


def format_scan_result(scan_result: Dict[str, Any]) -> str:
    """Format OCR scan result to HTML"""
    if not scan_result:
        return "<p>Không có dữ liệu</p>"

    # Kiểm tra nếu là căn cước công dân Lào thì sử dụng format chuyên dụng
    if scan_result.get('document_type') == 'lao_cccd':
        return format_lao_cccd_result(scan_result)

    # Format chung cho các loại tài liệu khác
    html = '<div class="scan-result">'

    if scan_result.get('text'):
        html += f'<h4><i class="fas fa-text-width"></i> Văn bản trích xuất:</h4>'
        html += f'<p class="extracted-text">{scan_result["text"]}</p>'

    if scan_result.get('document_type'):
        html += f'<h4><i class="fas fa-id-card"></i> Loại tài liệu:</h4>'
        html += f'<p class="document-type">{scan_result["document_type"]}</p>'

    if scan_result.get('display_name'):
        html += f'<h4><i class="fas fa-user"></i> Tên hiển thị:</h4>'
        html += f'<p class="display-name">{scan_result["display_name"]}</p>'

    # Add other fields
    excluded_fields = ["text", "document_type", "display_name", "img_base64"]
    for key, value in scan_result.items():
        if key not in excluded_fields:
            html += f'<h4><i class="fas fa-info-circle"></i> {key}:</h4>'
            html += f'<p>{value}</p>'

    html += "</div>"
    return html


def format_verify_result(verify_result: Dict[str, Any]) -> str:
    """Format face verification result to user-friendly HTML"""
    if not verify_result:
        return "<p>Không có dữ liệu xác thực</p>"

    html = '<div class="face-verification-result">'

    # Header với icon và tiêu đề
    html += '<div class="verification-header">'
    html += '<h3><i class="fas fa-user-check"></i> Kết quả xác thực khuôn mặt</h3>'
    html += '</div>'

    # Xác định trạng thái chính
    is_success = verify_result.get('status') == "success"
    same_person = verify_result.get('same_person')
    similarity = verify_result.get('similarity')

    # Legacy format support
    if same_person is None:
        same_person = verify_result.get('is_match')
    if similarity is None:
        similarity = verify_result.get('match_score')

    if is_success and same_person is not None:
        # Thành công và có kết quả
        if same_person:
            # Xác thực thành công
            html += '<div class="verification-success">'
            html += '<div class="success-icon">'
            html += '<i class="fas fa-check-circle"></i>'
            html += '</div>'
            html += '<div class="success-content">'
            html += '<h4>✅ Xác thực thành công!</h4>'
            html += '<p>Khuôn mặt trong ảnh căn cước và ảnh selfie là cùng một người.</p>'

            # Hiển thị độ tương đồng một cách thân thiện
            if similarity is not None:
                similarity_percent = similarity * 100 if similarity <= 1 else similarity
                html += '<div class="similarity-display">'
                html += f'<div class="similarity-score">{similarity_percent:.1f}%</div>'
                html += '<div class="similarity-label">Độ khớp</div>'
                html += '</div>'

            html += '</div>'
            html += '</div>'

            # Thông báo tiếp theo
            html += '<div class="next-steps">'
            html += '<h5><i class="fas fa-info-circle"></i> Bước tiếp theo:</h5>'
            html += '<p>Quá trình eKYC của bạn đã hoàn tất thành công! Bạn có thể sử dụng dịch vụ.</p>'
            html += '</div>'

        else:
            # Xác thực thất bại
            html += '<div class="verification-failed">'
            html += '<div class="failed-icon">'
            html += '<i class="fas fa-times-circle"></i>'
            html += '</div>'
            html += '<div class="failed-content">'
            html += '<h4>❌ Xác thực không thành công</h4>'
            html += '<p>Khuôn mặt trong ảnh căn cước và ảnh selfie không khớp nhau.</p>'

            if similarity is not None:
                similarity_percent = similarity * 100 if similarity <= 1 else similarity
                html += '<div class="similarity-display">'
                html += f'<div class="similarity-score low">{similarity_percent:.1f}%</div>'
                html += '<div class="similarity-label">Độ khớp</div>'
                html += '</div>'

            html += '</div>'
            html += '</div>'

            # Hướng dẫn khắc phục
            html += '<div class="troubleshooting">'
            html += '<h5><i class="fas fa-lightbulb"></i> Gợi ý khắc phục:</h5>'
            html += '<ul>'
            html += '<li>Đảm bảo ánh sáng đủ sáng khi chụp ảnh</li>'
            html += '<li>Nhìn thẳng vào camera, không đeo kính râm</li>'
            html += '<li>Chụp ảnh selfie với góc độ tương tự như ảnh căn cước</li>'
            html += '<li>Thử lại với ảnh selfie khác</li>'
            html += '</ul>'
            html += '</div>'
    else:
        # Lỗi hoặc không có kết quả
        html += '<div class="verification-error">'
        html += '<div class="error-icon">'
        html += '<i class="fas fa-exclamation-triangle"></i>'
        html += '</div>'
        html += '<div class="error-content">'
        html += '<h4>⚠️ Không thể xác thực</h4>'
        html += '<p>Có lỗi xảy ra trong quá trình xác thực khuôn mặt.</p>'

        if verify_result.get('msg'):
            html += f'<div class="error-message">{verify_result["msg"]}</div>'

        html += '</div>'
        html += '</div>'

        # Hướng dẫn khắc phục
        html += '<div class="troubleshooting">'
        html += '<h5><i class="fas fa-tools"></i> Khắc phục sự cố:</h5>'
        html += '<ul>'
        html += '<li>Kiểm tra kết nối internet</li>'
        html += '<li>Thử lại sau vài phút</li>'
        html += '<li>Liên hệ hỗ trợ nếu vấn đề tiếp tục</li>'
        html += '</ul>'
        html += '</div>'

    html += '</div>'
    return html


def format_markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown text to beautiful HTML for chatbot responses"""
    if not markdown_text:
        return "<p>Không có nội dung</p>"

    html = '<div class="chatbot-response">'

    # Split into lines for processing
    lines = markdown_text.split('\n')
    in_list = False
    in_code_block = False

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            if in_list:
                html += '</ul>'
                in_list = False
            html += '<br>'
            continue

        # Code blocks
        if line.startswith('```'):
            if not in_code_block:
                html += '<div class="code-block"><pre><code>'
                in_code_block = True
            else:
                html += '</code></pre></div>'
                in_code_block = False
            continue

        if in_code_block:
            html += f'{line}\n'
            continue

        # Headers
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('# ').strip()
            html += f'<h{min(level, 6)} class="response-header">{header_text}</h{min(level, 6)}>'
            continue

        # Lists
        if line.startswith('- ') or line.startswith('* '):
            if not in_list:
                html += '<ul class="response-list">'
                in_list = True
            item_text = line[2:].strip()
            # Process bold/italic in list items
            item_text = _process_inline_formatting(item_text)
            html += f'<li class="response-list-item">{item_text}</li>'
            continue

        # Numbered lists
        if re.match(r'^\d+\.\s', line):
            if not in_list:
                html += '<ol class="response-list">'
                in_list = True
            item_text = re.sub(r'^\d+\.\s', '', line).strip()
            item_text = _process_inline_formatting(item_text)
            html += f'<li class="response-list-item">{item_text}</li>'
            continue

        # End list if we hit a non-list item
        if in_list:
            html += '</ul>'
            in_list = False

        # Regular paragraphs
        if line:
            processed_line = _process_inline_formatting(line)
            html += f'<p class="response-paragraph">{processed_line}</p>'

    # Close any open list
    if in_list:
        html += '</ul>'

    html += '</div>'
    return html


def _process_inline_formatting(text: str) -> str:
    """Process inline Markdown formatting (bold, italic, etc.)"""
    # Bold text **text** or __text__
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong class="response-bold">\1</strong>', text)
    text = re.sub(r'__(.*?)__', r'<strong class="response-bold">\1</strong>', text)

    # Italic text *text* or _text_
    text = re.sub(r'\*(.*?)\*', r'<em class="response-italic">\1</em>', text)
    text = re.sub(r'_(.*?)_', r'<em class="response-italic">\1</em>', text)

    # Inline code `code`
    text = re.sub(r'`(.*?)`', r'<code class="response-code">\1</code>', text)

    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" class="response-link" target="_blank">\1</a>', text)

    return text


def format_chatbot_response(response_text: str) -> str:
    """Format chatbot response text to clean, readable HTML"""
    if not response_text:
        return "<p>Không có phản hồi</p>"

    # Check if it's already HTML
    if response_text.strip().startswith('<'):
        return response_text

    # Convert Markdown to HTML
    return format_markdown_to_html(response_text)
