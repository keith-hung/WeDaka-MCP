"""Data models for WeDaka MCP Server"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., description="Employee AD account")
    deviceId: str = Field(..., description="Device ID for authentication")


class LoginResponse(BaseModel):
    """Login response model"""
    success: bool
    message: str
    empId: Optional[str] = None
    empName: Optional[str] = None
    token: Optional[str] = None
    phoneUuid: Optional[str] = None


class TimeLogRequest(BaseModel):
    """Time log request model"""
    empId: str = Field(..., description="Employee ID")
    logType: str = Field(..., description="Log type: 上班 or 下班")
    logTime: str = Field(..., description="Log time in ISO format")
    latitude: Optional[float] = Field(None, description="GPS latitude")
    longitude: Optional[float] = Field(None, description="GPS longitude")
    address: Optional[str] = Field(None, description="Address description")
    note: Optional[str] = Field(None, description="Additional notes")


class TimeLogResponse(BaseModel):
    """Time log response model"""
    success: bool
    message: str
    logId: Optional[str] = None
    logTime: Optional[str] = None


class TimeLogRecord(BaseModel):
    """Time log record model"""
    logId: str
    empId: str
    logType: str
    logTime: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    note: Optional[str] = None


class SearchTimelogResponse(BaseModel):
    """Search timelog response model"""
    success: bool
    message: str
    data: Optional[List[TimeLogRecord]] = None


class ApiError(BaseModel):
    """API error response model"""
    success: bool = False
    message: str
    errorCode: Optional[str] = None
    details: Optional[str] = None