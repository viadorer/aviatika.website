# -*- coding: utf-8 -*-
"""Generátor webu Aviatika. Spuštění: python3 build.py

Veškerá data jsou v data/projekt.json, texty stránek v tomhle souboru
ve funkcích page_*. Výstup jde do web/ — obsah té složky se nasazuje.
"""
import json, os, re, shutil, html
from datetime import date

ROOT = "web"
D = json.load(open("data/projekt.json", encoding="utf-8"))
try:
    ROZ = json.load(open("data/rozmery.json", encoding="utf-8"))
except FileNotFoundError:      # build_images.py ještě neproběhl
    ROZ = {}

W = D["web"]
P = D["prodej"]
M = D["model_vynosu"]
FOTO = {k: v for k, v in D["foto"].items() if not k.startswith("_")}

DNES = date.today().strftime("%-d. %-m. %Y")   # české datum, ne ISO
DNES_ISO = date.today().isoformat()            # sitemap potřebuje ISO


# ---------------------------------------------------------------- pomocné

def esc(s):
    return html.escape(str(s), quote=True)


def czk(n):
    return f"{int(round(n)):,}".replace(",", " ") + " Kč"


def mil(n):
    """7900000 → '7,9 mil.' — pro velké částky v nadpisech a dlaždicích."""
    v = n / 1_000_000
    t = f"{v:.1f}".rstrip("0").rstrip(".").replace(".", ",")
    return f"{t} mil."


def doplnit(klic):
    """Hodnoty, které klient teprve dodá, se drží pod pojistkou: dokud text
    začíná slovem DOPLNIT, na web se nedostane vůbec. Placeholder tak nemůže
    uniknout návštěvníkům."""
    v = W.get(klic, "")
    return "" if not v or v.startswith("DOPLNIT") else v


# ---------------------------------------------------------------- ikony

IKONY = {
    "budova":    '<path d="M3 21h18M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M15 9h2a2 2 0 0 1 2 2v10M9 7h2M9 11h2M9 15h2"/>',
    "kladivo":   '<path d="m14 6-8.5 8.5a2.12 2.12 0 1 0 3 3L17 9M15 4l5 5M17.5 6.5 21 3"/>',
    "kostky":    '<path d="M12 2 2 7l10 5 10-5-10-5ZM2 17l10 5 10-5M2 12l10 5 10-5"/>',
    "dokument":  '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 15l2 2 4-4"/>',
    "hora":      '<path d="m8 3 4 8 5-5 5 15H2L8 3z"/>',
    "auto":      '<path d="M5 17h14M6 17V9l2-4h8l2 4v8M6 17v2M18 17v2"/><circle cx="8" cy="14" r="1"/><circle cx="16" cy="14" r="1"/>',
    "obchod":    '<path d="M3 9h18l-1 11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2L3 9ZM3 9l2-6h14l2 6M8 13a4 4 0 0 0 8 0"/>',
    "turistika": '<path d="M12 3v18M12 8l5-3M12 14l6 4M12 12 6 9M8 21h8"/>',
    "lyze":      '<path d="M3 20h18M6 20 16 4M12 20 8 6M18 12l-8 5"/>',
    "check":     '<path d="m5 12 5 5L20 7"/>',
    "sipka":     '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "chevron":   '<path d="m6 9 6 6 6-6"/>',
    "info":      '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    "telefon":   '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 4.2 2 2 0 0 1 4 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.1a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
    "mail":      '<path d="M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z"/><path d="m22 7-10 6L2 7"/>',
    "pin":       '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "hodiny":    '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "zavrit":    '<path d="M18 6 6 18M6 6l12 12"/>',
    "vlevo":     '<path d="m15 18-6-6 6-6"/>',
    "vpravo":    '<path d="m9 18 6-6-6-6"/>',
}


def ico(jmeno, trida="ico"):
    return (f'<svg class="{trida}" viewBox="0 0 24 24" aria-hidden="true">'
            f'{IKONY.get(jmeno, IKONY["check"])}</svg>')


# ---------------------------------------------------------------- obrázky

def obr(klic, trida="shot", sizes="100vw", lazy=True, prioritni=False):
    """Vypíše <picture> s WebP i JPEG ve třech velikostech.

    Rozměry se berou z data/rozmery.json — deskriptor v srcset nesmí lhát,
    jinak prohlížeč vybere jinou variantu, než jakou čekáme. Když rozměry
    ještě nejsou spočítané, srcset se vynechá a vypíše se prostý <img>."""
    meta = FOTO.get(klic)
    if not meta:
        return f"<!-- chybí obrázek {klic} -->"
    alt = esc(meta.get("alt", ""))
    r = ROZ.get(klic)

    nacitani = 'loading="lazy" decoding="async"' if lazy and not prioritni else 'decoding="async"'
    if prioritni:
        nacitani = 'fetchpriority="high" decoding="async"'

    if not r:
        return (f'<figure class="{trida}"><img src="/assets/img/{klic}.jpg" alt="{alt}" '
                f'{nacitani}></figure>')

    w, h = r["full"]
    sada = lambda ext: (f"/assets/img/small/{klic}.{ext} {r['small'][0]}w, "
                        f"/assets/img/thumb/{klic}.{ext} {r['thumb'][0]}w, "
                        f"/assets/img/{klic}.{ext} {w}w")
    return (f'<figure class="{trida}"><picture>'
            f'<source type="image/webp" srcset="{sada("webp")}" sizes="{sizes}">'
            f'<img src="/assets/img/{klic}.jpg" srcset="{sada("jpg")}" sizes="{sizes}" '
            f'alt="{alt}" width="{w}" height="{h}" {nacitani}>'
            f'</picture></figure>')


def obr_lb(klic, trida="shot", sizes="100vw"):
    """Obrázek, který se dá otevřít v lightboxu. Odkaz míří na plnou velikost,
    app.js si u prohlížečů s podporou WebP přepíše příponu sám."""
    meta = FOTO.get(klic)
    if not meta:
        return f"<!-- chybí obrázek {klic} -->"
    return (f'<a href="/assets/img/{klic}.jpg" data-lightbox data-alt="{esc(meta["alt"])}">'
            f'{obr(klic, trida, sizes)}</a>')


# ---------------------------------------------------------------- kostra

