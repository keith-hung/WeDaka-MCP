/**
 * Integration tests for WedakaApiClient with real API
 * These tests use actual .env configuration to test against the real API
 */

import { WedakaApiClient } from '../client/WedakaApiClient';

describe('WedakaApiClient Integration Tests', () => {
  let client: WedakaApiClient;

  beforeAll(() => {
    // Skip tests if required environment variables are not set
    const required = ['WEDAKA_API_URL', 'WEDAKA_USERNAME', 'WEDAKA_DEVICE_ID', 'WEDAKA_EMP_NO'];
    const missing = required.filter(env => !process.env[env]);
    
    if (missing.length > 0) {
      console.warn(`Skipping integration tests. Missing environment variables: ${missing.join(', ')}`);
      console.warn('Please set these in your .env file to run integration tests.');
    }
  });

  beforeEach(() => {
    client = new WedakaApiClient();
  });

  describe('Real API Integration', () => {
    const skipIfNoEnv = () => {
      const required = ['WEDAKA_API_URL', 'WEDAKA_USERNAME', 'WEDAKA_DEVICE_ID', 'WEDAKA_EMP_NO'];
      const missing = required.filter(env => !process.env[env]);
      if (missing.length > 0) {
        return test.skip;
      }
      return test;
    };

    skipIfNoEnv()('should check work day status for today', async () => {
      const today = new Date().toISOString().split('T')[0];
      console.log(`\n🔍 Testing getDateType for today: ${today}`);
      
      const result = await client.getDateType(today);
      
      console.log('📊 Date Type Result:', {
        date: today,
        dateType: result.DateType,
        status: result.Status,
        errorMessage: result.ErrorMessage,
        isWorkDay: result.DateType === '1'
      });
      
      expect(result.Status).toBe(true);
      expect(result.DateType).toBeDefined();
    }, 30000);

    skipIfNoEnv()('should check work day status for a specific date', async () => {
      const testDate = '2025-07-14';
      console.log(`\n🔍 Testing getDateType for date: ${testDate}`);
      
      const result = await client.getDateType(testDate);
      
      console.log('📊 Date Type Result:', {
        date: testDate,
        dateType: result.DateType,
        status: result.Status,
        errorMessage: result.ErrorMessage,
        isWorkDay: result.DateType === '1'
      });
      
      expect(result.Status).toBe(true);
      expect(result.DateType).toBeDefined();
    }, 30000);

    skipIfNoEnv()('should search timelog for current month', async () => {
      const now = new Date();
      const month = now.getMonth() + 1;
      const year = now.getFullYear();
      
      console.log(`\n🔍 Testing searchTimelog for ${year}-${month.toString().padStart(2, '0')}`);
      
      const result = await client.searchTimelog(month, year);
      
      console.log('📊 Timelog Search Result:', {
        month,
        year,
        status: result.Status,
        errorMessage: result.ErrorMessage,
        recordCount: result.TimeLog?.length || 0,
        records: result.TimeLog?.slice(0, 3) || [] // Show first 3 records
      });
      
      expect(result.Status).toBe(true);
      if (result.TimeLog) {
        expect(Array.isArray(result.TimeLog)).toBe(true);
      }
    }, 30000);

    skipIfNoEnv()('should simulate clock-in validation (without actual clock-in)', async () => {
      console.log('\n🔍 Testing clock-in validation logic (simulation)');
      
      // Test date validation
      const today = new Date().toISOString().split('T')[0];
      const futureDate = '2030-12-31';
      
      console.log('📊 Testing future date rejection...');
      const futureResult = await client.insertTimeLog('上班', 'Test note', futureDate);
      console.log('Future date result:', {
        status: futureResult.Status,
        errorMessage: futureResult.ErrorMessage
      });
      expect(futureResult.Status).toBe(false);
      expect(futureResult.ErrorMessage).toContain('未來日期');
      
      console.log('📊 Testing work day validation for today...');
      const dateTypeResult = await client.getDateType(today);
      console.log('Today work day check:', {
        date: today,
        dateType: dateTypeResult.DateType,
        isWorkDay: dateTypeResult.DateType === '1',
        status: dateTypeResult.Status
      });
      
      // Only test actual clock-in if it's a work day
      if (dateTypeResult.DateType === '1') {
        console.log('⚠️  Today is a work day - actual clock-in test would succeed');
        console.log('   (Skipping actual clock-in to avoid duplicate records)');
      } else {
        console.log('📊 Testing non-work day rejection...');
        const nonWorkDayResult = await client.insertTimeLog('上班', 'Test note', today);
        console.log('Non-work day result:', {
          status: nonWorkDayResult.Status,
          errorMessage: nonWorkDayResult.ErrorMessage
        });
        expect(nonWorkDayResult.Status).toBe(false);
        expect(nonWorkDayResult.ErrorMessage).toContain('不是工作日');
      }
    }, 30000);

    skipIfNoEnv()('should test API connectivity and authentication', async () => {
      console.log('\n🔍 Testing API connectivity and authentication');
      
      const today = new Date().toISOString().split('T')[0];
      const result = await client.getDateType(today);
      
      console.log('📊 API Connectivity Test:', {
        apiUrl: process.env.WEDAKA_API_URL?.replace(/^https?:\/\//, '').split('/')[0],
        deviceId: process.env.WEDAKA_DEVICE_ID?.substring(0, 4) + '...',
        empNo: process.env.WEDAKA_EMP_NO,
        username: process.env.WEDAKA_USERNAME,
        connectionStatus: result.Status ? '✅ Connected' : '❌ Failed',
        errorMessage: result.ErrorMessage
      });
      
      expect(result.Status).toBe(true);
    }, 30000);
  });
});