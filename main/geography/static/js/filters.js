(function() {
  'use strict';
  /* Filters */
  angular.module('blindMaps.filters', [])

  .filter('percent', function() {
    return function(n) {
      n = n || 0;
      return Math.round(100 * n) + '%';
    };
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
    };
  })

  .filter('colNum', function() {
    return function(colsCount) {
      return Math.floor(12 / colsCount);
    };
  })

  .filter('isActive',['$location', function($location) {
    return function(path) {
      if ($location.path() == path) {
        return 'active';
      } else {
        return '';
      }
    };
  }])

  .filter('isFindOnMapType', function() {
    return function(question) {
      return question && question.type < 20;
    };
  })

  .filter('isPickNameOfType', function() {
    return function(question) {
      return question && question.type >= 20;
    };
  })

  .filter('isAllowedOption', function() {
    return function(question, code) {
      return !question.options || 1 == question.options.filter(function(place) {
        return place.code == code;
      }).length;
    };
  })

  .filter('isTypeCategory', function() {
    return function(types, category) {
      types = types && types.filter(function(t){
        return category.types.filter(function(slug){
          return slug == t.slug;
        }).length == 1;
      });
      return types;
    };
  })

  .filter('codeToName',['places', function(places) {
    return function(code) {
      return places.getName(code) || "Neznámý";
    };
  }])

  .filter('probColor', ['colorScale', function(colorScale) {
    return function(probability) {
      return colorScale(probability).hex();
    };
  }])

  .filter('avgProb', [ function() {
    return function(places) {
      if (places.length === 0) {
        return 0;
      }
      var sum = places.map(function(p){
        return p.probability;
      }).reduce(function(a, b) { 
        return a + b;
      });
      var avg = sum / places.length;
      return avg;
    };
  }])

  .filter('sumCounts', [ function() {
    return function(layers) {
      if (!layers || layers.length === 0) {
        return 0;
      }
      var sum = layers.map(function(p){
        return p.count;
      }).reduce(function(a, b) { 
        return a + b;
      });
      return sum;
    };
  }]);
}());
