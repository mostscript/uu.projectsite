// rewrite <base> tag in Plone 4 DOM to match window.location.href

(function () {
  "use strict";

  var head = document.getElementsByTagName('head')[0],
      existing = head.getElementsByTagName('base'),
      base = document.createElement('base'),
      loc = window.location,
      oldHref = (existing.length) ? existing[0].getAttribute('href') || '' : '',
      slash = oldHref.slice(-1) === '/',
      href = loc.href.replace(loc.search, '').replace(loc.hash, ''),
      excludedViews = ['view'];
  if (existing.length) {
    head.removeChild(existing[0]);
    if (slash) {
      href += '/';
    }
  }
  // exclude some views from path, due to effect on relative a hrefs:
  excludedViews.forEach(function (path) {
    href = href.split(path)[0];
  });
  base.setAttribute('href', href);
  if (head.firstChild) {
    head.insertBefore(base, head.firstChild);
  } else {
    head.appendChild(base);
  }
}());

