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
- [ ] **Sladit čísla projektu — nejdůležitější bod.** Deklarované hodnoty
      z původního webu si odporovaly navzájem i s kalkulačkou:

      | Tvrzení na webu | Co z něj plyne |
      |---|---|
      | roční příjem 1,5–2,5 mil. při 2 500 Kč/noc | asi 5,5 pronajímané jednotky, ne 20 |
      | zhodnocení 50–80 % na hodnotu 15–18 mil. | CAPEX jen 0,4–4,1 mil. na dostavbu celého objektu |
      | hodnota po dokončení 15–18 mil. | při CAPEX 17 mil. je investice 24,9 mil., tedy ztráta 7–10 mil. |

      Dlaždice se proto už nezadávají ručně — výnos i zhodnocení se počítají
      z bloku `kalkulacka`, takže se s kalkulačkou nemohou rozejít. Samostatně
      zůstává jen `hodnota_po_dokonceni_min/max`, kterou z provozního modelu
      odvodit nelze. Když vyjde nižší než cena + CAPEX, web sám zobrazí
      upozornění, že projekt v tom modelu končí ve ztrátě.
      Doplnit je potřeba reálný odhad hodnoty a reálné parametry provozu.
- [ ] **Výchozí parametry kalkulačky** — blok `kalkulacka`. Řídí i dlaždice nad
      kalkulačkou, takže na nich teď záleží dvojnásob. Ověřit zvlášť
      `pocet_jednotek` (20), `adr` (2 500 Kč) a `opex_pct` (35 %, na ubytovací
      provoz nízké — nezahrnuje personál, energie, úklid ani provize portálů).
      CAPEX schválně zůstává 0: dokud se nedoplní, kalkulačka i dlaždice místo
      výnosu ukážou „—“ a vysvětlí proč.
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
