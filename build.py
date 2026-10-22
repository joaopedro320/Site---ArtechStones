#!/usr/bin/env python3
"""Gerador do site Artechstone (5 idiomas).
Uso:  python3 build.py            -> gera dist/ (producao, URLs limpas)
      python3 build.py --preview  -> gera preview/ (links relativos com index.html, para pre-visualizacao)
"""
import json, os, sys, shutil, html, datetime, urllib.parse, importlib

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from content.alts import ALT
from content.extra import X, WHO_IMG

PREVIEW = "--preview" in sys.argv
OUT = os.path.join(ROOT, "preview" if PREVIEW else "dist")
TODAY = datetime.date.today().isoformat()

# ---------------------------------------------------------------- dados fixos do cliente (briefing)
BASE = "https://artechstonebrasil.com.br"   # PENDENTE: confirmar dominio final
GTM_ID = "GTM-XXXXXXX"                      # PENDENTE: ID do GTM
SITE = {
  "name": "Artechstone",
  "legal": "Artechstone do Brasil",
  "cnpj": "26.427.026/0001-04",
  "phone": "+55 28 3028-2299", "phone_href": "+552830282299",
  "wa": "+55 28 3521-2416", "wa_num": "552835212416",
  "email": "contato@artechstonedobrasil.com.br",   # PENDENTE: briefing veio com e-mail quebrado, este e o do site atual
  "instagram": "https://www.instagram.com/artechstonebrasil/",
  "facebook": "https://www.facebook.com/artechstone",
  "qh4": "https://www.instagram.com/qh4growth/",   # PENDENTE: confirmar @ da QH4
  "hq": {"street":"Rua Joanna Payer, 66C", "district":"Boa Vista Aeroporto", "city":"Cachoeiro de Itapemirim", "region":"ES", "cep":"", "country":"BR"},
  "sp": {"street":"Rua Marcello Muller, 546", "district":"Jardim Independência", "city":"São Paulo", "region":"SP", "cep":"03223-060", "country":"BR"},
}
LANGS = ["pt", "en", "es", "zh", "ja"]
C = {k: importlib.import_module(f"content.{k}").L for k in LANGS}
def load_stones():
    folder = os.path.join(ROOT, "data", "stones")
    items = [json.load(open(os.path.join(folder, f), encoding="utf-8")) for f in os.listdir(folder) if f.endswith(".json")]
    return sorted(items, key=lambda x: (x.get("order", 9999), x["name"]))
STONES = load_stones()
STONE_PHOTOS = os.path.join(ROOT, "data", "stones", "fotos")

def process_stone_photos(out_dir):
    """Gera WebP 640/1200/2000 para fotos em data/stones/fotos/ (nome livre, informado em "image")."""
    if not any(s.get("image") for s in STONES): return
    try:
        from PIL import Image
    except ImportError:
        print("Pillow ausente: pip install pillow"); return
    for s in STONES:
        fn = s.get("image")
        if not fn: continue
        fn = os.path.basename(fn)  # o painel pode gravar com caminho
        src = os.path.join(STONE_PHOTOS, fn)
        if not os.path.exists(src):
            print(f"AVISO: foto {fn} da pedra {s['id']} nao encontrada em data/stones/fotos"); s["image"] = None; continue
        im = Image.open(src).convert("RGB"); w, h = im.size; sizes = []
        os.makedirs(os.path.join(out_dir, "assets", "img", "stones"), exist_ok=True)
        for tw in (640, 1200, 2000):
            if tw > w and sizes: break
            tw2 = min(tw, w); im.resize((tw2, round(h * tw2 / w)), Image.LANCZOS).save(os.path.join(out_dir, "assets", "img", "stones", f"{s['id']}-{tw}.webp"), "WEBP", quality=76, method=6)
            sizes.append(tw)
        key = f"stones/{s['id']}"
        IMG[key] = {"w": w, "h": h, "sizes": sizes, "c": "#%02x%02x%02x" % im.resize((1, 1)).getpixel((0, 0))}
        s["image"] = key
IMG = json.load(open(os.path.join(ROOT, "imgmeta.json")))
LINES = ["laminas", "quartzo", "nano", "natural"]
LINE_IMG = {"laminas": "ultracompact-slab-veining-detail", "quartzo": "stone-samples-table", "nano": "showroom-wide-view", "natural": "lounge-exotic-stone-slab"}
LINE_IMG2 = {"laminas": ["slab-consultation", "showroom-marble-look-slabs"], "quartzo": ["sculpted-sink-stone-surface", "stone-samples-hands"], "nano": ["showroom-mezzanine-slabs", "hand-on-slab-texture"], "natural": ["lounge-chair-stone-slab", "visitors-reviewing-slab"]}
LINE_FAQ = {"laminas": [1, 2], "quartzo": [3, 7, 5], "nano": [4, 6, 5], "natural": [8, 13]}
TESTI = [
  ("Venho registrar a minha satisfação em relação à empresa no geral.", "Ricardo", "Granmad", "São Paulo, SP"),
  ("Material de muita qualidade, sempre acompanhado de um atendimento especial.", "Ivanildo", "So Pedras", "Cabo Frio, RJ"),
  ("Eu, meus clientes e parceiros estamos trabalhando com os materiais da Artechstone há mais de um ano.", "Ulisses Miranda", "Monte Sinai", "Espírito Santo"),
  ("Artechstone do Brasil, empresa que tem um atendimento de excelência.", "Marmoraria Aliança", "", "Salvador, BA"),
  ("Estou feliz com a agilidade no orçamento, com as respostas, prazo de entrega.", "Rony", "SI Advisors", "São Paulo, SP"),
  ("O material é nota 11! O ArtechNano excepcional.", "Arley", "Gramapan", "Espírito Santo"),
]
GALLERY = ["showroom-ultracompact-slabs-aisle", "lounge-exotic-stone-slab", "sculpted-sink-stone-surface",
           "hand-on-slab-texture", "showroom-mezzanine-slabs", "stone-samples-table",
           "artechstone-gallery-entrance", "reading-artechstone-catalogue", "showroom-slabs-portrait",
           "stone-samples-hands", "architects-event-gallery"]
APPS_T = {"pt":"Aplicações","en":"Applications","es":"Aplicaciones","zh":"应用","ja":"用途"}
PAGE_KEYS = ["home", "stones"] + LINES + ["about", "warranty", "downloads", "faq", "contact", "thanks"]
NOINDEX = {"thanks"}

esc = lambda s: html.escape(str(s), quote=True)

# ---------------------------------------------------------------- caminhos
def slug(lang, key):
    return C[lang]["slugs"][key]

def path_of(lang, key):
    s = slug(lang, key)
    return "/" + (s + "/" if s else "")

def abs_url(lang, key):
    return BASE + path_of(lang, key)

class Ctx:
    def __init__(self, lang, key):
        self.lang, self.key = lang, key
        self.L = C[lang]; self.ui = C[lang]["ui"]
        self.dir = slug(lang, key)
    def rel(self, target_path):
        """target_path: caminho absoluto do site ('/en/stones/' ou '/assets/x.css')"""
        if not PREVIEW:
            return target_path
        here = "/" + (self.dir + "/" if self.dir else "")
        t = target_path
        is_dir = t.endswith("/")
        r = os.path.relpath(t if not is_dir else t.rstrip("/") or "/", here.rstrip("/") or "/")
        if is_dir:
            r = (r + "/index.html") if r != "." else "index.html"
        return r
    def href(self, key, lang=None):
        return self.rel(path_of(lang or self.lang, key))
    def asset(self, p):
        return self.rel("/assets/" + p)

# ---------------------------------------------------------------- imagens
def img(ctx, name, sizes="100vw", cls="", eager=False, alt=None, priority=False):
    m = IMG[name]; w, h = m["w"], m["h"]
    srcset = ", ".join(f'{ctx.asset(f"img/{name}-{s}.webp")} {s}w' for s in m["sizes"])
    src = ctx.asset(f"img/{name}-{m['sizes'][-2] if len(m['sizes'])>1 else m['sizes'][0]}.webp")
    a = alt if alt is not None else ALT[name][ctx.lang]
    load = 'loading="eager"' if eager else 'loading="lazy" decoding="async"'
    fp = ' fetchpriority="high"' if priority else ""
    style = f' style="background-color:{m["c"]}"'
    return f'<img class="{cls}" src="{src}" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" alt="{esc(a)}" {load}{fp}{style}>'

def img_url(name, size=1200):
    m = IMG[name]; s = size if size in m["sizes"] else m["sizes"][-1]
    return f"{BASE}/assets/img/{name}-{s}.webp"

