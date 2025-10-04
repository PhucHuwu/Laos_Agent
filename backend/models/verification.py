"""
Verification and scan result models
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScanResult:
    """Result from OCR scanning"""
    text: Optional[str] = None
    document_type: Optional[str] = None
    display_name: Optional[str] = None
    confidence: Optional[float] = None
    status: str = "success"
    message: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "text": self.text,
            "document_type": self.document_type,
            "display_name": self.display_name,
            "confidence": self.confidence,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

        # Add raw data if available
        if self.raw_data:
            data.update(self.raw_data)

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScanResult':
        """Create from dictionary"""
        return cls(
            text=data.get("text"),
            document_type=data.get("document_type"),
            display_name=data.get("display_name"),
            confidence=data.get("confidence"),
            status=data.get("status", "success"),
            message=data.get("message"),
            raw_data=data
        )


@dataclass
class VerificationResult:
    """Result from face verification"""
    same_person: Optional[bool] = None
    similarity: Optional[float] = None
    confidence: Optional[float] = None
    status: str = "success"
    message: Optional[str] = None
    match_score: Optional[float] = None  # Legacy field
    is_match: Optional[bool] = None      # Legacy field
    raw_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "same_person": self.same_person,
            "similarity": self.similarity,
            "confidence": self.confidence,
            "status": self.status,
            "message": self.message,
            "match_score": self.match_score,  # Legacy
            "is_match": self.is_match,        # Legacy
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

        # Add raw data if available
        if self.raw_data:
            data.update(self.raw_data)

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationResult':
        """Create from dictionary"""
        return cls(
            same_person=data.get("same_person"),
            similarity=data.get("similarity"),
            confidence=data.get("confidence"),
            status=data.get("status", "success"),
            message=data.get("message") or data.get("msg"),  # Handle both 'message' and 'msg'
            match_score=data.get("match_score"),  # Legacy
            is_match=data.get("is_match"),        # Legacy
            raw_data=data
        )

    def is_successful(self) -> bool:
        """Check if verification was successful"""
        return (
            self.status == "success" and
            self.same_person is True and
            self.similarity is not None and
            self.similarity > 0.8
        )
