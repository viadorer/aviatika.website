# Aviatika Kovářská — prodejní web

Statický web (HTML + CSS + vanilla JS) generovaný Pythonem. Žádný framework,
žádná databáze. Nasazuje se na Vercel, obsah složky `web/` je hotový web.

## Struktura projektu

```
README.md                ← tenhle návod (schválně mimo web/, aby se nenasazoval)
data/projekt.json        ← VŠECHNA DATA: cena, kontakty, dispozice, lokalita, fotky
data/rozmery.json        ← rozměry obrázků, generuje build_images.py
build.py                 ← generátor stránek (spustit po každé změně dat)
build_images.py          ← převod obrázků z images/ do web/assets/img/
images/                  ← zdrojové obrázky (velké PNG, na web se nenasazují)
web/                     ← HOTOVÝ WEB — tuhle složku nasazuje Vercel
api/contact.js           ← serverless proxy na Realvisor CRM (běží na Vercelu)
```

## Jak něco změnit

**Cena, kontakty, dispozice, vzdálenosti** → uprav `data/projekt.json`, pak:

```bash
python3 build.py
```

Cena je v souboru jen jednou (`prodej.cena`) a propíše se do nadpisů, dlaždic,
kalkulačky i meta popisků. Ručně ji nikde nepřepisuj.

**Texty stránek** → přímo v `build.py` ve funkcích `page_*`.

**Fotografie** → přidej soubor do `images/`, zapiš ho do bloku `foto`
v `data/projekt.json` (klíč, `zdroj`, `alt`, `typ`), pak:

```bash
python3 build_images.py && python3 build.py
```

`build_images.py` z každého zdroje udělá JPEG i WebP ve třech velikostech
(1800 / 900 / 480 px). Přepočítává jen to, co chybí nebo se změnilo;
`--all` vynutí přegenerování všeho.

## Lokální náhled

```bash
python3 -m http.server 8890 --directory web
```

Kontaktní formulář lokálně neodešle — `/api/contact` běží až na Vercelu.

## Pojistka proti úniku placeholderů

Klíče `penb` a `dph_text` v bloku `web` fungují jako u sesterského projektu:
dokud jejich hodnota začíná slovem `DOPLNIT`, věta se na web vůbec nevypíše.
Placeholder se tedy nemůže dostat před návštěvníky. `build.py` na konci vypíše,
co ještě čeká na doplnění.

## Co ověřit před spuštěním

- [ ] **PENB** — třída energetické náročnosti. Původní web tvrdil u každé
      dispozice třídu A bez průkazu. Zákon č. 406/2000 Sb. vyžaduje uvedení
      třídy z průkazu; do doplnění klíče `penb` se na web nevypisuje nic.
- [ ] **DPH u kupní ceny** — klíč `dph_text`.
- [ ] **Licence tří fotek Krušných hor** — `krusne-hory-*.jpg` pocházejí ze
      zdrojů sesterského projektu penzionavionika.cz. Názvy souborů odpovídají
      Pixabay, ale původ není doložený. Ověřit, nebo nahradit vlastními.
- [ ] **Provozní parametry kalkulačky — blok `kalkulacka`.** Výchozí hodnoty
      pocházejí z původního webu a dávají nereálné výsledky:

      | Parametr | Hodnota | Problém |
      |---|---|---|
      | `capex` | 0 | Prodává se hrubá stavba, dostavba nemůže být zdarma. Web proto bez CAPEX výsledek vůbec nezobrazí. |
      | `pocet_jednotek` | 20 | Web nikde neuvádí, kolik jednotek objekt má. Ověřit. |
      | `adr` | 2 500 Kč | 20 × 2 500 × 182 = 9,1 mil. tržeb ročně. Ověřit. |
      | `opex_pct` | 35 % | Na ubytovací provoz nízké — nezahrnuje personál, energie, úklid, praní, pojištění, správu ani provize portálů. Reálně spíš 60–75 %. |

      Při výchozích hodnotách vycházel čistý zisk 5,9 mil. ročně proti kupní ceně
      7,9 mil., tedy návratnost 16 měsíců. Proto se provozní model už neukazuje
      jako headline — je jen v kalkulačce, kde si ho návštěvník zadá sám.
- [ ] **Odhad hodnoty po dokončení — dnes se nezveřejňuje.**
      Původní web tvrdil 15–18 mil. Nepodařilo se to doložit a proti vašim
      vlastním cenám to nesedí: Apartmány Avionika v téže obci prodávají
      15 dokončených jednotek o 392 m² za 34,95 mil., tedy 89 252 Kč/m².
      Při té hladině by 15–18 mil. odpovídalo jen 168–202 m² prodejné plochy,
      zhruba čtyřem bytům — zatímco kalkulačka počítá s dvaceti jednotkami.
      Klíče `hodnota_po_dokonceni_min/max` jsou proto `null` a sekce zatím
      ukazuje jen ověřená fakta. Jakmile vyplníte obě čísla, web sám přidá
      dlaždici s hodnotou i s rozdílem, ze kterého se hradí dostavba.
      K doložení stačí buď ocenění, nebo prodejní ceník jednotek Aviatiky.
- [ ] **Prodávající** — web uvádí PTF Reality, s.r.o., IČO 06684394 (Plzeň).
      Sesterský projekt prodává PTF reality PRAHA s.r.o., IČO 07666969.
      Zkontrolovat, která entita prodává tenhle projekt.
- [ ] **Turistické trasy a vzdálenosti v lokalitě** — původní web uváděl trasu
      „Kovářská – Meštery (5 km)“; takové místo v okolí Kovářské není, položka byla
      nahrazena doloženými cíli (Velký Špičák, Měděnec, Klínovec). Barvy značek
      a kilometry ověřit u KČT. Neověřené jsou i vzdálenosti v bloku
      `lokalita.skupiny` (občanská vybavenost, dojezdové časy) — převzato z původního webu.
- [ ] **Půdorysy jednotek** — do `web/assets/doc/`, odkázat ze skladby projektu.
- [ ] **Fotografie skutečného stavu stavby** — dnes web ukazuje jen vizualizace
      a všude to říká nahlas. Reálné fotky by prodeji pomohly.
- [ ] **Měřicí kódy** (GA4 / Meta Pixel) — navěsit až na události
      `consent:statistiky` a `consent:marketing`, viz níže.

## Cookies a GDPR

Cookie lišta se zobrazí při první návštěvě a volbu si pamatuje v `localStorage`.
Statistické a marketingové skripty se nesmí načítat dřív, než návštěvník udělí
souhlas — `web/assets/js/app.js` k tomu vysílá události `consent:statistiky`
a `consent:marketing`. Měřicí kódy navěs na ně, ne přímo do `<head>`.

Kontaktní formulář bez zaškrtnutého souhlasu neodešle.

## Nasazení

Vercel bere `outputDirectory: "web"` z `vercel.json`. Složka `api/` zůstává
v kořeni — Vercel z ní dělá serverless funkce nezávisle na output directory.

Formulář posílá data na `/api/contact`, což je proxy na Realvisor. API klíč je
v proměnné prostředí `REALVISOR_API_KEY` na Vercelu, v repozitáři není a nikdy
nebyl.

**Build na Vercelu:** projekt je bez `package.json`, takže Vercel nespustí
`build.py` sám. Buď generovaný `web/` commituj (výchozí stav), nebo nastav
Build Command na `python3 build_images.py && python3 build.py`.
