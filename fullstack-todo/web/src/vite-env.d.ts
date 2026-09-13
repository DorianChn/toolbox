/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Absolute API origin, e.g. https://api.example.com. Empty means "same origin". */
  readonly VITE_API_BASE?: string;
}
