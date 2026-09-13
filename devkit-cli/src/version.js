import { readFileSync } from 'node:fs';

/**
 * Single source of truth for the version.
 *
 * Reading it from package.json (instead of hardcoding a string here) means
 * `--version`, the help banner, and the published package can never drift
 * apart. npm always ships package.json, so this also works from an installed
 * copy, not just from a git checkout.
 */
const pkg = JSON.parse(
  readFileSync(new URL('../package.json', import.meta.url), 'utf8'),
);

export const VERSION = pkg.version;