ONE = {"pt":"1 pedra","en":"1 stone","es":"1 piedra","zh":"1 款石材","ja":"1 種類"}
def count_txt(ctx, n):
    return ONE[ctx.lang] if n == 1 else ctx.ui["stones_count"].format(n=n)

# ---------------------------------------------------------------- whatsapp
def wa(text):
    return f"https://wa.me/{SITE['wa_num']}?text=" + urllib.parse.quote(text)

def addr_line(a, with_country=False):
    parts = [a["street"], a["district"], f'{a["city"]}/{a["region"]}']
    if a["cep"]: parts.append("CEP " + a["cep"])
    return ", ".join(parts)

def maps_link(a):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(addr_line(a) + ", Brasil")

def maps_embed(a):
    return "https://maps.google.com/maps?q=" + urllib.parse.quote(addr_line(a) + ", Brasil") + "&output=embed"

# ---------------------------------------------------------------- JSON-LD
def org_ld(lang):
    L = C[lang]
    return {
      "@type": "Organization", "@id": BASE + "/#org",
      "name": SITE["name"], "alternateName": [SITE["legal"], "Artechstone Brasil"],
      "url": BASE + "/", "logo": BASE + "/assets/img/logo.png",
      "image": img_url("artechstone-gallery-sao-paulo-facade", 2000),
      "description": L["ui"]["footer_about"],
      "foundingDate": "2016-10",
      "founder": [{"@type": "Person", "name": "Fabiane Braga"}, {"@type": "Person", "name": "Colin B. Thomas"}],
      "taxID": SITE["cnpj"], "email": SITE["email"], "telephone": SITE["phone"],
      "address": postal(SITE["hq"]),
      "areaServed": {"@type": "Country", "name": "Brasil"},
      "sameAs": [SITE["instagram"], SITE["facebook"]],
      "contactPoint": [{"@type": "ContactPoint", "contactType": "sales", "telephone": SITE["wa"], "areaServed": "BR", "availableLanguage": ["pt-BR", "en"]}],
      "knowsAbout": ["Sintered ultra-compact slabs", "Engineered quartz", "Crystallised glass stone", "Granite", "Marble", "Quartzite", "Stone import"],
      "brand": [{"@type": "Brand", "name": n} for n in ["ArtechLâminas", "ArtechQuartzo", "ArtechNano"]],
      "subOrganization": [{"@id": BASE + "/#hq"}, {"@id": BASE + "/#gallery-sp"}],
    }

def postal(a):
    d = {"@type": "PostalAddress", "streetAddress": a["street"] + ", " + a["district"], "addressLocality": a["city"], "addressRegion": a["region"], "addressCountry": "BR"}
    if a["cep"]: d["postalCode"] = a["cep"]
    return d

def locs_ld(lang):
    L = C[lang]
    out = []
    for lid, key, label, im in (("hq", "hq", L["ui"]["hq"], "showroom-wide-view"), ("gallery-sp", "sp", L["ui"]["sp"], "artechstone-gallery-sao-paulo-facade")):
        out.append({"@type": "HomeAndConstructionBusiness", "@id": f"{BASE}/#{lid}",
                    "name": f"Artechstone, {SITE[key]['city']}", "description": label,
                    "address": postal(SITE[key]), "telephone": SITE["phone"], "email": SITE["email"],
                    "image": img_url(im), "url": abs_url(lang, "contact"), "hasMap": maps_link(SITE[key]),
                    "parentOrganization": {"@id": BASE + "/#org"}, "areaServed": "BR"})
    return out

def website_ld():
    return {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": SITE["name"],
            "inLanguage": [C[l]["lang"] for l in LANGS], "publisher": {"@id": BASE + "/#org"},
            "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": BASE + "/pedras/?q={search_term_string}"}, "query-input": "required name=search_term_string"}}

def crumbs(ctx, trail):
    """trail: lista de (nome, key)"""
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(ctx.lang, k)} for i, (n, k) in enumerate(trail)]
    return {"@type": "BreadcrumbList", "@id": abs_url(ctx.lang, ctx.key) + "#breadcrumb", "itemListElement": items}

def faq_ld(pairs, url):
    return {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}

def page_ld(ctx, ptype, title, desc, image, extra=None, has_crumbs=True):
    url = abs_url(ctx.lang, ctx.key)
    wp = {"@type": ptype, "@id": url + "#webpage", "url": url, "name": title, "description": desc,
          "inLanguage": ctx.L["lang"], "isPartOf": {"@id": BASE + "/#website"}, "about": {"@id": BASE + "/#org"},
          "publisher": {"@id": BASE + "/#org"}, "dateModified": TODAY,
          "primaryImageOfPage": {"@type": "ImageObject", "url": img_url(image, 2000)}}
    if has_crumbs: wp["breadcrumb"] = {"@id": url + "#breadcrumb"}
    graph = [org_ld(ctx.lang), website_ld(), wp] + locs_ld(ctx.lang) if ctx.key == "home" or ctx.key == "contact" else [org_ld(ctx.lang), website_ld(), wp]
    if extra: graph += extra
    return {"@context": "https://schema.org", "@graph": graph}

# ---------------------------------------------------------------- partes comuns
FONTS = {
 "base": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@300;400;500&display=swap",
 "zh": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@300;400;500&family=Noto+Sans+SC:wght@300;400;500&display=swap",
 "ja": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@300;400;500&family=Noto+Sans+JP:wght@300;400;500&display=swap",
}

def head(ctx, title, desc, image, ld, preload=None, noindex=False):
    L = ctx.L
    alts = ""
    if ctx.key not in NOINDEX:
        for l in LANGS:
            alts += f'<link rel="alternate" hreflang="{C[l]["lang"]}" href="{abs_url(l, ctx.key)}">\n'
        alts += f'<link rel="alternate" hreflang="x-default" href="{abs_url("pt", ctx.key)}">\n'
    oglocs = "".join(f'<meta property="og:locale:alternate" content="{C[l]["ogLocale"]}">\n' for l in LANGS if l != ctx.lang)
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    pre = ""
    if preload:
        m = IMG[preload["name"]]
        pn = preload["name"]
        ss = ", ".join(f'{ctx.asset(f"img/{pn}-{s}.webp")} {s}w' for s in m["sizes"])
        media = f' media="{preload["media"]}"' if preload.get("media") else ""
        pre = f'<link rel="preload" as="image" type="image/webp" imagesrcset="{ss}" imagesizes="{preload.get("sizes","100vw")}"{media} fetchpriority="high">\n'
        if preload.get("alt"):
            m2 = IMG[preload["alt"]]
            pa = preload["alt"]
            ss2 = ", ".join(f'{ctx.asset(f"img/{pa}-{s}.webp")} {s}w' for s in m2["sizes"])
            pre += f'<link rel="preload" as="image" type="image/webp" imagesrcset="{ss2}" imagesizes="100vw" media="(max-width: 760px)" fetchpriority="high">\n'
    font = FONTS.get(ctx.lang, FONTS["base"])
    gtm = "" if GTM_ID.startswith("GTM-XXXX") else f"""<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{GTM_ID}');</script>"""
    return f"""<!doctype html>
<html lang="{L['lang']}" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{abs_url(ctx.lang, ctx.key)}">
{alts}<meta name="author" content="Artechstone">
<meta name="geo.region" content="BR-ES">
<meta name="geo.placename" content="Cachoeiro de Itapemirim; São Paulo">
<meta name="format-detection" content="telephone=no">
<meta name="theme-color" content="#2f2c2c">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Artechstone">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{abs_url(ctx.lang, ctx.key)}">
<meta property="og:image" content="{BASE}/assets/img/og-artechstone.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(ALT['artechstone-gallery-sao-paulo-facade'][ctx.lang])}">
<meta property="og:locale" content="{L['ogLocale']}">
{oglocs}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}/assets/img/og-artechstone.jpg">
<link rel="icon" href="{ctx.asset('img/favicon.svg')}" type="image/svg+xml">
<link rel="icon" href="{ctx.asset('img/favicon-32.png')}" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{ctx.asset('img/apple-touch-icon.png')}">
<link rel="manifest" href="{ctx.rel('/site.webmanifest')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{pre}<link rel="stylesheet" href="{font}">
<link rel="stylesheet" href="{ctx.asset('css/site.css')}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(',', ':'))}</script>
{gtm}
<script>document.documentElement.classList.add("js");setTimeout(function(){{if(!window.__motion)document.documentElement.classList.remove("js")}},3500);</script>
</head>
<body class="page-{ctx.key} lang-{ctx.lang}">
<a class="skip" href="#main">{esc(ctx.ui['skip'])}</a>
"""

