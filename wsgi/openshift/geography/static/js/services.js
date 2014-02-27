(function() {
  'use strict';

  /* Services */
  angular.module('blindMaps.services', [])

  .factory('places', function($http) {
    var cache = {};
    var names = {
        'us' : 'USA',
        'world' : 'Svět'
      };
    var categories = [
      {
        slug :'political',
        name :'Politická mapa',
        types : ['state', 'city', 'region', 'province', 'region_cz', 'region_it', 'autonomous_comunity']
      },{
        slug : 'water',
        name : 'Vodstvo',
        types : ['river', 'lake'],
        hidden:true
      },{
        slug : 'surface',
        name : 'Povrch',
        types : [],
        hidden:true
      }
    ];
    
    return {
      get : function(part, user, fn) {
        var url = 'usersplaces/' + part + '/' + user;
        $http.get(url, {cache: user == 'average'}).success(function(data) {
          var placesTypes = data.placesTypes.filter(function(d) {
              return d.places && d.places.length > 0;
            });
          cache[url] = placesTypes;
          if (!names[part]) {
            names[part] = data.name;
          }
          fn(placesTypes);
        });
      },
      getCached : function(part, user) {
        var url = 'usersplaces/' + part + '/' + user;
        return cache[url] || undefined;
      },
      getName : function(part) {
        return names[part];
      },
      getCategories : function() {
        return categories;
      }
    };
  })

  .factory('mapTitle', function(places) {
    return function(part, user) {
      var name = places.getName(part);
      if (!name) {
        return;
      } else if (user === '' || user == 'average') {
        return name;
      } else {
        return name + ' - ' + user;
      }
    };
  })

  .service('question', function($http, $log) {
    var qIndex = 0;
    var url;
    function returnQuestion(fn) {
      var q = questions[qIndex++];
      if (q)
        q.response_time = -new Date().valueOf();
      fn(q);
    }
    function hasNoTwoSameInARow(array) {
      for (var i = 0, j = array.length; i + 1 < j; i++) {
        if (array[i].code == array[i + 1].code) {
          return false;
        }
      }
      return true;
    }
    var questions = [];
    var summary = [];
    return {
      first : function(part, placeType, fn) {
        url = 'question/' + part + '/' + (placeType ? placeType : '');
        summary = [];
        $http.get(url).success(function(data) {
          qIndex = 0;
          questions = data;
          returnQuestion(fn);
        });
      },
      next : function(part, placeType, fn) {
        returnQuestion(fn);
      },
      answer : function(question) {
        question.response_time += new Date().valueOf();
        question.index = qIndex - 1;
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
              $log.log('questions updated, question index', qIndex);
            }
          }
        });
        return 100 * qIndex / questions.length;
      },
      summary : function() {
        var correctlyAnswered = summary.filter(function(q) {
            return q.code == q.answer;
          });
        return {
          correctlyAnsweredRatio : correctlyAnswered.length / summary.length,
          questions : summary
        };
      }
    };
  })

  .factory('user', function($http, $cookies, events) {
    var user;
    return {
      getUser : function(callback) {
        if (!user) {
          $http.get('user/').success(function(data) {
            user = data;
            callback(user);
            events.emit('userUpdated', user);
          });
        }
        return user;
      },
      logout : function(callback) {
        $http.get('user/logout/').success(callback);
        user = {
          'username' : '',
          'points' : 0
        };
        events.emit('userUpdated', user);
        return user;
      },
      addPoint : function() {
        user.points++;
        $cookies.points = user.points;
        events.emit('userUpdated', user);
      }
    };
  })

  .factory('events', function() {
    var handlers = {};
    return {
      on : function(eventName, handler) {
        handlers[eventName] = handlers[eventName] || [];
        handlers[eventName].push(handler);
      },
      emit : function(eventName, args) {
        handlers[eventName] = handlers[eventName] || [];
        handlers[eventName].map(function(handler) {
          handler(args);
        });
      }
    };
  });
}());
