from pathlib import Path

root = Path('/tmp/ffh4x-key-system-inspect')
home_path = root / 'client/src/pages/Home.tsx'
index_path = root / 'client/index.html'
css_path = root / 'client/src/index.css'
home = home_path.read_text()
css = css_path.read_text()

old_brand = '''function Brand() {
  return <div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-[#ed1c2f] text-sm font-extrabold text-white shadow-[0_0_22px_rgba(237,28,47,.28)]">F4X</div><div><div className="text-sm font-extrabold tracking-[.22em] text-white">FFH4X</div><div className="mt-0.5 text-[9px] font-semibold tracking-[.2em] text-[#85858e]">KEY SYSTEM</div></div></div>;
}'''
new_brand = '''function Brand() {
  return <div className="brand-lockup flex items-center gap-3"><div className="brand-logo-wrap"><img className="brand-logo" src="/retzada-logo.jpg" alt="Logo RETZADA" /></div><div><div className="text-sm font-extrabold tracking-[.22em] text-white">RETZADA</div><div className="mt-0.5 text-[9px] font-semibold uppercase tracking-[.2em] text-[#85858e]">FORNECEDOR</div></div></div>;
}'''
if old_brand not in home:
    raise SystemExit('Função Brand não encontrada')
home = home.replace(old_brand, new_brand, 1)
home_path.write_text(home)

index = index_path.read_text()
index = index.replace('<title>FFH4X Key System</title>', '<title>RETZADA — Fornecedor</title>')
index_path.write_text(index)

css += '''

/* Identidade RETZADA */
.brand-logo-wrap { width: 40px; height: 40px; flex: 0 0 auto; overflow: hidden; border: 1px solid color-mix(in srgb, var(--accent) 45%, rgba(255,255,255,.12)); border-radius: 12px; background: #0b0b0e; box-shadow: 0 0 24px color-mix(in srgb, var(--accent) 22%, transparent); }
.brand-logo { display: block; width: 100%; height: 100%; object-fit: cover; object-position: center; }
@media (min-width: 640px) { .brand-logo-wrap { width: 42px; height: 42px; } }
'''
css_path.write_text(css)
print('Branding applied')