def lang_switch(ctx, cls=""):
    items = ""
    for l in LANGS:
        cur = ' aria-current="true"' if l == ctx.lang else ""
        items += f'<li><a href="{ctx.href(ctx.key, l)}" hreflang="{C[l]["lang"]}" lang="{C[l]["lang"]}"{cur} data-lang="{l}">{esc(C[l]["langName"])}</a></li>'
    return f"""<details class="lang {cls}"><summary aria-label="{esc(ctx.ui['language'])}: {esc(ctx.L['langName'])}"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/></svg><span>{esc(ctx.L['short'])}</span></summary><ul>{items}</ul></details>"""

def header(ctx, transparent=False):
    ui = ctx.ui
    cur = lambda k: ' aria-current="page"' if (ctx.key == k or (k == "stones" and ctx.key in LINES)) else ""
    nav = "".join(f'<li><a href="{ctx.href(k)}"{cur(k)}>{esc(ui["nav"][k])}</a></li>' for k in ["stones", "about", "warranty", "downloads", "faq", "contact"])
    return f"""<header class="site-header{' is-over' if transparent else ''}" data-header>
<div class="wrap header-in">
<a class="brand" href="{ctx.href('home')}" aria-label="Artechstone, {esc(ui['home'])}"><img src="{ctx.asset('img/logo.svg')}" alt="Artechstone" width="189" height="26" class="logo-dark"><img src="{ctx.asset('img/logo-light.svg')}" alt="" width="189" height="26" class="logo-light" aria-hidden="true"></a>
<nav class="nav" aria-label="{esc(ui['menu'])}" id="site-nav"><ul>{nav}</ul>
<div class="nav-extra">{lang_switch(ctx, 'lang-mobile')}<a class="btn btn-solid" href="{wa(ui['wa_default'])}" target="_blank" rel="noopener" data-track="whatsapp_click" data-place="menu">{esc(ui['cta_whatsapp'])}</a></div></nav>
<div class="header-actions">{lang_switch(ctx)}<a class="btn btn-solid btn-sm hide-sm" href="{ctx.href('contact')}">{esc(ui['cta_quote'])}</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" data-menu><span class="sr">{esc(ui['menu'])}</span><i></i><i></i></button></div>
</div></header>
"""

def footer(ctx):
    ui, L = ctx.ui, ctx.L
    navs = "".join(f'<li><a href="{ctx.href(k)}">{esc(ui["nav"][k])}</a></li>' for k in ["stones", "about", "warranty", "downloads", "faq", "contact"])
    lines = "".join(f'<li><a href="{ctx.href(k)}">{esc(L["lines"][k]["name"])}</a></li>' for k in LINES)
    langs = " ".join(f'<a href="{ctx.href(ctx.key if ctx.key not in NOINDEX else "home", l)}" hreflang="{C[l]["lang"]}" lang="{C[l]["lang"]}">{esc(C[l]["langName"])}</a>' for l in LANGS)
    year = datetime.date.today().year
    return f"""<footer class="site-footer">
<div class="wrap">
<div class="foot-top">
<div class="foot-brand"><img src="{ctx.asset('img/logo-light.svg')}" alt="Artechstone" width="218" height="30" loading="lazy"><p>{esc(ui['footer_about'])}</p>
<p class="foot-langs">{langs}</p></div>
<nav class="foot-col" aria-label="{esc(ui['footer_nav'])}"><h2>{esc(ui['footer_nav'])}</h2><ul>{navs}</ul></nav>
<nav class="foot-col" aria-label="{esc(ui['footer_lines'])}"><h2>{esc(ui['footer_lines'])}</h2><ul>{lines}</ul></nav>
<div class="foot-col"><h2>{esc(ui['footer_contact'])}</h2>
<ul class="foot-contact"><li><a href="{wa(ui['wa_default'])}" target="_blank" rel="noopener" data-track="whatsapp_click" data-place="footer">{esc(ui['whatsapp'])} {SITE['wa']}</a></li><li><a href="tel:{SITE['phone_href']}">{esc(ui['phone'])} {SITE['phone']}</a></li><li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li></ul>
<address><strong>{esc(ui['hq'])}</strong><br>{esc(addr_line(SITE['hq']))}</address>
<address><strong>{esc(ui['sp'])}</strong><br>{esc(addr_line(SITE['sp']))}</address>
<p class="foot-social"><a href="{SITE['instagram']}" target="_blank" rel="noopener">Instagram</a> <a href="{SITE['facebook']}" target="_blank" rel="noopener">Facebook</a></p>
</div></div>
<div class="foot-bottom"><p>© {year} {SITE['legal']} · CNPJ {SITE['cnpj']}. {esc(ui['rights'])}</p><p><a href="{SITE['qh4']}" target="_blank" rel="noopener">{esc(ui['dev_by'])}</a></p></div>
</div></footer>
<a class="wa-float" href="{wa(ui['wa_default'])}" target="_blank" rel="noopener" aria-label="{esc(ui['wa_float'])}" data-track="whatsapp_click" data-place="float"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.7c-2 0-4-.6-5.7-1.6l-.4-.2-3.9 1 1-3.8-.3-.4A10.7 10.7 0 1 1 16 26.7zm5.9-8c-.3-.2-1.9-1-2.2-1-.3-.1-.5-.2-.7.1l-1 1.3c-.2.2-.4.2-.7.1a8.8 8.8 0 0 1-4.4-3.8c-.3-.6.3-.5 1-1.7.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.2 1.4 3.5c.2.2 2.4 3.6 5.8 5 2.1.9 3 1 4 .8.7-.1 1.9-.8 2.2-1.5.3-.8.3-1.4.2-1.5l-.7-.4z"/></svg></a>
"""

def i18n_script(ctx):
    ui = ctx.ui
    data = {"lang": ctx.lang, "wa": SITE["wa_num"], "form": ui["form"], "gallery": [ui["gallery_prev"], ui["gallery_next"], ui["close"]],
            "results": ui["results"], "thanks": ctx.href("thanks"), "waDefault": ui["wa_default"],
            "cursor": {"view": X[ctx.lang]["cursor_view"], "zoom": X[ctx.lang]["cursor_zoom"], "drag": X[ctx.lang]["cursor_drag"]}, "loading": X[ctx.lang]["loading"], "mark": ctx.asset("img/mark-light.svg"), "logo": ctx.asset("img/logo-light.svg"),
            "suggest": {l: {"text": C[l]["ui"]["lang_suggest"], "btn": C[l]["ui"]["lang_suggest_btn"], "dismiss": C[l]["ui"]["dismiss"], "url": ctx.href(ctx.key if ctx.key not in NOINDEX else "home", l)} for l in LANGS}}
    vend = "".join(f'<script src="{ctx.asset("js/vendor/" + v)}" defer></script>' for v in ["gsap.min.js", "ScrollTrigger.min.js", "SplitText.min.js", "lenis.min.js"])
    return f'<script id="i18n" type="application/json">{json.dumps(data, ensure_ascii=False)}</script>\n{vend}\n<script src="{ctx.asset("js/site.js")}" defer></script>\n</body>\n</html>\n'

def breadcrumb_html(ctx, trail):
    lis = ""
    for i, (n, k) in enumerate(trail):
        if i == len(trail) - 1:
            lis += f'<li aria-current="page">{esc(n)}</li>'
        else:
            lis += f'<li><a href="{ctx.href(k)}">{esc(n)}</a></li>'
    return f'<nav class="crumbs" aria-label="{esc(ctx.ui["breadcrumb"])}"><ol>{lis}</ol></nav>'

def btn_wa(ctx, text=None, cls="btn btn-solid", place="body", msg=None):
    return f'<a class="{cls}" href="{wa(msg or ctx.ui["wa_default"])}" target="_blank" rel="noopener" data-track="whatsapp_click" data-place="{place}">{esc(text or ctx.ui["cta_whatsapp"])}</a>'

def faq_list(pairs, open_first=False):
    out = ""
    for i, (q, a) in enumerate(pairs):
        out += f'<details class="qa"{" open" if (open_first and i == 0) else ""}><summary><h3>{esc(q)}</h3><span class="qa-icon" aria-hidden="true"></span></summary><div class="qa-a"><p>{esc(a)}</p></div></details>'
    return f'<div class="qa-list">{out}</div>'

