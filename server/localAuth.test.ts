import { describe, expect, it } from "vitest";
import { createLocalSession, getUserIdFromLocalSession } from "./_core/localAuth";

describe("local authentication session", () => {
  it("round-trips a signed user id", () => {
    const token = createLocalSession(42);
    expect(getUserIdFromLocalSession(token)).toBe(42);
  });

  it("rejects tampered sessions", () => {
    const token = createLocalSession(42);
    expect(getUserIdFromLocalSession(`${token}x`)).toBeUndefined();
    expect(getUserIdFromLocalSession("not-a-session")).toBeUndefined();
  });
});
