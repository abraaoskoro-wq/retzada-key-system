from pathlib import Path
import re

root = Path('/tmp/ffh4x-key-system-inspect')
router = root / 'server/routers.ts'
text = router.read_text()
old = '        if (!fresh.length) throw new TRPCError({ code: "CONFLICT", message: "Todas as keys coladas já estão no estoque." });'
new = '        if (!fresh.length) throw new TRPCError({ code: "CONFLICT", message: `A key ${codes[0]} já foi cadastrada. Cole uma key nova e exclusiva.` });'
if old not in text:
    raise SystemExit('duplicate message not found')
router.write_text(text.replace(old, new, 1))

home = root / 'client/src/pages/Home.tsx'
text = home.read_text()
text = text.replace('  const [stockProductId, setStockProductId] = useState(""); const [stockQuantity, setStockQuantity] = useState("10"); const [importContent, setImportContent] = useState("");', '  const [stockProductId, setStockProductId] = useState(""); const [importContent, setImportContent] = useState("");')
old = '  const addStock = trpc.admin.addStock.useMutation({ onSuccess: async data => { await Promise.all([utils.admin.products.invalidate(), utils.admin.dashboard.invalidate()]); toast.success(`${data.added} keys adicionadas imediatamente.`); setStockQuantity("10"); setStockProductId(""); }, onError: error => toast.error(error.message) });\n'
if old not in text:
    raise SystemExit('visual stock mutation not found')
text = text.replace(old, '', 1)
start = text.find('<div className="surface rounded-2xl p-6"><div className="mb-5 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#f6c55b]/10 text-[#f6c55b]"><Plus size={18} /></span><div><h2 className="font-bold text-white">Adicionar estoque</h2>')
if start < 0:
    raise SystemExit('visual stock card start not found')
end_marker = '<div className="surface rounded-2xl p-6"><div className="mb-5 flex items-center gap-3"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#43c47a]/10 text-[#43c47a]"><Database size={18} /></span>'
end = text.find(end_marker, start)
if end < 0:
    # Current markup does not have shrink-0 on this icon; use the actual marker.
    end_marker = '<div className="surface rounded-2xl p-6"><div className="mb-5 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#43c47a]/10 text-[#43c47a]"><Database size={18} /></span>'
    end = text.find(end_marker, start)
if end < 0:
    raise SystemExit('manual import card marker not found')
text = text[:start] + text[end:]
text = text.replace('const importKeys = trpc.admin.importKeys.useMutation({ onSuccess: data => { toast.success(`${data.imported} keys importadas.`); setImportContent(""); void utils.admin.products.invalidate(); void utils.admin.dashboard.invalidate(); }, onError: error => toast.error(error.message) });', 'const importKeys = trpc.admin.importKeys.useMutation({ onSuccess: async data => { await Promise.all([utils.admin.products.invalidate(), utils.admin.dashboard.invalidate()]); toast.success(`${data.imported} keys manuais adicionadas ao estoque.`); setImportContent(""); setStockProductId(""); }, onError: error => toast.error(error.message) });')
home.write_text(text)
