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
