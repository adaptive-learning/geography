'use strict';

/* Services */

angular.module('blindMaps.services', [])

  .factory('usersplaces', function($http, placeName) {
    var cache = {};

    return {
      get : function(part, user, fn) {
        var url = 'usersplaces/' + part + '/' + user;
        $http.get(url).success(function(data) {
            placeName(part, data.name);
            var placesTypes = data.placesTypes.filter(function(d){
                return d.places && d.places.length > 0;
            })
            cache[url] = placesTypes;
            fn(placesTypes);
        });
      },
      getCached : function(part, user) {
        var url = 'usersplaces/' + part + '/' + user;
        return cache[url] || undefined;
      }
    }
  })

  .factory('placeName', function($http) {
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

  .service('question', function($http, $cookies) {

    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] =  'application/x-www-form-urlencoded'
      var qIndex = 0;
      var url;
      function returnQuestion (fn){
            var q = questions[qIndex++];
            if(q) q.response_time = - (new Date()).valueOf();
            fn(q);
      }
      function hasNoTwoSameInARow(array) {
          for(var i=0,j=array.length; i+1<j; i++) {
              if (array[i].code == array[i+1].code) {
                  return false;
              }
          }
          return true
      }
      var questions = [];
      var summary = [];
      return {
          first: function(part, placeType, fn){
              url = 'question/' + part + '/' + (placeType ? placeType : "");
              summary = [];
                $http.get(url).success(function(data) {
                    qIndex = 0;
                    questions = data;
                    returnQuestion(fn);
                });
          },
          next: function(part, placeType, fn){
                returnQuestion(fn);
          },
          answer: function(question) {
                question.response_time += (new Date()).valueOf();
                question.index = qIndex-1;
                summary.push(question);
                $http.post(url, question).success(function(data) {
                    var futureLength = qIndex + data.length;
                    // questions array should be always the same size
                    // if data sent by server is longer, it means the server is delayed
                    if (questions.length == futureLength) {
                        // try to handle interleaving
                        var questionsCandidate = questions.slice(0, qIndex).concat(data);
                        if (hasNoTwoSameInARow(questionsCandidate)) {
                            questions = questionsCandidate;
                            console.log('questions updated, question index', qIndex)
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

  .factory('user', function($http) {
    return {
      getUser : function(callback) {
          $http.get('user/').success(callback);
      },
      logout : function(callback){
          $http.get('user/logout/').success(callback);
          return  {
              'username' : '',
              'points' :  0
          };
      }
    }
  })
