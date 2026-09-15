from pathlib import Path

root = Path('/tmp/ffh4x-key-system-inspect')
home_path = root / 'client/src/pages/Home.tsx'
css_path = root / 'client/src/index.css'
home = home_path.read_text()
css = css_path.read_text()

home = home.replace('import { useMemo, useState } from "react";', 'import { useEffect, useMemo, useState } from "react";')
color_block = r'''
const ACCENT_COLORS = [
  { id: "red", label: "Vermelho", value: "#ed1c2f", soft: "rgba(237,28,47,.15)" },
  { id: "blue", label: "Azul", value: "#3b82f6", soft: "rgba(59,130,246,.15)" },
  { id: "purple", label: "Roxo", value: "#8b5cf6", soft: "rgba(139,92,246,.15)" },
  { id: "cyan", label: "Ciano", value: "#06b6d4", soft: "rgba(6,182,212,.15)" },
  { id: "green", label: "Verde", value: "#22c55e", soft: "rgba(34,197,94,.15)" },
  { id: "amber", label: "Âmbar", value: "#f59e0b", soft: "rgba(245,158,11,.15)" },
  { id: "pink", label: "Rosa", value: "#ec4899", soft: "rgba(236,72,153,.15)" },
] as const;

function AccentPicker() {
  const [accent, setAccent] = useState(() => localStorage.getItem("ffh4x-accent") || "red");
  const selected = ACCENT_COLORS.find(color => color.id === accent) ?? ACCENT_COLORS[0];
  const apply = (id: string) => {
    const color = ACCENT_COLORS.find(item => item.id === id) ?? ACCENT_COLORS[0];
    setAccent(color.id);
    localStorage.setItem("ffh4x-accent", color.id);
    document.documentElement.dataset.accent = color.id;
  };
  return <div className="relative group">
    <button className="accent-trigger" title="Personalizar cor" aria-label="Personalizar cor" style={{ borderColor: selected.value, color: selected.value }}><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: selected.value }} /> <span className="hidden sm:inline">Cor</span></button>
    <div className="accent-menu">{ACCENT_COLORS.map(color => <button key={color.id} className="accent-option" onClick={() => apply(color.id)} aria-label={color.label}><span className="h-4 w-4 rounded-full" style={{ backgroundColor: color.value, boxShadow: accent === color.id ? "0 0 0 3px " + color.soft : undefined }} />{color.label}{accent === color.id && <Check size={14} className="ml-auto" />}</button>)}</div>
  </div>;
}
'''
home = home.replace('const OWNER_EMAIL = "abraaoskoro@gmail.com";\n', 'const OWNER_EMAIL = "abraaoskoro@gmail.com";\n' + color_block)
home = home.replace('  const [mobileOpen, setMobileOpen] = useState(false);', '  const [mobileOpen, setMobileOpen] = useState(false);\n  useEffect(() => { document.documentElement.dataset.accent = localStorage.getItem("ffh4x-accent") || "red"; }, []);', 1)
home = home.replace('<div className="ml-auto flex items-center gap-3"><span className="hidden items-center gap-2 text-xs text-[#777780] sm:flex">', '<div className="ml-auto flex items-center gap-3"><AccentPicker /><span className="hidden items-center gap-2 text-xs text-[#777780] sm:flex">', 1)
old = '<div className="hidden grid-cols-[1.2fr_1fr_.8fr_.7fr] gap-4 bg-[#131316] px-5 py-3 text-[10px] font-bold uppercase tracking-[.14em] text-[#777780] sm:grid"><span>Produto</span><span>Código da key</span><span>Data de criação</span><span className="text-right">Status</span></div>{query.data.map(item => <div key={item.id} className="grid gap-3 p-5 sm:grid-cols-[1.2fr_1fr_.8fr_.7fr] sm:items-center sm:gap-4"><div><p className="font-semibold text-white">{item.productName}</p><p className="mt-1 text-xs text-[#777780]">{item.durationDays} dias · {item.status === "redeemed" ? "Resgatada" : "Disponível"}</p></div><p className="break-all font-mono text-xs font-bold text-[#ff334b]">{item.code}</p><p className="text-xs text-[#a9a9b2]">{item.createdAt ? new Date(item.createdAt).toLocaleString("pt-BR") : "Agora"}</p><span className={`w-fit rounded-full px-3 py-1 text-xs font-bold sm:ml-auto ${item.status === "redeemed" ? "bg-[#43c47a]/10 text-[#43c47a]" : "bg-[#00b4d8]/10 text-[#50d7e5]"}`}>{item.status === "redeemed" ? "Resgatada" : "Disponível"}</span></div>)}'
new = '<div className="hidden grid-cols-[1.1fr_1fr_.8fr_.7fr_auto] gap-4 bg-[#131316] px-5 py-3 text-[10px] font-bold uppercase tracking-[.14em] text-[#777780] sm:grid"><span>Produto</span><span>Código da key</span><span>Data de criação</span><span className="text-right">Status</span><span /></div>{query.data.map(item => <div key={item.id} className="grid gap-3 p-5 sm:grid-cols-[1.1fr_1fr_.8fr_.7fr_auto] sm:items-center sm:gap-4"><div><p className="font-semibold text-white">{item.productName}</p><p className="mt-1 text-xs text-[#777780]">{item.durationDays} dias · {item.status === "redeemed" ? "Resgatada" : "Disponível"}</p></div><p className="break-all font-mono text-xs font-bold text-[#ff334b]">{item.code}</p><p className="text-xs text-[#a9a9b2]">{item.createdAt ? new Date(item.createdAt).toLocaleString("pt-BR") : "Agora"}</p><span className={`w-fit rounded-full px-3 py-1 text-xs font-bold sm:ml-auto ${item.status === "redeemed" ? "bg-[#43c47a]/10 text-[#43c47a]" : "bg-[#00b4d8]/10 text-[#50d7e5]"}`}>{item.status === "redeemed" ? "Resgatada" : "Disponível"}</span><button className="btn-copy" title="Copiar key" aria-label={`Copiar ${item.code}`} onClick={async () => { try { await navigator.clipboard.writeText(item.code); toast.success("Key copiada."); } catch { toast.error("Não foi possível copiar a key."); } }}><Copy size={14} /> <span className="hidden lg:inline">Copiar</span></button></div>)}'
if old not in home:
    raise SystemExit('Trecho de Minhas keys não encontrado')
