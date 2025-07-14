/**
 * Jest test setup - loads environment variables from .env file
 */

import { config } from 'dotenv';
import { resolve } from 'path';

// Load environment variables from .env file for testing
// This allows tests to use real configuration when .env file exists
config({ path: resolve(process.cwd(), '.env') });