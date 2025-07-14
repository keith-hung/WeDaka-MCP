"""Data models for WeDaka MCP Server"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field




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
    model_config = {"populate_by_name": True}
    
    Status: bool
    ErrorMessage: Optional[str] = ""
    HolidayList: Optional[Any] = None
    LogId: Optional[str] = None  # May not be present in all responses
    LogTime: Optional[str] = None  # May not be present in all responses
    
    @property
    def success(self) -> bool:
        return self.Status
    
    @property 
    def message(self) -> str:
        return self.ErrorMessage or ""


class TimeLogRecord(BaseModel):
    """Time log record model - matches SearchTimelog API response structure"""
    model_config = {"populate_by_name": True}
    
    # Based on Go WorkTimeData structure and actual API response
    DateType: Optional[str] = None
    LeaveHours: Optional[int] = None
    Memo: Optional[str] = None
    WorkItem: Optional[str] = None
    WorkTime: Optional[str] = None
    WorkType: Optional[str] = None
    WorkDate: Optional[str] = None  # Additional field found in SearchTimelog response
    
    # Compatibility properties for original interface
    @property
    def logId(self) -> Optional[str]:
        # WorkItem might serve as identifier, or we can use a combination
        return self.WorkItem
    
    @property
    def empId(self) -> Optional[str]:
        # Employee ID is not directly in the record, might be in parent response
        return None
    
    @property
    def logType(self) -> Optional[str]:
        return self.WorkType
    
    @property
    def logTime(self) -> Optional[str]:
        return self.WorkTime
    
    @property
    def latitude(self) -> Optional[float]:
        # GPS coordinates not available in this response structure
        return None
    
    @property
    def longitude(self) -> Optional[float]:
        # GPS coordinates not available in this response structure
        return None
    
    @property
    def address(self) -> Optional[str]:
        # Address not available in this response structure
        return None
    
    @property
    def note(self) -> Optional[str]:
        return self.Memo


class SearchTimelogResponse(BaseModel):
    """Search timelog response model"""
    model_config = {"populate_by_name": True}
    
    Status: bool
    ErrorMessage: Optional[str] = ""
    TimeLog: Optional[List[TimeLogRecord]] = None
    
    @property
    def success(self) -> bool:
        return self.Status
    
    @property 
    def message(self) -> str:
        return self.ErrorMessage or ""
    
    @property
    def data(self) -> Optional[List[TimeLogRecord]]:
        return self.TimeLog


class ApiError(BaseModel):
    """API error response model"""
    success: bool = False
    message: str
    errorCode: Optional[str] = None
    details: Optional[str] = None