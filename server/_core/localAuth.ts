import { createHmac, timingSafeEqual } from "node:crypto";
import { ENV } from "./env";

function signature(payload: string) {
  return createHmac("sha256", ENV.cookieSecret || "ffh4x-local-session").update(payload).digest("hex");
}

export function createLocalSession(userId: number) {
  const payload = String(userId);
  return `${payload}.${signature(payload)}`;
}

export function getUserIdFromLocalSession(token: string | undefined) {
  if (!token) return undefined;
  const [payload, providedSignature] = token.split(".");
  if (!payload || !providedSignature || !/^\d+$/.test(payload)) return undefined;
  const expectedSignature = signature(payload);
  const expected = Buffer.from(expectedSignature, "utf8");
  const provided = Buffer.from(providedSignature, "utf8");
  if (expected.length !== provided.length || !timingSafeEqual(expected, provided)) return undefined;
  return Number(payload);
}