def stone_card(ctx, s):
    L, ui = ctx.L, ctx.ui
    line = L["lines"][s["line"]]["name"]
    kind = ui.get(s.get("type", ""), "") if s.get("type") else L["lines"][s["line"]]["kind"]
    msg = ui["wa_stone"].format(name=s["name"], line=line)
    media = img(ctx, s["image"], "(max-width:640px) 50vw, 25vw", "card-img", alt=f'{s["name"]}, {line}') if s.get("image") else f'<div class="swatch" aria-hidden="true"><span>{esc(line)}</span><b>{esc(s["name"])}</b></div>'
    so = f'<span class="badge">{esc(ui["sold_out"])}</span>' if s.get("soldOut") else ""
    fin = f'<p class="stone-fin">{esc(", ".join(s["finishes"]))}</p>' if s.get("finishes") else ""
    note = "" if s.get("image") else f'<p class="stone-note">{esc(ui["photo_soon"])}</p>'
    return f"""<article class="stone{' is-sold' if s.get('soldOut') else ''}" id="{s['id']}" data-line="{s['line']}" data-name="{esc(s['name'].lower())}">
<div class="stone-media">{media}{so}</div>
<div class="stone-body"><p class="stone-line">{esc(kind)}</p><h3>{esc(s['name'])}</h3>{fin}{note}
<a class="link-arrow" href="{wa(msg)}" target="_blank" rel="noopener" data-track="stone_inquiry" data-place="{s['id']}">{esc(ui['ask_stone'])}</a></div>
</article>"""

def stones_ld(ctx, stones):
    L = ctx.L
    items = []
    for i, s in enumerate(stones):
        p = {"@type": "Product", "name": f"{s['name']} {L['lines'][s['line']]['name'] if s['line'] != 'natural' else ''}".strip(),
             "brand": {"@type": "Brand", "name": "Artechstone"}, "category": L["lines"][s["line"]]["kind"],
             "url": abs_url(ctx.lang, s["line"]) + "#" + s["id"]}
        if s.get("image"): p["image"] = img_url(s["image"])
        items.append({"@type": "ListItem", "position": i + 1, "item": p})
    return {"@type": "ItemList", "@id": abs_url(ctx.lang, ctx.key) + "#stones", "numberOfItems": len(stones), "itemListElement": items}

def section_final(ctx):
    h = ctx.L["pages"]["home"]
    return f"""<section class="final">
<div class="final-media"><div class="pin-in" data-speed="-0.2">{img(ctx, 'showroom-mezzanine-slabs', '100vw', 'cover')}</div></div>
<div class="wrap final-in"><h2 data-split>{esc(h['final_title'])}</h2><p data-fade>{esc(h['final_text'])}</p>
<div class="btns">{btn_wa(ctx, cls='btn btn-light', place='final')}<a class="btn btn-ghost-light" href="{ctx.href('contact')}">{esc(ctx.ui['cta_quote'])}</a></div></div>
</section>"""

def places(ctx, title=None):
    ui = ctx.ui
    t = f'<h2 class="h2" data-split>{esc(title)}</h2>' if title else ""
    return f"""<section class="places wrap">{t}
<div class="places-grid">
<article class="place"><div class="place-media" data-reveal><div class="pin-in" data-speed="-0.1">{img(ctx, 'artechstone-gallery-facade-night', '(max-width:760px) 100vw, 50vw', 'cover')}</div></div>
<h3>{esc(ui['sp'])}</h3><address>{esc(addr_line(SITE['sp']))}</address><a class="link-arrow" href="{maps_link(SITE['sp'])}" target="_blank" rel="noopener">{esc(ui['map'])}</a></article>
<article class="place"><div class="place-media" data-reveal><div class="pin-in" data-speed="-0.1">{img(ctx, 'showroom-ultracompact-slabs-aisle', '(max-width:760px) 100vw, 50vw', 'cover')}</div></div>
<h3>{esc(ui['hq'])}</h3><address>{esc(addr_line(SITE['hq']))}</address><a class="link-arrow" href="{maps_link(SITE['hq'])}" target="_blank" rel="noopener">{esc(ui['map'])}</a></article>
</div></section>"""

# ---------------------------------------------------------------- formularios
def form_html(ctx, kind):
    f = ctx.ui["form"]; L = ctx.L
    opts = "".join(f"<option>{esc(p)}</option>" for p in f["profiles"])
    lines = "".join(f"<option>{esc(L['lines'][k]['name'])}</option>" for k in LINES) + f"<option>{esc(f['interest_any'])}</option>"
    common = f"""<div class="field"><label for="f-name-{kind}">{esc(f['name'])} *</label><input id="f-name-{kind}" name="{esc(f['name'])}" autocomplete="name" required minlength="2"></div>
<div class="field"><label for="f-phone-{kind}">{esc(f['phone'])} *</label><input id="f-phone-{kind}" name="{esc(f['phone'])}" type="tel" autocomplete="tel" required minlength="8" inputmode="tel"></div>
<div class="field"><label for="f-email-{kind}">{esc(f['email'])} *</label><input id="f-email-{kind}" name="{esc(f['email'])}" type="email" autocomplete="email" required></div>
<div class="field"><label for="f-prof-{kind}">{esc(f['profile'])} *</label><select id="f-prof-{kind}" name="{esc(f['profile'])}" required><option value="">{esc(f['profile_ph'])}</option>{opts}</select></div>"""
    if kind == "contact":
        extra = f"""<div class="field"><label for="f-comp-{kind}">{esc(f['company'])}</label><input id="f-comp-{kind}" name="{esc(f['company'])}" autocomplete="organization"></div>
<div class="field"><label for="f-city-{kind}">{esc(f['city'])} *</label><input id="f-city-{kind}" name="{esc(f['city'])}" autocomplete="address-level2" required></div>
<div class="field"><label for="f-int-{kind}">{esc(f['interest'])}</label><select id="f-int-{kind}" name="{esc(f['interest'])}"><option value="">{esc(f['profile_ph'])}</option>{lines}</select></div>
<div class="field field-full"><label for="f-msg-{kind}">{esc(f['message'])}</label><textarea id="f-msg-{kind}" name="{esc(f['message'])}" rows="4" placeholder="{esc(f['message_ph'])}"></textarea></div>"""
        intro, submit = f["wa_intro_contact"], f["submit_contact"]
    else:
        extra = f"""<div class="field"><label for="f-comp-{kind}">{esc(f['company'])}</label><input id="f-comp-{kind}" name="{esc(f['company'])}" autocomplete="organization"></div>"""
        intro, submit = f["wa_intro_catalogue"], f["submit_catalogue"]
    return f"""<form class="lead-form" data-form="{kind}" data-intro="{esc(intro)}" novalidate>
<div class="fields">{common}{extra}</div>
<p class="form-hint">{esc(f['hint'])} <span>* {esc(f['required'])}</span></p>
<button class="btn btn-solid btn-block" type="submit" disabled>{esc(submit)}</button>
</form>"""

