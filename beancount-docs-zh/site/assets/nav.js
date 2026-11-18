(function () {
  var a = document.getElementById('backlink');
  if (!a) return;
  var parent = a.getAttribute('data-parent') || 'index.html';
  var target = null;

  try {
    if (document.referrer) {
      var ref = new URL(document.referrer);
      if (ref.origin === location.origin && ref.pathname !== location.pathname) {
        target = ref.pathname + ref.search + ref.hash;
      }
    }
  } catch (e) {}

  if (!target) {
    try {
      var prev = sessionStorage.getItem('beancount-prev');
      if (prev && prev !== location.pathname) target = prev;
    } catch (e) {}
  }

  if (target) {
    a.href = target;
    a.textContent = '← 返回上一页';
  } else {
    a.href = parent;
    a.textContent = '← 返回分类';
  }

  try {
    sessionStorage.setItem('beancount-prev', location.pathname + location.search);
  } catch (e) {}
})();

// 左右方向键翻页（输入框内不触发）
(function () {
  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) return;
    var t = e.target;
    if (!t) return;
    var tag = (t.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || t.isContentEditable) return;
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    var dir = e.key === 'ArrowLeft' ? 'prev' : 'next';
    var link = document.querySelector('.pager-card.pager-' + dir);
    if (!link || !link.getAttribute('href')) return;
    e.preventDefault();
    location.href = link.getAttribute('href');
  });
})();