NAV = [
    ("", "Úvod"),
    ("predmet-prodeje/", "Předmět prodeje"),
    ("skladba-projektu/", "Skladba projektu"),
    ("investice/", "Investice"),
    ("lokalita/", "Lokalita"),
    ("galerie/", "Galerie"),
    ("kontakt/", "Kontakt"),
]


def hlavicka(aktivni):
    odkazy = ""
    for cesta, popis in NAV:
        cur = ' aria-current="page"' if cesta == aktivni else ""
        odkazy += f'<a href="/{cesta}"{cur}>{popis}</a>'
    return f"""<a class="skip" href="#obsah">Přejít k obsahu</a>
<header class="site-header">
<div class="wrap header-inner">
  <a class="brand" href="/">
    <b>AVIATIKA</b><span>{esc(W['tagline'])}</span>
  </a>
  <button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span></button>
  <nav class="nav" id="nav" aria-label="Hlavní">
    {odkazy}
    <a class="btn btn--primary btn--sm" href="/kontakt/">Mám zájem</a>
  </nav>
</div>
</header>"""


def paticka():
    return f"""<footer class="site-footer">
<div class="wrap">
  <div class="footer-grid">
    <div class="footer-brand">
      <b>AVIATIKA</b><span>{esc(W['tagline'])}</span>
      <img src="/assets/img/logo.png" alt="PTF Reality" width="110" height="50" loading="lazy">
    </div>
    <div>
      <h4>Projekt</h4>
      <ul>
        <li><a href="/predmet-prodeje/">Předmět prodeje</a></li>
        <li><a href="/skladba-projektu/">Skladba projektu</a></li>
        <li><a href="/investice/">Investice</a></li>
        <li><a href="/lokalita/">Lokalita</a></li>
        <li><a href="/galerie/">Galerie</a></li>
      </ul>
    </div>
    <div>
      <h4>Kontakt</h4>
      <ul>
        <li><a href="tel:{W['makler_tel_link']}">{esc(W['makler_tel'])}</a></li>
        <li><a href="mailto:{W['makler_email']}">{esc(W['makler_email'])}</a></li>
        <li>{esc(W['otviraci_doba'])}</li>
        <li><a href="/kontakt/">Domluvit prohlídku</a></li>
      </ul>
    </div>
    <div>
      <h4>Prodávající</h4>
      <ul>
        <li>{esc(W['prodavajici'])}</li>
        <li>IČO: {esc(W['prodavajici_ico'])}</li>
        <li>{esc(W['prodavajici_adresa'])}</li>
      </ul>
      <ul style="margin-top:14px">
        <li><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a></li>
        <li><a href="/zasady-pouzivani-cookies/">Cookies</a></li>
        <li><a href="#" data-cookie-open>Nastavení cookies</a></li>
      </ul>
    </div>
  </div>
  <p class="disclaimer">{esc(W['prodavajici_rejstrik'])}
    Informace uvedené na tomto webu mají informativní charakter a nepředstavují nabídku
    ve smyslu § 1731 ani § 1732 zákona č. 89/2012 Sb., občanského zákoníku.
    Vizualizace zobrazují zamýšlený stav po dokončení, nikoli současný stav objektu.</p>
  <div class="footer-bottom">
    <span>&copy; {date.today().year} {esc(W['prodavajici'])}</span>
    <span>{esc(W['adresa_objektu'])}</span>
  </div>
</div>
</footer>

<div class="cookiebar" role="dialog" aria-label="Nastavení cookies">
  <h4>Cookies</h4>
  <p>Nezbytné cookies web potřebuje k provozu. Statistické a marketingové použijeme
     jen s vaším souhlasem. Podrobnosti v <a href="/zasady-pouzivani-cookies/">zásadách používání cookies</a>.</p>
  <div class="cookiebar__prefs">
    <label><input type="checkbox" checked disabled> <span><strong>Nezbytné</strong> — bez nich web nefunguje. Nelze vypnout.</span></label>
    <label><input type="checkbox" id="ck-stat"> <span><strong>Statistické</strong> — anonymní měření návštěvnosti.</span></label>
    <label><input type="checkbox" id="ck-mark"> <span><strong>Marketingové</strong> — měření účinnosti kampaní.</span></label>
  </div>
  <div class="btn-row">
    <button class="btn btn--primary btn--sm" data-cookie="all">Přijmout vše</button>
    <button class="btn btn--ghost btn--sm" data-cookie="none">Jen nezbytné</button>
    <button class="btn btn--ghost btn--sm" data-cookie="prefs">Nastavení</button>
    <button class="btn btn--ghost btn--sm" data-cookie="save">Uložit volbu</button>
  </div>
</div>

<div class="lightbox" aria-hidden="true" aria-label="Prohlížeč fotografií">
  <button class="lb-close" aria-label="Zavřít">{ico('zavrit')}</button>
  <button class="lb-prev" aria-label="Předchozí">{ico('vlevo')}</button>
  <button class="lb-next" aria-label="Další">{ico('vpravo')}</button>
  <img src="" alt="">
</div>"""


def stranka(soubor, titulek, popis, telo, aktivni="", leaflet=False, og="budova-zahrada"):
    kanon = W["url"] + "/" + (soubor.replace("index.html", "") if soubor.endswith("index.html") else soubor)
    kanon = kanon.rstrip("/") + "/" if soubor.endswith("index.html") else kanon

    cfg = json.dumps({
        "kalkulacka": D["kalkulacka"],
        "tel": W["makler_tel"],
    }, ensure_ascii=False)

    leaflet_css = ('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">'
                   if leaflet else "")
    leaflet_js = ('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" defer></script>'
                  if leaflet else "")

    doc = f"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulek)}</title>
<meta name="description" content="{esc(popis)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{kanon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(W['nazev'])}">
<meta property="og:title" content="{esc(titulek)}">
<meta property="og:description" content="{esc(popis)}">
<meta property="og:image" content="{W['url']}/assets/img/{og}.jpg">
<meta property="og:url" content="{kanon}">
<meta property="og:locale" content="cs_CZ">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2D5A4B">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
{leaflet_css}
</head>
<body>
{hlavicka(aktivni)}
<main id="obsah">
{telo}
</main>
{paticka()}
<script>window.AVIATIKA_CFG = {cfg};</script>
{leaflet_js}
<script src="/assets/js/app.js" defer></script>
</body>
</html>
"""
    cesta = os.path.join(ROOT, soubor)
    os.makedirs(os.path.dirname(cesta), exist_ok=True)
    open(cesta, "w", encoding="utf-8").write(doc)
    return len(doc)


# ---------------------------------------------------------------- díly

def cta_band(nadpis, text):
    return f"""<section class="cta-band">
