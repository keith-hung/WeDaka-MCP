#!/usr/bin/env node

/**
 * WeDaka MCP Server - Entry point for NPX execution
 */

import { main } from './server/index';

main().catch((error: unknown) => {
  console.error('Server error:', error);
  process.exit(1);
});