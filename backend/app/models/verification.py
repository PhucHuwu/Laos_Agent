"""
Verification and scan result models
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ScanResult(BaseModel):
    """Result from OCR scanning"""
    text: Optional[str] = None
    document_type: Optional[str] = None
    display_name: Optional[str] = None
    confidence: Optional[float] = None
    status: str = "success"
    message: Optional[str] = None
    fields: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ScanResult":
        """Create from API response - handles various data formats"""
        # Handle text field - can be string or list
        text_value = data.get("text")
        if isinstance(text_value, list):
            text_value = "\n".join(str(item) for item in text_value)
        elif text_value is not None:
            text_value = str(text_value)

        # Handle display_name - can be string or list
        display_name = data.get("display_name")
        if isinstance(display_name, list):
            display_name = " ".join(str(item) for item in display_name)
        elif display_name is not None:
            display_name = str(display_name)

        return cls(
            text=text_value,
            document_type=data.get("document_type"),
            display_name=display_name,
            confidence=data.get("confidence"),
            status=data.get("status", "success"),
            message=data.get("message"),
            fields=data.get("fields"),
            raw_data=data
        )

    def is_successful(self) -> bool:
        """Check if scan was successful and has valid data"""
        title_check = False
        if self.document_type:
            title_check = True
        
        # Check if we have at least some fields extracted
        fields_check = False
        if self.fields and len(self.fields) > 0:
            fields_check = True
            
        return (
            self.status == "success" and
            (title_check or fields_check)
        )


class VerificationResult(BaseModel):
    """Result from face verification"""
    same_person: Optional[bool] = None
    similarity: Optional[float] = None
    confidence: Optional[float] = None
    status: str = "success"
    message: Optional[str] = None
    bbox: Optional[List[float]] = None
    raw_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "VerificationResult":
        """Create from API response"""
        return cls(
            same_person=data.get("same_person"),
            similarity=data.get("similarity"),
            confidence=data.get("confidence"),
            status=data.get("status", "success"),
            message=data.get("message") or data.get("msg"),
            bbox=data.get("bbox"),
            raw_data=data
        )

    def is_successful(self) -> bool:
        """Check if verification was successful"""
        return (
            self.status == "success" and
            self.same_person is True and
            self.similarity is not None and
            self.similarity > 0.5
        )
