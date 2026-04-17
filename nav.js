// nav.js — ไอหมอก v6 — auto-generated 2026-04-17
// ✅ ครบทุกหมวด 30 หมวด
(function() {
  var SITE_NAME = "ไอหมอก";
  var PRIMARY   = "#1e40af";
  var DARK      = "#0f172a";

  var MAIN_CATS = [
    { label: "ข่าวสาร", href: "news.html" },
    { label: "ไลฟ์สไตล์", href: "lifestyle.html" },
    { label: "สุขภาพ", href: "health.html" },
    { label: "อาหาร", href: "food.html" },
    { label: "การเงิน", href: "finance.html" },
    { label: "เทคโนโลยี", href: "technology.html" },
    { label: "บันเทิง", href: "entertainment.html" },
    { label: "travel", href: "travel.html" },
  ];

  var EXTRA_CATS = [
    { label: "ดูดวง", href: "horoscope.html" },
    { label: "เรื่องลี้ลับ", href: "ghost.html" },
    { label: "หวย", href: "lottery.html" },
    { label: "ความงาม", href: "beauty.html" },
    { label: "กีฬา", href: "sport.html" },
    { label: "การศึกษา", href: "education.html" },
    { label: "เกมมิ่ง", href: "gaming.html" },
    { label: "ดีไอวาย", href: "diy.html" },
    { label: "สัตว์เลี้ยง", href: "pet.html" },
    { label: "รถยนต์", href: "car.html" },
    { label: "กฎหมาย", href: "law.html" },
    { label: "ธุรกิจ", href: "business.html" },
    { label: "อนิเมะ", href: "anime.html" },
    { label: "ภาพยนตร์", href: "movie.html" },
    { label: "ทำอาหาร", href: "cooking.html" },
    { label: "นิทาน/เรื่องเล่า", href: "story.html" },
    { label: "ตลก", href: "comedy.html" },
    { label: "เคล็ดลับ", href: "tips.html" },
    { label: "นิทานพื้นบ้าน", href: "story.html" },
    { label: "การ์ตูน", href: "story.html" },
    { label: "ละคร/ดราม่า", href: "entertainment.html" },
    { label: "สร้างแรงบันดาลใจ", href: "lifestyle.html" },
  ];

  function renderNav() {
    var nav = document.querySelector('nav');
    if (!nav) return;

    var currentPage = location.pathname.split('/').pop() || '/';

    // สร้าง main links
    var mainHTML = MAIN_CATS.map(function(item) {
      var active = currentPage === item.href;
      return '<a href="' + item.href + '" style="color:#fff;text-decoration:none;'
        + 'padding:.4rem .65rem;border-radius:6px;font-size:.88rem;font-weight:600;white-space:nowrap;'
        + (active ? 'background:rgba(255,255,255,.22);' : 'opacity:.88;')
        + 'transition:background .18s;" '
        + 'onmouseover="this.style.background='rgba(255,255,255,.18)'" '
        + 'onmouseout="this.style.background='' + (active ? 'rgba(255,255,255,.22)' : '') + ''">'
        + item.label + '</a>';
    }).join('');

    // สร้าง dropdown "เพิ่มเติม"
    var dropHTML = EXTRA_CATS.map(function(item) {
      var active = currentPage === item.href;
      return '<a href="' + item.href + '" style="display:block;padding:.45rem .85rem;'
        + 'color:#1e293b;text-decoration:none;font-size:.85rem;font-weight:' + (active ? '700' : '500') + ';'
        + 'background:' + (active ? '#e0f2fe' : 'transparent') + ';'
        + 'transition:background .15s;" '
        + 'onmouseover="this.style.background='#f1f5f9'" '
        + 'onmouseout="this.style.background='' + (active ? '#e0f2fe' : 'transparent') + ''">'
        + item.label + '</a>';
    }).join('');

    nav.style.cssText = 'position:sticky;top:0;z-index:999;background:' + PRIMARY
      + ';box-shadow:0 2px 10px rgba(0,0,0,.22);font-family:Sarabun,sans-serif;';

    nav.innerHTML = [
      '<div style="max-width:1140px;margin:0 auto;padding:0 1rem;display:flex;align-items:center;gap:.25rem;height:52px;">',
      // Logo
      '<a href="/" style="color:#fff;text-decoration:none;font-size:1.15rem;font-weight:800;',
      'letter-spacing:.02em;margin-right:.75rem;flex-shrink:0;white-space:nowrap;">' + SITE_NAME + '</a>',
      // Main links (desktop)
      '<div class="nav-main" style="display:flex;align-items:center;gap:.15rem;flex:1;overflow:hidden;flex-wrap:nowrap;">',
      mainHTML,
      '</div>',
      // Dropdown เพิ่มเติม
      '<div class="nav-more" style="position:relative;flex-shrink:0;">',
      '<button id="nav-more-btn" style="background:rgba(255,255,255,.15);border:none;color:#fff;',
      'padding:.38rem .75rem;border-radius:6px;cursor:pointer;font-family:inherit;font-size:.85rem;',
      'font-weight:600;display:flex;align-items:center;gap:.35rem;" ',
      'onclick="(function(){var d=document.getElementById('nav-more-drop');',
      'd.style.display=d.style.display==='block'?'none':'block';})()" >',
      'เพิ่มเติม <span style="font-size:.65rem;">▼</span></button>',
      '<div id="nav-more-drop" style="display:none;position:absolute;top:calc(100% + 6px);right:0;',
      'background:#fff;border-radius:10px;box-shadow:0 8px 28px rgba(0,0,0,.18);',
      'min-width:160px;max-height:70vh;overflow-y:auto;z-index:9999;padding:.35rem 0;">',
      dropHTML,
      '</div></div>',
      // Hamburger (mobile)
      '<button id="nav-ham" style="display:none;background:none;border:none;color:#fff;',
      'font-size:1.3rem;cursor:pointer;padding:.3rem .5rem;margin-left:.5rem;" ',
      'onclick="(function(){var m=document.getElementById('nav-mobile');',
      'm.style.display=m.style.display==='flex'?'none':'flex';})()" >☰</button>',
      '</div>',
      // Mobile menu
      '<div id="nav-mobile" style="display:none;flex-direction:column;background:' + DARK + ';',
      'padding:.6rem 1rem 1rem;gap:.2rem;flex-wrap:wrap;">',
      MAIN_CATS.concat(EXTRA_CATS).map(function(item) {
        return '<a href="' + item.href + '" style="color:rgba(255,255,255,.88);text-decoration:none;',
          'padding:.4rem .6rem;border-radius:6px;font-size:.9rem;font-weight:500;">' + item.label + '</a>';
      }).join(''),
      '</div>',
      // Responsive CSS
      '<style>@media(max-width:760px){.nav-main{display:none!important;}.nav-more{display:none!important;}#nav-ham{display:block!important;}}</style>',
    ].join('');

    // ปิด dropdown เมื่อคลิกข้างนอก
    document.addEventListener('click', function(e) {
      var btn  = document.getElementById('nav-more-btn');
      var drop = document.getElementById('nav-more-drop');
      if (drop && btn && !btn.contains(e.target) && !drop.contains(e.target)) {
        drop.style.display = 'none';
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderNav);
  } else {
    renderNav();
  }
})();
