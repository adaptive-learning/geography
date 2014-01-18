'use strict';

/* Filters */

angular.module('blindMaps.filters', [])

  .filter('percent', function() {
    return function(n) {
      var n = n || 0;
      return Math.round(100 * n) + '%';
    }
  })

  .filter('StatesFromPlaces', function() {
    return function(data) {
        var places = {};
        if (data && data[0]) {
            angular.forEach(data, function(category) {
                if (!category.haveMaps && category.places) {
                    angular.forEach(category.places, function(place) {
                        places[place.code] = place;
                    });
                }
            });
        }
        return places;
    }
  })

  .filter('colNum', function() {
    return function(colsCount) {
        return Math.floor(12/colsCount);
    };
  })

  .filter('isActive', function($location) {
    return function(path) {
        if ($location.path().substr(0, path.length) == path) {
          return "active";
        } else {
          return "";
        }
    }
  });