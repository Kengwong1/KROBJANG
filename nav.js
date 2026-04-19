// nav.js — ไอหมอก — 2-row layout (auto-generated)
(function() {
  var SITE_NAME = "ไอหมอก";
  var PRIMARY   = "#1e40af";
  var DARK      = "#0f172a";

  var ROW1 = [
    { label: "ข่าวสาร",    href: "news.html" },
    { label: "ไลฟ์สไตล์", href: "lifestyle.html" },
    { label: "สุขภาพ",     href: "health.html" },
    { label: "อาหาร",      href: "food.html" },
    { label: "การเงิน",    href: "finance.html" },
    { label: "เทคโนโลยี", href: "technology.html" },
    { label: "บันเทิง",    href: "entertainment.html" },
    { label: "travel",      href: "travel.html" },
    { label: "ดูดวง",      href: "horoscope.html" },
    { label: "เรื่องลี้ลับ", href: "ghost.html" },
    { label: "หวย",        href: "lottery.html" },
  ];

  var ROW2 = [
    { label: "ความงาม",    href: "beauty.html" },
    { label: "กีฬา",       href: "sport.html" },
    { label: "การศึกษา",  href: "education.html" },
    { label: "เกมมิ่ง",   href: "gaming.html" },
    { label: "ดีไอวาย",   href: "diy.html" },
    { label: "สัตว์เลี้ยง", href: "pet.html" },
    { label: "รถยนต์",    href: "car.html" },
    { label: "กฎหมาย",    href: "law.html" },
    { label: "ธุรกิจ",     href: "business.html" },
    { label: "อนิเมะ",    href: "anime.html" },
    { label: "ภาพยนตร์",  href: "movie.html" },
    { label: "ทำอาหาร",   href: "cooking.html" },
    { label: "นิทาน/เรื่องเล่า", href: "story.html" },
    { label: "ตลก",        href: "comedy.html" },
    { label: "เคล็ดลับ",  href: "tips.html" },
    { label: "นิทานพื้นบ้าน", href: "folktale.html" },
    { label: "การ์ตูน",   href: "cartoon.html" },
    { label: "ละคร/ดราม่า", href: "drama.html" },
    { label: "สร้างแรงบันดาลใจ", href: "inspirational.html" },
  ];

  var ALL = ROW1.concat(ROW2);

  function makeLink(item, currentPage, opts) {
    opts = opts || {};
    var active = currentPage === item.href;
    var el = document.createElement('a');
    el.href = item.href;
    el.textContent = item.label;
    if (opts.pill) {
      el.style.cssText = [
        'display:inline-flex;align-items:center;',
        'padding:.22rem .7rem;border-radius:999px;',
        'font-size:.78rem;font-weight:600;',
        'text-decoration:none;white-space:nowrap;',
        'transition:background .18s,color .18s;',
        active ? 'background:rgba(255,255,255,.95);color:#1e40af;'
               : 'background:rgba(255,255,255,.13);color:rgba(255,255,255,.92);',
      ].join('');
      el.addEventListener('mouseover', function() {
        if (!active) this.style.background = 'rgba(255,255,255,.25)';
      });
      el.addEventListener('mouseout', function() {
        if (!active) this.style.background = 'rgba(255,255,255,.13)';
      });
    } else {
      el.style.cssText = [
        'padding:.38rem .72rem;border-radius:7px;',
        'font-size:.88rem;font-weight:700;',
        'text-decoration:none;white-space:nowrap;',
        'transition:background .18s;',
        active ? 'background:rgba(255,255,255,.22);color:#fff;'
               : 'color:rgba(255,255,255,.92);',
      ].join('');
      el.addEventListener('mouseover', function() {
        if (!active) this.style.background = 'rgba(255,255,255,.15)';
      });
      el.addEventListener('mouseout', function() {
        if (!active) this.style.background = '';
      });
    }
    return el;
  }

  function renderNav() {
    var nav = document.querySelector('nav');
    if (!nav) return;
    var currentPage = location.pathname.split('/').pop() || 'index.html';

    nav.style.cssText = [
      'position:sticky;top:0;z-index:999;',
      'background:#1e40af;',
      'box-shadow:0 2px 12px rgba(0,0,0,.25);',
      'font-family:Sarabun,sans-serif;',
    ].join('');

    // แถว 1
    var row1 = document.createElement('div');
    row1.style.cssText = 'max-width:1200px;margin:0 auto;padding:0 1rem;display:flex;align-items:center;gap:.3rem;height:48px;overflow-x:auto;scrollbar-width:none;';

    var logo = document.createElement('a');
    logo.href = '/';
    logo.textContent = SITE_NAME;
    logo.style.cssText = 'color:#fff;text-decoration:none;font-size:1.15rem;font-weight:800;letter-spacing:.03em;margin-right:.6rem;flex-shrink:0;';
    row1.appendChild(logo);

    ROW1.forEach(function(item) {
      row1.appendChild(makeLink(item, currentPage, {}));
    });

    var ham = document.createElement('button');
    ham.id = 'nav-ham-btn';
    ham.innerHTML = '☰';
    ham.style.cssText = 'display:none;margin-left:auto;background:none;border:none;color:#fff;font-size:1.3rem;cursor:pointer;padding:.3rem .5rem;flex-shrink:0;';
    row1.appendChild(ham);

    // Mobile menu
    var mobileMenu = document.createElement('div');
    mobileMenu.style.cssText = 'display:none;flex-wrap:wrap;background:#0f172a;padding:.6rem 1rem 1rem;gap:.3rem;';
    ALL.forEach(function(item) {
      var a = document.createElement('a');
      a.href = item.href;
      a.textContent = item.label;
      a.style.cssText = 'color:rgba(255,255,255,.88);text-decoration:none;padding:.35rem .6rem;border-radius:6px;font-size:.88rem;font-weight:500;';
      mobileMenu.appendChild(a);
    });
    ham.addEventListener('click', function() {
      mobileMenu.style.display = mobileMenu.style.display === 'flex' ? 'none' : 'flex';
    });

    // แถว 2
    var row2 = document.createElement('div');
    row2.className = 'nav-row2';
    row2.style.cssText = 'background:rgba(0,0,0,.18);border-top:1px solid rgba(255,255,255,.08);overflow-x:auto;scrollbar-width:none;';
    var row2inner = document.createElement('div');
    row2inner.style.cssText = 'max-width:1200px;margin:0 auto;padding:.35rem 1rem;display:flex;align-items:center;gap:.35rem;flex-wrap:nowrap;';
    ROW2.forEach(function(item) {
      row2inner.appendChild(makeLink(item, currentPage, { pill: true }));
    });
    row2.appendChild(row2inner);

    var style = document.createElement('style');
    style.textContent = '.nav-row2{display:block;}div::-webkit-scrollbar{display:none;}@media(max-width:700px){.nav-row2{display:none!important;}#nav-ham-btn{display:block!important;}}';

    nav.innerHTML = '';
    nav.appendChild(style);
    nav.appendChild(row1);
    nav.appendChild(row2);
    nav.appendChild(mobileMenu);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderNav);
  } else {
    renderNav();
  }
})();
