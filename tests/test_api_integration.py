"""Integration tests for WeDaka API client"""

import os
import pytest
import asyncio
from datetime import datetime, timedelta
from wedaka.api_client import WedakaApiClient
from wedaka.models import TimeLogResponse, SearchTimelogResponse, DateTypeResponse


class TestWedakaApiIntegration:
    """Integration tests for WeDaka API client"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Create API client for testing"""
        return WedakaApiClient()
    
    @pytest.fixture(scope="class") 
    def check_env_vars(self):
        """Check required environment variables are set"""
        required_vars = [
            "WEDAKA_API_URL",
            "WEDAKA_USERNAME", 
            "WEDAKA_DEVICE_ID",
            "WEDAKA_EMP_NO"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            pytest.skip(f"Missing environment variables: {', '.join(missing_vars)}")
    
    
    @pytest.mark.asyncio
    async def test_clock_in(self, api_client, check_env_vars):
        """Test clock in functionality"""
        async with api_client:
            response = await api_client.insert_time_log(
                log_type="上班",
                note="Integration test clock in"
            )
            
            assert isinstance(response, TimeLogResponse)
            
            if response.success:
                assert response.Status is True
                # LogId and LogTime might be None for leave records or duplicate entries
                if response.LogId is not None and response.LogTime is not None:
                    print(f"Clock in successful - Log ID: {response.LogId}, Time: {response.LogTime}")
                else:
                    print(f"Clock in processed - {response.message}")
            else:
                print(f"Clock in failed: {response.message}")
    
    @pytest.mark.asyncio
    async def test_clock_out(self, api_client, check_env_vars):
        """Test clock out functionality"""
        async with api_client:
            response = await api_client.insert_time_log(
                log_type="下班", 
                note="Integration test clock out"
            )
            
            assert isinstance(response, TimeLogResponse)
            
            if response.success:
                assert response.Status is True
                # LogId and LogTime might be None for leave records or duplicate entries
                if response.LogId is not None and response.LogTime is not None:
                    print(f"Clock out successful - Log ID: {response.LogId}, Time: {response.LogTime}")
                else:
                    print(f"Clock out processed - {response.message}")
            else:
                print(f"Clock out failed: {response.message}")
    
    @pytest.mark.asyncio
    async def test_search_timelog(self, api_client, check_env_vars):
        """Test search timelog functionality"""
        current_date = datetime.now()
        month = current_date.month
        year = current_date.year
        
        async with api_client:
            response = await api_client.search_timelog(month, year)
            
            assert isinstance(response, SearchTimelogResponse)
            
            if response.success:
                assert response.Status is True
                print(f"Search timelog successful - Found {len(response.data or [])} records")
                
                # Print detailed record information
                if response.data:
                    for i, record in enumerate(response.data):
                        print(f"   Record {i+1}:")
                        print(f"     DateType: {record.DateType}")
                        print(f"     LeaveHours: {record.LeaveHours}")
                        print(f"     Memo: {record.Memo}")
                        print(f"     WorkItem: {record.WorkItem}")
                        print(f"     WorkTime: {record.WorkTime}")
                        print(f"     WorkType: {record.WorkType}")
                        print(f"     WorkDate: {record.WorkDate}")
                        print(f"     ---")
                else:
                    print("   No records found")
            else:
                print(f"Search timelog failed: {response.message}")
    
    @pytest.mark.asyncio
    async def test_response_models_validation(self, api_client, check_env_vars):
        """Test that response models correctly validate API responses"""
        async with api_client:
            # Test timelog response
            timelog_response = await api_client.insert_time_log("上班", "Validation test")
            assert isinstance(timelog_response, TimeLogResponse)
            
            # Test search response
            search_response = await api_client.search_timelog(
                datetime.now().month, 
                datetime.now().year
            )
            assert isinstance(search_response, SearchTimelogResponse)
            
            # Test date type response
            date_type_response = await api_client.get_date_type(
                datetime.now().strftime("%Y-%m-%d")
            )
            assert isinstance(date_type_response, DateTypeResponse)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, check_env_vars):
        """Test error handling with invalid configuration"""
        # Test with missing API URL
        original_url = os.getenv("WEDAKA_API_URL")
        
        if "WEDAKA_API_URL" in os.environ:
            del os.environ["WEDAKA_API_URL"]
        
        try:
            with pytest.raises(ValueError, match="WEDAKA_API_URL environment variable is required"):
                WedakaApiClient()
        finally:
            # Restore original URL
            if original_url:
                os.environ["WEDAKA_API_URL"] = original_url
    
    @pytest.mark.asyncio
    async def test_work_day_check(self, api_client, check_env_vars):
        """Test work day checking functionality"""
        async with api_client:
            # Test today
            today = datetime.now().strftime("%Y-%m-%d")
            response = await api_client.get_date_type(today)
            
            assert isinstance(response, DateTypeResponse)
            
            if response.success:
                assert response.DateType in ["1", "2", "3", "4"]
                print(f"Today ({today}) is DateType {response.DateType}")
                print(f"Is work day: {response.is_work_day}")
            else:
                print(f"Work day check failed: {response.message}")
            
            # Test invalid date format
            invalid_response = await api_client.get_date_type("2024/01/01")
            assert not invalid_response.success
            assert "Invalid date format" in invalid_response.message
    
    @pytest.mark.asyncio
    async def test_work_day_protection(self, api_client, check_env_vars):
        """Test that clock in/out is protected by work day check"""
        async with api_client:
            # Try to find a non-work day (last Saturday)
            days_since_monday = datetime.now().weekday()
            last_saturday = datetime.now() - timedelta(days=days_since_monday + 2)
            saturday_date = last_saturday.strftime("%Y-%m-%d")
            
            # Check if Saturday is a work day
            date_check = await api_client.get_date_type(saturday_date)
            
            if date_check.success and not date_check.is_work_day:
                # Try to clock in on Saturday (should be rejected)
                clock_in_response = await api_client.insert_time_log(
                    log_type="上班",
                    note="Test Saturday clock in",
                    clock_date=saturday_date,
                    clock_time="09:00:00"
                )
                
                assert not clock_in_response.success
                assert "不是工作日" in clock_in_response.message
                print(f"Saturday ({saturday_date}) protection working correctly")
            else:
                print(f"Saturday ({saturday_date}) is unexpectedly a work day or check failed")
    
    @pytest.mark.asyncio
    async def test_future_date_protection(self, api_client, check_env_vars):
        """Test that future dates are rejected for clock in/out"""
        async with api_client:
            # Test tomorrow (should be rejected)
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_date = tomorrow.strftime("%Y-%m-%d")
            
            # Try to clock in for tomorrow
            clock_in_response = await api_client.insert_time_log(
                log_type="上班",
                note="Future date test",
                clock_date=tomorrow_date,
                clock_time="09:00:00"
            )
            
            assert not clock_in_response.success
            assert "未來日期" in clock_in_response.message
            print(f"Future date protection working: {clock_in_response.message}")
            
            # Try to clock out for tomorrow
            clock_out_response = await api_client.insert_time_log(
                log_type="下班",
                note="Future date test",
                clock_date=tomorrow_date,
                clock_time="18:00:00"
            )
            
            assert not clock_out_response.success
            assert "未來日期" in clock_out_response.message
            
            # Today should pass the future date check (but may fail work day check)
            today = datetime.now().strftime("%Y-%m-%d")
            today_response = await api_client.insert_time_log(
                log_type="上班",
                note="Today test",
                clock_date=today,
                clock_time="09:00:00"
            )
            
            # Should not fail with future date error
            if not today_response.success:
                assert "未來日期" not in today_response.message
                print(f"Today rejected for other reason: {today_response.message}")
            else:
                print("Today clock in successful")


