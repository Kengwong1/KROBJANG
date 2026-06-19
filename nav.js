/* nav.js — search + nav behavior */
(function() {
  var idx = null;
  function loadIndex(cb) {
    if (idx) return cb(idx);
    fetch('/search-index.json').then(r=>r.json()).then(d=>{idx=d;cb(d);}).catch(()=>cb([]));
  }
  window.doSearch = function(q) {
    var res = document.getElementById('search-results');
    if (!q || q.length < 2) { res.innerHTML=''; return; }
    loadIndex(function(data) {
      var found = data.filter(function(a) {
        return (a.title||'').toLowerCase().includes(q.toLowerCase());
      }).slice(0,8);
      res.innerHTML = found.length
        ? found.map(a=>'<a href="/'+a.filename+'">'+a.title+'</a>').join('')
        : '<p style="color:#94a3b8;font-size:.9rem">ไม่พบบทความ</p>';
    });
  };
  document.addEventListener('click', function(e) {
    var modal = document.getElementById('search-modal');
    if (modal && !modal.contains(e.target) && !e.target.classList.contains('nav-search-btn')) {
      modal.classList.remove('open');
    }
  });
})();