# ---------------------------------------------------------------- paginas
def pg_home(ctx):
    L, ui = ctx.L, ctx.ui; h = L["pages"]["home"]; x = X[ctx.lang]
    trail = [(ui["home"], "home")]
    faqs = [L["faq"][i] for i in L["home_faq"]]
    ld = page_ld(ctx, "WebPage", h["title"], h["desc"], "artechstone-gallery-sao-paulo-facade", [crumbs(ctx, trail)], has_crumbs=True)
    out = head(ctx, h["title"], h["desc"], "artechstone-gallery-sao-paulo-facade", ld,
               preload={"name": "artechstone-gallery-sao-paulo-facade", "media": "(min-width: 761px)", "alt": "artechstone-gallery-entrance"})
    out += header(ctx, transparent=True)
    facts = "".join(f"<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>" for a, b in h["facts"])
    counters = "".join(f'<li><span class="num" data-count="{esc(n)}">{esc(n)}</span><span class="num-l">{esc(l)}</span></li>' for n, l in x["counters"])
    # linhas no estilo das refs: rotulo grande + seta, imagem deslocada alternando lados
    lines = ""
    for i, k in enumerate(LINES):
        ln = L["lines"][k]; n = sum(1 for s in STONES if s["line"] == k)
        side = "l" if i % 2 == 0 else "r"
        lines += f"""<li class="ln ln-{side}"><a href="{ctx.href(k)}" class="ln-a" data-cursor="{esc(x['cursor_view'])}">
<div class="ln-media" data-reveal><div class="pin-in" data-speed="-0.12">{img(ctx, LINE_IMG[k], '(max-width:760px) 100vw, 60vw', 'cover')}</div></div>
<div class="ln-text"><span class="ln-arrow" aria-hidden="true"><svg viewBox="0 0 40 40"><path d="M10 30L30 10M14 10h16v16"/></svg></span>
<h3 class="ln-name" data-split>{esc(ln['name'])}</h3><p class="ln-kind">{esc(ln['kind'])}</p><p class="ln-short">{esc(ln['short'])}</p><p class="ln-count">{esc(count_txt(ctx, n))}</p></div>
</a></li>"""
    gal = ""
    for i, g in enumerate(GALLERY):
        big = ctx.asset(f"img/{g}-{IMG[g]['sizes'][-1]}.webp")
        orient = "p" if IMG[g]["h"] > IMG[g]["w"] else "w"
        gal += f'<li class="hg-{orient}"><button type="button" class="g-item" data-full="{big}" data-alt="{esc(ALT[g][ctx.lang])}" aria-label="{esc(ui["gallery_open"])}: {esc(ALT[g][ctx.lang])}" data-cursor="{esc(x["cursor_zoom"])}"><span class="g-in">{img(ctx, g, "(max-width:760px) 80vw, 40vw")}</span></button></li>'
    who = "".join(f'<li data-who="{i}"><h3>{esc(a)}</h3><p>{esc(b)}</p></li>' for i, (a, b) in enumerate(h["who"]))
    who_imgs = "".join(f'<div class="who-img{" on" if i == 0 else ""}" data-who-img="{i}">{img(ctx, w, "(max-width:760px) 100vw, 40vw", "cover")}</div>' for i, w in enumerate(WHO_IMG))
    tl = ""
    for i, (q, a, c, p) in enumerate(TESTI):
        quote = esc(q) if ctx.lang == "pt" else esc(L["testimonials"][i])
        note = "" if ctx.lang == "pt" else f'<span class="t-note" title="{esc(q)}">{esc(ui["translated"])}</span>'
        who_l = ", ".join(z for z in [c, p] if z)
        tl += f'<figure class="tq{" on" if i == 0 else ""}" data-tq="{i}"><blockquote><p>{quote}</p></blockquote><figcaption><strong>{esc(a)}</strong><span>{esc(who_l)}</span>{note}</figcaption></figure>'
    dots = "".join(f'<button type="button" class="tdot{" on" if i == 0 else ""}" data-tdot="{i}" aria-label="{i+1}/{len(TESTI)}"></button>' for i in range(len(TESTI)))
    markets = "".join(f"<span>{esc(m)}</span>" for m in L["pages"]["about"]["markets"])
    out += f"""<main id="main">
<section class="hero" data-hero>
<div class="hero-frame" data-hero-frame>
<picture class="hero-media">
<source media="(max-width: 760px)" srcset="{', '.join(f'{ctx.asset(f"img/artechstone-gallery-entrance-{s}.webp")} {s}w' for s in IMG['artechstone-gallery-entrance']['sizes'])}" sizes="100vw">
{img(ctx, 'artechstone-gallery-sao-paulo-facade', '100vw', 'cover', eager=True, priority=True)}
</picture></div>
<h1 class="hero-h1"><span class="hero-a" data-hero-a>{esc(x['hero_a'])}</span> <span class="hero-b" data-hero-b>{esc(x['hero_b'])}</span> <span class="sr">{esc(x['hero_tag'])}</span></h1>
<div class="hero-foot wrap">
<p class="hero-lead" data-fade>{esc(h['lead'])}</p>
<div class="btns" data-fade><a class="btn btn-light" href="{ctx.href('stones')}" data-magnetic>{esc(ui['cta_stones'])}</a>{btn_wa(ctx, cls='btn btn-ghost-light', place='hero')}</div>
</div>
</section>

<section class="statement-sec">
<div class="wrap">
<p class="statement" data-words>{esc(h['statement'])}</p>
<ul class="counters">{counters}</ul>
<details class="facts"><summary>{esc(h['facts_title'])}</summary><dl>{facts}</dl></details>
</div>
</section>

<section class="lines wrap" aria-labelledby="ln-t">
<div class="sec-head"><h2 id="ln-t" class="h2" data-split>{esc(x['lines_title'])}</h2><p data-fade>{esc(x['lines_lead'])}</p></div>
<ul class="ln-list">{lines}</ul>
</section>

<section class="marquee" aria-label="{esc(x['marquee_label'])}">
<p class="marquee-l wrap">{esc(x['marquee_label'])}</p>
<div class="mq" data-marquee><div class="mq-track">{markets}{markets}</div></div>
</section>

<section class="hgal" aria-labelledby="gal-t" data-hgal>
<div class="hgal-pin">
<div class="hgal-head"><h2 id="gal-t" class="h2" data-split>{esc(h['gallery_title'])}</h2><p>{esc(h['gallery_lead'])}</p><span class="hgal-progress" aria-hidden="true"><i data-hgal-bar></i></span></div>
<ul class="hgal-track" data-hgal-track>{gal}</ul>
</div>
</section>

<section class="who wrap" aria-labelledby="who-t">
<div class="who-side"><div class="who-stick"><h2 id="who-t" class="h2" data-split>{esc(h['who_title'])}</h2><div class="who-media">{who_imgs}</div></div></div>
<ul class="who-list">{who}</ul>
</section>

<section class="import">
<div class="import-media" data-reveal><div class="pin-in" data-speed="-0.15">{img(ctx, 'showroom-marble-look-slabs', '(max-width:760px) 100vw, 50vw', 'cover')}</div></div>
<div class="import-in"><h2 class="h2" data-split>{esc(h['import_title'])}</h2><p data-fade>{esc(h['import_text'])}</p>{btn_wa(ctx, h['import_cta'], 'btn btn-light', 'import')}</div>
</section>

<section class="testi" aria-labelledby="t-t" data-testi>
<div class="wrap">
<h2 id="t-t" class="h2" data-split>{esc(h['testi_title'])}</h2>
<div class="tq-stage" aria-live="polite">{tl}</div>
<div class="tq-ctrl"><button type="button" class="tq-btn" data-tq-prev aria-label="{esc(x['testi_prev'])}"><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg></button><div class="tdots">{dots}</div><button type="button" class="tq-btn" data-tq-next aria-label="{esc(x['testi_next'])}"><svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg></button></div>
</div>
</section>

{places(ctx, h['places_title'])}

<section class="faq-teaser wrap" aria-labelledby="fq-t">
<div class="sec-head"><h2 id="fq-t" class="h2" data-split>{esc(h['faq_title'])}</h2><a class="link-arrow" href="{ctx.href('faq')}">{esc(h['faq_more'])}</a></div>
{faq_list(faqs)}
</section>
{section_final(ctx)}
</main>
"""
    out += footer(ctx) + i18n_script(ctx)
    return out

def page_hero(ctx, title, lead, trail, image=None, btns=""):
    media = f'<div class="ph-media" data-reveal><div class="pin-in" data-speed="-0.08">{img(ctx, image, "(max-width:760px) 100vw, 50vw", "cover", eager=True, priority=True)}</div></div>' if image else ""
    return f"""<section class="ph{' ph-img' if image else ''}"><div class="wrap ph-in">
<div class="ph-text">{breadcrumb_html(ctx, trail)}<h1 data-split>{esc(title)}</h1><p class="lead" data-fade>{esc(lead)}</p>{f'<div class="btns">{btns}</div>' if btns else ''}</div>
{media}</div></section>"""

def pg_stones(ctx):
    L, ui = ctx.L, ctx.ui; p = L["pages"]["stones"]
    trail = [(ui["home"], "home"), (ui["nav"]["stones"], "stones")]
    ld = page_ld(ctx, "CollectionPage", p["title"], p["desc"], "showroom-ultracompact-slabs-aisle", [crumbs(ctx, trail), stones_ld(ctx, STONES)])
    out = head(ctx, p["title"], p["desc"], "showroom-ultracompact-slabs-aisle", ld) + header(ctx)
    chips = f'<button type="button" class="chip" aria-pressed="true" data-filter="all">{esc(ui["filter_all"])} <span>{len(STONES)}</span></button>'
    for k in LINES:
        n = sum(1 for s in STONES if s["line"] == k)
        chips += f'<button type="button" class="chip" aria-pressed="false" data-filter="{k}">{esc(L["lines"][k]["name"])} <span>{n}</span></button>'
    cards = "".join(stone_card(ctx, s) for s in STONES)
    lines_nav = "".join(f'<li><a href="{ctx.href(k)}"><strong>{esc(L["lines"][k]["name"])}</strong><span>{esc(L["lines"][k]["short"])}</span></a></li>' for k in LINES)
    out += f"""<main id="main">
{page_hero(ctx, p['h1'], p['lead'], trail)}
<section class="wrap lines-nav"><ul>{lines_nav}</ul></section>
<section class="wrap catalog" data-catalog>
<div class="cat-tools"><div class="chips" role="group" aria-label="{esc(ui['footer_lines'])}">{chips}</div>
<div class="search"><label for="q" class="sr">{esc(ui['search_label'])}</label><input id="q" type="search" placeholder="{esc(ui['search_ph'])}" autocomplete="off" data-search><span class="count" aria-live="polite" data-count></span></div></div>
<div class="stones">{cards}</div>
<p class="empty" hidden data-empty>{esc(ui['no_results'])}</p>
</section>
{section_final(ctx)}
</main>
"""
    return out + footer(ctx) + i18n_script(ctx)

