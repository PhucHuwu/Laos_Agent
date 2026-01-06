"""
Data formatting utilities for Laos eKYC Agent
"""

from typing import Dict, Any, Optional


def format_file_size(bytes_size: int) -> str:
    """Format file size in bytes to human readable format"""
    if bytes_size == 0:
        return "0 Bytes"

    import math
    k = 1024
    sizes = ["Bytes", "KB", "MB", "GB"]
    i = int(math.floor(math.log(bytes_size) / math.log(k)))

    return f"{math.floor((bytes_size / math.pow(k, i)) * 100) / 100} {sizes[i]}"


def format_scan_result(scan_result: Optional[Dict[str, Any]]) -> str:
    """Format OCR scan result to HTML"""
    if not scan_result:
        return "<p>No scan data</p>"

    # Check if it's Lao CCCD format
    if scan_result.get("document_type") == "lao_cccd":
        return format_lao_cccd_result(scan_result)

    # Generic format
    html = '<div class="scan-result">'

    if scan_result.get("text"):
        html += f'<h4><i class="fas fa-text-width"></i> Extracted Text:</h4>'
        html += f'<p class="extracted-text">{scan_result["text"]}</p>'

    if scan_result.get("document_type"):
        html += f'<h4><i class="fas fa-id-card"></i> Document Type:</h4>'
        html += f'<p class="document-type">{scan_result["document_type"]}</p>'

    if scan_result.get("display_name"):
        html += f'<h4><i class="fas fa-user"></i> Display Name:</h4>'
        html += f'<p class="display-name">{scan_result["display_name"]}</p>'

    # Add other fields
    excluded_fields = ["text", "document_type", "display_name", "img_base64", "raw_data", "timestamp"]
    for key, value in scan_result.items():
        if key not in excluded_fields and value:
            html += f'<h4><i class="fas fa-info-circle"></i> {key}:</h4>'
            html += f'<p>{value}</p>'

    html += "</div>"
    return html


def format_lao_cccd_result(ocr_result: Dict[str, Any]) -> str:
    """Format OCR result for Lao CCCD to beautiful HTML display"""
    if not ocr_result:
        return "<p>No ID card data</p>"

    html = '<div class="lao-cccd-result">'

    # Header
    html += '<div class="cccd-header">'
    html += '<h3><i class="fas fa-id-card"></i> Lao National ID Card</h3>'
    html += '</div>'

    # Personal information
    fields = ocr_result.get("fields", {})
    if fields:
        html += '<div class="cccd-section">'
        html += '<h4><i class="fas fa-user"></i> Personal Information</h4>'
        html += '<div class="cccd-info-grid">'

        # ID number
        if fields.get("id_number"):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-hashtag"></i> ID Number:</span>'
            html += f'<span class="info-value">{fields["id_number"]}</span>'
            html += '</div>'

        # Full name
        if fields.get("fullname"):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-signature"></i> Full Name:</span>'
            html += f'<span class="info-value">{fields["fullname"]}</span>'
            html += '</div>'

        # Date of birth
        if fields.get("dob"):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-birthday-cake"></i> Date of Birth:</span>'
            html += f'<span class="info-value">{fields["dob"]}</span>'
            html += '</div>'

        # Nationality
        if fields.get("nationality"):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-flag"></i> Nationality:</span>'
            html += f'<span class="info-value">{fields["nationality"]}</span>'
            html += '</div>'

        # Ethnicity
        if fields.get("ethnicity"):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-users"></i> Ethnicity:</span>'
            html += f'<span class="info-value">{fields["ethnicity"]}</span>'
            html += '</div>'

        html += '</div>'
        html += '</div>'

        # Address
        address = fields.get("address", {})
        if address:
            html += '<div class="cccd-section">'
            html += '<h4><i class="fas fa-map-marker-alt"></i> Address</h4>'
            html += '<div class="cccd-info-grid">'

            if address.get("address"):
                html += '<div class="info-item full-width">'
                html += '<span class="info-label"><i class="fas fa-home"></i> Address:</span>'
                html += f'<span class="info-value">{address["address"]}</span>'
                html += '</div>'

            children = address.get("childrent", {})
            if children:
                if children.get("address_village"):
                    html += '<div class="info-item">'
                    html += '<span class="info-label"><i class="fas fa-building"></i> Village:</span>'
                    html += f'<span class="info-value">{children["address_village"]}</span>'
                    html += '</div>'

                if children.get("address_district"):
                    html += '<div class="info-item">'
                    html += '<span class="info-label"><i class="fas fa-map"></i> District:</span>'
                    html += f'<span class="info-value">{children["address_district"]}</span>'
                    html += '</div>'

                if children.get("address_province"):
                    html += '<div class="info-item">'
                    html += '<span class="info-label"><i class="fas fa-city"></i> Province:</span>'
                    html += f'<span class="info-value">{children["address_province"]}</span>'
                    html += '</div>'

            html += '</div>'
            html += '</div>'

        # Dates
        html += '<div class="cccd-section">'
        html += '<h4><i class="fas fa-calendar-alt"></i> Date Information</h4>'
        html += '<div class="cccd-info-grid">'

        if fields.get("issue_date"):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-calendar-plus"></i> Issue Date:</span>'
            html += f'<span class="info-value">{fields["issue_date"]}</span>'
            html += '</div>'

        if fields.get("expiry_date"):
            html += '<div class="info-item">'
            html += '<span class="info-label"><i class="fas fa-calendar-times"></i> Expiry Date:</span>'
            html += f'<span class="info-value">{fields["expiry_date"]}</span>'
            html += '</div>'

        html += '</div>'
        html += '</div>'

    html += '</div>'
    return html


