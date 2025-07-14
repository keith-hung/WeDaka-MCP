#!/usr/bin/env python3
"""
Quick test runner for WeDaka API integration tests

This script provides a simple way to run integration tests manually
without requiring full pytest setup.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path so we can import wedaka modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tests.test_api_integration import run_integration_tests


def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "WEDAKA_API_URL",
        "WEDAKA_USERNAME", 
        "WEDAKA_DEVICE_ID",
        "WEDAKA_EMP_NO"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   {var}")
        print("\nPlease set these variables before running tests:")
        print("You can either:")
        print("1. Export them in your shell:")
        for var in missing_vars:
            print(f"   export {var}=your_value")
        print("2. Create a .env file in the project root")
        print("3. Copy .env.test.example to .env.test and fill in values")
        return False
    
    print("✅ All required environment variables are set:")
    for var in required_vars:
        value = os.getenv(var)
        # Hide sensitive info
        if len(value) > 8:
            display_value = f"{value[:4]}...{value[-4:]}"
        else:
            display_value = "***"
        print(f"   {var}: {display_value}")
    
    return True


def main():
    """Main entry point"""
    print("WeDaka MCP Server - API Integration Test Runner")
    print("=" * 50)
    
    # Try to load .env files
    try:
        from dotenv import load_dotenv
        
        # Try .env.test first, then .env
        env_files = [".env.test", ".env"]
        for env_file in env_files:
            if os.path.exists(env_file):
                load_dotenv(env_file)
                print(f"📁 Loaded environment from {env_file}")
                break
        else:
            print("📁 No .env file found, using system environment variables")
    except ImportError:
        print("📁 python-dotenv not installed, using system environment variables")
    
    print()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print()
    print("🚀 Starting integration tests...")
    print("-" * 30)
    
    # Run tests
    try:
        asyncio.run(run_integration_tests())
        print("\n✅ Integration tests completed!")
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()