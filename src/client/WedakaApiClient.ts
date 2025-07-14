/**
 * API client for WeDaka system integration
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import https from 'https';
import { config } from 'dotenv';
import {
  DateTypeResponse,
  TimeLogResponse,
  SearchTimelogResponse,
  DateTypeResponseSchema,
  TimeLogResponseSchema,
  SearchTimelogResponseSchema,
} from '../models';

// Load environment variables
config();

export class WedakaApiClient {
  private client: AxiosInstance;
  private baseUrl: string;
  private timeout: number = 30000;

  constructor() {
    this.baseUrl = process.env.WEDAKA_API_URL || '';
    if (!this.baseUrl) {
      throw new Error('WEDAKA_API_URL environment variable is required');
    }

    // Create HTTPS agent with custom SSL verification (as per API spec)
    const httpsAgent = new https.Agent({
      rejectUnauthorized: false,
    });

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: this.timeout,
      httpsAgent,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'WeDaka-MCP-TS/1.0',
      },
    });
  }

  /**
   * Get date type to check if it's a work day
   */
  async getDateType(date: string, empId?: string): Promise<DateTypeResponse> {
    if (!empId) {
      empId = process.env.WEDAKA_EMP_NO;
    }

    if (!empId) {
      return {
        DateType: '0',
        Status: false,
        ErrorMessage: 'WEDAKA_EMP_NO environment variable is required',
      };
    }

    try {
      // Validate date format
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateRegex.test(date)) {
        return {
          DateType: '0',
          Status: false,
          ErrorMessage: `Invalid date format: ${date}. Expected YYYY-MM-DD`,
        };
      }

      // API request parameters
      const params = {
        empID: empId,
        date: date,
      };

      // Add X-UUID header for authentication
      const deviceId = process.env.WEDAKA_DEVICE_ID;
      const headers = deviceId ? { 'X-UUID': deviceId } : {};

      const response = await this.client.get('/worktime/GetDateType/', {
        params,
        headers,
      });

      // Debug: print raw response for troubleshooting
      if (process.env.DEBUG_API) {
        console.log(`DEBUG: GetDateType response:`, response.data);
      }

      // Validate response with Zod
      const validatedData = DateTypeResponseSchema.parse(response.data);
      return validatedData;
    } catch (error) {
      if (error instanceof AxiosError) {
        return {
          DateType: '0',
          Status: false,
          ErrorMessage: `Network error: ${error.message}`,
        };
      }
      return {
        DateType: '0',
        Status: false,
        ErrorMessage: `Unexpected error: ${error}`,
      };
    }
  }

  /**
   * Insert time log (clock in/out) using environment variables
   */
  async insertTimeLog(
    logType: string,
    note?: string,
    clockDate?: string,
    clockTime?: string
  ): Promise<TimeLogResponse> {
    const empNo = process.env.WEDAKA_EMP_NO;

    if (!empNo) {
      return {
        Status: false,
        ErrorMessage: 'WEDAKA_EMP_NO environment variable is required',
      };
    }

    try {
      let targetDate: string;
      let parsedDateTime: Date;

      // Handle date and time parameters
      if (clockDate) {
        // Parse date in YYYY-MM-DD format
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(clockDate)) {
          return {
            Status: false,
            ErrorMessage: `Invalid date format: ${clockDate}. Expected YYYY-MM-DD`,
          };
        }
        parsedDateTime = new Date(clockDate);
        targetDate = clockDate;
      } else {
        parsedDateTime = new Date();
        targetDate = parsedDateTime.toISOString().split('T')[0];
      }

      // MANDATORY: Check if the date is not in the future
      const today = new Date().toISOString().split('T')[0];
      if (targetDate > today) {
        return {
          Status: false,
          ErrorMessage: `無法為未來日期（${targetDate}）打卡。只能為今天或過去的日期打卡。`,
        };
      }

      // MANDATORY: Check if the date is a work day
      const dateTypeResponse = await this.getDateType(targetDate, empNo);
      if (!dateTypeResponse.Status) {
        return {
          Status: false,
          ErrorMessage: `Failed to check work day: ${dateTypeResponse.ErrorMessage}`,
        };
      }

      if (dateTypeResponse.DateType !== '1') {
        return {
          Status: false,
          ErrorMessage: `該日期（${targetDate}）不是工作日，無法打卡。日期類型：${dateTypeResponse.DateType}`,
        };
      }

      if (clockTime) {
        // Parse time in HH:MM:SS format
        const timeRegex = /^(\d{2}):(\d{2}):(\d{2})$/;
        const timeMatch = clockTime.match(timeRegex);
        if (!timeMatch) {
          return {
            Status: false,
            ErrorMessage: `Invalid time format: ${clockTime}. Expected HH:MM:SS`,
          };
        }

        const [, hour, minute, second] = timeMatch;
        parsedDateTime.setHours(parseInt(hour), parseInt(minute), parseInt(second));
      }

      // Use WorkTimeLogData array format
      const payload = {
        UserName: process.env.WEDAKA_USERNAME, // Use username, not empNo
        WorkTimeLogData: [
          {
            DateType: '1', // Work day
            LeaveHours: 0,
            Memo: note || '',
            WorkItem: logType === '上班' ? '1' : '4', // 1=checkin, 4=checkout
            WorkTime: this.formatDateTime(parsedDateTime), // Time format
            WorkType: logType === '上班' ? '1' : '2', // 1=checkin, 2=checkout
          },
        ],
      };

      // Add X-UUID header for authentication
      const deviceId = process.env.WEDAKA_DEVICE_ID;
      const headers = deviceId ? { 'X-UUID': deviceId } : {};

      const response = await this.client.post('/worktime/InsertTimeLog', payload, {
        headers,
      });

      // Debug: print raw response for troubleshooting
      if (process.env.DEBUG_API) {
        console.log(`DEBUG: InsertTimeLog response:`, response.data);
      }

      // Validate response with Zod
      const validatedData = TimeLogResponseSchema.parse(response.data);
      return validatedData;
    } catch (error) {
      if (error instanceof AxiosError) {
        return {
          Status: false,
          ErrorMessage: `Network error: ${error.message}`,
        };
      }
      return {
        Status: false,
        ErrorMessage: `Unexpected error: ${error}`,
      };
    }
  }

  /**
   * Search employee time logs using environment variables
   */
  async searchTimelog(month: number, year: number): Promise<SearchTimelogResponse> {
    const username = process.env.WEDAKA_USERNAME;
    if (!username) {
      return {
        Status: false,
        ErrorMessage: 'WEDAKA_USERNAME environment variable is required',
      };
    }

    try {
      // Use username parameter
      const params = {
        username: username,
        month: month,
        year: year,
      };

      // Add X-UUID header for authentication
      const deviceId = process.env.WEDAKA_DEVICE_ID;
      const headers = deviceId ? { 'X-UUID': deviceId } : {};

      const response = await this.client.get('/worktime/SearchTimelog/', {
        params,
        headers,
      });

      // Debug: print raw response for troubleshooting
      if (process.env.DEBUG_API) {
        console.log(`DEBUG: SearchTimelog response:`, response.data);
      }

      // Validate response with Zod
      const validatedData = SearchTimelogResponseSchema.parse(response.data);
      return validatedData;
    } catch (error) {
      if (error instanceof AxiosError) {
        return {
          Status: false,
          ErrorMessage: `Network error: ${error.message}`,
        };
      }
      return {
        Status: false,
        ErrorMessage: `Unexpected error: ${error}`,
      };
    }
  }

  /**
   * Format datetime to YYYY/MM/DD HH:MM:SS format
   */
  private formatDateTime(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
  }
}