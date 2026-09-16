from pathlib import Path

root = Path('/tmp/ffh4x-key-system-inspect')
router = root / 'server/routers.ts'
text = router.read_text()
old = '''    products: protectedProcedure.query(async () => (await getProducts()).filter(product => product.stock > 0)),
    generatedKeys: protectedProcedure.query(async ({ ctx }) => {'''
new = '''    products: protectedProcedure.query(async () => (await getProducts()).filter(product => product.stock > 0)),
    announcements: protectedProcedure.query(async () => {
      const db = await getDb();
      return db ? db.select().from(announcements).orderBy(desc(announcements.createdAt)).limit(20) : [];
    }),
    generatedKeys: protectedProcedure.query(async ({ ctx }) => {'''
if old not in text:
    raise SystemExit('member route anchor not found')
router.write_text(text.replace(old, new, 1))

home = root / 'client/src/pages/Home.tsx'
text = home.read_text()
old = '''function ClientOverview({ setActive }: { setActive: (section: Section) => void }) {
  const dashboard = trpc.member.dashboard.useQuery();
  const stats = dashboard.data;'''
new = '''function ClientOverview({ setActive }: { setActive: (section: Section) => void }) {
  const dashboard = trpc.member.dashboard.useQuery();
  const announcements = trpc.member.announcements.useQuery();
  const stats = dashboard.data;'''
if old not in text:
    raise SystemExit('client overview anchor not found')
text = text.replace(old, new, 1)
old = '''<div className="mt-6 grid gap-5 lg:grid-cols-[1.25fr_.75fr]"><div className="surface rounded-2xl p-6">'''
new = '''{announcements.data?.length ? <div className="surface mb-6 overflow-hidden rounded-2xl"><div className="flex items-center gap-3 border-b border-white/[.06] p-5"><span className="grid h-9 w-9 place-items-center rounded-xl bg-[#f6c55b]/10 text-[#f6c55b]"><Megaphone size={17} /></span><div><p className="text-[10px] font-bold uppercase tracking-[.16em] text-[#f6c55b]">Comunicados</p><h2 className="mt-1 text-lg font-bold text-white">Avisos do fornecedor</h2></div></div><div className="divide-y divide-white/[.06]">{announcements.data.map(item => <article key={item.id} className="p-5"><h3 className="font-bold text-white">{item.title}</h3><p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-[#a9a9b2]">{item.message}</p><time className="mt-3 block text-[11px] text-[#777780]">{item.createdAt ? new Date(item.createdAt).toLocaleString("pt-BR") : "Agora"}</time></article>)}</div></div> : null}<div className="mt-6 grid gap-5 lg:grid-cols-[1.25fr_.75fr]"><div className="surface rounded-2xl p-6">'''
if old not in text:
    raise SystemExit('overview layout anchor not found')
text = text.replace(old, new, 1)
old = '''  const query = trpc.admin.products.useQuery();
  const [name, setName] = useState("");'''
new = '''  const query = trpc.admin.products.useQuery();
  const utils = trpc.useUtils();
  const [name, setName] = useState("");'''
if old not in text:
    raise SystemExit('products query anchor not found')
text = text.replace(old, new, 1)
old = '''  const addStock = trpc.admin.addStock.useMutation({ onSuccess: () => { toast.success("Estoque atualizado."); setStockQuantity("10"); query.refetch(); }, onError: error => toast.error(error.message) });
  const importKeys = trpc.admin.importKeys.useMutation({ onSuccess: data => { toast.success(`${data.imported} keys importadas.`); setImportContent(""); query.refetch(); }, onError: error => toast.error(error.message) });'''
new = '''  const addStock = trpc.admin.addStock.useMutation({ onSuccess: () => { toast.success("Estoque atualizado."); setStockQuantity("10"); void utils.admin.products.invalidate(); void utils.admin.dashboard.invalidate(); }, onError: error => toast.error(error.message) });
  const importKeys = trpc.admin.importKeys.useMutation({ onSuccess: data => { toast.success(`${data.imported} keys importadas.`); setImportContent(""); void utils.admin.products.invalidate(); void utils.admin.dashboard.invalidate(); }, onError: error => toast.error(error.message) });'''
if old not in text:
    raise SystemExit('stock mutation anchor not found')
text = text.replace(old, new, 1)
home.write_text(text)
