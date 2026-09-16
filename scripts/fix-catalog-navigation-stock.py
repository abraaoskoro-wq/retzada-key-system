from pathlib import Path

root = Path('/tmp/ffh4x-key-system-inspect')
router = root / 'server/routers.ts'
text = router.read_text()
old = '    products: protectedProcedure.query(async () => (await getProducts()).filter(product => product.stock > 0)),'
new = '    products: protectedProcedure.query(() => getProducts()),'
if old not in text:
    raise SystemExit('member products filter not found')
router.write_text(text.replace(old, new, 1))

home = root / 'client/src/pages/Home.tsx'
text = home.read_text()
old = 'type Section = "overview" | "generate" | "keys" | "support" | "products" | "team" | "settings" | "resellers" | "inventory" | "mods" | "announcements" | "downloads" | "audit";'
new = 'type Section = "overview" | "generate" | "keys" | "support" | "clientOverview" | "clientGenerate" | "clientKeys" | "clientSupport" | "products" | "team" | "settings" | "resellers" | "inventory" | "mods" | "announcements" | "downloads" | "audit";'
if old not in text:
    raise SystemExit('section type not found')
text = text.replace(old, new, 1)
old = '''const navAdmin: { id: Section; label: string; icon: typeof KeyRound }[] = [
  { id: "overview", label: "Visão geral", icon: LayoutDashboard },'''
new = '''const navAdmin: { id: Section; label: string; icon: typeof KeyRound }[] = [
  { id: "clientOverview", label: "Cliente · Visão geral", icon: LayoutDashboard },
  { id: "clientGenerate", label: "Cliente · Gerar keys", icon: Sparkles },
  { id: "clientKeys", label: "Cliente · Minhas keys", icon: KeyRound },
  { id: "clientSupport", label: "Cliente · Suporte", icon: Headphones },
  { id: "overview", label: "Administração · Visão geral", icon: LayoutDashboard },'''
if old not in text:
    raise SystemExit('admin nav anchor not found')
text = text.replace(old, new, 1)
old = '  const [active, setActive] = useState<Section>("overview");'
new = '  const [active, setActive] = useState<Section>("generate");'
if old not in text:
    raise SystemExit('initial active not found')
text = text.replace(old, new, 1)
old = '''function AdminApp({ user, setActive, active }: { user: any; setActive: (section: Section) => void; active: Section }) { return <>{active === "overview" && <AdminOverview setActive={setActive} />}{active === "generate" && <AdminGenerate />}{active === "products" && <AdminProducts />}{active === "team" && <AdminTeam />}{active === "support" && <AdminTickets />}{active === "settings" && <Settings />}{active === "resellers" && <AdminResellers />}{active === "inventory" && <AdminProducts />}{active === "mods" && <AdminMods />}{active === "announcements" && <AdminAnnouncements />}{active === "downloads" && <AdminGenerate />}{active === "audit" && <AdminAudit />}</>; }'''
new = '''function AdminApp({ user, setActive, active }: { user: any; setActive: (section: Section) => void; active: Section }) { return <>{active === "clientOverview" && <ClientOverview setActive={setActive} />}{active === "clientGenerate" && <ClientGenerate />}{active === "clientKeys" && <ClientKeys />}{active === "clientSupport" && <ClientSupport />}{active === "overview" && <AdminOverview setActive={setActive} />}{active === "generate" && <AdminGenerate />}{active === "products" && <AdminProducts />}{active === "team" && <AdminTeam />}{active === "support" && <AdminTickets />}{active === "settings" && <Settings />}{active === "resellers" && <AdminResellers />}{active === "inventory" && <AdminProducts />}{active === "mods" && <AdminMods />}{active === "announcements" && <AdminAnnouncements />}{active === "downloads" && <AdminGenerate />}{active === "audit" && <AdminAudit />}</>; }'''
if old not in text:
    raise SystemExit('admin app mapping not found')
text = text.replace(old, new, 1)
old = '  const addStock = trpc.admin.addStock.useMutation({ onSuccess: () => { toast.success("Estoque atualizado."); setStockQuantity("10"); void utils.admin.products.invalidate(); void utils.admin.dashboard.invalidate(); }, onError: error => toast.error(error.message) });'
new = '  const addStock = trpc.admin.addStock.useMutation({ onSuccess: async data => { await Promise.all([utils.admin.products.invalidate(), utils.admin.dashboard.invalidate()]); toast.success(`${data.added} keys adicionadas imediatamente.`); setStockQuantity("10"); setStockProductId(""); }, onError: error => toast.error(error.message) });'
if old not in text:
    raise SystemExit('stock mutation not found')
text = text.replace(old, new, 1)
home.write_text(text)
