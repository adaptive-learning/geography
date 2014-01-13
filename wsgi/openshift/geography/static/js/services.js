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
      var lastAnswerIndex = -1;
      var worldPart;
      function returnQuestion (fn){
            var q = questions[qIndex++];
            if(q) q.response_time = - (new Date()).valueOf();
            fn(q);
      }
      function hasNoTwoSameInARow (array) {
        for(var i=0,j=array.length; i+1<j; i++){
          if (array[i].code == array[i+1].code) {
              return false;
          }
        };
        return true;
      }
      var questions = [];
      var summary = [];
      return {
          first: function(part, fn){
              worldPart = part;
              summary = [];
                $http.get('question/' + part).success(function(data) {
                    qIndex = 0;
                    lastAnswerIndex = -1;
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
                    var newLastAnswerIndex = questions.length - data.length -1;
                    // if it is not a delayed response
                    if (lastAnswerIndex < newLastAnswerIndex) {
                        lastAnswerIndex = newLastAnswerIndex;
                        var newQuestions = questions.slice(0, lastAnswerIndex +1).concat(data);
                        if (hasNoTwoSameInARow(newQuestions)) {
                            questions = newQuestions;
                        }
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
