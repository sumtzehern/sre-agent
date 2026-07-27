/**
 * Re-exports the CDN incident fixture as a string, for the "paste incident"
 * preset in ChatInput. Single source of truth is fixtures/cdn-incident.md at
 * the repo root — the standalone script (scripts/rca_demo.py) reads the same
 * file directly.
 */
// eslint-disable-next-line import/no-unresolved
import cdnIncident from '../../fixtures/cdn-incident.md?raw';

export default cdnIncident as string;
