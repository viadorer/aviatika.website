# -*- coding: utf-8 -*-
"""Převede zdrojové obrázky z images/ do web/assets/img/ v podobě, kterou
unese web: JPEG + WebP ve třech velikostech (1800 / 900 / 480 px).

Zdrojové PNG mají kolem 1 MB kus, výstupní JPEG vychází na desítky kB.
Mapování zdroj → výstupní název je v data/projekt.json v bloku "foto",
takže se přidává fotka bez zásahu do kódu.

Spuštění:  python3 build_images.py          (dopočítá jen chybějící)
           python3 build_images.py --all    (přegeneruje všechno)
"""
import json, os, sys
from PIL import Image

SRC = "images"
DST = "web/assets/img"

SIRKY = {"": 1800, "thumb": 900, "small": 480}
Q_JPEG = 82
Q_WEBP = 78

FORCE = "--all" in sys.argv


def aktualni(out, src):
    """True, pokud se výstup nemusí generovat znovu."""
    if FORCE or not os.path.exists(out):
        return False
    return os.path.getmtime(out) >= os.path.getmtime(src)


def uloz(im, out, sirka):
    if im.width > sirka:
        im = im.resize((sirka, round(im.height * sirka / im.width)), Image.LANCZOS)
    if out.endswith(".webp"):
        im.save(out, "WEBP", quality=Q_WEBP, method=6)
    else:
        im.save(out, "JPEG", quality=Q_JPEG, optimize=True, progressive=True)
    return im.size


def main():
    data = json.load(open("data/projekt.json", encoding="utf-8"))
    foto = {k: v for k, v in data["foto"].items() if not k.startswith("_")}

    for pod in SIRKY:
        os.makedirs(os.path.join(DST, pod), exist_ok=True)

    rozmery = {}
    hotovo = preskoceno = chybi = 0

    for jmeno, meta in sorted(foto.items()):
        src = os.path.join(SRC, meta["zdroj"])
        if not os.path.exists(src):
            print(f"  CHYBÍ ZDROJ: {meta['zdroj']}  (klíč {jmeno})")
            chybi += 1
            continue

        cile = []
        for pod, sirka in SIRKY.items():
            for pripona in (".jpg", ".webp"):
                cile.append((os.path.join(DST, pod, jmeno + pripona), sirka))

        if all(aktualni(o, src) for o, _ in cile):
            preskoceno += 1
        else:
            with Image.open(src) as im:
                # Průhledné PNG (logo, portrét) se podkládají bílou — JPEG alfu neumí
                # a šedý podklad by se na bílé stránce projevil jako špinavý okraj.
                if im.mode in ("RGBA", "LA", "P"):
                    im = im.convert("RGBA")
                    podklad = Image.new("RGB", im.size, (255, 255, 255))
                    podklad.paste(im, mask=im.split()[-1])
                    im = podklad
                else:
                    im = im.convert("RGB")
                for out, sirka in cile:
                    uloz(im, out, sirka)
                    hotovo += 1

        # Skutečné rozměry si build.py doplní do width/height a srcset —
        # deskriptor v srcset nesmí lhát, jinak prohlížeč vybere špatnou variantu.
        rozmery[jmeno] = {}
        for pod in SIRKY:
            with Image.open(os.path.join(DST, pod, jmeno + ".jpg")) as im:
                rozmery[jmeno][pod or "full"] = [im.width, im.height]

    json.dump(rozmery, open("data/rozmery.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)

    def mb(d):
        return sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d)
                   if os.path.isfile(os.path.join(d, f))) / 1048576

    print(f"Vygenerováno {hotovo} souborů, přeskočeno {preskoceno} aktuálních"
          + (f", CHYBÍ {chybi} zdrojů" if chybi else "") + ".")
    print(f"Rozměry uloženy pro {len(rozmery)} obrázků do data/rozmery.json")
    for pod in SIRKY:
        cesta = os.path.join(DST, pod)
        print(f"  {cesta:26} {mb(cesta):6.2f} MB")


if __name__ == "__main__":
    main()
