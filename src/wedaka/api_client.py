"""API client for WeDaka system integration"""

import ssl
import os
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from .models import (
    LoginRequest, LoginResponse, TimeLogRequest, TimeLogResponse,
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
    
    async def login(self) -> LoginResponse:
        """
        Employee login using environment variables
            
        Returns:
            LoginResponse object
        """
        username = os.getenv("WEDAKA_USERNAME")
        device_id = os.getenv("WEDAKA_DEVICE_ID")
        
        if not username or not device_id:
            return LoginResponse(
                success=False,
                message="WEDAKA_USERNAME and WEDAKA_DEVICE_ID environment variables are required"
            )
        try:
            # Note: API spec shows password field but requirements say no password needed
            # Using empty password as placeholder
            payload = {
                "username": username,
                "password": "",  # Empty password per requirements
                "deviceId": device_id
            }
            
            response = await self.client.post("/worktime/login", json=payload)
            response.raise_for_status()
            
            data = response.json()
            return LoginResponse(**data)
            
        except httpx.HTTPError as e:
            return LoginResponse(
                success=False,
                message=f"Network error: {str(e)}"
            )
        except Exception as e:
            return LoginResponse(
                success=False,
                message=f"Unexpected error: {str(e)}"
            )
    
    async def insert_time_log(
        self,
        log_type: str,
        note: Optional[str] = None
    ) -> TimeLogResponse:
        """
        Insert time log (clock in/out) using environment variables
        
        Args:
            log_type: "上班" for clock in, "下班" for clock out
            note: Additional notes
            
        Returns:
            TimeLogResponse object
        """
        emp_no = os.getenv("WEDAKA_EMP_NO")
        
        if not emp_no:
            return TimeLogResponse(
                success=False,
                message="WEDAKA_EMP_NO environment variable is required"
            )
        try:
            payload = {
                "empNo": emp_no,
                "logType": log_type,
                "logTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": note or ""
            }
            
            response = await self.client.post("/worktime/InsertTimeLog", json=payload)
            response.raise_for_status()
            
            data = response.json()
            return TimeLogResponse(**data)
            
        except httpx.HTTPError as e:
            return TimeLogResponse(
                success=False,
                message=f"Network error: {str(e)}"
            )
        except Exception as e:
            return TimeLogResponse(
                success=False,
                message=f"Unexpected error: {str(e)}"
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
                success=False,
                message="WEDAKA_USERNAME environment variable is required"
            )
        try:
            params = {
                "username": username,
                "month": month,
                "year": year
            }
            
            response = await self.client.get("/worktime/SearchTimelog/", params=params)
            response.raise_for_status()
            
            data = response.json()
            return SearchTimelogResponse(**data)
            
        except httpx.HTTPError as e:
            return SearchTimelogResponse(
                success=False,
                message=f"Network error: {str(e)}"
            )
        except Exception as e:
            return SearchTimelogResponse(
                success=False,
                message=f"Unexpected error: {str(e)}"
            )