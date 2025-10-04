"""
Data formatting utilities
"""

from typing import Dict, Any


def formatFileSize(bytes: int) -> str:
    """Format file size in bytes to human readable format"""
    if bytes == 0:
        return "0 Bytes"
    
    import math
    k = 1024
    sizes = ["Bytes", "KB", "MB", "GB"]
    i = int(math.floor(math.log(bytes) / math.log(k)))
    
    return f"{math.floor((bytes / math.pow(k, i)) * 100) / 100} {sizes[i]}"


def formatScanResult(scanResult: Dict[str, Any]) -> str:
    """Format OCR scan result to HTML"""
    if not scanResult:
        return "<p>Không có dữ liệu</p>"

    # Kiểm tra nếu là căn cước công dân Lào thì sử dụng format chuyên dụng
    if scanResult.get('document_type') == 'lao_cccd':
        return formatLaoCCCDResult(scanResult)

    # Format chung cho các loại tài liệu khác
    html = '<div class="scan-result">'

    if scanResult.get('text'):
        html += f'<h4><i class="fas fa-text-width"></i> Văn bản trích xuất:</h4>'
        html += f'<p class="extracted-text">{scanResult["text"]}</p>'

    if scanResult.get('document_type'):
        html += f'<h4><i class="fas fa-id-card"></i> Loại tài liệu:</h4>'
        html += f'<p class="document-type">{scanResult["document_type"]}</p>'

    if scanResult.get('display_name'):
        html += f'<h4><i class="fas fa-user"></i> Tên hiển thị:</h4>'
        html += f'<p class="display-name">{scanResult["display_name"]}</p>'

    # Add other fields
    excluded_fields = ["text", "document_type", "display_name", "img_base64"]
    for key, value in scanResult.items():
        if key not in excluded_fields:
            html += f'<h4><i class="fas fa-info-circle"></i> {key}:</h4>'
            html += f'<p>{value}</p>'

    html += "</div>"
    return html


def formatLaoCCCDResult(ocrResult: Dict[str, Any]) -> str:
    """Format OCR result for Lao CCCD to beautiful HTML display"""
    if not ocrResult:
        return "<p>Không có dữ liệu căn cước</p>"

    html = '<div class="lao-cccd-result">'
    
    # Header với tên tài liệu
    html += '<div class="cccd-header">'
    html += f'<h3><i class="fas fa-id-card"></i> {ocrResult.get("display_name", "Căn cước công dân Lào")}</h3>'
    html += '</div>'
    
    # Thông tin cá nhân chính
    fields = ocrResult.get('fields', {})
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
    if ocrResult.get('img_url'):
        html += '<div class="cccd-section">'
        html += '<h4><i class="fas fa-image"></i> Ảnh căn cước</h4>'
        html += '<div class="cccd-image-container">'
        html += f'<img src="{ocrResult["img_url"]}" alt="Ảnh căn cước công dân" class="cccd-image" />'
        html += '</div>'
        html += '</div>'
    
    # Văn bản gốc (nếu cần debug)
    if ocrResult.get('text'):
        html += '<div class="cccd-section">'
        html += '<h4><i class="fas fa-file-text"></i> Văn bản trích xuất</h4>'
        html += '<div class="cccd-text-container">'
        html += f'<pre class="cccd-text">{ocrResult["text"]}</pre>'
        html += '</div>'
        html += '</div>'
    
    html += '</div>'
    return html


def formatVerifyResult(verifyResult: Dict[str, Any]) -> str:
    """Format face verification result to HTML"""
    if not verifyResult:
        return "<p>Không có dữ liệu xác thực</p>"

    html = '<div class="verify-result">'

    # Handle new WebSocket API format
    if verifyResult.get('status') == "success":
        html += '<h4><i class="fas fa-check-circle"></i> Trạng thái:</h4>'
        html += '<p class="match-success">Xác thực thành công</p>'

        if verifyResult.get('same_person') is not None:
            matchStatus = "Cùng một người" if verifyResult['same_person'] else "Không cùng người"
            matchClass = "match-success" if verifyResult['same_person'] else "match-fail"
            html += '<h4><i class="fas fa-user-check"></i> Kết quả:</h4>'
            html += f'<p class="{matchClass}">{matchStatus}</p>'

        if verifyResult.get('similarity') is not None:
            html += '<h4><i class="fas fa-percentage"></i> Độ tương đồng:</h4>'
            html += f'<p class="match-score">{(verifyResult["similarity"] * 100):.2f}%</p>'

        if verifyResult.get('msg'):
            html += '<h4><i class="fas fa-comment"></i> Thông báo:</h4>'
            html += f'<p>{verifyResult["msg"]}</p>'
    else:
        html += '<h4><i class="fas fa-times-circle"></i> Trạng thái:</h4>'
        html += '<p class="match-fail">Xác thực thất bại</p>'

        if verifyResult.get('msg'):
            html += '<h4><i class="fas fa-exclamation-triangle"></i> Lỗi:</h4>'
            html += f'<p>{verifyResult["msg"]}</p>'

    # Handle legacy format (backward compatibility)
    if verifyResult.get('match_score') is not None:
        html += '<h4><i class="fas fa-percentage"></i> Điểm khớp:</h4>'
        html += f'<p class="match-score">{(verifyResult["match_score"] * 100):.2f}%</p>'

    if verifyResult.get('is_match') is not None:
        matchStatus = "Khớp" if verifyResult['is_match'] else "Không khớp"
        matchClass = "match-success" if verifyResult['is_match'] else "match-fail"
        html += '<h4><i class="fas fa-check-circle"></i> Kết quả:</h4>'
        html += f'<p class="{matchClass}">{matchStatus}</p>'

    if verifyResult.get('confidence') is not None:
        html += '<h4><i class="fas fa-chart-line"></i> Độ tin cậy:</h4>'
        html += f'<p class="confidence">{(verifyResult["confidence"] * 100):.2f}%</p>'

    # Add other fields
    excluded_fields = [
        "status", "same_person", "similarity", "msg",
        "match_score", "is_match", "confidence"
    ]
    for key, value in verifyResult.items():
        if key not in excluded_fields:
            html += f'<h4><i class="fas fa-info-circle"></i> {key}:</h4>'
            html += f'<p>{value}</p>'

    html += "</div>"
    return html