<div class="wrap split">
  <div>
    <h2>{nadpis}</h2>
    <p class="mt-sm">{text}</p>
  </div>
  <div class="btn-row" style="justify-content:flex-end">
    <a class="btn btn--light" href="tel:{W['makler_tel_link']}">{esc(W['makler_tel'])}</a>
    <a class="btn btn--primary" href="/kontakt/" style="background:#fff;color:#1C3830">Nezávazně poptat</a>
  </div>
</div>
</section>"""


def formular(zajem="Koupě celého projektu"):
    return f"""<form class="form" data-form>
  <div class="form__row">
    <div class="field">
      <label for="f-jmeno">Jméno a příjmení <span aria-hidden="true">*</span></label>
      <input type="text" id="f-jmeno" name="jmeno" autocomplete="name" required>
    </div>
    <div class="field">
      <label for="f-telefon">Telefon <span aria-hidden="true">*</span></label>
      <input type="tel" id="f-telefon" name="telefon" autocomplete="tel" required>
    </div>
  </div>
  <div class="field">
    <label for="f-email">E-mail <span aria-hidden="true">*</span></label>
    <input type="email" id="f-email" name="email" autocomplete="email" required>
  </div>
  <input type="hidden" name="zajem" value="{esc(zajem)}">
  <div class="field">
    <label for="f-zprava">Zpráva</label>
    <textarea id="f-zprava" name="zprava" rows="4" placeholder="Co vás o projektu zajímá?"></textarea>
  </div>
  <label class="consent">
    <input type="checkbox" name="souhlas" value="1" required>
    <span>Souhlasím se zpracováním osobních údajů za účelem vyřízení mé poptávky.
      Podrobnosti v <a href="/ochrana-osobnich-udaju/">zásadách ochrany osobních údajů</a>.</span>
  </label>
  <button type="submit" class="btn btn--primary">Odeslat poptávku</button>
  <p class="form-msg" role="status" aria-live="polite"></p>
</form>"""


def model_dlazdice():
    """Modelová čísla vždy s viditelnou poznámkou — jde o odhad, ne o příslib."""
    polozky = [
        (f"{M['roi_pct_min']}–{M['roi_pct_max']} %", "Modelové zhodnocení při dokončení"),
        (f"{mil(M['prijem_rocne_min']).replace(' mil.', '')}–{mil(M['prijem_rocne_max'])}", "Modelový roční příjem z provozu"),
        (f"{mil(M['hodnota_po_dokonceni_min']).replace(' mil.', '')}–{mil(M['hodnota_po_dokonceni_max'])}", "Odhad hodnoty po dokončení"),
    ]
    karty = "".join(
        f'<div class="card"><b style="display:block;font:500 clamp(1.7rem,3vw,2.4rem)/1.1 var(--serif);'
        f'letter-spacing:-.02em;color:var(--brand)">{c}</b>'
        f'<p style="margin-top:12px">{p}</p></div>'
        for c, p in polozky
    )
    return f"""<div class="grid grid--3">{karty}</div>
<div class="note mt">{ico('info', 'ico ico--sm')}<div><strong>Modelový propočet.</strong>
  {esc(M['disclaimer'])}</div></div>"""


# ---------------------------------------------------------------- stránky

def page_index():
    dph = doplnit("dph_text")
    # Šest vizualizací napříč dispozicemi; celou sadu nese stránka Galerie.
    vyber = ["3kk-01", "2kk-01", "1kk-01", "3kk-11", "2kk-09", "1kk-08"]
    ukazka = "".join(obr_lb(k, "shot", "(max-width:520px) 100vw, (max-width:860px) 50vw, 33vw")
                     for k in vyber if k in FOTO)
    pocet_fotek = len(D["galerie"])
    polozky = "".join(
        f'<div class="card">{ico(p["ikona"])}<h3>{esc(p["nazev"])}</h3><p>{esc(p["popis"])}</p></div>'
        for p in P["polozky"]
    )
    dispozice = "".join(
        f'<div class="card"><span class="card__num">{esc(d["typ"])}</span>'
        f'<h3>{esc(d["nazev"])}</h3><p>{esc(d["perex"])}</p>'
        f'<p style="margin-top:14px;color:var(--brand);font-weight:600">{esc(d["plocha"])}</p></div>'
        for d in D["dispozice"]
    )

    telo = f"""<section class="hero">
  <div class="hero__bg">{obr('budova-zahrada', 'shot shot--free', '100vw', lazy=False, prioritni=True)}</div>
  <div class="hero__inner"><div class="wrap">
    <p class="eyebrow eyebrow--light">Kovářská · Krušné hory</p>
    <h1>Rozestavěný horský resort připravený k dokončení</h1>
    <div class="hero__price">
      <b>{czk(P['cena'])}</b><span>za celý projekt</span>
    </div>
    <p class="lead">{esc(P['predmet_souhrn'])} — vše v jedné transakci.
      Povolovací řízení už proběhlo, materiál je na místě. Dá se rovnou stavět.</p>
    <div class="btn-row">
      <a class="btn btn--primary" href="/predmet-prodeje/">Co přesně se prodává</a>
      <a class="btn btn--light" href="/investice/">Spočítat návratnost</a>
    </div>
    <p class="hero__note">{esc(D['vizualizace_poznamka'])}</p>
  </div></div>
</section>

<section class="statbar">
  <div class="wrap"><ul>
    <li><b>{mil(P['cena'])}</b><span>kupní cena celého projektu</span></li>
    <li><b>3</b><span>typy dispozic 1+kk až 3+kk</span></li>
    <li><b>15 min</b><span>na Klínovec</span></li>
    <li><b>Platné</b><span>stavební povolení a dokumentace</span></li>
  </ul></div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Předmět prodeje</p>
      <h2>Čtyři věci, které kupujete najednou</h2>
      <p>Prodává se celek, ne pozemek s příslibem. Sehnat každou z těchto částí zvlášť
         by trvalo měsíce — tady jsou pohromadě a v ceně.</p>
    </div>
    <div class="grid grid--4">{polozky}</div>
    {'<div class="note mt">' + ico('info', 'ico ico--sm') + '<div>' + esc(dph) + '</div></div>' if dph else ''}
    <div class="btn-row mt">
      <a class="btn btn--ghost" href="/predmet-prodeje/">Detail předmětu prodeje {ico('sipka', 'ico ico--sm')}</a>
    </div>
  </div>
