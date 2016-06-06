/*jshint browser: true, nomen: false, eqnull: true, es5:true, trailing:true,undef:true */
/*global jQuery, console, QUnit, COREMODELNS, window, alert */

// polyfills for ES5 array support in IE8- -- via MDN...

(function () {

  // Array.prototype.indexOf, via MDN:
  if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function(searchElement, fromIndex) {
      var k;
      if (this == null) {
        throw new TypeError('"this" is null or not defined');
      }
      var o = Object(this);
      var len = o.length >>> 0;
      if (len === 0) {
        return -1;
      }
      var n = +fromIndex || 0;
      if (Math.abs(n) === Infinity) {
        n = 0;
      }
      if (n >= len) {
        return -1;
      }
      k = Math.max(n >= 0 ? n : len - Math.abs(n), 0);
      while (k < len) {
        if (k in o && o[k] === searchElement) {
          return k;
        }
        k++;
      }
      return -1;
    };
  }

  // Array.prototype.forEach, via MDN:
  if (!Array.prototype.forEach) {
    Array.prototype.forEach = function(callback, thisArg) {
      var T, k;
      if (this == null) {
        throw new TypeError(' this is null or not defined');
      }
      var O = Object(this);
      var len = O.length >>> 0;
      if (typeof callback !== "function") {
        throw new TypeError(callback + ' is not a function');
      }
      if (arguments.length > 1) {
        T = thisArg;
      }
      k = 0;
      while (k < len) {
        var kValue;
        if (k in O) {
          kValue = O[k];
          callback.call(T, kValue, k, O);
        }
        k++;
      }
    };
  }

  // Array.prototype.map, via MDN:
  if (!Array.prototype.map) {
    Array.prototype.map = function(callback, thisArg) {
      var T, A, k;
      if (this == null) {
        throw new TypeError(' this is null or not defined');
      }
      var O = Object(this);
      var len = O.length >>> 0;
      if (typeof callback !== 'function') {
        throw new TypeError(callback + ' is not a function');
      }
      if (arguments.length > 1) {
        T = thisArg;
      }
      A = new Array(len);
      k = 0;
      while (k < len) {
        var kValue, mappedValue;
        if (k in O) {
          kValue = O[k];
          mappedValue = callback.call(T, kValue, k, O);
          A[k] = mappedValue;
        }
        k++;
      }
      return A;
    };
  }

  // Array.prototype.reduce, via MDN:
  if (!Array.prototype.reduce) {
    Array.prototype.reduce = function(callback /*, initialValue*/) {
      'use strict';
      if (this == null) {
        throw new TypeError('Array.prototype.reduce called on null or undefined');
      }
      if (typeof callback !== 'function') {
        throw new TypeError(callback + ' is not a function');
      }
      var t = Object(this), len = t.length >>> 0, k = 0, value;
      if (arguments.length == 2) {
        value = arguments[1];
      } else {
        while (k < len && !(k in t)) {
          k++;
        }
        if (k >= len) {
          throw new TypeError('Reduce of empty array with no initial value');
        }
        value = t[k++];
      }
      for (; k < len; k++) {
        if (k in t) {
          value = callback(value, t[k], k, t);
        }
      }
      return value;
    };
  }

}());

// checkbrowser core:

