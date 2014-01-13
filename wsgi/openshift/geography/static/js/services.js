'use strict';

/* Services */

// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('myApp.services', []).
  value('version', '0.1')

  .factory('usersplaces', function($rootScope, $http, placeName) {
    var cache = {};

    return function(part, user, fn) {
        var url = 'usersplaces/' + part + '/' + user;
        $http.get(url).success(function(data) {
            placeName(part, data.name);
            var placesTypes = data.placesTypes.filter(function(d){
                return d.places && d.places.length > 0;
            })
            cache[url] = placesTypes;
            fn(placesTypes);
        });
        return cache[url] || undefined;
    }
  })

  .factory('placeName', function($rootScope, $http) {
    var names = {
        'us' : 'USA',
        'world' : 'Svět'
    }

    return function(part, name) {
        if (name && !names[part]) {
            names[part] = name;
        }
        return names[part];
    }
  })

  .service('question', function($rootScope, $http, $cookies) {

    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] =  'application/x-www-form-urlencoded'
      var qIndex = 0;
      var worldPart;
      function returnQuestion (fn){
            var q = questions[qIndex++];
            if(q) q.response_time = - (new Date()).valueOf();
            fn(q);
      }
      var questions = [];
      var summary = [];
      return {
          first: function(part, fn){
              worldPart = part;
              summary = [];
                $http.get('question/' + part).success(function(data) {
                    qIndex = 0;
                    questions = data;
                    returnQuestion(fn);
                });
          },
          next: function(part, fn){
                returnQuestion(fn);
          },
          answer: function(question) {
                question.response_time += (new Date()).valueOf();
                question.index = qIndex-1;
                summary.push(question);
                $http.post('question/' + worldPart, question).success(function(data) {
                    var futureLength = qIndex + data.length;
                    // questions array should be always the same size
                    // if data sent by server is longer, it means the server is delayed
                    if (questions.length == futureLength &&
                        // try to handle interleaving
                        (data.length < 2 || data[1].code != questions[qIndex].code)) {
                        questions = questions.slice(0, qIndex).concat(data);
                        console.log('questions updated, question index', qIndex)
                    }
                });

                return  100 * qIndex / questions.length;
          },
          summary: function() {
              var correctlyAnswered = summary.filter(function(q){
                      return q.code == q.answer;
                  })

              return {
                  correctlyAnsweredRatio : correctlyAnswered.length / summary.length,
                  questions : summary
              }
          }
      }

  })