def format_verify_result(verify_result: Optional[Dict[str, Any]]) -> str:
    """Format face verification result to user-friendly HTML"""
    if not verify_result:
        return "<p>No verification data</p>"

    html = '<div class="face-verification-result">'

    # Header
    html += '<div class="verification-header">'
    html += '<h3><i class="fas fa-user-check"></i> Face Verification Result</h3>'
    html += '</div>'

    same_person = verify_result.get("same_person")
    similarity = verify_result.get("similarity")

    if same_person is not None:
        if same_person:
            html += '<div class="verification-success">'
            html += '<div class="success-icon"><i class="fas fa-check-circle"></i></div>'
            html += '<div class="success-content">'
            html += '<h4>Verification Successful!</h4>'
            html += '<p>The face in ID card and selfie match.</p>'

            if similarity is not None:
                similarity_percent = (similarity + 1) / 2 * 100
                html += f'<div class="similarity-display">'
                html += f'<div class="similarity-score">{similarity_percent:.1f}%</div>'
                html += '<div class="similarity-label">Similarity</div>'
                html += '</div>'

            html += '</div>'
            html += '</div>'
        else:
            html += '<div class="verification-failed">'
            html += '<div class="failed-icon"><i class="fas fa-times-circle"></i></div>'
            html += '<div class="failed-content">'
            html += '<h4>Verification Failed</h4>'
            html += '<p>The face in ID card and selfie do not match.</p>'

            if similarity is not None:
                similarity_percent = (similarity + 1) / 2 * 100
                html += f'<div class="similarity-display">'
                html += f'<div class="similarity-score low">{similarity_percent:.1f}%</div>'
                html += '<div class="similarity-label">Similarity</div>'
                html += '</div>'

            html += '</div>'
            html += '</div>'
    else:
        html += '<div class="verification-error">'
        html += '<div class="error-icon"><i class="fas fa-exclamation-triangle"></i></div>'
        html += '<div class="error-content">'
        html += '<h4>Verification Error</h4>'
        html += '<p>An error occurred during face verification.</p>'
        html += '</div>'
        html += '</div>'

    html += '</div>'
    return html
