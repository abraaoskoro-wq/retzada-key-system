import { z } from "zod";
import { and, desc, eq, inArray, isNull, or, sql } from "drizzle-orm";
import { randomBytes } from "node:crypto";
import { TRPCError } from "@trpc/server";
import { COOKIE_NAME, LOCAL_COOKIE_NAME } from "@shared/const";
import { getLocalSessionCookieOptions, getSessionCookieOptions } from "./_core/cookies";
import { getDb, getKeysForUser, getProducts, getTicketsForUser, getUserByEmail, getUserByUsername, hashPassword, OWNER_EMAIL, verifyPassword } from "./db";
import { ENV } from "./_core/env";
import { createLocalSession } from "./_core/localAuth";
import { announcements, auditLogs, keys, mods, products, tickets, users } from "../drizzle/schema";
import { systemRouter } from "./_core/systemRouter";
import { protectedProcedure, publicProcedure, router } from "./_core/trpc";

const adminProcedure = protectedProcedure.use(({ ctx, next }) => {
  const isOwner = ctx.user.role === "admin" || ctx.user.openId === ENV.ownerOpenId || ctx.user.email?.toLowerCase() === OWNER_EMAIL || ctx.user.username?.toLowerCase() === "retzada";
  if (!isOwner) throw new TRPCError({ code: "FORBIDDEN", message: "Acesso exclusivo do proprietário." });
  return next({ ctx });
});

export function parseImportedCodes(content: string) {
  return Array.from(new Set(
    content
      .split(/\r?\n/)
      .map(code => code.trim())
      .filter(code => code.length >= 1 && code.length <= 64),
  ));
}