def pg_line(ctx):
    k = ctx.key; L, ui = ctx.L, ctx.ui; ln = L["lines"][k]
    trail = [(ui["home"], "home"), (ui["nav"]["stones"], "stones"), (ln["name"], k)]
    stones = [s for s in STONES if s["line"] == k]
    faqs = [L["faq"][i] for i in LINE_FAQ[k]]
    url = abs_url(ctx.lang, k)
    ld = page_ld(ctx, "CollectionPage", ln["title"], ln["desc"], LINE_IMG[k], [crumbs(ctx, trail), stones_ld(ctx, stones), faq_ld(faqs, url)])
    out = head(ctx, ln["title"], ln["desc"], LINE_IMG[k], ld, preload={"name": LINE_IMG[k], "sizes": "(max-width:760px) 100vw, 50vw"}) + header(ctx)
    props = "".join(f"<li>{esc(x)}</li>" for x in ln["props"])
    apps = "".join(f"<li>{esc(x)}</li>" for x in ln["apps"])
    paras = "".join(f"<p>{esc(x)}</p>" for x in ln["paras"])
    cards = "".join(stone_card(ctx, s) for s in stones)
    others = "".join(f'<li><a class="idx-row idx-sm" href="{ctx.href(o)}"><span class="idx-name">{esc(L["lines"][o]["name"])}</span><span class="idx-kind">{esc(L["lines"][o]["kind"])}</span></a></li>' for o in LINES if o != k)
    i1, i2 = LINE_IMG2[k]
    out += f"""<main id="main">
{page_hero(ctx, ln['h1'], ln['lead'], trail, LINE_IMG[k], btn_wa(ctx, place='line-hero', msg=ui['wa_stone'].format(name=ln['name'], line=ln['kind'])) + f'<a class="btn btn-outline" href="{ctx.href("downloads")}">{esc(ui["cta_catalogue"])}</a>')}
<section class="wrap line-body">
<div class="prose">{paras}</div>
<aside class="spec"><h2>{esc(ln['kind'])}</h2><ul class="ticks">{props}</ul><h3>{esc(APPS_T[ctx.lang])}</h3><ul class="plain">{apps}</ul></aside>
</section>
<section class="wrap pair"><div class="pair-a" data-reveal><div class="pin-in" data-speed="-0.1">{img(ctx, i1, '(max-width:760px) 100vw, 60vw', 'cover')}</div></div><div class="pair-b" data-reveal><div class="pin-in" data-speed="-0.06">{img(ctx, i2, '(max-width:760px) 100vw, 40vw', 'cover')}</div></div></section>
<section class="wrap catalog" aria-labelledby="st-t">
<div class="sec-head"><h2 id="st-t" class="h2">{esc(ln['name'])}</h2><p>{esc(count_txt(ctx, len(stones)))}</p></div>
<div class="stones">{cards}</div>
</section>
<section class="wrap faq-teaser"><div class="sec-head"><h2 class="h2">{esc(L['pages']['home']['faq_title'])}</h2><a class="link-arrow" href="{ctx.href('faq')}">{esc(L['pages']['home']['faq_more'])}</a></div>{faq_list(faqs)}</section>
<section class="wrap others"><ul class="idx">{others}</ul></section>
{section_final(ctx)}
</main>
"""
    return out + footer(ctx) + i18n_script(ctx)

def pg_about(ctx):
    L, ui = ctx.L, ctx.ui; p = L["pages"]["about"]
    trail = [(ui["home"], "home"), (ui["nav"]["about"], "about")]
    founders_ld = [{"@type": "Person", "name": n, "description": d, "worksFor": {"@id": BASE + "/#org"}} for n, d in p["founders"]]
    ld = page_ld(ctx, "AboutPage", p["title"], p["desc"], "showroom-wide-view", [crumbs(ctx, trail)] + founders_ld)
    out = head(ctx, p["title"], p["desc"], "showroom-wide-view", ld, preload={"name": "showroom-wide-view", "sizes": "(max-width:760px) 100vw, 50vw"}) + header(ctx)
    story = "".join(f"<p>{esc(x)}</p>" for x in p["story"])
    founders = "".join(f'<li><h3>{esc(n)}</h3><p>{esc(d)}</p></li>' for n, d in p["founders"])
    markets = "".join(f"<li>{esc(m)}</li>" for m in p["markets"])
    what = "".join(f'<li><h3>{esc(n)}</h3><p>{esc(d)}</p></li>' for n, d in p["what"])
    out += f"""<main id="main">
{page_hero(ctx, p['h1'], p['lead'], trail, 'showroom-wide-view')}
<section class="wrap story"><h2 class="h2">{esc(p['story_title'])}</h2><div class="prose prose-lg">{story}</div>
<figure class="story-fig">{img(ctx, 'reading-artechstone-catalogue', '(max-width:760px) 100vw, 35vw')}</figure></section>
<section class="markets"><div class="wrap"><h2 class="markets-t">{esc(p['markets_title'])}</h2><ul class="markets-list">{markets}</ul></div></section>
<section class="wrap duo"><div data-fade><h2 class="h2">{esc(p['diff_title'])}</h2><p class="statement statement-sm">{esc(p['diff'])}</p></div>
<div data-fade><h2 class="h2">{esc(p['founders_title'])}</h2><ul class="people">{founders}</ul></div></section>
<section class="wrap duo"><div><h2 class="h2">{esc(p['what_title'])}</h2></div><ul class="people">{what}</ul></section>
{places(ctx, L['pages']['home']['places_title'])}
{section_final(ctx)}
</main>
"""
    return out + footer(ctx) + i18n_script(ctx)

def pg_warranty(ctx):
    L, ui = ctx.L, ctx.ui; p = L["pages"]["warranty"]
    trail = [(ui["home"], "home"), (ui["nav"]["warranty"], "warranty")]
    ld = page_ld(ctx, "WebPage", p["title"], p["desc"], "hand-on-slab-texture", [crumbs(ctx, trail)])
    out = head(ctx, p["title"], p["desc"], "hand-on-slab-texture", ld) + header(ctx)
    blocks = "".join(f'<article class="w-block"><h2>{esc(a)}</h2><p>{esc(b)}</p></article>' for a, b in p["blocks"])
    care = "".join(f'<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>' for a, b in p["care"])
    out += f"""<main id="main">
{page_hero(ctx, p['h1'], p['lead'], trail, 'hand-on-slab-texture')}
<section class="wrap w-blocks">{blocks}</section>
<section class="wrap care"><h2 class="h2">{esc(p['care_title'])}</h2><dl class="care-list">{care}</dl>
<div class="btns">{btn_wa(ctx, p['cta'], place='warranty')}</div></section>
{section_final(ctx)}
</main>
"""
    return out + footer(ctx) + i18n_script(ctx)

def pg_downloads(ctx):
    L, ui = ctx.L, ctx.ui; p = L["pages"]["downloads"]
    trail = [(ui["home"], "home"), (ui["nav"]["downloads"], "downloads")]
    ld = page_ld(ctx, "WebPage", p["title"], p["desc"], "artechstone-catalogue", [crumbs(ctx, trail)])
    out = head(ctx, p["title"], p["desc"], "artechstone-catalogue", ld) + header(ctx)
    inc = "".join(f"<li>{esc(x)}</li>" for x in p["includes"])
    out += f"""<main id="main">
<section class="ph"><div class="wrap split">
<div class="split-text">{breadcrumb_html(ctx, trail)}<h1>{esc(p['h1'])}</h1><p class="lead">{esc(p['lead'])}</p>
<h2 class="h3">{esc(p['includes_title'])}</h2><ul class="ticks">{inc}</ul>
<div class="split-media">{img(ctx, 'artechstone-catalogue', '(max-width:760px) 100vw, 40vw', '', eager=True)}</div></div>
<div class="form-card">{form_html(ctx, 'catalogue')}</div>
</div></section>
</main>
"""
    return out + footer(ctx) + i18n_script(ctx)

