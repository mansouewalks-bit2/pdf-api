"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from enum import Enum


class MarginOptions(BaseModel):
    top: str = "10mm"
    right: str = "10mm"
    bottom: str = "10mm"
    left: str = "10mm"


class PDFOptions(BaseModel):
    format: str = "A4"
    margin: MarginOptions = MarginOptions()
    landscape: bool = False
    header_html: Optional[str] = None
    footer_html: Optional[str] = None
    print_background: bool = True
    scale: float = Field(default=1.0, ge=0.1, le=2.0)


class HtmlToPdfRequest(BaseModel):
    html: str = Field(..., min_length=1, max_length=5_000_000)
    options: PDFOptions = PDFOptions()


class UrlToPdfRequest(BaseModel):
    url: str = Field(..., min_length=1)
    options: PDFOptions = PDFOptions()


class CompressionQuality(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class WatermarkPosition(str, Enum):
    center = "center"
    top_left = "top-left"
    top_right = "top-right"
    bottom_left = "bottom-left"
    bottom_right = "bottom-right"
    diagonal = "diagonal"


class Plan(str, Enum):
    free = "free"
    starter = "starter"
    pro = "pro"
    business = "business"


PLAN_LIMITS = {
    "free": {"monthly_limit": 50, "watermark": True, "priority": False},
    "starter": {"monthly_limit": 500, "watermark": False, "priority": False},
    "pro": {"monthly_limit": 5000, "watermark": False, "priority": True},
    "business": {"monthly_limit": 20000, "watermark": False, "priority": True},
}


class UsageResponse(BaseModel):
    used: int
    remaining: int
    plan: str
    monthly_limit: int
    reset_date: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
