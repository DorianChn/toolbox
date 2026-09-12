/**
 * Small ANSI color helpers. Respects NO_COLOR and non-TTY output so piped
 * output stays clean.
 * See: https://no-color.org/
 */

const enabled =
  !process.env.NO_COLOR &&
  (process.env.FORCE_COLOR === '1' || process.stdout.isTTY === true);

const wrap = (open) => (text) => (enabled ? `\x1b[${open}m${text}\x1b[0m` : String(text));

export const red = wrap('31');
export const green = wrap('32');
export const yellow = wrap('33');
export const blue = wrap('34');
export const magenta = wrap('35');
export const cyan = wrap('36');
export const gray = wrap('90');
export const bold = wrap('1');
export const dim = wrap('2');

export const colorsEnabled = enabled;
