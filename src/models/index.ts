/**
 * Zod schemas for WeDaka MCP Server validation
 */

import { z } from 'zod';

/**
 * WorkItem type definitions
 * Represents the type of work time log entry
 */
export enum WorkItemType {
  CLOCK_IN = '1',      // Clock in (上班打卡)
  LEAVE = '2',         // Leave/Time off (請假)
  CLOCK_OUT = '4',     // Clock out (下班打卡)
}

/**
 * Get human-readable description for WorkItem code
 */
export function getWorkItemDescription(workItem: string | null | undefined): string {
  if (!workItem) return 'Unknown';

  switch (workItem) {
    case WorkItemType.CLOCK_IN:
      return 'Clock In (上班打卡)';
    case WorkItemType.LEAVE:
      return 'Leave/Time Off (請假)';
    case WorkItemType.CLOCK_OUT:
      return 'Clock Out (下班打卡)';
    default:
      return `Unknown (${workItem})`;
  }
}

/**
 * WorkType type definitions
 * Alternative encoding for work time log type
 */
export enum WorkType {
  CLOCK_IN = '1',   // Clock in (上班)
  CLOCK_OUT = '2',  // Clock out (下班)
}

/**
 * DateType definitions
 * Represents the type of day
 */
export enum DateType {
  WORK_DAY = '1',     // Work day (工作日)
  LEAVE_DAY = '2',    // Leave day (休假日)
  HOLIDAY = '3',      // Holiday (例假日)
}

export const DateTypeResponseSchema = z.object({
  DateType: z.string(),
  Status: z.boolean(),
  ErrorMessage: z.string().optional(),
});

export const TimeLogResponseSchema = z.object({
  Status: z.boolean(),
  ErrorMessage: z.string().optional(),
  HolidayList: z.any().optional(),
  LogId: z.string().optional(),
  LogTime: z.string().optional(),
});

export const TimeLogRecordSchema = z.object({
  DateType: z.string().nullable().optional(),
  LeaveHours: z.number().nullable().optional(),
  Memo: z.string().nullable().optional(),
  WorkItem: z.string().nullable().optional(),
  WorkTime: z.string().nullable().optional(),
  WorkType: z.string().nullable().optional(),
  WorkDate: z.string().nullable().optional(),
});

export const SearchTimelogResponseSchema = z.object({
  Status: z.boolean(),
  ErrorMessage: z.string().optional(),
  TimeLog: z.array(TimeLogRecordSchema).optional(),
});

export const WedakaConfigSchema = z.object({
  apiUrl: z.string().url(),
  username: z.string(),
  deviceId: z.string(),
  empNo: z.string(),
});

export const ClockInRequestSchema = z.object({
  date: z.string().optional(),
  time: z.string().optional(),
  memo: z.string().optional(),
  empId: z.string().optional(),
});

export const ClockOutRequestSchema = z.object({
  date: z.string().optional(),
  time: z.string().optional(),
  memo: z.string().optional(),
  empId: z.string().optional(),
});

export const GetTimelogRequestSchema = z.object({
  year: z.string(),
  month: z.string(),
  empId: z.string().optional(),
});

export const CheckWorkDayRequestSchema = z.object({
  date: z.string(),
  empId: z.string().optional(),
});

// Type exports
export type DateTypeResponse = z.infer<typeof DateTypeResponseSchema>;
export type TimeLogResponse = z.infer<typeof TimeLogResponseSchema>;
export type TimeLogRecord = z.infer<typeof TimeLogRecordSchema>;
export type SearchTimelogResponse = z.infer<typeof SearchTimelogResponseSchema>;
export type WedakaConfig = z.infer<typeof WedakaConfigSchema>;
export type ClockInRequest = z.infer<typeof ClockInRequestSchema>;
export type ClockOutRequest = z.infer<typeof ClockOutRequestSchema>;
export type GetTimelogRequest = z.infer<typeof GetTimelogRequestSchema>;
export type CheckWorkDayRequest = z.infer<typeof CheckWorkDayRequestSchema>;