</section>

<section class="bg-alt">
  <div class="wrap split split--wide">
    <div>
      <p class="eyebrow">Stav projektu</p>
      <h2>Hrubá stavba v pokročilé fázi</h2>
      <p class="lead mt-sm">Objekt stojí v centru Kovářské na náměstí J. Švermy.
        Projektová dokumentace i stavební povolení jsou hotové a platné, takže nový
        vlastník nemusí procházet povolovacím řízením znovu.</p>
      <ul class="ticks mt">
        <li>{ico('check', 'ico ico--sm')}<span>Kompletní projektová dokumentace</span></li>
        <li>{ico('check', 'ico ico--sm')}<span>Platné stavební povolení</span></li>
        <li>{ico('check', 'ico ico--sm')}<span>Materiál na hrubou stavbu už na místě</span></li>
        <li>{ico('check', 'ico ico--sm')}<span>{esc(P['rozsiritelnost'])}</span></li>
      </ul>
    </div>
    <div>
      {obr('budova-ulice', 'shot shot--wide', '(max-width:900px) 100vw, 50vw')}
      <p class="caption">Vizualizace uličního průčelí z náměstí J. Švermy.</p>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Skladba projektu</p>
      <h2>Tři typy dispozic</h2>
      <p>Projekt počítá s apartmány od kompaktních 1+kk po 3+kk o 90 m².
         Skladba, která pokryje páry, rodiny i delší pobyty.</p>
    </div>
    <div class="grid grid--3">{dispozice}</div>
    <div class="btn-row mt">
      <a class="btn btn--ghost" href="/skladba-projektu/">Podrobná skladba a vizualizace {ico('sipka', 'ico ico--sm')}</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Vizualizace</p>
      <h2>Jak bude objekt vypadat</h2>
      <p>Architektonické vizualizace dokončeného stavu — exteriér i všechny tři
         typy apartmánů.</p>
    </div>
    <div class="gallery">{ukazka}</div>
    <div class="btn-row mt">
      <a class="btn btn--ghost" href="/galerie/">Celá galerie ({pocet_fotek} vizualizací) {ico('sipka', 'ico ico--sm')}</a>
    </div>
  </div>
</section>

<section class="bg-soft">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Investiční potenciál</p>
      <h2>Proč zrovna Krušné hory</h2>
      <p>Kovářská má plnou zimní i letní sezónu. Objekt se dá provozovat po celý rok,
         ne jen čtyři měsíce v zimě.</p>
    </div>
    {model_dlazdice()}
    <div class="btn-row mt">
      <a class="btn btn--primary" href="/investice/">Otevřít kalkulačku návratnosti</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap split">
    <div>
      <p class="eyebrow">Lokalita</p>
      <h2>Mezi Klínovcem a saskou hranicí</h2>
      <p class="lead mt-sm">{esc(D['lokalita']['perex'])}</p>
      <ul class="datalist mt">
        <li><span>Klínovec</span><b>15 min</b></li>
        <li><span>Fichtelberg (DE)</span><b>20 min</b></li>
        <li><span>Karlovy Vary</span><b>45 min</b></li>
        <li><span>Praha</span><b>2 hodiny</b></li>
      </ul>
      <div class="btn-row mt">
        <a class="btn btn--ghost" href="/lokalita/">Vše o lokalitě {ico('sipka', 'ico ico--sm')}</a>
      </div>
    </div>
    <div>
      {obr('krusne-hory-inverze', 'shot shot--tall', '(max-width:900px) 100vw, 50vw')}
      <p class="caption">Hřeben Krušných hor nad Kovářskou.</p>
    </div>
  </div>
</section>

{cta_band('Prohlídku domluvíme podle vás',
          'Projekt je možné vidět na místě včetně dokumentace a soupisu materiálu. '
          'Ozvěte se a domluvíme termín.')}"""

    return stranka(
        "index.html",
        f"{W['nazev']} — prodej celého projektu za {P['cena_slovy']}",
        f"Rozestavěný horský resort v Kovářské k prodeji za {P['cena_slovy']}. "
        f"{P['predmet_souhrn']}. 15 minut od Klínovce.",
        telo, aktivni="",
    )


def page_predmet():
    polozky = ""
    for i, p in enumerate(P["polozky"], 1):
        polozky += f"""<div class="card">
  <span class="card__num">{i}</span>
  <h3>{esc(p['nazev'])}</h3>
  <p>{esc(p['popis'])}</p>
</div>"""
    dph = doplnit("dph_text")
    penb = doplnit("penb")

    telo = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Předmět prodeje</p>
    <h1>Co přesně kupujete za {czk(P['cena'])}</h1>
    <p class="lead">Prodává se celek jednou smlouvou: pozemek s rozestavěnou stavbou,
       materiál složený na místě a platné povolení včetně dokumentace.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid grid--2">{polozky}</div>
    <div class="note mt">{ico('info', 'ico ico--sm')}<div>
      <strong>Rozšiřitelnost.</strong> {esc(P['rozsiritelnost'])}</div></div>
    {'<div class="note mt-sm">' + ico('info', 'ico ico--sm') + '<div><strong>DPH.</strong> ' + esc(dph) + '</div></div>' if dph else ''}
    {'<div class="note mt-sm">' + ico('info', 'ico ico--sm') + '<div><strong>Energetická náročnost.</strong> ' + esc(penb) + '</div></div>' if penb else ''}
  </div>
</section>

<section class="bg-alt">
  <div class="wrap split split--wide">
    <div>
      {obr('budova-ulice', 'shot shot--wide', '(max-width:900px) 100vw, 50vw')}
      <p class="caption">Vizualizace uličního průčelí.</p>
    </div>
    <div>
      <p class="eyebrow">Co tím získáte</p>
      <h2>Povolovací řízení už proběhlo</h2>
      <p class="lead mt-sm">U srovnatelného projektu na zelené louce se počítá s měsíci
        na územní řízení, stavební povolení a projekt. Tady je to hotové a platné.</p>
      <ul class="ticks mt">
        <li>{ico('check', 'ico ico--sm')}<span>Žádná demolice ani příprava pozemku</span></li>
        <li>{ico('check', 'ico ico--sm')}<span>Hrubá stavba v pokročilé fázi</span></li>
        <li>{ico('check', 'ico ico--sm')}<span>Materiál na dokončení hrubé stavby v ceně</span></li>
        <li>{ico('check', 'ico ico--sm')}<span>Dokumentace k předání při podpisu</span></li>
      </ul>
    </div>
  </div>
</section>

{cta_band('Chcete vidět dokumentaci?',
          'Projektovou dokumentaci, stavební povolení i soupis materiálu předáme '
          'zájemcům k nahlédnutí. Stačí se ozvat.')}"""

    return stranka(
        "predmet-prodeje/index.html",
        f"Předmět prodeje — {W['nazev']}",
        f"Co je součástí prodeje za {P['cena_slovy']}: nemovitost, rozestavěná stavba, "
        f"materiál na hrubou stavbu a platné stavební povolení.",
        telo, aktivni="predmet-prodeje/", og="budova-ulice",
    )