async function writeAudit(actorId: number, action: string, details: string) {
  const db = await getDb();
  if (db) await db.insert(auditLogs).values({ actorId, action, details });
}

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    register: publicProcedure
      .input(z.object({ email: z.string().trim().toLowerCase().email().refine(value => value.endsWith("@gmail.com"), "Use um endereço Gmail válido."), name: z.string().trim().min(2).max(80), username: z.string().trim().min(3).max(40).regex(/^[a-zA-Z0-9_.-]+$/), password: z.string().min(3).max(128) }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        const email = input.email.toLowerCase();
        const existingEmail = await getUserByEmail(email);
        const existingUsername = await getUserByUsername(input.username);
        if (existingUsername && existingUsername.id !== existingEmail?.id) throw new TRPCError({ code: "CONFLICT", message: "Este nome de usuário já está em uso." });
        const isOwner = email === OWNER_EMAIL;
        if (existingEmail && !isOwner) throw new TRPCError({ code: "CONFLICT", message: "Este Gmail já está cadastrado." });
        if (existingEmail) {
          await db.update(users).set({ name: input.name, username: input.username, passwordHash: hashPassword(input.password), loginMethod: "local", role: isOwner ? "admin" : existingEmail.role, accountStatus: isOwner ? "approved" : existingEmail.accountStatus }).where(eq(users.id, existingEmail.id));
        } else {
          await db.insert(users).values({ openId: `local_${randomBytes(18).toString("hex")}`, name: input.name, email, username: input.username, passwordHash: hashPassword(input.password), loginMethod: "local", role: isOwner ? "admin" : "user", accountStatus: isOwner ? "approved" : "pending" });
        }
        const user = await getUserByEmail(email);
        if (!user) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Não foi possível criar a conta." });
        if (!isOwner && user.accountStatus !== "approved") return user;
        ctx.res.cookie(LOCAL_COOKIE_NAME, createLocalSession(user.id), { ...getLocalSessionCookieOptions(ctx.req), maxAge: 1000 * 60 * 60 * 24 * 30 });
        return user;
      }),
    login: publicProcedure
      .input(z.object({ username: z.string().trim().min(3).max(40), password: z.string().min(1).max(128) }))
      .mutation(async ({ ctx, input }) => {
        const user = await getUserByUsername(input.username);
        if (!user || !verifyPassword(input.password, user.passwordHash)) throw new TRPCError({ code: "UNAUTHORIZED", message: "Nome de usuário ou senha incorretos." });
        if (user.accountStatus !== "approved") throw new TRPCError({ code: "FORBIDDEN", message: "Sua conta está aguardando aprovação do administrador." });
        const db = await getDb();
        if (db) await db.update(users).set({ lastSignedIn: new Date() }).where(eq(users.id, user.id));
        ctx.res.cookie(LOCAL_COOKIE_NAME, createLocalSession(user.id), { ...getLocalSessionCookieOptions(ctx.req), maxAge: 1000 * 60 * 60 * 24 * 30 });
        return user;
      }),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      ctx.res.clearCookie(LOCAL_COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),

  member: router({
    dashboard: protectedProcedure.query(async ({ ctx }) => {
      const db = await getDb();
      if (!db) return { redeemed: 0, openTickets: 0 };
      const redeemed = await db.select({ id: keys.id }).from(keys).where(or(eq(keys.generatedBy, ctx.user.id), eq(keys.redeemedBy, ctx.user.id)));
      const openTickets = await db.select({ id: tickets.id }).from(tickets).where(and(eq(tickets.userId, ctx.user.id), eq(tickets.status, "open")));
      return { redeemed: redeemed.length, openTickets: openTickets.length };
    }),
    myKeys: protectedProcedure.query(({ ctx }) => getKeysForUser(ctx.user.id)),
    products: protectedProcedure.query(() => getProducts()),
    announcements: protectedProcedure.query(async () => {
      const db = await getDb();
      return db ? db.select().from(announcements).orderBy(desc(announcements.createdAt)).limit(20) : [];
    }),
    generatedKeys: protectedProcedure.query(async ({ ctx }) => {
      const db = await getDb();
      if (!db) return [];
      return db.select().from(keys).where(eq(keys.generatedBy, ctx.user.id)).orderBy(desc(keys.createdAt)).limit(50);
    }),
    generateKeys: protectedProcedure
      .input(z.object({ productId: z.number().int().positive(), quantity: z.number().int().min(1).max(20) }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        const product = (await db.select().from(products).where(eq(products.id, input.productId)).limit(1))[0];
        if (!product) throw new TRPCError({ code: "NOT_FOUND", message: "Produto não encontrado." });
        const available = await db.select().from(keys).where(and(eq(keys.productId, product.id), eq(keys.status, "available"), isNull(keys.generatedBy))).limit(input.quantity);
        if (available.length < input.quantity) throw new TRPCError({ code: "BAD_REQUEST", message: `Estoque insuficiente. Disponível: ${available.length}.` });
        const ids = available.map(item => item.id);
        await db.transaction(async tx => {
          await tx.update(keys).set({ generatedBy: ctx.user.id }).where(inArray(keys.id, ids));
          await tx.update(products).set({ stock: sql`${products.stock} - ${input.quantity}` }).where(eq(products.id, product.id));
        });
        return { success: true, codes: available.map(value => value.code) };
      }),
    myTickets: protectedProcedure.query(({ ctx }) => getTicketsForUser(ctx.user.id)),
    createTicket: protectedProcedure
      .input(z.object({ subject: z.string().trim().min(3).max(160), message: z.string().trim().min(5).max(4000) }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        await db.insert(tickets).values({ userId: ctx.user.id, subject: input.subject, message: input.message });
        return { success: true } as const;
      }),
  }),

  admin: router({
    dashboard: adminProcedure.query(async () => {
      const db = await getDb();
      if (!db) return { totalKeys: 0, availableKeys: 0, redeemedKeys: 0, products: 0, recent: [] };
      const [allKeys, available, redeemed, productRows, recent] = await Promise.all([
        db.select({ id: keys.id }).from(keys),
        db.select({ id: keys.id }).from(keys).where(eq(keys.status, "available")),
        db.select({ id: keys.id }).from(keys).where(eq(keys.status, "redeemed")),
        db.select({ id: products.id }).from(products),
        db.select().from(keys).orderBy(desc(keys.createdAt)).limit(6),
      ]);
      return { totalKeys: allKeys.length, availableKeys: available.length, redeemedKeys: redeemed.length, products: productRows.length, recent };
    }),
    products: adminProcedure.query(() => getProducts()),
    createProduct: adminProcedure
      .input(z.object({ name: z.string().trim().min(2).max(120), category: z.string().trim().min(2).max(80), durationDays: z.number().int().min(1).max(3650) }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        await db.insert(products).values({ ...input, stock: 0 });
        await writeAudit(ctx.user.id, "create_product", `Produto ${input.name} criado`);
        return { success: true } as const;
      }),
    importKeys: adminProcedure
      .input(z.object({ productId: z.number().int().positive(), content: z.string().trim().min(1).max(200000) }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        const product = (await db.select().from(products).where(eq(products.id, input.productId)).limit(1))[0];
        if (!product) throw new TRPCError({ code: "NOT_FOUND", message: "Produto não encontrado." });
        const codes = parseImportedCodes(input.content);
        if (!codes.length) throw new TRPCError({ code: "BAD_REQUEST", message: "Cole pelo menos uma key válida, uma por linha." });
        const existing = await db.select({ code: keys.code }).from(keys).where(inArray(keys.code, codes));
        const existingCodes = new Set(existing.map(item => item.code));
        const fresh = codes.filter(code => !existingCodes.has(code));
        if (!fresh.length) throw new TRPCError({ code: "CONFLICT", message: `A key ${codes[0]} já foi cadastrada. Cole uma key nova e exclusiva.` });
        await db.transaction(async tx => {
          await tx.insert(keys).values(fresh.map(code => ({ code, productId: product.id, productName: product.name, durationDays: product.durationDays })));
          await tx.update(products).set({ stock: sql`${products.stock} + ${fresh.length}` }).where(eq(products.id, product.id));
        });
        await writeAudit(ctx.user.id, "import_keys", `${fresh.length} keys importadas para ${product.name}`);
        return { success: true, imported: fresh.length, duplicated: codes.length - fresh.length } as const;
      }),
    generateKeys: adminProcedure
      .input(z.object({ productId: z.number().int().positive(), quantity: z.number().int().min(1).max(20) }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        const product = (await db.select().from(products).where(eq(products.id, input.productId)).limit(1))[0];
        if (!product) throw new TRPCError({ code: "NOT_FOUND", message: "Produto não encontrado." });
        const available = await db.select().from(keys).where(and(eq(keys.productId, product.id), eq(keys.status, "available"), isNull(keys.generatedBy))).limit(input.quantity);
        if (available.length < input.quantity) throw new TRPCError({ code: "BAD_REQUEST", message: `Estoque insuficiente. Disponível: ${available.length}.` });
        const ids = available.map(item => item.id);
        await db.transaction(async tx => {
          await tx.update(keys).set({ generatedBy: ctx.user.id }).where(inArray(keys.id, ids));
          await tx.update(products).set({ stock: sql`${products.stock} - ${input.quantity}` }).where(eq(products.id, product.id));
        });
        await writeAudit(ctx.user.id, "generate_keys", `${input.quantity} keys de ${product.name}`);
        return { success: true, codes: available.map(value => value.code) };
      }),
    listKeys: adminProcedure.query(async () => {
      const db = await getDb();
      if (!db) return [];
      return db.select().from(keys).orderBy(desc(keys.createdAt)).limit(100);
    }),
    users: adminProcedure.query(async () => {
      const db = await getDb();
      if (!db) return [];
      return db.select({ id: users.id, name: users.name, email: users.email, role: users.role, accountStatus: users.accountStatus, lastSignedIn: users.lastSignedIn }).from(users).orderBy(desc(users.lastSignedIn)).limit(100);
    }),
    approveUser: adminProcedure
      .input(z.object({ id: z.number().int().positive() }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        const target = (await db.select({ id: users.id, name: users.name, role: users.role }).from(users).where(eq(users.id, input.id)).limit(1))[0];
        if (!target) throw new TRPCError({ code: "NOT_FOUND", message: "Usuário não encontrado." });
        await db.update(users).set({ accountStatus: "approved" }).where(eq(users.id, input.id));
        await writeAudit(ctx.user.id, "approve_user", `Usuário #${input.id} aprovado`);
        return { success: true } as const;
      }),
    deleteUser: adminProcedure
      .input(z.object({ id: z.number().int().positive() }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        const target = (await db.select({ id: users.id, email: users.email, role: users.role }).from(users).where(eq(users.id, input.id)).limit(1))[0];
        if (!target) throw new TRPCError({ code: "NOT_FOUND", message: "Usuário não encontrado." });
        if (target.role === "admin" || target.email?.toLowerCase() === OWNER_EMAIL) throw new TRPCError({ code: "FORBIDDEN", message: "A conta do administrador não pode ser excluída." });
        await db.delete(users).where(eq(users.id, input.id));
        await writeAudit(ctx.user.id, "delete_user", `Usuário #${input.id} excluído`);
        return { success: true } as const;
      }),
    tickets: adminProcedure.query(async () => {
      const db = await getDb();
      if (!db) return [];
      return db.select().from(tickets).orderBy(desc(tickets.createdAt)).limit(100);
    }),
    createReseller: adminProcedure
      .input(z.object({ email: z.string().trim().toLowerCase().email().refine(value => value.endsWith("@gmail.com"), "Use um Gmail válido."), name: z.string().trim().min(2).max(80), username: z.string().trim().min(3).max(40).regex(/^[a-zA-Z0-9_.-]+$/), password: z.string().min(3).max(128) }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        if (await getUserByEmail(input.email) || await getUserByUsername(input.username)) throw new TRPCError({ code: "CONFLICT", message: "Gmail ou usuário já cadastrado." });
        await db.insert(users).values({ openId: `local_${randomBytes(18).toString("hex")}`, name: input.name, email: input.email, username: input.username, passwordHash: hashPassword(input.password), loginMethod: "local", role: "reseller" });
        await writeAudit(ctx.user.id, "create_reseller", `Revendedor ${input.username} criado`);
        return { success: true } as const;
      }),
    mods: adminProcedure.query(async () => {
      const db = await getDb();
      return db ? db.select().from(mods).orderBy(desc(mods.createdAt)) : [];
    }),
    createMod: adminProcedure
      .input(z.object({ name: z.string().trim().min(2).max(120), status: z.enum(["online", "offline", "maintenance"]) }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        await db.insert(mods).values(input);
        await writeAudit(ctx.user.id, "create_mod", `Mod ${input.name} criado`);
        return { success: true } as const;
      }),
    updateModStatus: adminProcedure
      .input(z.object({ id: z.number().int().positive(), status: z.enum(["online", "offline", "maintenance"]) }))
      .mutation(async ({ ctx, input }) => {
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
        await db.update(mods).set({ status: input.status }).where(eq(mods.id, input.id));
        await writeAudit(ctx.user.id, "update_mod_status", `Mod #${input.id}: ${input.status}`);
        return { success: true } as const;
      }),
    deleteMod: adminProcedure.input(z.object({ id: z.number().int().positive() })).mutation(async ({ ctx, input }) => {
      const db = await getDb();
      if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
      await db.delete(mods).where(eq(mods.id, input.id));
      await writeAudit(ctx.user.id, "delete_mod", `Mod #${input.id} removido`);
      return { success: true } as const;
    }),
    announcements: adminProcedure.query(async () => {
      const db = await getDb();
      return db ? db.select().from(announcements).orderBy(desc(announcements.createdAt)).limit(100) : [];
    }),
    createAnnouncement: adminProcedure.input(z.object({ title: z.string().trim().min(3).max(160), message: z.string().trim().min(3).max(4000) })).mutation(async ({ ctx, input }) => {
      const db = await getDb();
      if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Banco de dados indisponível." });
      await db.insert(announcements).values({ ...input, createdBy: ctx.user.id });
      await writeAudit(ctx.user.id, "create_announcement", input.title);
      return { success: true } as const;
    }),
    audit: adminProcedure.query(async () => {
      const db = await getDb();
      return db ? db.select().from(auditLogs).orderBy(desc(auditLogs.createdAt)).limit(200) : [];
    }),
  }),
});

export type AppRouter = typeof appRouter;
