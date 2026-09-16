from pathlib import Path

root = Path('/tmp/ffh4x-key-system-inspect')
p = root / 'client/src/pages/Home.tsx'
text = p.read_text()

anchor = 'function ClientGenerate() {'
helper = '''function platformLabel(category: string) {
  const normalized = category.trim().toLowerCase();
  if (normalized.includes("ios") || normalized.includes("iphone") || normalized.includes("apple")) return "iOS";
  if (normalized.includes("android")) return "Android";
  return category.trim() || "Outros";
}

function PlatformProductPicker({ products, productId, setProductId }: { products: any[]; productId: string; setProductId: (id: string) => void }) {
  const grouped = ["Android", "iOS"].map(platform => ({ platform, items: products.filter(product => platformLabel(product.category) === platform) })).filter(group => group.items.length);
  const others = products.filter(product => !["Android", "iOS"].includes(platformLabel(product.category)));
  if (others.length) grouped.push({ platform: "Outros", items: others });
  return <div className="space-y-4" aria-label="Escolha a plataforma e a duração">
    {grouped.length ? grouped.map(group => <section key={group.platform} className="rounded-2xl border border-white/[.07] bg-[#131316] p-4">
      <div className="mb-3 flex items-center justify-between"><h3 className="text-sm font-extrabold uppercase tracking-[.14em] text-white">{group.platform}</h3><span className="text-[10px] font-bold uppercase tracking-[.12em] text-[#777780]">Produtos disponíveis</span></div>
      <div className="grid gap-2 sm:grid-cols-3">{group.items.sort((a, b) => a.durationDays - b.durationDays).map(product => <button type="button" key={product.id} onClick={() => product.stock > 0 && setProductId(String(product.id))} disabled={product.stock <= 0} className={`flex items-center justify-between gap-3 rounded-xl border p-3 text-left transition ${productId === String(product.id) ? "border-[var(--accent)] bg-[var(--accent-soft)]" : "border-white/[.08] bg-[#1a1a20] hover:border-white/[.2]"} ${product.stock <= 0 ? "cursor-not-allowed opacity-45" : ""}`}><span><span className="block text-sm font-bold text-white">{product.name}</span><span className="mt-1 block text-xs text-[#a9a9b2]">{product.durationDays} {product.durationDays === 1 ? "dia" : "dias"}</span></span><span className={`shrink-0 rounded-full px-2 py-1 text-[10px] font-bold ${product.stock > 0 ? "bg-[#43c47a]/10 text-[#43c47a]" : "bg-[#ed1c2f]/10 text-[#ff4353]"}`}>{product.stock > 0 ? `${product.stock} disponíveis` : "Sem estoque"}</span></button>)}</div>
    </section>) : <div className="rounded-xl border border-dashed border-white/[.1] p-5 text-center text-sm text-[#777780]">Nenhum produto liberado no momento.</div>}
  </div>;
}

'''
if anchor not in text:
    raise SystemExit('anchor not found')
text = text.replace(anchor, helper + anchor, 1)
old = '<label className="mb-2 mt-7 block text-sm font-bold text-white" htmlFor="client-product">Categoria</label><select id="client-product" className="input-dark" value={productId} onChange={event => setProductId(event.target.value)}><option value="">Selecione uma categoria</option>{products.data?.map(product => <option key={product.id} value={product.id}>{product.name}</option>)}</select>'
new = '<div className="mb-2 mt-7 flex items-center justify-between"><label className="text-sm font-bold text-white">Plataforma e duração</label><span className="text-xs text-[#777780]">Android ou iOS</span></div><PlatformProductPicker products={products.data ?? []} productId={productId} setProductId={setProductId} />'
if old not in text:
    raise SystemExit('client selector not found')
text = text.replace(old, new, 1)
p.write_text(text)