def page_skladba():
    bloky = ""
    for d in D["dispozice"]:
        mistnosti = "".join(
            f'<li>{ico("check", "ico ico--sm")}<span>{esc(m)}</span></li>' for m in d["mistnosti"]
        )
        chipy = "".join(f"<span>{esc(c)}</span>" for c in d["parametry"])
        fotky = "".join(
            obr_lb(k, "shot", "(max-width:860px) 100vw, 45vw") for k in d["foto"]
        )
        bloky += f"""<div class="unit">
  <button class="unit__head" aria-expanded="false" aria-controls="u-{d['klic']}">
    <span class="unit__tag">{esc(d['typ'])}</span>
    <h3>{esc(d['nazev'])}</h3>
    <span class="unit__meta">{esc(d['plocha'])} · {len(d['foto'])} vizualizací</span>
    {ico('chevron', 'ico unit__chev')}
  </button>
  <div class="unit__body" id="u-{d['klic']}" hidden>
    <div class="unit__grid">
      <div>
        <p class="lead">{esc(d['perex'])}</p>
        <ul class="ticks mt">{mistnosti}</ul>
        <div class="chips">{chipy}</div>
        <p class="caption mt-sm">{esc(D['vybaveni_poznamka'])}</p>
      </div>
      <div class="mosaic">{fotky}</div>
    </div>
  </div>
</div>"""

    telo = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Skladba projektu</p>
    <h1>Dispozice a kapacita</h1>
    <p class="lead">Projekt počítá se třemi typy apartmánů. Rozklikněte si typ
       a uvidíte dispozici i vizualizace interiéru.</p>
  </div>
</section>

<section>
  <div class="wrap">
    {bloky}
    <div class="note mt">{ico('info', 'ico ico--sm')}<div>
      {esc(D['vizualizace_poznamka'])} {esc(D['vybaveni_poznamka'])}</div></div>
  </div>
</section>

{cta_band('Zajímá vás konkrétní dispozice?',
          'Půdorysy a výměry jednotlivých jednotek posíláme na vyžádání.')}"""

    return stranka(
        "skladba-projektu/index.html",
        f"Skladba projektu — {W['nazev']}",
        "Tři typy dispozic od 1+kk po 3+kk, 36 až 90 m². Vizualizace interiérů "
        "a přehled místností jednotlivých apartmánů.",
        telo, aktivni="skladba-projektu/", og="3kk-01",
    )


def page_investice():
    K = D["kalkulacka"]
    telo = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Investice</p>
    <h1>Kalkulačka návratnosti projektu</h1>
    <p class="lead">Nastavte parametry podle svého záměru a uvidíte, jak se mění
       cash flow a celkový výnos. Všechna čísla jsou modelová.</p>
  </div>
</section>

<section>
  <div class="wrap">
    {model_dlazdice()}
  </div>
</section>

<section class="bg-alt">
  <div class="wrap">
    <div class="calc" id="calc">
      <div class="calc__panel">
        <h3>Vstupy</h3>
        <div class="mt-sm"></div>
        <div class="field">
          <label for="calc-cena">Kupní cena projektu</label>
          <input type="number" id="calc-cena" value="{K['cena_projektu']}" step="100000" min="0">
        </div>
        <div class="field">
          <label for="calc-capex">Náklady na dokončení (CAPEX)</label>
          <input type="number" id="calc-capex" value="{K['capex']}" step="100000" min="0">
        </div>
        <div class="field">
          <label for="calc-jednotky">Počet pronajímaných jednotek</label>
          <input type="number" id="calc-jednotky" value="{K['pocet_jednotek']}" step="1" min="1">
        </div>
        <div class="field">
          <label for="calc-adr">Průměrná cena za noc</label>
          <input type="number" id="calc-adr" value="{K['adr']}" step="100" min="0">
        </div>
        <div class="field">
          <label for="calc-obsazenost">Obsazenost <output id="val-obsazenost"></output></label>
          <input type="range" id="calc-obsazenost" value="{K['obsazenost_dni']}" min="60" max="330" step="1">
        </div>
        <div class="field">
          <label for="calc-opex">Provozní náklady <output id="val-opex"></output></label>
          <input type="range" id="calc-opex" value="{K['opex_pct']}" min="10" max="70" step="1">
        </div>
        <div class="field">
          <label for="calc-vlastni">Vlastní zdroje <output id="val-vlastni"></output></label>
          <input type="range" id="calc-vlastni" value="{K['vlastni_zdroje_pct']}" min="0" max="100" step="5">
        </div>
        <div class="field">
          <label for="calc-urok">Úroková sazba <output id="val-urok"></output></label>
          <input type="range" id="calc-urok" value="{K['urok_pct']}" min="0" max="10" step="0.1">
        </div>
        <div class="field">
          <label for="calc-splatnost">Splatnost úvěru <output id="val-splatnost"></output></label>
          <input type="range" id="calc-splatnost" value="{K['splatnost_let']}" min="5" max="30" step="1">
        </div>
        <div class="field">
          <label for="calc-zhodnoceni">Roční zhodnocení nemovitosti <output id="val-zhodnoceni"></output></label>
          <input type="range" id="calc-zhodnoceni" value="{K['zhodnoceni_pct']}" min="0" max="10" step="0.5">
        </div>
      </div>

      <div class="calc__panel calc__panel--out">
        <h3>Výsledek</h3>
        <div class="mt-sm"></div>
        <div class="out"><span>Celková investice</span><b id="out-investice"></b></div>
        <div class="out"><span>Z toho vlastní zdroje</span><b id="out-vlastni"></b></div>
        <div class="out"><span>Úvěr</span><b id="out-uver"></b></div>
        <div class="out"><span>Splátka úvěru</span><b id="out-splatka"></b></div>

        <div class="out" style="margin-top:22px"><span>Roční tržby z provozu</span><b id="out-trzby"></b></div>
        <div class="out"><span>Provozní náklady</span><b id="out-naklady"></b></div>
        <div class="out"><span>Čistý provozní zisk</span><b id="out-cisty"></b></div>
        <div class="out"><span>Splátky úvěru ročně</span><b id="out-uver-rocne"></b></div>
        <div class="out"><span>Provozní cash flow</span><b id="out-cashflow"></b></div>
        <div class="out"><span>Měsíčně</span><b id="out-cashflow-mesic"></b></div>

        <div class="out" style="margin-top:22px"><span>Umořená jistina (nehotovostní)</span><b id="out-umoreni"></b></div>
        <div class="out"><span>Zhodnocení nemovitosti (nehotovostní)</span><b id="out-prirustek"></b></div>
        <div class="out"><span>Celkový roční přínos</span><b id="out-celkovy"></b></div>
        <div class="out out--hero"><span>Výnos z vlastních zdrojů</span><b id="out-vynos"></b></div>
        <p class="calc-warn" id="calc-warn" role="status" aria-live="polite"></p>
      </div>
    </div>

    <div class="note mt">{ico('info', 'ico ico--sm')}<div>
      <strong>Jak číst výsledek.</strong> Provozní cash flow je jediná položka, která
      skutečně přiteče na účet. Umořená jistina a zhodnocení nemovitosti jsou nehotovostní —
      zvyšují majetek, ne hotovost, a proto se vykazují odděleně.
      Do provozních nákladů patří personál, energie, úklid, praní, pojištění, správa
      a provize rezervačních portálů; u ubytovacího provozu bývají spíš vyšší než výchozích
      35 %. Kalkulačka nepočítá s daněmi, rezervou na opravy ani s náklady na prodej.
      Výsledek je model podle vámi zadaných čísel — nejde o finanční poradenství
      ani o příslib výnosu.</div></div>
  </div>
</section>

{cta_band('Chcete propočet na míru?',
          'Pošlete nám svůj záměr a projdeme čísla společně nad konkrétní dokumentací.')}"""

    return stranka(
        "investice/index.html",
        f"Investiční kalkulačka — {W['nazev']}",
        "Interaktivní propočet návratnosti projektu Aviatika: cash flow, splátka úvěru "
        "a výnos z vlastních zdrojů podle vašich parametrů.",
        telo, aktivni="investice/",
    )


