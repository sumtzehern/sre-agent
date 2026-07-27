/**
 * Extracts the structured RCA reasoning chain from an assistant message.
 *
 * The backend agent (agents/chat/index.py) is instructed to end its answer
 * with a fenced ```json code block containing an array of reasoning steps.
 * Apodex does not support API-level structured output (`response_format`),
 * so this contract is enforced purely by prompting on the backend and
 * parsed defensively here — any shape mismatch returns null and the message
 * just renders as plain chat text (no crash, no partial UI).
 */

import type { ReasoningStep } from '../types';

const JSON_FENCE_RE = /```json\s*([\s\S]*?)\s*```/g;

const CONFIDENCE_VALUES = new Set(['low', 'medium', 'high']);

/** Shape of one step as the backend emits it (snake_case, per the prompt contract). */
interface RawReasoningStep {
  hypothesis: string;
  evidence_checked: string[];
  conclusion: string;
  confidence: string;
}

function isRawReasoningStep(value: unknown): value is RawReasoningStep {
  if (!value || typeof value !== 'object') return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.hypothesis === 'string' &&
    typeof v.conclusion === 'string' &&
    Array.isArray(v.evidence_checked) &&
    v.evidence_checked.every(id => typeof id === 'string') &&
    typeof v.confidence === 'string' &&
    CONFIDENCE_VALUES.has(v.confidence)
  );
}

/** Parse the last fenced ```json block in `content` into a reasoning chain. */
export function parseReasoningChain(content: string): ReasoningStep[] | null {
  if (!content) return null;

  const matches = [...content.matchAll(JSON_FENCE_RE)];
  if (matches.length === 0) return null;

  const raw = matches[matches.length - 1][1];

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return null;
  }

  if (!Array.isArray(parsed) || parsed.length === 0) return null;
  if (!parsed.every(isRawReasoningStep)) return null;

  return (parsed as RawReasoningStep[]).map(step => ({
    hypothesis: step.hypothesis,
    evidenceChecked: step.evidence_checked,
    conclusion: step.conclusion,
    confidence: step.confidence as ReasoningStep['confidence'],
  }));
}
