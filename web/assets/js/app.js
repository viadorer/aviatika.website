/* Aviatika — interakce webu
   Jeden soubor, žádné závislosti. Každý blok se aktivuje jen tehdy, když
   na stránce najde svůj kořenový prvek, takže se stejný skript může načíst
   všude. */
(function () {
  'use strict';

  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  var czk = function (n) {
    return Math.round(n).toLocaleString('cs-CZ').replace(/ /g, ' ') + ' Kč';
  };

  /* ---------- hlavička: průhledná nad hero, plná po odscrollování ---------- */
  var header = $('.site-header');
  if (header) {
    /* Na podstránkách bez hero musí být hlavička plná hned — jinak by bílý
       text nadpisu ležel na bílém pozadí. */
    if ($('.hero')) {
      var prepni = function () {
        header.classList.toggle('is-solid', window.scrollY > 80);
      };
      prepni();
      window.addEventListener('scroll', prepni, { passive: true });
    } else {
      header.classList.add('is-solid');
    }
  }

  /* ---------- mobilní navigace ---------- */
  var toggle = $('.nav-toggle'), nav = $('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) { header.classList.add('is-solid'); }
    });
    $$('a', nav).forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- rozbalovací dispozice ---------- */
  $$('.unit__head').forEach(function (head) {
    head.addEventListener('click', function () {
      var open = head.getAttribute('aria-expanded') === 'true';
      var body = document.getElementById(head.getAttribute('aria-controls'));
      head.setAttribute('aria-expanded', open ? 'false' : 'true');
      if (body) { body.hidden = open; }
    });
  });

  /* ---------- mapa ---------- */
  var mapEl = $('#map');
  if (mapEl && window.L && mapEl.dataset.lat) {
    var lat = parseFloat(mapEl.dataset.lat), lon = parseFloat(mapEl.dataset.lon);
    var map = L.map(mapEl, { scrollWheelZoom: false }).setView([lat, lon], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    L.marker([lat, lon]).addTo(map).bindPopup(mapEl.dataset.popis || '').openPopup();
  }

  /* ---------- projektová kalkulačka ---------- */
  var calc = $('#calc');
  if (calc && window.AVIATIKA_CFG) {
    var cfg = window.AVIATIKA_CFG.kalkulacka;

    var pole = ['cena', 'capex', 'jednotky', 'adr', 'obsazenost', 'opex', 'vlastni', 'urok', 'splatnost', 'zhodnoceni'];

    function hod(id, zaloha) {
      var el = document.getElementById('calc-' + id);
      if (!el) { return zaloha; }
      var v = parseFloat(el.value);
      return isNaN(v) ? zaloha : v;
    }
    function set(id, text) {
      var e = document.getElementById('out-' + id);
      if (e) { e.textContent = text; }
    }
    function popisek(id, text) {
      var e = document.getElementById('val-' + id);
      if (e) { e.textContent = text; }
    }

    /* Anuitní splátka. Při nulovém úroku by vzorec dělil nulou, proto
       se v tom případě jistina jen rozpočítá na počet měsíců. */
    function anuita(jistina, sazbaPct, let_) {
      if (jistina <= 0 || let_ <= 0) { return 0; }
      var r = sazbaPct / 100 / 12, n = let_ * 12;
      if (r === 0) { return jistina / n; }
      return jistina * r / (1 - Math.pow(1 + r, -n));
    }

    function prepocti() {
      var cena        = hod('cena', cfg.cena_projektu);
      var capex       = hod('capex', cfg.capex);
      var jednotky    = hod('jednotky', cfg.pocet_jednotek);
      var adr         = hod('adr', cfg.adr);
      var obsazenost  = hod('obsazenost', cfg.obsazenost_dni);
      var opex        = hod('opex', cfg.opex_pct);
      var vlastniPct  = hod('vlastni', cfg.vlastni_zdroje_pct);
      var urok        = hod('urok', cfg.urok_pct);
      var splatnost   = hod('splatnost', cfg.splatnost_let);
      var zhodnoceni  = hod('zhodnoceni', cfg.zhodnoceni_pct);

      var investice = cena + capex;
      var vlastni   = Math.round(investice * vlastniPct / 100);
      var uver      = investice - vlastni;

      var splatka   = anuita(uver, urok, splatnost);
      var rocneUver = splatka * 12;

      var trzby     = jednotky * adr * obsazenost;
      var naklady   = trzby * opex / 100;
      var cisty     = trzby - naklady;

      /* Zhodnocení a umořená jistina nejsou hotovost — do peněženky
         nepřitečou. Vykazují se odděleně od provozního cash flow, aby
         čísla nevypadala lépe, než jaká reálně jsou. */
      var umoreni   = splatnost > 0 ? uver / splatnost : 0;
      var prirustek = investice * zhodnoceni / 100;

      var cashflow  = cisty - rocneUver;
      var celkovy   = cashflow + umoreni + prirustek;
      var vynos     = vlastni > 0 ? (celkovy / vlastni) * 100 : 0;

      set('investice', czk(investice));
      set('vlastni', czk(vlastni));
      set('uver', czk(uver));
      set('splatka', czk(splatka) + ' / měs.');
      set('trzby', czk(trzby));
      set('naklady', '− ' + czk(naklady));
      set('cisty', czk(cisty));
      set('uver-rocne', '− ' + czk(rocneUver));
      set('cashflow', (cashflow >= 0 ? '+ ' : '− ') + czk(Math.abs(cashflow)));
      set('cashflow-mesic', (cashflow >= 0 ? '+ ' : '− ') + czk(Math.abs(cashflow / 12)) + ' / měs.');
      set('umoreni', '+ ' + czk(umoreni));
      set('prirustek', '+ ' + czk(prirustek));
      set('celkovy', (celkovy >= 0 ? '+ ' : '− ') + czk(Math.abs(celkovy)));
      /* Bez CAPEX je výnos spočítaný z nedostavěného objektu. Číslo se proto
         vůbec nezobrazí — jinak by headline tvrdil stovky procent ročně. */
      set('vynos', capex > 0 ? vynos.toFixed(1).replace('.', ',') + ' % ročně' : '—');

      popisek('vlastni', vlastniPct + ' %');
      popisek('urok', urok.toFixed(2).replace('.', ',') + ' %');
      popisek('splatnost', splatnost + ' let');
      popisek('opex', opex + ' %');
      popisek('obsazenost', obsazenost + ' dní');
      popisek('zhodnoceni', zhodnoceni.toFixed(1).replace('.', ',') + ' %');

      var cfEl = document.getElementById('out-cashflow');
      if (cfEl) { cfEl.style.color = cashflow >= 0 ? '#8FD8B4' : '#F0A9A2'; }

      /* Předmětem prodeje je hrubá stavba. Bez nákladů na dokončení model
         počítá tržby z objektu, který se za nic nedostavěl — vyjde nesmyslně
         vysoký výnos. Dokud je CAPEX nula, je potřeba to říct nahlas. */
      var warn = document.getElementById('calc-warn');
      if (warn) {
        if (capex <= 0) {
          warn.textContent = 'Doplňte náklady na dokončení. Prodává se hrubá stavba — '
            + 'bez odhadu CAPEX model počítá tržby z objektu, který se dostavěl zadarmo, '
            + 'a výnos proto vychází nereálně vysoký.';
          warn.classList.add('is-on');
        } else {
          warn.classList.remove('is-on');
        }
      }
    }

    pole.forEach(function (id) {
      var el = document.getElementById('calc-' + id);
      if (el) {
        el.addEventListener('input', prepocti);
        el.addEventListener('change', prepocti);
      }
    });
    prepocti();
  }

  /* ---------- lightbox ---------- */
  var lb = $('.lightbox');
  if (lb) {
    var lbImg = $('img', lb), polozky = $$('[data-lightbox]'), idx = 0, odkud = null;

    /* Prohlížeče bez WebP dostanou původní JPEG. */
    var webpOk = (function () {
      try {
        return document.createElement('canvas').toDataURL('image/webp').indexOf('data:image/webp') === 0;
      } catch (e) { return false; }
    })();

    function otevri(i) {
      if (!polozky.length) { return; }
      idx = (i + polozky.length) % polozky.length;
      var a = polozky[idx];
      lbImg.src = webpOk ? a.href.replace(/\.jpg$/i, '.webp') : a.href;
      lbImg.alt = a.dataset.alt || '';
      lb.classList.add('is-open');
      lb.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      $('.lb-close', lb).focus();
    }
    function zavri() {
      lb.classList.remove('is-open');
      lb.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      /* Focus zpět na fotku, ze které se galerie otevřela. */
      if (odkud) { odkud.focus(); odkud = null; }
    }

    polozky.forEach(function (a, i) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        odkud = a;
        otevri(i);
      });
    });

    $('.lb-close', lb).addEventListener('click', zavri);
    $('.lb-prev', lb).addEventListener('click', function (e) { e.stopPropagation(); otevri(idx - 1); });
    $('.lb-next', lb).addEventListener('click', function (e) { e.stopPropagation(); otevri(idx + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) { zavri(); } });

    /* Focus nesmí utéct z otevřené galerie na stránku pod ní. */
    lb.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') { return; }
      var f = $$('button', lb), prvni = f[0], posledni = f[f.length - 1];
      if (e.shiftKey && document.activeElement === prvni) { e.preventDefault(); posledni.focus(); }
      else if (!e.shiftKey && document.activeElement === posledni) { e.preventDefault(); prvni.focus(); }
    });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('is-open')) { return; }
      if (e.key === 'Escape') { zavri(); }
      if (e.key === 'ArrowLeft') { otevri(idx - 1); }
      if (e.key === 'ArrowRight') { otevri(idx + 1); }
    });
  }

  /* ---------- kontaktní formulář → /api/contact (Realvisor) ---------- */
  $$('form[data-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var msg = $('.form-msg', form);
      var btn = $('[type=submit]', form);

      function zprava(druh, text) {
        if (!msg) { window.alert(text); return; }
        msg.className = 'form-msg is-on form-msg--' + druh;
        msg.textContent = text;
      }

      var data = new FormData(form);
      if (!data.get('souhlas')) {
        zprava('err', 'Pro odeslání je potřeba potvrdit souhlas se zpracováním osobních údajů.');
        return;
      }

      var jmeno = (data.get('jmeno') || '').trim();
      var mezera = jmeno.indexOf(' ');

      var payload = {
        firstName: mezera > 0 ? jmeno.slice(0, mezera) : jmeno,
        lastName:  mezera > 0 ? jmeno.slice(mezera + 1) : '',
        email:     (data.get('email') || '').trim(),
        phone:     (data.get('telefon') || '').trim(),
        message:   (data.get('zprava') || '').trim(),
        data: { source: 'web', interest: data.get('zajem') || 'Koupě celého projektu' }
      };

      var puvodni = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Odesílám…'; }

      fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (r) {
          if (!r.ok) { throw new Error('HTTP ' + r.status); }
          form.reset();
          zprava('ok', 'Děkujeme, poptávku jsme přijali. Ozveme se nejpozději následující pracovní den.');
        })
        .catch(function () {
          zprava('err', 'Odeslání se nezdařilo. Zavolejte nám prosím na ' +
            (window.AVIATIKA_CFG ? window.AVIATIKA_CFG.tel : '+420 774 052 232') + '.');
        })
        .then(function () {
          if (btn) { btn.disabled = false; btn.textContent = puvodni; }
        });
    });
  });

  /* ---------- cookie lišta ---------- */
  var bar = $('.cookiebar');
  if (bar) {
    var KLIC = 'aviatika_cookie_v1';
    var ulozeno = null;
    try { ulozeno = JSON.parse(localStorage.getItem(KLIC)); } catch (e) { ulozeno = null; }

    /* Měřicí kódy se navěšují na tyhle události, nikdy ne přímo do <head> —
       jinak by se načetly dřív, než návštěvník souhlas udělí. */
    function aktivuj(c) {
      if (c && c.statistiky) { document.dispatchEvent(new CustomEvent('consent:statistiky')); }
      if (c && c.marketing)  { document.dispatchEvent(new CustomEvent('consent:marketing')); }
    }
    function uloz(c) {
      c.ts = new Date().toISOString();
      try { localStorage.setItem(KLIC, JSON.stringify(c)); } catch (e) {}
      bar.classList.remove('is-on');
      aktivuj(c);
    }

    if (ulozeno) { aktivuj(ulozeno); } else { bar.classList.add('is-on'); }

    var prefs = $('.cookiebar__prefs', bar);
    var akce = {
      all:  function () { uloz({ nezbytne: true, statistiky: true,  marketing: true  }); },
      none: function () { uloz({ nezbytne: true, statistiky: false, marketing: false }); },
      prefs: function () {
        if (prefs) { prefs.classList.add('is-on'); }
        bar.classList.add('prefs-open');
      },
      save: function () {
        uloz({
          nezbytne: true,
          statistiky: $('#ck-stat', bar) ? $('#ck-stat', bar).checked : false,
          marketing:  $('#ck-mark', bar) ? $('#ck-mark', bar).checked : false
        });
      }
    };
    $$('[data-cookie]', bar).forEach(function (b) {
      var f = akce[b.dataset.cookie];
      if (f) { b.addEventListener('click', f); }
    });
    $$('[data-cookie-open]').forEach(function (a) {
      a.addEventListener('click', function (e) { e.preventDefault(); bar.classList.add('is-on'); });
    });
  }
})();