def page_lokalita():
    skupiny = ""
    for s in D["lokalita"]["skupiny"]:
        radky = "".join(f"<li><span>{esc(a)}</span><b>{esc(b)}</b></li>" for a, b in s["polozky"])
        skupiny += f"""<div class="card">
  {ico(s['ikona'])}
  <h3>{esc(s['nazev'])}</h3>
  <ul class="datalist mt-sm">{radky}</ul>
</div>"""

    trasy = ""
    for t in D["lokalita"]["trasy"]:
        body = "".join(f'<li>{ico("check", "ico ico--sm")}<span>{esc(b)}</span></li>' for b in t["polozky"])
        trasy += f"""<div class="feature">
  <div>
    {ico(t['ikona'])}
    <h2 style="margin-top:16px">{esc(t['nazev'])}</h2>
    <p class="lead mt-sm">{esc(t['popis'])}</p>
    <ul class="ticks mt">{body}</ul>
  </div>
  <div class="feature__media">
    {obr(t['foto'], 'shot shot--wide', '(max-width:860px) 100vw, 50vw')}
  </div>
</div>"""

    telo = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Lokalita</p>
    <h1>Kovářská pod Klínovcem</h1>
    <p class="lead">{esc(D['lokalita']['perex'])}</p>
    <p class="caption">{esc(W['adresa_objektu'])}</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="map" id="map"
         data-lat="{W['gps'][0]}" data-lon="{W['gps'][1]}"
         data-popis="{esc(W['nazev'])} — {esc(W['adresa_objektu'])}"></div>
    <div class="grid grid--3 mt">{skupiny}</div>
  </div>
</section>

<section class="bg-alt">
  <div class="wrap">
    {trasy}
  </div>
</section>

{cta_band('Přijeďte se podívat',
          'Prohlídku objektu i okolí domluvíme podle vás — včetně víkendu.')}"""

    return stranka(
        "lokalita/index.html",
        f"Lokalita Kovářská — {W['nazev']}",
        "Kovářská v Krušných horách pod Klínovcem: 15 minut do areálu, 45 minut do Karlových Varů, "
        "celoroční sezóna a kompletní občanská vybavenost v místě.",
        telo, aktivni="lokalita/", leaflet=True, og="krusne-hory-inverze",
    )


def page_galerie():
    dlazdice = ""
    for k in D["galerie"]:
        meta = FOTO.get(k)
        if not meta:
            continue
        r = ROZ.get(k, {})
        w, h = r.get("thumb", [900, 600])
        dlazdice += f"""<a href="/assets/img/{k}.jpg" data-lightbox data-alt="{esc(meta['alt'])}">
  <picture>
    <source type="image/webp" srcset="/assets/img/small/{k}.webp {r.get('small',[480])[0]}w, /assets/img/thumb/{k}.webp {w}w" sizes="(max-width:520px) 100vw, (max-width:860px) 50vw, 33vw">
    <img src="/assets/img/thumb/{k}.jpg" srcset="/assets/img/small/{k}.jpg {r.get('small',[480])[0]}w, /assets/img/thumb/{k}.jpg {w}w" sizes="(max-width:520px) 100vw, (max-width:860px) 50vw, 33vw" alt="{esc(meta['alt'])}" width="{w}" height="{h}" loading="lazy" decoding="async">
  </picture>
