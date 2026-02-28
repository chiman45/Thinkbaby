/**
 * Claim Hash Utilities
 * MUST match backend normalization and hashing exactly
 */

import { keccak256, toUtf8Bytes } from 'ethers';

/**
 * Normalize text using deterministic rules
 * MUST match backend: lowercase → trim → collapse multiple spaces to single space
 */
export function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .split(/\s+/)
    .join(' ');
}

/**
 * Generate keccak256 hash of normalized text
 * Returns hex string with 0x prefix
 * MUST match backend hash computation exactly
 */
export function hashClaim(text: string): string {
  const normalized = normalizeText(text);
  return keccak256(toUtf8Bytes(normalized));
}
