/// <reference path="../.astro/types.d.ts" />
/// <reference types="astro/client" />

interface ImportMetaEnv {
  /** Hosted geoapp FastAPI URL. Set to enable the live explorer embed. */
  readonly PUBLIC_GEOAPP_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
