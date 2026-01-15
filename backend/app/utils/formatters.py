"""
Data formatting utilities for Laos eKYC Agent
"""

from typing import Dict, Any, Optional
import math


def format_file_size(bytes_size: int) -> str:
    """Format file size in bytes to human readable format"""
    if bytes_size == 0:
        return "0 Bytes"

    k = 1024
    sizes = ["Bytes", "KB", "MB", "GB"]
    i = int(math.floor(math.log(bytes_size) / math.log(k)))

    return f"{math.floor((bytes_size / math.pow(k, i)) * 100) / 100} {sizes[i]}"


def format_scan_result(scan_result: Optional[Dict[str, Any]]) -> str:
    """Format OCR scan result to Markdown"""
    if not scan_result:
        return "ບໍ່ມີຂໍ້ມູນການສະແກນ"

    # Check if it's Lao CCCD format
    if scan_result.get("document_type") == "lao_cccd":
        return format_lao_cccd_result(scan_result)

    # Generic format
    md = "**ຜົນການສະແກນ**\n\n"

    if scan_result.get("text"):
        md += f"**ຂໍ້ຄວາມທີ່ດຶງໄດ້:**\n{scan_result['text']}\n\n"

    if scan_result.get("document_type"):
        md += f"**ປະເພດເອກະສານ:** {scan_result['document_type']}\n"

    if scan_result.get("display_name"):
        md += f"**ຊື່ສະແດງ:** {scan_result['display_name']}\n"

    # Add other fields
    excluded_fields = ["text", "document_type", "display_name", "img_base64", "raw_data", "timestamp"]
    for key, value in scan_result.items():
        if key not in excluded_fields and value:
            md += f"**{key}:** {value}\n"

    return md


def format_lao_cccd_result(ocr_result: Dict[str, Any]) -> str:
    """Format OCR result for Lao CCCD to clean Markdown display"""
    if not ocr_result:
        return "ບໍ່ມີຂໍ້ມູນບັດປະຈຳຕົວ"

    md = "### ບັດປະຈຳຕົວປະຊາຊົນລາວ\n\n"

    # Personal information
    fields = ocr_result.get("fields", {})
    if fields:
        md += "**ຂໍ້ມູນສ່ວນຕົວ**\n"

        # ID number
        if fields.get("id_number"):
            md += f"- **ເລກບັດ:** {fields['id_number']}\n"

        # Full name
        if fields.get("fullname"):
            md += f"- **ຊື່ ແລະ ນາມສະກຸນ:** {fields['fullname']}\n"

        # Date of birth
        if fields.get("dob"):
            md += f"- **ວັນເດືອນປີເກີດ:** {fields['dob']}\n"

        # Nationality
        if fields.get("nationality"):
            md += f"- **ສັນຊາດ:** {fields['nationality']}\n"

        # Ethnicity
        if fields.get("ethnicity"):
            md += f"- **ຊົນເຜົ່າ:** {fields['ethnicity']}\n"

        md += "\n"

        # Address
        address = fields.get("address", {})
        if address:
            md += "**ທີ່ຢູ່**\n"

            if address.get("address"):
                md += f"- **ທີ່ຢູ່:** {address['address']}\n"

            children = address.get("childrent", {})
            if children:
                if children.get("address_village"):
                    md += f"- **ບ້ານ:** {children['address_village']}\n"

                if children.get("address_district"):
                    md += f"- **ເມືອງ:** {children['address_district']}\n"

                if children.get("address_province"):
                    md += f"- **ແຂວງ:** {children['address_province']}\n"

            md += "\n"

        # Dates
        md += "**ຂໍ້ມູນວັນທີ**\n"
        if fields.get("issue_date"):
            md += f"- **ວັນທີອອກບັດ:** {fields['issue_date']}\n"

        if fields.get("expiry_date"):
            md += f"- **ວັນທີໝົດອາຍຸ:** {fields['expiry_date']}\n"

    return md


def format_verify_result(verify_result: Optional[Dict[str, Any]]) -> str:
    """Format face verification result to clean Markdown"""
    if not verify_result:
        return "ບໍ່ມີຂໍ້ມູນການຢັ້ງຢືນ"

    md = "### ຜົນການຢັ້ງຢືນໃບໜ້າ\n\n"

    same_person = verify_result.get("same_person")
    similarity = verify_result.get("similarity")

    if same_person is not None:
        if same_person:
            md += "**ການຢັ້ງຢືນສຳເລັດ!**\n"
            md += "ໃບໜ້າໃນບັດ ແລະ ຮູບຖ່າຍກົງກັນ.\n\n"

            if similarity is not None:
                similarity_percent = (similarity + 1) / 2 * 100
                md += f"- **ຄວາມຄ້າຍຄືກັນ:** {similarity_percent:.1f}%\n"
        else:
            md += "**ການຢັ້ງຢືນລົ້ມເຫລວ**\n"
            md += "ໃບໜ້າໃນບັດ ແລະ ຮູບຖ່າຍບໍ່ກົງກັນ.\n\n"

            if similarity is not None:
                similarity_percent = (similarity + 1) / 2 * 100
                md += f"- **ຄວາມຄ້າຍຄືກັນ:** {similarity_percent:.1f}%\n"
    else:
        md += "**ເກີດຂໍ້ຜິດພາດ**\n"
        md += "ເກີດຂໍ້ຜິດພາດໃນການຢັ້ງຢືນໃບໜ້າ.\n"

    return md
