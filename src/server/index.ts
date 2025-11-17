/**
 * WeDaka MCP Server - Employee Clock-in System (TypeScript Implementation)
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
  TextContent,
} from '@modelcontextprotocol/sdk/types.js';
import { WedakaApiClient } from '../client/WedakaApiClient.js';
import { getWorkItemDescription, WorkItemType } from '../models/index.js';
import { config } from 'dotenv';

// Load environment variables
config();

// Global API client instance
let apiClient: WedakaApiClient | null = null;

function getApiClient(): WedakaApiClient {
  if (!apiClient) {
    apiClient = new WedakaApiClient();
  }
  return apiClient;
}

// Create server instance
const server = new Server(
  {
    name: 'wedaka-ts',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  const tools: Tool[] = [
    {
      name: 'wedaka_clock_in',
      description: 'Clock in (上班打卡)',
      inputSchema: {
        type: 'object',
        properties: {
          note: {
            type: 'string',
            description: 'Additional notes (optional)',
          },
          clock_date: {
            type: 'string',
            description: 'Date in YYYY-MM-DD format (optional, defaults to today)',
          },
          clock_time: {
            type: 'string',
            description: 'Time in HH:MM:SS format (optional, defaults to current time)',
          },
        },
        required: [],
      },
    },
    {
      name: 'wedaka_clock_out',
      description: 'Clock out (下班打卡)',
      inputSchema: {
        type: 'object',
        properties: {
          note: {
            type: 'string',
            description: 'Additional notes (optional)',
          },
          clock_date: {
            type: 'string',
            description: 'Date in YYYY-MM-DD format (optional, defaults to today)',
          },
          clock_time: {
            type: 'string',
            description: 'Time in HH:MM:SS format (optional, defaults to current time)',
          },
        },
        required: [],
      },
    },
    {
      name: 'wedaka_get_timelog',
      description: 'Get employee time log records for a specific month',
      inputSchema: {
        type: 'object',
        properties: {
          month: {
            type: 'integer',
            description: 'Month (1-12)',
            minimum: 1,
            maximum: 12,
          },
          year: {
            type: 'integer',
            description: 'Year (e.g., 2024)',
            minimum: 2020,
            maximum: 2030,
          },
        },
        required: ['month', 'year'],
      },
    },
    {
      name: 'wedaka_check_work_day',
      description: 'Check if a specific date is a work day',
      inputSchema: {
        type: 'object',
        properties: {
          date: {
            type: 'string',
            description: 'Date in YYYY-MM-DD format',
          },
        },
        required: ['date'],
      },
    },
  ];

  return { tools };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'wedaka_clock_in') {
      const { note, clock_date, clock_time } = args as {
        note?: string;
        clock_date?: string;
        clock_time?: string;
      };

      const client = getApiClient();
      const response = await client.insertTimeLog('上班', note, clock_date, clock_time);

      const result = {
        success: response.Status,
        message: response.ErrorMessage || '',
        logId: response.LogId,
        logTime: response.LogTime,
      };

      return {
        content: [
          {
            type: 'text',
            text: `Clock in result: ${JSON.stringify(result, null, 2)}`,
          } as TextContent,
        ],
      };
    } else if (name === 'wedaka_clock_out') {
      const { note, clock_date, clock_time } = args as {
        note?: string;
        clock_date?: string;
        clock_time?: string;
      };

      const client = getApiClient();
      const response = await client.insertTimeLog('下班', note, clock_date, clock_time);

      const result = {
        success: response.Status,
        message: response.ErrorMessage || '',
        logId: response.LogId,
        logTime: response.LogTime,
      };

      return {
        content: [
          {
            type: 'text',
            text: `Clock out result: ${JSON.stringify(result, null, 2)}`,
          } as TextContent,
        ],
      };
    } else if (name === 'wedaka_get_timelog') {
      const { month, year } = args as {
        month: number;
        year: number;
      };

      const client = getApiClient();
      const response = await client.searchTimelog(month, year);

      let result: any;
      if (response.Status) {
        // Add human-readable interpretation to each record
        const enhancedRecords = (response.TimeLog || []).map((record) => {
          const workItemDesc = getWorkItemDescription(record.WorkItem);
          const isLeave = record.WorkItem === WorkItemType.LEAVE;

          return {
            ...record,
            WorkItemDescription: workItemDesc,
            IsLeave: isLeave,
            // Highlight leave information
            ...(isLeave && {
              LeaveInfo: `Employee on leave for ${record.LeaveHours || 0} hours`,
            }),
          };
        });

        // Count different types of records
        const clockInCount = enhancedRecords.filter(r => r.WorkItem === WorkItemType.CLOCK_IN).length;
        const clockOutCount = enhancedRecords.filter(r => r.WorkItem === WorkItemType.CLOCK_OUT).length;
        const leaveCount = enhancedRecords.filter(r => r.WorkItem === WorkItemType.LEAVE).length;

        result = {
          success: true,
          message: response.ErrorMessage || '',
          totalRecords: response.TimeLog?.length || 0,
          summary: {
            clockIns: clockInCount,
            clockOuts: clockOutCount,
            leaves: leaveCount,
          },
          records: enhancedRecords,
        };
      } else {
        result = {
          success: false,
          message: response.ErrorMessage || '',
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `Time log query result: ${JSON.stringify(result, null, 2)}`,
          } as TextContent,
        ],
      };
    } else if (name === 'wedaka_check_work_day') {
      const { date } = args as {
        date: string;
      };

      const client = getApiClient();
      const response = await client.getDateType(date);

      let result: any;
      if (response.Status) {
        const isWorkDay = response.DateType === '1';
        result = {
          success: true,
          date: date,
          dateType: response.DateType,
          isWorkDay: isWorkDay,
          message: `日期 ${date} 的類型為 ${response.DateType}${
            response.DateType === '1' ? ' (工作日)' : 
            response.DateType === '2' ? ' (休假日)' :
            response.DateType === '3' ? ' (例假日)' : ' (未知類型)'
          }`,
        };
      } else {
        result = {
          success: false,
          date: date,
          message: response.ErrorMessage || '',
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `Work day check result: ${JSON.stringify(result, null, 2)}`,
          } as TextContent,
        ],
      };
    } else {
      return {
        content: [
          {
            type: 'text',
            text: `Unknown tool: ${name}`,
          } as TextContent,
        ],
      };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing tool ${name}: ${error}`,
        } as TextContent,
      ],
    };
  }
});

export async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('WeDaka MCP Server (TypeScript) running on stdio');
}

// Handle shutdown gracefully
process.on('SIGINT', async () => {
  await server.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await server.close();
  process.exit(0);
});

if (require.main === module) {
  main().catch((error) => {
    console.error('Server error:', error);
    process.exit(1);
  });
}