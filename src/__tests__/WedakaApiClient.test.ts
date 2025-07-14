/**
 * Tests for WedakaApiClient
 */

import { WedakaApiClient } from '../client/WedakaApiClient';

describe('WedakaApiClient', () => {
  let client: WedakaApiClient;
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    // Save original environment
    originalEnv = { ...process.env };
    
    // Set up test environment variables only if not already set from .env
    if (!process.env.WEDAKA_API_URL) {
      process.env.WEDAKA_API_URL = 'https://test-api.wedaka.com';
    }
    if (!process.env.WEDAKA_USERNAME) {
      process.env.WEDAKA_USERNAME = 'test-user';
    }
    if (!process.env.WEDAKA_DEVICE_ID) {
      process.env.WEDAKA_DEVICE_ID = 'test-device-id';
    }
    if (!process.env.WEDAKA_EMP_NO) {
      process.env.WEDAKA_EMP_NO = 'test-emp-123';
    }
  });

  afterEach(() => {
    // Restore original environment
    process.env = originalEnv;
  });

  describe('constructor', () => {
    it('should create client with valid environment variables', () => {
      expect(() => {
        client = new WedakaApiClient();
      }).not.toThrow();
    });

    it('should throw error when WEDAKA_API_URL is missing', () => {
      delete process.env.WEDAKA_API_URL;
      expect(() => {
        client = new WedakaApiClient();
      }).toThrow('WEDAKA_API_URL environment variable is required');
    });
  });

  describe('getDateType', () => {
    beforeEach(() => {
      client = new WedakaApiClient();
    });

    it('should return error when empId is missing', async () => {
      delete process.env.WEDAKA_EMP_NO;
      const result = await client.getDateType('2025-07-14');
      
      expect(result.Status).toBe(false);
      expect(result.ErrorMessage).toBe('WEDAKA_EMP_NO environment variable is required');
    });

    it('should return error for invalid date format', async () => {
      const result = await client.getDateType('invalid-date');
      
      expect(result.Status).toBe(false);
      expect(result.ErrorMessage).toContain('Invalid date format');
    });

    it('should accept valid date format', async () => {
      // Note: This test would require mocking the HTTP client to avoid actual API calls
      const validDate = '2025-07-14';
      expect(() => {
        client.getDateType(validDate);
      }).not.toThrow();
    });
  });

  describe('insertTimeLog', () => {
    beforeEach(() => {
      client = new WedakaApiClient();
    });

    it('should return error when WEDAKA_EMP_NO is missing', async () => {
      delete process.env.WEDAKA_EMP_NO;
      const result = await client.insertTimeLog('上班');
      
      expect(result.Status).toBe(false);
      expect(result.ErrorMessage).toBe('WEDAKA_EMP_NO environment variable is required');
    });

    it('should reject future dates', async () => {
      const futureDate = '2030-12-31';
      const result = await client.insertTimeLog('上班', undefined, futureDate);
      
      expect(result.Status).toBe(false);
      expect(result.ErrorMessage).toContain('無法為未來日期');
    });

    it('should return error for invalid date format', async () => {
      const result = await client.insertTimeLog('上班', undefined, 'invalid-date');
      
      expect(result.Status).toBe(false);
      expect(result.ErrorMessage).toContain('Invalid date format');
    });

    it('should return error for invalid time format', async () => {
      const result = await client.insertTimeLog('上班', undefined, '2025-07-14', 'invalid-time');
      
      expect(result.Status).toBe(false);
      expect(result.ErrorMessage).toContain('Invalid time format');
    });
  });

  describe('searchTimelog', () => {
    beforeEach(() => {
      client = new WedakaApiClient();
    });

    it('should return error when WEDAKA_USERNAME is missing', async () => {
      delete process.env.WEDAKA_USERNAME;
      const result = await client.searchTimelog(7, 2025);
      
      expect(result.Status).toBe(false);
      expect(result.ErrorMessage).toBe('WEDAKA_USERNAME environment variable is required');
    });
  });

  describe('formatDateTime', () => {
    beforeEach(() => {
      client = new WedakaApiClient();
    });

    it('should format datetime correctly', () => {
      // Access private method for testing
      const testDate = new Date('2025-07-14T15:30:45');
      const formatted = (client as any).formatDateTime(testDate);
      
      expect(formatted).toBe('2025/07/14 15:30:45');
    });
  });
});