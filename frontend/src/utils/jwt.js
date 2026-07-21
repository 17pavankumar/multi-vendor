/** Decodes a JWT's payload without verifying the signature — safe here
 * because this only ever reads a token *we* just received directly
 * from our own backend over HTTPS; it's never used to trust a token
 * from anywhere else. */
export function decodeJwtPayload(token) {
  try {
    const payloadB64 = token.split(".")[1];
    const normalized = payloadB64.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), "=");
    return JSON.parse(atob(padded));
  } catch {
    return null;
  }
}
