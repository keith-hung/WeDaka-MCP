"""API client for WeDaka system integration"""

import ssl
import os
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from .models import (
    TimeLogRequest, TimeLogResponse,
    SearchTimelogResponse, ApiError
)


class WedakaApiClient:
    """API client for WeDaka system"""
    
    def __init__(self):
        self.base_url = os.getenv("WEDAKA_API_URL")
        if not self.base_url:
            raise ValueError("WEDAKA_API_URL environment variable is required")
        self.timeout = 30.0
        
        # Create SSL context with custom verification (as per API spec)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            verify=ssl_context,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "WeDaka-MCP/1.0"
            }
        )
    
    async def close(self) -> None:
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    
    async def insert_time_log(
        self,
        log_type: str,
        note: Optional[str] = None,
        clock_date: Optional[str] = None,
        clock_time: Optional[str] = None
    ) -> TimeLogResponse:
        """
        Insert time log (clock in/out) using environment variables
        
        Args:
            log_type: "上班" for clock in, "下班" for clock out
            note: Additional notes
            clock_date: Date in YYYY-MM-DD format (optional, defaults to today)
            clock_time: Time in HH:MM:SS format (optional, defaults to current time)
            
        Returns:
            TimeLogResponse object
        """
        emp_no = os.getenv("WEDAKA_EMP_NO")
        
        if not emp_no:
            return TimeLogResponse(
                Status=False,
                ErrorMessage="WEDAKA_EMP_NO environment variable is required"
            )
        try:
            # Handle date and time parameters
            if clock_date:
                # Parse date in YYYY-MM-DD format
                try:
                    parsed_date = datetime.strptime(clock_date, "%Y-%m-%d")
                except ValueError:
                    return TimeLogResponse(
                        Status=False,
                        ErrorMessage=f"Invalid date format: {clock_date}. Expected YYYY-MM-DD"
                    )
            else:
                parsed_date = datetime.now()
            
            if clock_time:
                # Parse time in HH:MM:SS format
                try:
                    time_parts = clock_time.split(":")
                    if len(time_parts) == 3:
                        hour, minute, second = map(int, time_parts)
                        parsed_datetime = parsed_date.replace(hour=hour, minute=minute, second=second)
                    else:
                        return TimeLogResponse(
                            Status=False,
                            ErrorMessage=f"Invalid time format: {clock_time}. Expected HH:MM:SS"
                        )
                except ValueError:
                    return TimeLogResponse(
                        Status=False,
                        ErrorMessage=f"Invalid time format: {clock_time}. Expected HH:MM:SS"
                    )
            else:
                parsed_datetime = parsed_date
            
            # Use WorkTimeLogData array format
            payload = {
                "UserName": os.getenv("WEDAKA_USERNAME"),  # Use username, not empNo
                "WorkTimeLogData": [{
                    "DateType": "1",  # Work day
                    "LeaveHours": 0,
                    "Memo": note or "",
                    "WorkItem": "1" if log_type == "上班" else "4",  # 1=checkin, 4=checkout
                    "WorkTime": parsed_datetime.strftime("%Y/%m/%d %H:%M:%S"),  # Time format
                    "WorkType": "1" if log_type == "上班" else "2"  # 1=checkin, 2=checkout
                }]
            }
            
            # Add X-UUID header for authentication
            device_id = os.getenv("WEDAKA_DEVICE_ID")
            headers = {"X-UUID": device_id} if device_id else {}
            response = await self.client.post("/worktime/InsertTimeLog", json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Debug: print raw response for troubleshooting
            if os.getenv("DEBUG_API"):
                print(f"DEBUG: InsertTimeLog response: {data}")
            
            return TimeLogResponse(**data)
            
        except httpx.HTTPError as e:
            return TimeLogResponse(
                Status=False,
                ErrorMessage=f"Network error: {str(e)}"
            )
        except Exception as e:
            return TimeLogResponse(
                Status=False,
                ErrorMessage=f"Unexpected error: {str(e)}"
            )
    
    async def search_timelog(
        self,
        month: int,
        year: int
    ) -> SearchTimelogResponse:
        """
        Search employee time logs using environment variables
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            SearchTimelogResponse object
        """
        username = os.getenv("WEDAKA_USERNAME")
        if not username:
            return SearchTimelogResponse(
                Status=False,
                ErrorMessage="WEDAKA_USERNAME environment variable is required"
            )
        
        try:
            # Use username parameter
            params = {
                "username": username,
                "month": month,
                "year": year
            }
            
            # Add X-UUID header for authentication
            device_id = os.getenv("WEDAKA_DEVICE_ID")
            headers = {"X-UUID": device_id} if device_id else {}
            response = await self.client.get("/worktime/SearchTimelog/", params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Debug: print raw response for troubleshooting
            if os.getenv("DEBUG_API"):
                print(f"DEBUG: SearchTimelog response: {data}")
            
            return SearchTimelogResponse(**data)
            
        except httpx.HTTPError as e:
            return SearchTimelogResponse(
                Status=False,
                ErrorMessage=f"Network error: {str(e)}"
            )
        except Exception as e:
            return SearchTimelogResponse(
                Status=False,
                ErrorMessage=f"Unexpected error: {str(e)}"
            )