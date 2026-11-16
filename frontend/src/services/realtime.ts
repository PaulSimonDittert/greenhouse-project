export type RealtimeEvent = {
  type: string;
  payload: unknown;
};

export function subscribeRealtime(_handler: (event: RealtimeEvent) => void): () => void {
  // Phase 12 replaces this in-process stub with a real WebSocket implementation.
  return () => undefined;
}
