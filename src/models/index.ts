/**
 * Zod schemas for WeDaka MCP Server validation
 */

import { z } from 'zod';

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