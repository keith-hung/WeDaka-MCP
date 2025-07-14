/**
 * TypeScript type definitions for WeDaka MCP Server
 */

export interface DateTypeResponse {
  DateType: string; // "1"=工作日, "2"/"3"/"4"=假日
  Status: boolean;
  ErrorMessage?: string;
}

export interface TimeLogResponse {
  Status: boolean;
  ErrorMessage?: string;
  HolidayList?: any;
  LogId?: string;
  LogTime?: string;
}

export interface TimeLogRecord {
  DateType?: string;
  LeaveHours?: number;
  Memo?: string;
  WorkItem?: string;
  WorkTime?: string;
  WorkType?: string;
  WorkDate?: string;
}

export interface SearchTimelogResponse {
  Status: boolean;
  ErrorMessage?: string;
  TimeLog?: TimeLogRecord[];
}

export interface ApiResponse<T = any> {
  Status: boolean;
  ErrorMessage?: string;
  data?: T;
}

export interface WedakaConfig {
  apiUrl: string;
  username: string;
  deviceId: string;
  empNo: string;
}

export interface ClockInRequest {
  date?: string;
  time?: string;
  memo?: string;
  empId?: string;
}

export interface ClockOutRequest {
  date?: string;
  time?: string;
  memo?: string;
  empId?: string;
}

export interface GetTimelogRequest {
  year: string;
  month: string;
  empId?: string;
}

export interface CheckWorkDayRequest {
  date: string;
  empId?: string;
}