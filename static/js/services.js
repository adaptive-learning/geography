'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('myApp.services', []).
  value('version', '0.1')

  .factory('maps', function($rootScope, $http) {
    var parts = {"Evropa": 0, "Asie" : 1, "Svět" : 2};
    return function (worldPart, fn) {
        if ($rootScope.maps) {
            fn(worldPart ?$rootScope.maps[parts[worldPart]] : $rootScope.maps);
        } else {
            $http.get('static/php/worldParts.json').success(function(data) {
                $rootScope.maps = data;
                fn(worldPart ?$rootScope.maps[parts[worldPart]] : $rootScope.maps);
            });
        }
    }
  })

  .factory('places', function($rootScope, $http) {

    return function(fn) {
        if ($rootScope.places) {
            fn($rootScope.places);
        } else {
            $http.get('static/php/places.json').success(function(data) {
                $rootScope.places = data;
                fn(data);
            });
        }
    }
  })
