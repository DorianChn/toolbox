import { UsageError } from './args.js';
import * as hash from './commands/hash.js';
import * as uuid from './commands/uuid.js';
import * as json from './commands/json.js';
import * as b64 from './commands/b64.js';
import * as pass from './commands/pass.js';
import * as ts from './commands/ts.js';
import * as help from './commands/help.js';

/**
 * The command registry. Adding a command means adding one entry here plus a
 * module in src/commands/ that exports `meta` and `run`.
 */
export const commands = new Map([
  ['hash', hash],
  ['uuid', uuid],
  ['json', json],
  ['b64', b64],
  ['pass', pass],
  ['ts', ts],
  ['help', help],
]);

/**
 * @param {string[]} argv
 * @returns {Promise<number>}
 */
export async function run(argv) {
  const [name, ...rest] = argv;

  if (!name || name === 'help' || name === '--help' || name === '-h') {
    return commands.get('help').run(name ? rest : []);
  }

  const command = commands.get(name);
  if (!command) {
    throw new UsageError(
      `unknown command "${name}"`,
      `run "devkit help" to see available commands`,
    );
  }

  return command.run(rest);
}