# Utility function for running tests manually
async def run_integration_tests():
    """Run integration tests manually (for debugging)"""
    required_vars = [
        "WEDAKA_API_URL",
        "WEDAKA_USERNAME", 
        "WEDAKA_DEVICE_ID",
        "WEDAKA_EMP_NO"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running tests:")
        for var in missing_vars:
            print(f"  export {var}=your_value")
        return
    
    print("Running WeDaka API integration tests...")
    
    try:
        client = WedakaApiClient()
        async with client:
            # Test clock in
            print("\n1. Testing clock in...")
            clock_in_response = await client.insert_time_log("上班", "Test clock in")
            print(f"   Status: {clock_in_response.success}")
            print(f"   Message: {clock_in_response.message}")
            
            # Test search timelog
            print("\n2. Testing search timelog...")
            current_date = datetime.now()
            search_response = await client.search_timelog(current_date.month, current_date.year)
            print(f"   Status: {search_response.success}")
            print(f"   Message: {search_response.message}")
            
            if search_response.success:
                print(f"   Found {len(search_response.data or [])} records")
                
                # Print detailed record information
                if search_response.data:
                    for i, record in enumerate(search_response.data):
                        print(f"     Record {i+1}: WorkType={record.WorkType}, WorkItem={record.WorkItem}")
                        print(f"       WorkTime={record.WorkTime}, WorkDate={record.WorkDate}")
                        print(f"       Memo={record.Memo}")
                else:
                    print("     No records data available")
            
    except Exception as e:
        print(f"Error during tests: {str(e)}")


if __name__ == "__main__":
    # Run tests manually if script is executed directly
    asyncio.run(run_integration_tests())