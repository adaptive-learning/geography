'use strict';

/* Filters */

angular.module('myApp.filters', []).
  filter('interpolate', ['version', function(version) {
    return function(text) {
      return String(text).replace(/\%VERSION\%/mg, version);
    }
  }])

  .filter('percent', function() {
    return function(n) {
      var n = n || 0;
      return Math.round(100 * n) + '%';
    }
  });