var checkbrowser = (function (ns, $) {

  var DEPRECATED = 'DEPRECATED',
      UNSUPPORTED = 'UNSUPPORTED',
      MSIE = 'Microsoft Internet Explorer',
      SUPPORTED = [
        'Firefox 31.0+ (mid-2014 or later)',
        'Google Chrome 28.0+ (mid-2013 and later)',
        'Internet Explorer 11.0 (mid-2013 or later)',
        'Microsoft Edge (Windows 10)',
        'Apple Safari 7.1+ (mid-2014 and later)'
      ],
      DISPLAY_SUPPORTED = '<h4>The following browsers are supported:</h4>' +
        $('<ul>')
          .html(
            SUPPORTED
            .map(function (s) { return '  <li>' + s + '</li>'; })
            .join('\n')
          )[0].outerHTML,
      DISPLAY_UNSUPPORTED = '<p>\n' +
        '  <em class="error">\n' +
        '    The web browser version this site has detected you are using ' +
        '    is unsupported.</em>\n' +
        '  Please update your browser version or install one of the ' +
        '  following supported browsers.' +
        '</p>\n',
      DISPLAY_DEPRECATED = '<p>\n' +
        '  <em class="warn">\n' +
        '    The web browser version this site has detected you are using ' +
        '    will soon be unsupported.</em>\n' +
        '  In anticipation, please update your browser version or install ' +
        '  one of the following supported browsers.' +
        '</p>\n',
      all = function (seq) {
        return seq.reduce(function (a, b) {
          return a == b && b === true;
          },
          true
        );
      };

  ns.headings = {
    UNSUPPORTED: 'Your web browser is unsupported on this site',
    DEPRECATED: 'Your web browser will not be supported at a time in the ' +
                'near future.'
  };

  ns.endOfDay = function () {
    /** returns today at end of day */
    var eod = new Date();
    eod.setHours(23);
    eod.setMinutes(59);
    eod.setSeconds(59);
    return eod;
  };

  // precondition functions for use by rules
  ns.loggedIn = function () {
    return $('body').hasClass('userrole-authenticated');
  };

  ns.notAlreadySeen = function () {
    /** returns true only if no 'browser-warning-seen-today' cookie exists */
    return document.cookie.indexOf('browser-warning-seen-today') === -1;
  };

  // Patterns and rules:
  ns.patterns = {
    MSIE7: {
      name: MSIE + ' 7.0',
      search: 'MSIE 7.0'
    },
    MSIE8: {
      name: MSIE + ' 8.0',
      search: 'MSIE 8.0'
    },
    MSIE9: {
      name: MSIE + ' 9.0',
      search: 'MSIE 9.0'
    },
    MSIE10: {
      name: MSIE + ' 10.0',
      search: 'MSIE 10.0'
    }
  };

  ns.rules = [
    {
      title: MSIE + ' versions 8 or less are unsupported',
      message: DISPLAY_UNSUPPORTED + DISPLAY_SUPPORTED,
      matching: [
        ns.patterns.MSIE7,
        ns.patterns.MSIE8
      ],
      type: UNSUPPORTED
    },
    {
      title: 'TeamSpace discontinued support of versions 9.0, 10.0 of ' +
             'Internet Explorer on May 15, 2016. Your browser may be ' +
             'unable to connect properly on/after June 15, 2016. ',
      message: DISPLAY_UNSUPPORTED + DISPLAY_SUPPORTED,
      matching: [
        ns.patterns.MSIE9,
        ns.patterns.MSIE10
      ],
      type: UNSUPPORTED,
      preconditions: [
        ns.notAlreadySeen,
        ns.loggedIn
      ]
    }
  ];

  ns.match = function (pattern, target) {
    return (target.indexOf(pattern) !== -1);
  };

  ns.alert = function (violations, detectedBrowser) {
    var alertBox = $('<div class="alertbox">'),
        target = $('#viewlet-above-content');
    // Append content into alertBox for each rule violated
    violations.forEach(function (rule) {
      var d = '<p class="detected"><em>' +
            'It appears you are using <span class="browsername">' +
            detectedBrowser +
            '</span>.</em></p>',
          heading = ns.headings[rule.type || UNSUPPORTED],
          hClass = (rule.type || UNSUPPORTED).toLowerCase();
      $('<h3>').addClass(hClass).html(heading).appendTo(alertBox);
      $('<h4>').html(rule.title).appendTo(alertBox);
      $(d).appendTo(alertBox);
      $('<div class="message-wrap">').html(rule.message).appendTo(alertBox);
      $('<hr />').appendTo(alertBox);
    });
    // attach alertBox to #viewlet-above-content
    if (!target.length) {
      target = $('body');  // fallback
    }
    target.prepend(alertBox);
  };

  ns.check = function () {
    var ua = navigator.userAgent,
        detected = '',
        violations = [];
    ns.rules.forEach(function (rule) {
      var preconditions = rule.preconditions || [],
          met = preconditions.map(function (fn) { return fn(); });
      if (!all(met)) return;
      rule.matching.forEach(function (pattern) {
        if (ns.match(pattern.search, ua)) {
          if (violations.indexOf(rule) === -1) {
            detected = pattern.name;
            violations.push(rule);  // add once
          }
          if (preconditions.indexOf(ns.notAlreadySeen) !== -1) {
              // no cookie, set (append) it now:
              document.cookie = 'browser-warning-seen-today=1; expires=' +
                ns.endOfDay() +
                '; path=/';
          }
        }
      });
    });
    if (violations.length) {
      ns.alert(violations, detected);
    }
  };

  $(document).ready(function () {
    ns.check();
  });

  return ns;

}(checkbrowser || {}, jQuery));