home = home.replace(old, new, 1)
css += r'''

/* Personalização de cor e refinamento visual */
:root { --accent: #ed1c2f; --accent-hover: #ff263a; --accent-soft: rgba(237,28,47,.14); }
:root[data-accent="blue"] { --accent: #3b82f6; --accent-hover: #60a5fa; --accent-soft: rgba(59,130,246,.14); }
:root[data-accent="purple"] { --accent: #8b5cf6; --accent-hover: #a78bfa; --accent-soft: rgba(139,92,246,.14); }
:root[data-accent="cyan"] { --accent: #06b6d4; --accent-hover: #22d3ee; --accent-soft: rgba(6,182,212,.14); }
:root[data-accent="green"] { --accent: #22c55e; --accent-hover: #4ade80; --accent-soft: rgba(34,197,94,.14); }
:root[data-accent="amber"] { --accent: #f59e0b; --accent-hover: #fbbf24; --accent-soft: rgba(245,158,11,.14); }
:root[data-accent="pink"] { --accent: #ec4899; --accent-hover: #f472b6; --accent-soft: rgba(236,72,153,.14); }
body { background: radial-gradient(circle at 12% 0%, color-mix(in srgb, var(--accent) 8%, transparent), transparent 30rem), #0b0b0e; }
.btn-red { background: var(--accent); box-shadow: 0 10px 24px color-mix(in srgb, var(--accent) 20%, transparent); }
.btn-red:hover { background: var(--accent-hover); }
.input-dark:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
::selection { background: var(--accent); }
[class~="text-[#ed1c2f]"], [class~="text-[#ff4353]"], [class~="text-[#ff334b]"] { color: var(--accent) !important; }
[class~="bg-[#ed1c2f]"] { background-color: var(--accent) !important; }
[class~="bg-[#ed1c2f]/10"] { background-color: var(--accent-soft) !important; }
[class~="border-[#ed1c2f]"], [class~="border-l-2"] { border-color: var(--accent) !important; }
.surface { box-shadow: 0 22px 60px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.025); }
.btn-copy, .accent-trigger { display: inline-flex; align-items: center; justify-content: center; gap: .4rem; border: 1px solid color-mix(in srgb, var(--accent) 35%, rgba(255,255,255,.12)); border-radius: 10px; color: var(--accent); background: var(--accent-soft); padding: .5rem .65rem; font-size: .72rem; font-weight: 700; transition: transform .16s, background .16s, color .16s; }
.btn-copy:hover, .accent-trigger:hover { color: white; background: color-mix(in srgb, var(--accent) 25%, transparent); transform: translateY(-1px); }
.accent-menu { position: absolute; right: 0; top: calc(100% + .6rem); z-index: 40; display: none; width: 150px; border: 1px solid rgba(255,255,255,.1); border-radius: 14px; background: #17171c; padding: .4rem; box-shadow: 0 18px 40px rgba(0,0,0,.35); }
.group:hover .accent-menu, .group:focus-within .accent-menu { display: block; }
.accent-option { display: flex; width: 100%; align-items: center; gap: .6rem; border-radius: 9px; padding: .55rem .6rem; color: #c7c7ce; font-size: .75rem; font-weight: 600; text-align: left; }
.accent-option:hover { background: rgba(255,255,255,.07); color: white; }
'''
home_path.write_text(home)
css_path.write_text(css)
print('UI improvements applied')
