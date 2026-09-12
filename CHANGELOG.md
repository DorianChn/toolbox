# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] — 2026-09-13

### Fixed

- **Version drift.** `src/version.js` hardcoded `1.0.0` while `package.json`
  carried its own copy, so the two could silently disagree. This is the bug
  class where two wrong values cancel out and the tests still pass. The version
  is now read from `package.json` at runtime, and a test asserts the two stay
  in sync.
- **`NO_COLOR` was ignored for error output.** `bin/devkit.js` emitted raw ANSI
  escapes instead of going through `src/colors.js`, so piping errors or setting
  `NO_COLOR=1` still produced colour — contradicting the documented
  "colour is opt-in" behaviour. Error and hint output now respect `NO_COLOR`
  and non-TTY output like everything else.
- **Entropy estimate was overstated.** `pass` computed entropy from a hardcoded
  alphabet size of 60, but the unambiguous alphabet is 57 characters
  (`LOWER` 25 + `UPPER` 24 + `DIGITS` 8), inflating the estimate by ~2 bits and
  guaranteeing silent drift if the character sets ever change. Entropy is now
  derived from the real alphabet via the new `alphabetSize()`.

### Changed

- **`json --indent` is validated.** Non-numeric input previously became `NaN`
  and was handed straight to `JSON.stringify` without complaint; it now fails
  with a clear usage error, and values outside `0..10` are rejected.
- **Removed dead code.** Dropped the unused `readFile` import in `hash.js` and
  `randomBytes` import in `uuid.js` — both were kept alive only by `void x;`
  statements.
- **Static imports.** `UsageError` was fetched with `await import('../args.js')`
  inside error paths in `uuid`, `pass`, `ts`, and `help`, even though those
  modules already import from `args.js` at the top; `b64` did the same for
  `node:fs/promises`. All are now plain static imports.

### Added

- Tests for version/`package.json` consistency, for `alphabetSize()`, and for
  generated passwords drawing only from the declared alphabet — 23 tests, up
  from 20.
- Repository metadata in `package.json` (`repository`, `homepage`, `bugs`,
  `author`) and a real clone URL in the README in place of the
  `<your-repo-url>` placeholder.
- This changelog.

## [1.0.0] — 2026-09-13

Initial release: six zero-dependency commands (`hash`, `uuid`, `json`, `b64`,
`pass`, `ts`) built on `node:crypto`, `node:fs`, and `node:stream`.
