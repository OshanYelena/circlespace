import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { readSession, SESSION_KEY, writeSession, type Session } from "./session.ts";

const session: Session = {
  token: "token",
  user: {
    id: 1,
    email: "ada@example.com",
    username: "ada",
    created_at: "2026-01-01T00:00:00Z",
    profile: { display_name: "Ada", bio: null, avatar_url: null, location: null },
  },
};

describe("session storage", () => {
  it("round trips a valid session", () => {
    const values = new Map<string, string>();
    const storage = {
      getItem: (key: string) => values.get(key) ?? null,
      setItem: (key: string, value: string) => values.set(key, value),
    };
    writeSession(storage, session);
    assert.deepEqual(readSession(storage), session);
    assert.equal(values.has(SESSION_KEY), true);
  });

  it("rejects malformed data", () => {
    assert.equal(readSession({ getItem: () => "not-json" }), null);
    assert.equal(readSession({ getItem: () => JSON.stringify({ token: "" }) }), null);
  });
});
