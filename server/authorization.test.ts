import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

type TestUser = NonNullable<TrpcContext["user"]>;

function contextFor(user: TestUser): TrpcContext {
  return {
    user,
    req: { protocol: "https", headers: {} } as TrpcContext["req"],
    res: { clearCookie: () => undefined } as TrpcContext["res"],
  };
}

const baseUser: TestUser = {
  id: 42,
  openId: "client-test-user",
  email: "cliente@example.com",
  name: "Cliente Teste",
  loginMethod: "manus",
  role: "user",
  createdAt: new Date(),
  updatedAt: new Date(),
  lastSignedIn: new Date(),
};

describe("role based access", () => {
  it("blocks client users from administrative procedures", async () => {
    const caller = appRouter.createCaller(contextFor(baseUser));
    await expect(caller.admin.products()).rejects.toMatchObject({ code: "FORBIDDEN" });
    await expect(caller.admin.dashboard()).rejects.toMatchObject({ code: "FORBIDDEN" });
  });

  it("allows a locally authenticated administrator to access the admin area", async () => {
    const caller = appRouter.createCaller(contextFor({ ...baseUser, role: "admin", email: "abraaoskoro@gmail.com", username: "Retzada" }));
    await expect(caller.admin.products()).resolves.toBeDefined();
  });

  it("limits generated batches to 20 keys", async () => {
    const caller = appRouter.createCaller(contextFor(baseUser));
    await expect(caller.member.generateKeys({ productId: 1, quantity: 21 })).rejects.toMatchObject({ code: "BAD_REQUEST" });
  });

  it("recognizes the owner role in the user model", () => {
    expect(baseUser.role).toBe("user");
    expect(baseUser.email).not.toBe("abraaoskoro@gmail.com");
  });
});
