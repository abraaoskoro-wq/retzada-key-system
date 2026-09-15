import type { CreateExpressContextOptions } from "@trpc/server/adapters/express";
import type { User } from "../../drizzle/schema";
import { getUserById } from "../db";
import { LOCAL_COOKIE_NAME } from "../../shared/const";
import { sdk } from "./sdk";
import { getUserIdFromLocalSession } from "./localAuth";

export type TrpcContext = {
  req: CreateExpressContextOptions["req"];
  res: CreateExpressContextOptions["res"];
  user: User | null;
};

export async function createContext(
  opts: CreateExpressContextOptions
): Promise<TrpcContext> {
  let user: User | null = null;

  const cookieHeader = opts.req.headers.cookie ?? "";
  const localToken = cookieHeader.split(";").map(value => value.trim()).find(value => value.startsWith(`${LOCAL_COOKIE_NAME}=`))?.slice(LOCAL_COOKIE_NAME.length + 1);
  const localUserId = getUserIdFromLocalSession(localToken);
  if (localUserId) {
    user = (await getUserById(localUserId)) ?? null;
  }

  if (!user) {
    try {
      user = await sdk.authenticateRequest(opts.req);
    } catch (error) {
      // Authentication is optional for public procedures.
      user = null;
    }
  }

  return {
    req: opts.req,
    res: opts.res,
    user,
  };
}
