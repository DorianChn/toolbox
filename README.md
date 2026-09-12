# devkit

A zero-dependency Swiss Army knife for everyday developer tasks.

`devkit` bundles the small utilities you keep reaching for — hashing, UUIDs, base64,
JSON formatting, password generation, timestamp conversion — into a single fast CLI
with no `node_modules` to install.

```
$ devkit hash "hello world"
sha256  b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
```

## Why

Most of these tasks have a one-liner solution, but the one-liner is different every
time and always slightly wrong:

```bash
# How do I hash a string again?
echo -n "hello" | shasum -a 256 | cut -d' ' -f1

# Is this timestamp in seconds or milliseconds?
node -e "console.log(new Date(1735689600 * 1000).toISOString())"
```

`devkit` makes them memorable and consistent: one tool, one flag style, sensible
defaults. Every command works with an argument, a file, or stdin.

## Requirements

Node.js **18 or newer**. That's it — there are no runtime dependencies.

## Install

Clone and link it globally:

```bash
git clone https://github.com/DorianChn/devkit-cli.git
cd devkit-cli
npm link
```

`npm link` puts `devkit` on your `PATH`. To uninstall later, run `npm unlink -g devkit`.

Prefer not to install anything? Run it directly:

```bash
node bin/devkit.js hash "hello"
```

## Commands

| Command | Description |
| --- | --- |
| `hash` | Checksum text, a file, or stdin (`sha256`, `sha1`, `sha512`, `md5`) |
| `uuid` | Generate one or many UUID v4 values |
| `json` | Validate, pretty-print, or minify JSON |
| `b64` | Base64 encode or decode, including URL-safe variants |
| `pass` | Generate strong random passwords or numeric PINs |
| `ts` | Convert between Unix timestamps and ISO dates |

Run `devkit help <command>` for per-command options and examples.

## Usage

### hash

Compute a checksum. Defaults to `sha256`; `--quiet` prints only the digest so it can
be piped into other tools. File hashing is streamed, so large files don't blow up memory.

```bash
devkit hash "hello world"
devkit hash --file ./dist/bundle.js --algo sha512
echo -n "abc" | devkit hash --quiet
```

### uuid

```bash
devkit uuid                  # one id
devkit uuid -n 5             # five ids
devkit uuid -n 3 --upper --no-dashes
```

### json

Validates as it formats. On invalid input it reports the position of the problem and
exits with code `1`.

```bash
devkit json ./package.json
cat data.json | devkit json --minify
devkit json config.json --sort-keys --indent 4
```

### b64

```bash
devkit b64 "hello"
devkit b64 "aGVsbG8=" --decode
cat image.png | devkit b64 --url-safe
```

### pass

Passwords use an unambiguous alphabet — `l`, `I`, `O`, `0`, and `1` are excluded so
they survive being read aloud or retyped. `--symbols` widens the alphabet, and the
entropy estimate is printed to stderr.

```bash
devkit pass
devkit pass --length 32 --symbols
devkit pass -n 5
devkit pass --pin --length 6
```

### ts

With no argument, prints the current time. With an argument, interprets it as a Unix
timestamp (seconds by default, milliseconds for 12+ digit values or when `--ms` is
passed) or as any date string `Date` can parse.

```bash
devkit ts
devkit ts 1735689600
devkit ts 2025-01-01T00:00:00Z
devkit ts 1735689600000 --ms
```

## Design notes

- **Zero dependencies.** Everything is built on Node's `node:crypto`, `node:fs`, and
  `node:stream`. No supply chain, no install step, no version conflicts.
- **Composable output.** Data goes to stdout, human-readable decoration goes to
  stderr. `--quiet` drops the decoration entirely.
- **Colour is opt-in.** ANSI colour is only emitted when stdout is a TTY, and it
  respects the [`NO_COLOR`](https://no-color.org/) convention.
- **Thin entry point.** `bin/devkit.js` only maps argv to exit codes; all logic lives
  in testable modules under `src/`.

## Project layout

```
devkit-cli/
├── bin/
│   └── devkit.js          # entry point: argv -> exit code
├── src/
│   ├── index.js           # command registry
│   ├── args.js            # argument parsing + UsageError
│   ├── colors.js          # ANSI helpers, NO_COLOR aware
│   ├── version.js
│   └── commands/
│       ├── hash.js
│       ├── uuid.js
│       ├── json.js
│       ├── b64.js
│       ├── pass.js
│       ├── ts.js
│       └── help.js
└── test/
    └── devkit.test.js
```

## Testing

Uses the built-in [`node:test`](https://nodejs.org/api/test.html) runner — no test
framework to install.

```bash
npm test
```

## Adding a command

1. Create `src/commands/yourcommand.js` exporting `meta` and an async `run(argv)`.
2. Register it in the `commands` map in `src/index.js`.

`bin/devkit.js` and `help` pick it up automatically — the help output re-derives its
column widths from the registry.

```js
export const meta = {
  name: 'yourcommand',
  summary: 'One line describing what it does',
  usage: 'devkit yourcommand [--flag]',
  examples: ['devkit yourcommand --flag'],
};

export async function run(argv) {
  // parse args, do work, print to stdout
  return 0;
}
```

## License

MIT — see [LICENSE](./LICENSE).
