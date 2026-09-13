import { commands } from '../index.js';
import { VERSION } from '../version.js';
import { UsageError } from '../args.js';
import { bold, cyan, gray, magenta } from '../colors.js';

export const meta = {
  name: 'help',
  summary: 'Show available commands, or details for one command',
  usage: 'devkit help [command]',
  examples: ['devkit help', 'devkit help hash'],
};

/**
 * Render the command list. Column width is computed from the actual names so
 * adding a long command name doesn't misalign everything.
 */
export function renderIndex() {
  const rows = [...commands.values()]
    .map((module) => module.meta)
    .filter(Boolean)
    .sort((a, b) => a.name.localeCompare(b.name));

  const width = Math.max(...rows.map((row) => row.name.length)) + 2;

  const lines = [
    `${bold('devkit')} ${gray(`v${VERSION}`)} — a zero-dependency developer toolkit`,
    '',
    `${bold('Usage')}  devkit <command> [options]`,
    '',
    `${bold('Commands')}`,
  ];

  for (const row of rows) {
    lines.push(`  ${cyan(row.name.padEnd(width))}${row.summary}`);
  }

  lines.push(
    '',
    `${gray('Run "devkit help <command>" for options and examples.')}`,
  );

  return lines.join('\n');
}

export function renderDetail(name) {
  const module = commands.get(name);
  if (!module?.meta) return null;

  const { meta } = module;
  const lines = [
    `${bold(meta.name)} — ${meta.summary}`,
    '',
    `${bold('Usage')}  ${meta.usage}`,
  ];

  if (meta.examples?.length) {
    lines.push('', `${bold('Examples')}`);
    for (const example of meta.examples) {
      lines.push(`  ${magenta('$')} ${example}`);
    }
  }

  return lines.join('\n');
}

export async function run(argv) {
  const target = argv[0];

  if (target) {
    const detail = renderDetail(target);
    if (!detail) {
      throw new UsageError(`no help available for "${target}"`);
    }
    console.log(detail);
    return 0;
  }

  console.log(renderIndex());
  return 0;
}
