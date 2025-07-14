"""Integration tests for WeDaka API client"""

import os
import pytest
import asyncio
from datetime import datetime
from wedaka.api_client import WedakaApiClient
from wedaka.models import TimeLogResponse, SearchTimelogResponse


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