</a>"""

    telo = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Galerie</p>
    <h1>Vizualizace projektu</h1>
    <p class="lead">{esc(D['vizualizace_poznamka'])} {esc(D['vybaveni_poznamka'])}</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="gallery">{dlazdice}</div>
  </div>
</section>

{cta_band('Chcete vidět skutečný stav?',
          'Fotografie současného stavu stavby a dokumentaci předáme na vyžádání při prohlídce.')}"""

    return stranka(
        "galerie/index.html",
        f"Galerie — {W['nazev']}",
        "Architektonické vizualizace objektu a interiérů apartmánů projektu Aviatika "
        "v Kovářské.",
        telo, aktivni="galerie/",
    )


def page_kontakt():
    telo = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Kontakt</p>
    <h1>Domluvme si prohlídku</h1>
    <p class="lead">Ozvěte se telefonicky nebo pošlete poptávku — reagujeme
       nejpozději následující pracovní den.</p>
  </div>
</section>

<section>
  <div class="wrap split split--top">
    <div>
      <div class="card">
        <div class="person">
          {obr('makler', 'shot shot--free', '96px')}
          <div>
            <h3>{esc(W['makler'])}</h3>
            <p>{esc(W['makler_role'])} · {esc(W['makler_praxe'])}</p>
            <a href="tel:{W['makler_tel_link']}">{esc(W['makler_tel'])}</a>
            <a href="mailto:{W['makler_email']}">{esc(W['makler_email'])}</a>
          </div>
        </div>
      </div>

      <div class="card mt">
        <h3>Kanceláře</h3>
        <ul class="ticks mt-sm">
          <li>{ico('pin', 'ico ico--sm')}<span><strong>Plzeň</strong><br>{esc(W['pobocka_plzen'])}</span></li>
          <li>{ico('pin', 'ico ico--sm')}<span><strong>Praha</strong><br>{esc(W['pobocka_praha'])}</span></li>
          <li>{ico('telefon', 'ico ico--sm')}<span>Kancelář: <a href="tel:{W['kancelar_tel_link']}">{esc(W['kancelar_tel'])}</a></span></li>
          <li>{ico('mail', 'ico ico--sm')}<span><a href="mailto:{W['firma_email']}">{esc(W['firma_email'])}</a></span></li>
          <li>{ico('hodiny', 'ico ico--sm')}<span>{esc(W['otviraci_doba'])}</span></li>
        </ul>
      </div>

      <div class="card mt">
        <h3>Adresa objektu</h3>
        <p class="mt-sm">{esc(W['adresa_objektu'])}<br>Parkování před budovou, prohlídky po domluvě.</p>
      </div>
    </div>

    <div>
      {formular()}
    </div>
  </div>
</section>"""

    return stranka(
        "kontakt/index.html",
        f"Kontakt — {W['nazev']}",
        f"Kontakt na prodej projektu Aviatika v Kovářské: {W['makler']}, "
        f"{W['makler_tel']}, {W['makler_email']}.",
        telo, aktivni="kontakt/",
    )


def page_gdpr():
    telo = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Právní informace</p>
    <h1>Zásady ochrany osobních údajů</h1>
    <p class="lead">Informace o zpracování osobních údajů dle Nařízení (EU) 2016/679 (GDPR).</p>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>1. Správce osobních údajů</h2>
    <p>Správcem osobních údajů je {esc(W['prodavajici'])}, IČO {esc(W['prodavajici_ico'])},
      se sídlem {esc(W['prodavajici_adresa'])} (dále jen „správce“ nebo „my“).
      Kontakt: <a href="mailto:{W['firma_email']}">{esc(W['firma_email'])}</a>,
      tel. <a href="tel:{W['kancelar_tel_link']}">{esc(W['kancelar_tel'])}</a>.</p>

    <h2>2. Účely a právní základy zpracování</h2>
    <ul>
      <li>Vyřízení poptávky odeslané kontaktním formulářem — jednání o smlouvě dle čl. 6 odst. 1 písm. b) GDPR.</li>
      <li>Plnění právních povinností dle čl. 6 odst. 1 písm. c) GDPR, zejména účetních a daňových.</li>
      <li>Oprávněný zájem dle čl. 6 odst. 1 písm. f) GDPR — ochrana právních nároků a bezpečnost webu.</li>
      <li>Marketing na základě souhlasu dle čl. 6 odst. 1 písm. a) GDPR, pokud jej udělíte.</li>
    </ul>

    <h2>3. Kategorie zpracovávaných údajů</h2>
    <p>Zpracováváme identifikační a kontaktní údaje (jméno, e-mail, telefon), obsah vaší
      zprávy a technické údaje o používání webu (cookies, IP adresa).</p>

    <h2>4. Doba uchování</h2>
    <p>Údaje uchováváme po dobu nezbytnou k naplnění účelu, případně po dobu stanovenou
      právními předpisy. U údajů z kontaktního formuláře zpravidla 12 měsíců od vyřízení
      požadavku, není-li právní důvod pro delší uchování.</p>

    <h2>5. Příjemci osobních údajů</h2>
    <p>Údaje předáváme zpracovatelům (poskytovatelé IT služeb a hostingu, provozovatel
      CRM systému, účetní), vždy na základě smlouvy o zpracování osobních údajů.</p>

    <h2>6. Předávání do třetích zemí</h2>
    <p>Osobní údaje zásadně nepředáváme mimo EU/EHP. Pokud by k tomu došlo, pouze při
      zajištění odpovídajících záruk dle kapitoly V GDPR.</p>

    <h2>7. Cookies</h2>
    <p>Web používá cookies. Statistické a marketingové se načítají až po vašem souhlasu.
      Podrobnosti najdete v <a href="/zasady-pouzivani-cookies/">zásadách používání cookies</a>,
      volbu můžete kdykoli změnit přes <a href="#" data-cookie-open>nastavení cookies</a>.</p>

    <h2>8. Vaše práva</h2>
    <ul>
      <li>Právo na přístup k osobním údajům — čl. 15 GDPR</li>
      <li>Právo na opravu — čl. 16 GDPR</li>
      <li>Právo na výmaz — čl. 17 GDPR</li>
      <li>Právo na omezení zpracování — čl. 18 GDPR</li>
      <li>Právo na přenositelnost údajů — čl. 20 GDPR</li>
      <li>Právo vznést námitku — čl. 21 GDPR</li>
      <li>Právo podat stížnost u Úřadu pro ochranu osobních údajů (<a href="https://www.uoou.cz" rel="noopener">uoou.cz</a>)</li>
    </ul>

    <h2>9. Jak uplatnit svá práva</h2>
    <p>Práva můžete uplatnit e-mailem na <a href="mailto:{W['firma_email']}">{esc(W['firma_email'])}</a>
      nebo písemně na adresu sídla správce. Z bezpečnostních důvodů si můžeme vyžádat
      ověření totožnosti.</p>

    <h2>10. Závěrečná ustanovení</h2>
    <p>Tyto zásady se mohou měnit, aktuální verze je vždy na této stránce.</p>
    <p><em>Poslední aktualizace: {DNES}</em></p>
  </div>
</section>"""

    return stranka(
        "ochrana-osobnich-udaju/index.html",
        f"Ochrana osobních údajů — {W['nazev']}",
        "Informace o zpracování osobních údajů dle GDPR pro web projektu Aviatika.",
        telo,
    )


