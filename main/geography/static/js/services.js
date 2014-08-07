(function() {
  'use strict';

  /* Services */
  angular.module('blindMaps.services', [
    'ngCookies'
  ])

  .factory('places', ['$http', 'gettext', function($http, gettext) {
    var cache = {};
    var mapCache = {};
    var categoriesCache = {};
    var names = {
        'us' : gettext('USA'),
        'world' : gettext('Svět')
      };
    var categories = [
      {
        slug :'political',
        name : gettext('Politická mapa'),
        types : [
          'state',
          'city',
          'region',
          'province',
          'region_cz',
          'region_it',
          'autonomous_comunity',
          'bundesland'
        ]
      },{
        slug : 'water',
        name : gettext('Vodstvo'),
        types : ['river', 'lake'],
        hidden:true
      },{
        slug : 'surface',
        name : gettext('Povrch'),
        types : ['mountains', 'island'],
        hidden:true
      }
    ];

    function addOneToNames(code, name) {
      if (!names[code]) {
        names[code] = name;
      }
    }

    function addToNames(code, placesTypes) {
      angular.forEach(placesTypes, function(type) {
        angular.forEach(type.places, function(place) {
          addOneToNames(place.code, place.name);
        });
      });
    }
    
    var that = {
      get : function(part, user, fn) {
        var url = '/usersplaces/' + part + '/' + user;
        var promise = $http.get(url, {cache: user == 'average'}).success(function(data) {
          var placesTypes = data.placesTypes;
          cache[url] = placesTypes;
          fn(placesTypes);
        });
        return promise;
      },
      setName : function(code, name) {
        names[code] = names[code] || name;
      },
      getName : function(code) {
        return names[code];
      },
      getCategories : function(part) {
        if (!categoriesCache[part]) {
          categoriesCache[part] = angular.copy(categories);
        }
        var allHidden = 0 === categoriesCache[part].filter(function(c){
          return !c.hidden;
        }).length;
        if (allHidden) {
          categoriesCache[part][0].hidden = false;
        }
        return categoriesCache[part];
      },
      _setActiveCategory : function (part, active) {
        that.getCategories(part, active);
        angular.forEach(categoriesCache[part], function(cat) {
          cat.hidden = cat.slug != active &&  
            0 === cat.types.filter(function(t){ 
              return t == active;
            }).length;
        });
      },
      practicing : function (part, type) {
        that._setActiveCategory(part, type);
        // To fetch names of all places on map and be able to show name of wrongly answered place
        var process = function(placesTypes){
          addToNames(part, placesTypes);
        };
        var url = '/usersplaces/' + part + '/';
        if (cache[url]) {
          process(cache[url]);
        } else {
          that.get(part, '', process);
        } 
      },
      getOverview : function () {
        return $http.get('/placesoverview/', {cache: true});
      },
      getMapLayers : function(map) {
        return mapCache[map].placesTypes.map(function(l){
          return l.slug;
        });
      },
      getMapLayerCount : function(map, layer) {
        if (!mapCache[map]) {
          return 0;
        }
        return mapCache[map].placesTypes.filter(function(l){
          return l.slug == layer;
        }).map(function(l){
          return l.count;
        })[0];
      }
    };
    that.getOverview().success(function(data){
      angular.forEach(data, function(category){
        angular.forEach(category.maps, function(map){
          mapCache[map.slug] = map;
        });
      });
    });
    return that;
  }])

  .factory('mapTitle', ['places', function(places) {
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
  }])

  .service('question', ['$http', '$log', '$cookies', 
      function($http, $log, $cookies) {
    var qIndex = 0;
    var url;
    $http.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
    
    function returnQuestion(fn) {
      var q = questions[qIndex++];
      if (q)
        q.response_time = -new Date().valueOf();
      fn(q);
    }
    function hasNoTwoSameInARow(array) {
      for (var i = 0, j = array.length; i + 1 < j; i++) {
        if (array[i].asked_code == array[i + 1].asked_code) {
          return false;
        }
      }
      return true;
    }
    var questions = [];
    var summary = [];
    return {
      first : function(part, placeType, fn) {
        url = '/question/' + part + '/' + (placeType ? placeType : '');
        summary = [];
        var promise = $http.get(url).success(function(data) {
          qIndex = 0;
          questions = data;
          returnQuestion(fn);
        });
        return promise;
      },
      next : function(part, placeType, fn) {
        returnQuestion(fn);
      },
      answer : function(question) {
        question.response_time += new Date().valueOf();
        question.index = qIndex - 1;
        summary.push(question);
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
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
            return q.asked_code == q.answered_code;
          });
        return {
          correctlyAnsweredRatio : correctlyAnswered.length / summary.length,
          questions : summary
        };
      }
    };
  }])

  .factory('user', ['$http', '$cookies', 'events', 
      function($http, $cookies, events) {
    var user;
    return {
      initUser : function(username, points, email) {
        user = {
          'username' : username,
          'points' : points,
          'email' : email,
        };
        return user;
      },
      getUser : function() {
        return user;
      },
      logout : function(callback) {
        $http.get('/user/logout/').success(callback);
        this.initUser('', 0);
        events.emit('userUpdated', user);
        return user;
      },
      addPoint : function() {
        user.points++;
        $cookies.points = user.points;
        events.emit('userUpdated', user);
      },
      getPromiseByName : function(name) {
        return $http.get('/user/' + name + '/');
      }
    };
  }])

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
  })

  .factory('pageTitle',['places', 'gettext', function(places, gettext) {

    var titles = {
      'static/tpl/about.html' : gettext('O prjektu') + ' - ',
      'static/tpl/overview_tpl.html' : gettext('Přehled map') + ' - ',
    };
    return function (route) {
      var title;
      if (route.controller == "AppView" || route.controller == "AppPractice") {
        title = places.getName(route.params.part) + ' - ';
      } else if (route.controller == "AppUser") {
        title = route.params.user + ' - ';
      } else {
        title = titles[route.templateUrl] || '';
      }
      return title;
    };
  }]);
}());
