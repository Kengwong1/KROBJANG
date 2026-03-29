(function(){
var CSS=`
header.site-header{background:linear-gradient(135deg,#1a1040 0%,#2d1b69 50%,#1a1040 100%);padding:0.75rem 1.25rem;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 20px rgba(106,76,147,0.4);position:sticky;top:0;z-index:1000;margin:0;box-sizing:border-box;}
.site-logo{font-family:'Sarabun',sans-serif;font-weight:800;font-size:1.3rem;color:#fff;text-decoration:none;letter-spacing:0.02em;white-space:nowrap;}
.site-logo span{color:#FFD166;}
.nav-toggle{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:6px;border-radius:8px;background:rgba(255,255,255,0.08);border:none;transition:background 0.2s;box-sizing:border-box;}
.nav-toggle:hover{background:rgba(255,255,255,0.15);}
.nav-toggle span{display:block;width:22px;height:2px;background:#fff;border-radius:2px;transition:all 0.3s ease;transform-origin:center;}
.nav-toggle.open span:nth-child(1){transform:translateY(7px) rotate(45deg);}
.nav-toggle.open span:nth-child(2){opacity:0;transform:scaleX(0);}
.nav-toggle.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg);}
nav.site-main-nav{background:#fff;border-bottom:1px solid #ede8f5;box-shadow:0 2px 8px rgba(106,76,147,0.08);margin:0;padding:0;box-sizing:border-box;}
nav.site-main-nav .nav-wrap{display:flex;flex-wrap:wrap;justify-content:center;gap:0;max-width:1200px;margin:0 auto;padding:0 0.5rem;box-sizing:border-box;overflow-x:auto;white-space:nowrap;}
nav.site-main-nav .nav-wrap a{display:inline-flex;align-items:center;gap:0.4rem;padding:0.65rem 0.85rem;font-family:'Sarabun',sans-serif;font-size:0.88rem;font-weight:600;color:#3d2b6b;text-decoration:none;border-bottom:3px solid transparent;transition:all 0.2s ease;white-space:nowrap;box-sizing:border-box;}
nav.site-main-nav .nav-wrap a:hover{color:#6A4C93;background:#f5f0ff;border-bottom-color:#c4a8ff;}
nav.site-main-nav .nav-wrap a.active{color:#6A4C93;border-bottom-color:#6A4C93;background:#f5f0ff;}
nav.site-main-nav .nav-wrap a i{font-size:0.9rem;}
.site-nav-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:998;opacity:0;transition:opacity 0.3s;}
.site-nav-overlay.show{display:block;opacity:1;}
@media(max-width:768px){
.nav-toggle{display:flex;}
nav.site-main-nav{position:fixed;top:0;right:-280px;width:280px;height:100vh;background:#1a1040;z-index:999;transition:right 0.3s ease;box-shadow:-4px 0 20px rgba(0,0,0,0.3);overflow-y:auto;padding-top:70px;border-bottom:none;}
nav.site-main-nav.open{right:0;}
nav.site-main-nav .nav-wrap{flex-direction:column;flex-wrap:nowrap;padding:0.5rem 0;gap:0;white-space:normal;}
nav.site-main-nav .nav-wrap a{color:#e0d6ff;padding:0.9rem 1.5rem;border-bottom:1px solid rgba(255,255,255,0.06);border-left:3px solid transparent;font-size:0.95rem;justify-content:flex-start;display:flex;}
nav.site-main-nav .nav-wrap a:hover,nav.site-main-nav .nav-wrap a.active{background:rgba(255,255,255,0.08);border-left-color:#FFD166;border-bottom-color:rgba(255,255,255,0.06);color:#FFD166;}
nav.site-main-nav .nav-wrap a i{font-size:1rem;width:20px;text-align:center;}
}`;
var HTML=`
<header class="site-header">
<a href="index.html" class="site-logo">ครบจัง<span>ดอทคอม</span></a>
<button class="nav-toggle" id="navToggle" aria-label="เปิดเมนู"><span></span><span></span><span></span></button>
</header>
<div class="site-nav-overlay" id="navOverlay"></div>
<nav class="site-main-nav" id="mainNav">
<div class="nav-wrap">
<a href="index.html" data-page="index"><i class="fas fa-home" style="color:#45B7D1;"></i> หน้าแรก</a>
<a href="news.html" data-page="news"><i class="fas fa-bolt" style="color:#FF6B6B;"></i> ข่าวด่วน</a>
<a href="lotto.html" data-page="lotto"><i class="fas fa-ticket-alt" style="color:#FFD166;"></i> ตรวจหวย</a>
<a href="horoscope.html" data-page="horoscope"><i class="fas fa-star" style="color:#c084fc;"></i> ดูดวง</a>
<a href="sport.html" data-page="sport"><i class="fas fa-futbol" style="color:#E76F51;"></i> กีฬา</a>
<a href="video.html" data-page="video"><i class="fas fa-play-circle" style="color:#FF9F1C;"></i> วีดีโอ</a>
<a href="ai.html" data-page="ai"><i class="fas fa-robot" style="color:#2EC4B6;"></i> AI</a>
<a href="food.html" data-page="food"><i class="fas fa-utensils" style="color:#F59E0B;"></i> อาหาร</a>
<a href="health.html" data-page="health"><i class="fas fa-heartbeat" style="color:#10B981;"></i> สุขภาพ</a>
<a href="finance.html" data-page="finance"><i class="fas fa-coins" style="color:#F59E0B;"></i> การเงิน</a>
<a href="lifestyle.html" data-page="lifestyle"><i class="fas fa-heart" style="color:#ec4899;"></i> ไลฟ์สไตล์</a>
<a href="games.html" data-page="games"><i class="fas fa-gamepad" style="color:#E76F51;"></i> เกมส์</a>
<a href="shopping.html" data-page="shopping"><i class="fas fa-shopping-bag" style="color:#4ECDC4;"></i> ช้อป</a>
<a href="booking.html" data-page="booking"><i class="fas fa-umbrella-beach" style="color:#45B7D1;"></i> ท่องเที่ยว</a>
<a href="contact.html" data-page="contact"><i class="fas fa-headset" style="color:#a78bfa;"></i> ติดต่อเรา</a>
</div>
</nav>
<nav class="bottom-nav" id="bottomNav">
<div class="bottom-nav-inner">
<a href="index.html" data-page="index"><i class="fas fa-home"></i>หน้าแรก</a>
<a href="news.html" data-page="news"><i class="fas fa-bolt"></i>ข่าว</a>
<a href="horoscope.html" data-page="horoscope"><i class="fas fa-star"></i>ดวง</a>
<a href="lotto.html" data-page="lotto"><i class="fas fa-ticket-alt"></i>หวย</a>
<a href="food.html" data-page="food"><i class="fas fa-utensils"></i>อาหาร</a>
</div>
</nav>`;
var s=document.createElement('style');s.textContent=CSS;document.head.appendChild(s);
var w=document.createElement('div');w.innerHTML=HTML;var r=document.body.firstChild;
while(w.firstChild){document.body.insertBefore(w.firstChild,r);}
var page=location.pathname.split('/').pop().replace('.html','')||'index';
document.querySelectorAll('nav.site-main-nav .nav-wrap a[data-page], nav.bottom-nav a[data-page]').forEach(function(a){
if(a.dataset.page===page)a.classList.add('active');});
if(!document.querySelector('nav.site-main-nav .nav-wrap a.active')){
var cat=page.split('_')[0];
var m=document.querySelector('nav.site-main-nav .nav-wrap a[data-page="'+cat+'"]');
if(m)m.classList.add('active');}
if(!document.querySelector('nav.bottom-nav a.active')){
var cat2=page.split('_')[0];
var m2=document.querySelector('nav.bottom-nav a[data-page="'+cat2+'"]');
if(m2)m2.classList.add('active');}
var toggle=document.getElementById('navToggle');
var nav=document.getElementById('mainNav');
var overlay=document.getElementById('navOverlay');
function openMenu(){nav.classList.add('open');toggle.classList.add('open');overlay.classList.add('show');document.body.style.overflow='hidden';}
function closeMenu(){nav.classList.remove('open');toggle.classList.remove('open');overlay.classList.remove('show');document.body.style.overflow='';}
if(toggle)toggle.addEventListener('click',function(){nav.classList.contains('open')?closeMenu():openMenu();});
if(overlay)overlay.addEventListener('click',closeMenu);
document.querySelectorAll('nav.site-main-nav .nav-wrap a').forEach(function(a){
a.addEventListener('click',function(){if(window.innerWidth<=768)closeMenu();});});
})();