def page_cookies():
    telo = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Právní informace</p>
    <h1>Zásady používání cookies</h1>
    <p class="lead">Jaké cookies web používá a jak nad nimi máte kontrolu.</p>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>Co jsou cookies</h2>
    <p>Cookies jsou malé soubory, které web ukládá do vašeho prohlížeče. Slouží
      k zajištění funkčnosti webu a případně k měření návštěvnosti.</p>

    <h2>Kategorie</h2>
    <h3>Nezbytné</h3>
    <p>Zajišťují základní funkčnost webu a uchovávají vaši volbu v nastavení cookies.
      Bez nich by web nefungoval, proto je nelze vypnout. Ukládají se na základě
      oprávněného zájmu.</p>

    <h3>Statistické</h3>
    <p>Anonymní měření návštěvnosti — kolik lidí web navštíví a které stránky si
      prohlédnou. Načítají se <strong>až po vašem souhlasu</strong>.</p>

    <h3>Marketingové</h3>
    <p>Měření účinnosti reklamních kampaní. Načítají se <strong>až po vašem souhlasu</strong>.</p>

    <h2>Jak volbu změnit</h2>
    <p>Svou volbu můžete kdykoli změnit přes
      <a href="#" data-cookie-open>nastavení cookies</a>. Cookies lze také smazat
      nebo blokovat přímo v prohlížeči — v takovém případě nemusí některé části webu
      fungovat správně.</p>

    <h2>Služby třetích stran</h2>
    <p>Web načítá písma z Google Fonts, mapové podklady z OpenStreetMap a knihovnu
      Leaflet z veřejné CDN. Tyto služby se dozvědí vaši IP adresu. Kontaktní formulář
      odesílá vyplněné údaje do našeho CRM systému.</p>

    <h2>Kontakt</h2>
    <p>Dotazy k cookies i k ochraně údajů posílejte na
      <a href="mailto:{W['firma_email']}">{esc(W['firma_email'])}</a>. Podrobnosti
      o zpracování údajů najdete v
      <a href="/ochrana-osobnich-udaju/">zásadách ochrany osobních údajů</a>.</p>

    <p><em>Poslední aktualizace: {DNES}</em></p>
  </div>
</section>"""

    return stranka(
        "zasady-pouzivani-cookies/index.html",
        f"Zásady používání cookies — {W['nazev']}",
        "Jaké cookies web projektu Aviatika používá a jak nad nimi máte kontrolu.",
        telo,
    )


def page_404():
    telo = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Chyba 404</p>
    <h1>Tuto stránku jsme nenašli</h1>
    <p class="lead">Odkaz je nejspíš zastaralý. Zkuste některou z hlavních stránek.</p>
    <div class="btn-row mt">
      <a class="btn btn--primary" href="/">Na úvod</a>
      <a class="btn btn--ghost" href="/kontakt/">Kontakt</a>
    </div>
  </div>
</section>
<section></section>"""
    return stranka("404.html", f"Stránka nenalezena — {W['nazev']}",
                   "Požadovaná stránka nebyla nalezena. Přejděte na úvodní stránku projektu Aviatika Kovářská nebo na kontakty.", telo)


# ---------------------------------------------------------------- doplňky

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#2D5A4B"/>
<path d="M18 44 32 18l14 26" fill="none" stroke="#fff" stroke-width="5"
      stroke-linecap="round" stroke-linejoin="round"/>
<path d="M25 38h14" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/>
</svg>
"""


def doplnky():
    open(os.path.join(ROOT, "assets/img/favicon.svg"), "w", encoding="utf-8").write(FAVICON)

    # Logo prodejce se nezmenšuje ani nepřevádí — má průhledné pozadí.
    if os.path.exists("logo.png"):
        shutil.copyfile("logo.png", os.path.join(ROOT, "assets/img/logo.png"))

    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {W['url']}/sitemap.xml\n"
    )

    urls = ["", "predmet-prodeje/", "skladba-projektu/", "investice/",
            "lokalita/", "galerie/", "kontakt/",
            "ochrana-osobnich-udaju/", "zasady-pouzivani-cookies/"]
    polozky = "".join(
        f"  <url><loc>{W['url']}/{u}</loc><lastmod>{DNES_ISO}</lastmod>"
        f"<priority>{'1.0' if u == '' else '0.8' if u in ('predmet-prodeje/', 'investice/') else '0.6'}</priority></url>\n"
        for u in urls
    )
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{polozky}</urlset>\n'
    )

    if os.path.exists("CNAME"):
        shutil.copyfile("CNAME", os.path.join(ROOT, "CNAME"))


# ---------------------------------------------------------------- main

def main():
    stranky = [page_index, page_predmet, page_skladba, page_investice,
               page_lokalita, page_galerie, page_kontakt,
               page_gdpr, page_cookies, page_404]
    celkem = 0
    for f in stranky:
        celkem += f()
    doplnky()

    chybi = [k for k in W if isinstance(W[k], str) and W[k].startswith("DOPLNIT")]
    print(f"Vygenerováno {len(stranky)} stránek ({celkem/1024:.0f} kB HTML) do {ROOT}/")
    if chybi:
        print("Čeká na doplnění v data/projekt.json (na web se zatím nevypisuje):")
        for k in chybi:
            print(f"  · {k}")


if __name__ == "__main__":
    main()
