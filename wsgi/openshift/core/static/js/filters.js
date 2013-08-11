'use strict';

/* Filters */

angular.module('myApp.filters', []).
  filter('interpolate', ['version', function(version) {
    return function(text) {
      return String(text).replace(/\%VERSION\%/mg, version);
    }
  }])

  .filter('shorten', function() {
    return function(str) {
      if (str.length >= 2) {
          str = str[0] + "-" + str[str.length-1]
      }
      return str;
    }
  })

  .filter('starters', function() {
    return function (places) {
        var starters = []
        var lastStarterCount = 8;
        angular.forEach(places , function(p, i) {
            var lastStarter = starters[starters.length -1] || '';
            var firstLetter = p.name[0]
            if (lastStarterCount > 7 && lastStarter.indexOf(firstLetter) == -1) {
                starters.push("");
                lastStarter = starters[starters.length -1];
                lastStarterCount = 0;
            }
            lastStarterCount++;
            var lastStarter = starters[starters.length -1];
            if (lastStarter.indexOf(firstLetter) == -1) {
                starters[starters.length -1] += firstLetter;
            }
        })
        return starters;
    }
  })

  .filter('starterLettersFilter', function() {
    return function(states, letetrs) {
        if (letetrs && letetrs != "") {
            states = states.filter(function(s) {
                return letetrs.indexOf(s.name[0]) != -1
            })
        }
        return states;
    }
  })

  .filter('percent', function() {
    return function(n) {
      var n = n || 0;
      return Math.round(100 * n) + '%';
    }
  })
  
  .filter('StatesFromPlaces', function() {
    return function(data) {
        var places = {};
        if (data[0] && data[0].places) {
            angular.forEach(data[0].places, function(place) {
                places[place.code] = place;
            });
        }
        return places;
    }
  });
