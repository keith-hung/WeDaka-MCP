"""Data models for WeDaka MCP Server"""

from typing import Optional, List, Any
from pydantic import BaseModel


class DateTypeResponse(BaseModel):
    """Date type response model"""
    model_config = {"populate_by_name": True}
    
    DateType: str  # "1"=工作日, "2"/"3"/"4"=假日
    Status: bool
    ErrorMessage: Optional[str] = ""
    
    @property
    def success(self) -> bool:
        return self.Status
    
    @property 
    def message(self) -> str:
        return self.ErrorMessage or ""
    
    @property
    def is_work_day(self) -> bool:
        """Check if the date is a work day"""
        return self.DateType == "1"


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


