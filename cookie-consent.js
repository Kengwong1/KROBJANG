// cookie-consent.js — ไอหมอก
(function(){
  if(localStorage.getItem('cookie_ok')) return;
  var banner=document.getElementById('cookie-banner');
  if(!banner) return;
  banner.style.display='flex';
  document.getElementById('cookie-accept').onclick=function(){
    localStorage.setItem('cookie_ok','1');
    banner.style.display='none';
  };
  var dec=document.getElementById('cookie-decline');
  if(dec) dec.onclick=function(){banner.style.display='none';};
})();