def pg_faq(ctx):
    L, ui = ctx.L, ctx.ui; p = L["pages"]["faq"]
    trail = [(ui["home"], "home"), (ui["nav"]["faq"], "faq")]
    url = abs_url(ctx.lang, "faq")
    ld = page_ld(ctx, "WebPage", p["title"], p["desc"], "stone-samples-selection", [crumbs(ctx, trail), faq_ld(L["faq"], url)])
    out = head(ctx, p["title"], p["desc"], "stone-samples-selection", ld) + header(ctx)
    out += f"""<main id="main">
{page_hero(ctx, p['h1'], p['lead'], trail)}
<section class="wrap faq-page">{faq_list(L['faq'], open_first=True)}
<aside class="faq-aside"><div class="faq-aside-in">{img(ctx, 'stone-samples-selection', '(max-width:760px) 100vw, 30vw')}<p>{esc(L['pages']['home']['final_text'])}</p>{btn_wa(ctx, place='faq')}</div></aside></section>
{section_final(ctx)}
</main>
"""
    return out + footer(ctx) + i18n_script(ctx)

def pg_contact(ctx):
    L, ui = ctx.L, ctx.ui; p = L["pages"]["contact"]
    trail = [(ui["home"], "home"), (ui["nav"]["contact"], "contact")]
    ld = page_ld(ctx, "ContactPage", p["title"], p["desc"], "artechstone-gallery-facade-night", [crumbs(ctx, trail)])
    out = head(ctx, p["title"], p["desc"], "artechstone-gallery-facade-night", ld) + header(ctx)
    out += f"""<main id="main">
<section class="ph"><div class="wrap split">
<div class="split-text">{breadcrumb_html(ctx, trail)}<h1>{esc(p['h1'])}</h1><p class="lead">{esc(p['lead'])}</p>
<ul class="contact-list">
<li><span>{esc(ui['whatsapp'])}</span><a href="{wa(ui['wa_default'])}" target="_blank" rel="noopener" data-track="whatsapp_click" data-place="contact">{SITE['wa']}</a></li>
<li><span>{esc(ui['phone'])}</span><a href="tel:{SITE['phone_href']}">{SITE['phone']}</a></li>
<li><span>{esc(ui['email'])}</span><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
<li><span>Instagram</span><a href="{SITE['instagram']}" target="_blank" rel="noopener">@artechstonebrasil</a></li>
</ul></div>
<div class="form-card">{form_html(ctx, 'contact')}</div>
</div></section>
<section class="wrap maps">
<article><h2 class="h3">{esc(ui['hq'])}</h2><address>{esc(addr_line(SITE['hq']))}</address><div class="map"><iframe title="{esc(ui['hq'])}" src="{maps_embed(SITE['hq'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div></article>
<article><h2 class="h3">{esc(ui['sp'])}</h2><address>{esc(addr_line(SITE['sp']))}</address><div class="map"><iframe title="{esc(ui['sp'])}" src="{maps_embed(SITE['sp'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div></article>
</section>
</main>
"""
    return out + footer(ctx) + i18n_script(ctx)

def pg_thanks(ctx):
    L, ui = ctx.L, ctx.ui; p = L["pages"]["thanks"]
    ld = page_ld(ctx, "WebPage", p["title"], p["desc"], "artechstone-gallery-entrance", has_crumbs=False)
    out = head(ctx, p["title"], p["desc"], "artechstone-gallery-entrance", ld, noindex=True) + header(ctx)
    out += f"""<main id="main" class="thanks">
<section class="wrap thanks-in"><div><h1>{esc(p['h1'])}</h1><p class="lead">{esc(p['lead'])}</p>
<div class="btns"><a class="btn btn-solid" href="{wa(ui['wa_default'])}" data-thanks-wa target="_blank" rel="noopener">{esc(ui['cta_whatsapp'])}</a><a class="btn btn-outline" href="{ctx.href('home')}">{esc(p['back'])}</a></div></div>
<div class="thanks-media">{img(ctx, 'artechstone-gallery-entrance', '(max-width:760px) 100vw, 40vw', '', eager=True)}</div></section>
</main>
"""
    return out + footer(ctx) + i18n_script(ctx)

RENDER = {"home": pg_home, "stones": pg_stones, "about": pg_about, "warranty": pg_warranty, "downloads": pg_downloads,
          "faq": pg_faq, "contact": pg_contact, "thanks": pg_thanks, **{k: pg_line for k in LINES}}

def pg_404():
    ctx = Ctx("pt", "home"); ctx.dir = ""
    blocks = ""
    for l in LANGS:
        c2 = Ctx(l, "home"); c2.dir = ""
        p = C[l]["pages"]["404"]
        links = " ".join(f'<a href="{c2.href(k)}">{esc(C[l]["ui"]["nav"][k] if k != "home" else C[l]["ui"]["home"])}</a>' for k in ["home", "stones", "contact"])
        blocks += f'<div lang="{C[l]["lang"]}" class="nf-lang"><h2>{esc(p["h1"])}</h2><p>{esc(p["lead"])}</p><p class="nf-links">{links}</p></div>'
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(C['pt']['pages']['404']['title'])}</title><meta name="robots" content="noindex">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{FONTS['base']}"><link rel="stylesheet" href="/assets/css/site.css"></head>
<body class="page-404"><main class="nf wrap"><a href="/" class="brand"><img src="/assets/img/logo.svg" alt="Artechstone" width="190" height="36"></a>
<p class="nf-code">404</p><div class="nf-grid">{blocks}</div></main></body></html>"""

# ---------------------------------------------------------------- arquivos de SEO / GEO
def sitemap():
    urls = ""
    for key in PAGE_KEYS:
        if key in NOINDEX: continue
        for l in LANGS:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{C[x]["lang"]}" href="{abs_url(x, key)}"/>' for x in LANGS)
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url("pt", key)}"/>'
            imgs = ""
            if key == "home":
                for g in ["artechstone-gallery-sao-paulo-facade"] + GALLERY:
                    imgs += f"<image:image><image:loc>{img_url(g, 2000)}</image:loc></image:image>"
            elif key in LINES:
                imgs = f"<image:image><image:loc>{img_url(LINE_IMG[key], 2000)}</image:loc></image:image>"
            pr = "1.0" if key == "home" else ("0.9" if key in LINES or key == "stones" else "0.7")
            urls += f"<url><loc>{abs_url(l, key)}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority>{alts}{imgs}</url>\n"
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n{urls}</urlset>\n'

def robots():
    dis = "".join(f"Disallow: {path_of(l, 'thanks')}\n" for l in LANGS) + "Disallow: /admin/\nDisallow: /api/\n"
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot", "Bytespider", "Baiduspider", "YandexBot"]
    ai = "".join(f"User-agent: {b}\nAllow: /\n{dis}\n" for b in bots)
    return f"User-agent: *\nAllow: /\n{dis}\n{ai}Sitemap: {BASE}/sitemap.xml\n"

def llms_txt():
    L = C["en"]; P = C["pt"]
    lines = "\n".join(f"- [{L['lines'][k]['name']}]({abs_url('en', k)}): {L['lines'][k]['short']}" for k in LINES)
    langs = "\n".join(f"- {C[l]['langName']}: {abs_url(l, 'home')}" for l in LANGS)
    return f"""# Artechstone

> Artechstone (Artechstone do Brasil) is a Brazilian importer and distributor of premium imported stone, founded in 2016 by Fabiane Braga and Colin B. Thomas. It sells sintered ultra-compact slabs (ArtechLâminas, its hero product), engineered quartz (ArtechQuartzo), crystallised glass stone (ArtechNano) and natural granite, marble and quartzite to stone fabricators, stone companies, architects, interior designers and builders across Brazil. Head office and warehouse in Cachoeiro de Itapemirim (Espírito Santo); gallery in São Paulo.

## Key facts
- Founded: 2016 (October), by Fabiane Braga (27 years in Singapore, stone industry career selling to Dubai, Australia, China, Thailand, the Philippines, Vietnam, Indonesia, Malaysia and Singapore) and British investor Colin B. Thomas.
- Head office and warehouse: {addr_line(SITE['hq'])}, Brazil.
- São Paulo gallery: {addr_line(SITE['sp'])}, Brazil.
- WhatsApp: {SITE['wa']} · Phone: {SITE['phone']} · Email: {SITE['email']}
- CNPJ: {SITE['cnpj']}
- Quality: ArtechQuartzo and ArtechNano are manufactured to ISO 9000 quality standards. ArtechNano carries a 1-year warranty.
- Imports: large-volume stone imports through a network of manufacturers in China.
- Natural stone origins: Brazil, Spain, Mexico, India and other countries.
- Serves all of Brazil.

