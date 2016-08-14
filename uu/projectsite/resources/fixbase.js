// rewrite <base> tag in Plone 4 DOM to match window.location.href

(function () {
  "use strict";

  var head = document.getElementsByTagName('head')[0],
      existing = head.getElementsByTagName('base'),
      base = document.createElement('base'),
      loc = window.location,
      href = loc.href.replace(loc.search, '').replace(loc.hash, '');
  if (existing.length) {
    head.removeChild(existing[0]);
  }
  base.setAttribute('href', href);
  if (head.firstChild) {
    head.insertBefore(base, head.firstChild);
  } else {
    head.appendChild(base);
  }
}());

