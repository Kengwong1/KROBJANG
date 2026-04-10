/* ไอหมอก — nav.js v2 */
(function(){
var SITE_NAME = "ไอหมอก";
var SITE_URL  = "https://krobjang.vercel.app/";
var CAT_TH    = {"news": "ข่าวสาร", "lifestyle": "ไลฟ์สไตล์", "health": "สุขภาพ", "food": "อาหาร", "finance": "การเงิน", "technology": "เทคโนโลยี", "entertainment": "บันเทิง"};
var NAV_LINKS = [{"href": "index.html", "icon": "fa-home", "text": "หน้าแรก"}, {"href": "news.html", "icon": "fa-tag", "text": "ข่าวสาร", "cat": "news"}, {"href": "lifestyle.html", "icon": "fa-tag", "text": "ไลฟ์สไตล์", "cat": "lifestyle"}, {"href": "health.html", "icon": "fa-tag", "text": "สุขภาพ", "cat": "health"}, {"href": "food.html", "icon": "fa-tag", "text": "อาหาร", "cat": "food"}, {"href": "finance.html", "icon": "fa-tag", "text": "การเงิน", "cat": "finance"}, {"href": "technology.html", "icon": "fa-tag", "text": "เทคโนโลยี", "cat": "technology"}, {"href": "entertainment.html", "icon": "fa-tag", "text": "บันเทิง", "cat": "entertainment"}];

function buildNav(){
  var cur = location.pathname.split("/").pop()||"index.html";
  var html = '<div class="nav-inner">';
  html += '<a class="nav-brand" href="index.html">'+SITE_NAME+'</a>';
  html += '<ul class="nav-links">';
  NAV_LINKS.forEach(function(l){
    var active = cur===l.href?" class=\"active\"":"";
    html += '<li><a href="'+l.href+'"'+active+'>';
    html += '<i class="fas '+l.icon+'" style="margin-right:.3rem;font-size:.8rem;"></i>'+l.text+'</a></li>';
  });
  html += '</ul>';
  html += '<div style="display:flex;align-items:center;gap:.5rem;"><button class='dark-toggle' onclick='toggleDark()' title='สลับ Dark/Light Mode'>🌙</button></div>';
  html += '</div>';
  var nav = document.querySelector("nav");
  if(nav) nav.innerHTML = html;
  else { var n=document.createElement("nav"); n.innerHTML=html; document.body.prepend(n); }
}

function initSearch(){
  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  if(!input||!results) return;
  input.addEventListener("input",function(){
    var q = this.value.trim().toLowerCase();
    if(q.length<2){results.innerHTML="";return;}
    fetch("search-index.json").then(function(r){return r.json();}).then(function(data){
      var hits = data.filter(function(a){
        return a.title.toLowerCase().includes(q)||a.snippet.toLowerCase().includes(q);
      }).slice(0,8);
      results.innerHTML = hits.length
        ? hits.map(function(a){
            return '<a href="'+a.file+'" style="display:block;padding:.5rem .75rem;border-bottom:1px solid var(--border);text-decoration:none;color:var(--text);">'
              +'<span style="font-size:.78rem;color:var(--primary);font-weight:600;">'+(CAT_TH[a.cat]||a.cat)+'</span> '
              +a.title+'</a>';
          }).join("")
        : '<p style="padding:.5rem .75rem;color:var(--muted);font-size:.88rem;">ไม่พบผลลัพธ์</p>';
    }).catch(function(){});
  });
  document.addEventListener("click",function(e){
    if(!input.contains(e.target)&&!results.contains(e.target)) results.innerHTML="";
  });
}


function toggleDark() {
  document.body.classList.toggle('dark-mode');
  var btn = document.querySelector('.dark-toggle');
  if (btn) btn.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
  try { localStorage.setItem('darkMode', document.body.classList.contains('dark-mode') ? '1' : '0'); } catch(e) {}
}
(function(){ try { if(localStorage.getItem('darkMode')==='1') { document.body.classList.add('dark-mode'); var b=document.querySelector('.dark-toggle'); if(b) b.textContent='☀️'; } } catch(e) {} })();

document.addEventListener("DOMContentLoaded",function(){
  buildNav();
  initSearch();
});
})();
