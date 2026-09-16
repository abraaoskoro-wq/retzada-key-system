from pathlib import Path

root = Path('/tmp/ffh4x-key-system-inspect')
router = root / 'server/routers.ts'
text = router.read_text()
old = '''        const product = (await db.select({ id: products.id }).from(products).where(eq(products.id, input.productId)).limit(1))[0];
        if (!product) throw new TRPCError({ code: "NOT_FOUND", message: "Produto não encontrado." });
        await db.update(products).set({ stock: sql`${products.stock} + ${input.quantity}` }).where(eq(products.id, input.productId));
        await writeAudit(ctx.user.id, "add_stock", `${input.quantity} unidades adicionadas ao produto #${input.productId}`);
        return { success: true } as const;'''
new = '''        const product = (await db.select().from(products).where(eq(products.id, input.productId)).limit(1))[0];
        if (!product) throw new TRPCError({ code: "NOT_FOUND", message: "Produto não encontrado." });
        const generated = Array.from({ length: input.quantity }, () => ({
          code: createKey(product.category),
          productId: product.id,
          productName: product.name,
          durationDays: product.durationDays,
          status: "available" as const,
        }));
        await db.transaction(async tx => {
          await tx.insert(keys).values(generated);
          await tx.update(products).set({ stock: sql`${products.stock} + ${input.quantity}` }).where(eq(products.id, input.productId));
        });
        await writeAudit(ctx.user.id, "add_stock", `${input.quantity} unidades adicionadas ao produto #${input.productId}`);
        return { success: true, added: input.quantity } as const;'''
if old not in text:
    raise SystemExit('backend stock block not found')
router.write_text(text.replace(old, new, 1))

home = root / 'client/src/pages/Home.tsx'
text = home.read_text()
old = '''<input className="input-dark" type="number" min="1" value={durationDays} onChange={event => setDurationDays(event.target.value)} placeholder="Duração em dias" /><button className="btn-red mt-4 w-full" disabled={create.isPending || !name || !category} onClick={() => create.mutate({ name, category, durationDays: Number(durationDays) })}><Plus size={16} /> Adicionar produto</button></div><div className="surface rounded-2xl p-6"><div className="mb-5 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#43c47a]/10 text-[#43c47a]"><Database size={18} /></span><div><h2 className="font-bold text-white">Importar keys para estoque</h2>'''
new = '''<input className="input-dark" type="number" min="1" value={durationDays} onChange={event => setDurationDays(event.target.value)} placeholder="Duração em dias" /><button className="btn-red mt-4 w-full" disabled={create.isPending || !name || !category} onClick={() => create.mutate({ name, category, durationDays: Number(durationDays) })}><Plus size={16} /> Adicionar produto</button></div><div className="surface rounded-2xl p-6"><div className="mb-5 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#f6c55b]/10 text-[#f6c55b]"><Plus size={18} /></span><div><h2 className="font-bold text-white">Adicionar estoque</h2><p className="text-xs text-[#777780]">Cria keys disponíveis imediatamente para o produto.</p></div></div><select className="input-dark mb-3" value={stockProductId} onChange={event => setStockProductId(event.target.value)}><option value="">Selecione o produto</option>{query.data?.map(product => <option key={product.id} value={product.id}>{product.name} · atual: {product.stock}</option>)}</select><input className="input-dark" type="number" min="1" max="1000000" value={stockQuantity} onChange={event => setStockQuantity(event.target.value)} placeholder="Quantidade de keys" /><button className="btn-red mt-4 w-full" disabled={addStock.isPending || !stockProductId || Number(stockQuantity) < 1} onClick={() => addStock.mutate({ productId: Number(stockProductId), quantity: Number(stockQuantity) })}><Plus size={16} /> {addStock.isPending ? "Adicionando..." : "Adicionar estoque agora"}</button></div><div className="surface rounded-2xl p-6"><div className="mb-5 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#43c47a]/10 text-[#43c47a]"><Database size={18} /></span><div><h2 className="font-bold text-white">Importar keys para estoque</h2>'''
if old not in text:
    raise SystemExit('frontend stock insertion point not found')
home.write_text(text.replace(old, new, 1))
