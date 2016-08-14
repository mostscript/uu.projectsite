// rewrite <base> tag in Plone 4 DOM to match window.location.href

(function () {
  "use strict";

  var head = document.getElementsByTagName('head')[0],
      existing = head.getElementsByTagName('base'),
      base = document.createElement('base'),
      loc = window.location,
      slash = existing.length && existing.attr('href').slice(-1) === '/',
      href = loc.href.replace(loc.search, '').replace(loc.hash, '');
  if (existing.length) {
    head.removeChild(existing[0]);
    if (slash) {
      href += '/';
    }
  }
  base.setAttribute('href', href);
  if (head.firstChild) {
    head.insertBefore(base, head.firstChild);
  } else {
    head.appendChild(base);
  }
}());

