'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('myApp.services', []).
  value('version', '0.1')
/*
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
*/
  .factory('places', function($rootScope, $http) {

    return function(part, fn) {
        $http.get('places/' + part, { cache: true }).success(function(data) {
            fn(data);
        });
    }
  })

  .service('question', function($rootScope, $http, $cookies) {

    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] =  'application/x-www-form-urlencoded'
      var qIndex = 0;
      function returnQuestion (fn){
            var q = $rootScope.questions[qIndex++];
            q.msResponseTime = - (new Date()).valueOf();
            fn(q);
      }
      return {
          first: function(part, fn){
                $http.get('question/' + part).success(function(data) {
                    qIndex = 0;
                    $rootScope.questions = data;
                    returnQuestion(fn);
                });
          },
          next: function(part, fn){
                returnQuestion(fn);
          },
          answer: function(question) {
                question.msResponseTime += (new Date()).valueOf();
                $http.post('question/', question).success(function(data) {
                });

                return  100 * qIndex / $rootScope.questions.length;
          }
      }

  })
