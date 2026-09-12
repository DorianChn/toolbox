#!/usr/bin/env node

/**
 * devkit - entry point.
 *
 * Keeps this file intentionally thin: it only handles process-level concerns
 * (argv, exit codes, error formatting) and delegates all real work to the
 * command registry in src/.
 */

import { run } from '../src/index.js';
import { VERSION } from '../src/version.js';
import { red, gray } from '../src/colors.js';

const argv = process.argv.slice(2);

// Fast path for version/help so they work even if a command module is broken.
if (argv.includes('--version') || argv.includes('-v')) {
  console.log(VERSION);
  process.exit(0);
}

try {
  const code = await run(argv);
  process.exit(code ?? 0);
} catch (error) {
  const label = error?.name === 'UsageError' ? 'Usage' : 'Error';
  console.error(`${red(`${label}:`)} ${error?.message ?? error}`);
  if (error?.hint) console.error(gray(`Hint: ${error.hint}`));
  process.exit(1);
}