## Product lines
{lines}

## Main pages (English)
- [All stones]({abs_url('en','stones')})
- [About]({abs_url('en','about')})
- [Warranty and quality]({abs_url('en','warranty')})
- [Catalogue]({abs_url('en','downloads')})
- [FAQ]({abs_url('en','faq')})
- [Contact]({abs_url('en','contact')})

## Languages
{langs}

## Optional
- [Full facts and FAQ]({BASE}/llms-full.txt)
"""

def llms_full():
    out = llms_txt() + "\n\n# Full content\n"
    for l in ["en", "pt"]:
        L = C[l]
        out += f"\n## {L['langName']}\n"
        for k in LINES:
            ln = L["lines"][k]
            out += f"\n### {ln['name']} ({ln['kind']})\nURL: {abs_url(l, k)}\n{ln['lead']}\n" + "\n".join(ln["paras"]) + "\nProperties: " + "; ".join(ln["props"]) + "\nApplications: " + "; ".join(ln["apps"]) + "\nStones: " + ", ".join(s["name"] for s in STONES if s["line"] == k) + "\n"
        out += "\n### About\n" + "\n".join(L["pages"]["about"]["story"]) + "\n"
        out += "\n### FAQ\n" + "\n".join(f"Q: {q}\nA: {a}\n" for q, a in L["faq"])
    return out

def manifest():
    return json.dumps({"name": "Artechstone", "short_name": "Artechstone", "start_url": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#2f2c2c",
                       "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "/assets/img/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, indent=1)

def vercel():
    old = {"/artechlaminas": "/pedras/artechlaminas/", "/artechquartzo": "/pedras/artechquartzo/", "/artechnano": "/pedras/artechnano/", "/artechprime": "/pedras/",
           "/granito": "/pedras/pedras-naturais/", "/distribuidora-de-pedras-importadas": "/sobre/", "/guia-de-pedras-importadas": "/perguntas-frequentes/",
           "/faq-perguntas-frequentes": "/perguntas-frequentes/", "/linha-estrelar": "/pedras/artechquartzo/", "/linha-liso": "/pedras/artechquartzo/",
           "/linha-com-veios": "/pedras/artechquartzo/", "/linha-prime": "/pedras/", "/linha-nano-2": "/pedras/artechnano/", "/home": "/", "/inicio": "/"}
    redirects = []
    for a, b in old.items():
        redirects.append({"source": a, "destination": b, "permanent": True})
        redirects.append({"source": a + "/", "destination": b, "permanent": True})
    redirects.append({"source": "/pt", "destination": "/", "permanent": True})
    redirects.append({"source": "/pt/:path*", "destination": "/:path*", "permanent": True})
    sec = [{"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
           {"key": "X-Frame-Options", "value": "SAMEORIGIN"}, {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"},
           {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"}]
    return json.dumps({"cleanUrls": True, "trailingSlash": True, "redirects": redirects,
                       "headers": [{"source": "/(.*)", "headers": sec},
                                   {"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
                                   {"source": "/(llms.txt|llms-full.txt|robots.txt|sitemap.xml)", "headers": [{"key": "Cache-Control", "value": "public, max-age=3600"}]}]}, indent=1)

OLD_URLS = {"/artechlaminas": "/pedras/artechlaminas/", "/artechquartzo": "/pedras/artechquartzo/", "/artechnano": "/pedras/artechnano/", "/artechprime": "/pedras/",
            "/granito": "/pedras/pedras-naturais/", "/distribuidora-de-pedras-importadas": "/sobre/", "/guia-de-pedras-importadas": "/perguntas-frequentes/",
            "/faq-perguntas-frequentes": "/perguntas-frequentes/", "/linha-estrelar": "/pedras/artechquartzo/", "/linha-liso": "/pedras/artechquartzo/",
            "/linha-com-veios": "/pedras/artechquartzo/", "/linha-prime": "/pedras/", "/linha-nano-2": "/pedras/artechnano/", "/home": "/", "/inicio": "/", "/contato": "/contato/"}
SEC_HEADERS = [("X-Content-Type-Options", "nosniff"), ("Referrer-Policy", "strict-origin-when-cross-origin"), ("X-Frame-Options", "SAMEORIGIN"),
               ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"), ("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")]

def htaccess():
    red = "\n".join(f"RewriteRule ^{a.strip('/')}/?$ {b} [R=301,L]" for a, b in OLD_URLS.items() if a != "/contato")
    hdr = "\n".join(f'  Header always set {k} "{v}"' for k, v in SEC_HEADERS)
    return f"""# Gerado pelo build.py
Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html
RewriteEngine On
# HTTPS e dominio sem www
RewriteCond %{{HTTPS}} off [OR]
RewriteCond %{{HTTP_HOST}} ^www\\. [NC]
RewriteCond %{{HTTP_HOST}} ^(?:www\\.)?(.+)$ [NC]
RewriteRule ^ https://%1%{{REQUEST_URI}} [R=301,L]
# /pt/ -> raiz
RewriteRule ^pt/?(.*)$ /$1 [R=301,L]
# URLs do site antigo (WordPress)
{red}
# Login do painel (/api/auth e /api/callback -> PHP)
RewriteRule ^api/(auth|callback)$ /api/$1.php [L]
# Barra no final das pastas
RewriteCond %{{REQUEST_FILENAME}} -d
RewriteCond %{{REQUEST_URI}} !/$
RewriteRule ^(.*)$ /$1/ [R=301,L]
<IfModule mod_headers.c>
{hdr}
  <FilesMatch "\\.(webp|jpg|png|svg|css|js|woff2)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
</IfModule>
<FilesMatch "^(build\\.py|requirements\\.txt|README\\.md)$">
  Require all denied
</FilesMatch>
"""

def cf_redirects():
    lines = ["/pt /  301", "/pt/* /:splat 301"]
    for a, b in OLD_URLS.items():
        if a == "/contato": continue
        lines += [f"{a} {b} 301", f"{a}/ {b} 301"]
    return "\n".join(lines) + "\n"

def cf_headers():
    sec = "\n".join(f"  {k}: {v}" for k, v in SEC_HEADERS)
    return f"/*\n{sec}\n/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n"

# ---------------------------------------------------------------- build
def write(rel, text):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, "src"), os.path.join(OUT, "assets"))
    process_stone_photos(OUT)
    n = 0
    for l in LANGS:
        for key in PAGE_KEYS:
            ctx = Ctx(l, key)
            d = slug(l, key)
            write(os.path.join(d, "index.html"), RENDER[key](ctx)); n += 1
    write("404.html", pg_404())
    write("sitemap.xml", sitemap()); write("robots.txt", robots())
    write("llms.txt", llms_txt()); write("llms-full.txt", llms_full())
    write("site.webmanifest", manifest())
    # Painel de edição (Decap CMS) em /admin/ e login em /api/
    os.makedirs(os.path.join(OUT, "admin"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "admin", "index.html"), os.path.join(OUT, "admin", "index.html"))
    write(os.path.join("admin", "config.yml"), open(os.path.join(ROOT, "admin", "config.yml"), encoding="utf-8").read().replace("__BASE__", BASE))
    if not PREVIEW:
        write("vercel.json", vercel())
        # vercel.json da raiz: o mesmo + como buildar (sem isso a Vercel acha que é app Python)
        vc = json.loads(vercel()); vc = {"$schema": "https://openapi.vercel.sh/vercel.json", "framework": None,
              "installCommand": "python3 -m pip install -r requirements.txt", "buildCommand": "python3 build.py", "outputDirectory": "dist", **vc}
        open(os.path.join(ROOT, "vercel.json"), "w", encoding="utf-8").write(json.dumps(vc, indent=1, ensure_ascii=False) + "\n")
        write(".htaccess", htaccess())          # Hostinger (Apache/LiteSpeed)
        write("_redirects", cf_redirects())     # Cloudflare Pages / Netlify
        write("_headers", cf_headers())
        os.makedirs(os.path.join(OUT, "api"), exist_ok=True)  # login do painel na Hostinger (PHP)
        for f in ("auth.php", "callback.php"): shutil.copy(os.path.join(ROOT, "oauth-php", f), os.path.join(OUT, "api", f))
    print(f"{n} paginas geradas em {OUT}")

if __name__ == "__main__":
    main()
