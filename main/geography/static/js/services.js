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
    var placeTypeNames = {};

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
      },
      setPlaceTypeNames : function (obj) {
        placeTypeNames = obj;
      },
      getPlaceTypeName : function (slug) {
        return placeTypeNames[slug];
      },
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

  .service('question', ['$http', '$log', '$cookies', 'goal', '$analytics', 'params',
      function($http, $log, $cookies, goal, $analytics, params) {
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
        url = '/question/' + part + '/' + (placeType ? placeType : '') +
          params.queryString().replace('&', '?');
        $analytics.eventTrack('started', {
          category: 'practice',
          label: url,
        });
        summary = [];
        var promise = $http.get(url).success(function(data) {
          qIndex = 0;
          questions = data.questions;
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
          var futureLength = qIndex + data.questions.length;
          // questions array should be always the same size
          // if data sent by server is longer, it means the server is delayed
          if (questions.length == futureLength) {
            // try to handle interleaving
            var questionsCandidate = questions.slice(0, qIndex).concat(data.questions);
            if (hasNoTwoSameInARow(questionsCandidate)) {
              questions = questionsCandidate;
              $log.log('questions updated, question index', qIndex);
            }
          }
          if (data.goals) {
            goal.update(data.goals);
          }
        });
        return 100 * qIndex / questions.length;
      },
      summary : function() {
        $analytics.eventTrack('finished', {
          category: 'practice',
          label: url,
        });
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

  .factory('user', ['$http', '$cookies', 'events', '$routeParams', '$timeout', 'loginModal',
      function($http, $cookies, events, $routeParams, $timeout, loginModal) {

    var user;

    function updateUser(data) {
      user.points = data.points;
      user.answered_count = data.answered_count;
      user.email = data.email;
      user.first_name = data.first_name;
      user.last_name = data.last_name;
      user.send_emails = data.send_emails;
    }

    var that = {
      initUser : function(userObject) {
        user = userObject;
        user.getLevelInfo = function() {
          return that.getLevelInfo(user);
        };
        
        $timeout(function() {
          if ($routeParams.requirelogin) {
            loginModal.open(user);
          }
        }, 100);

        $http.get('/user/').success(updateUser);
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
      addAnswer : function(isCorrect) {
        if (isCorrect) {
          user.points++;
        }
        user.answered_count++;
        $cookies.points = user.points;
        events.emit('userUpdated', user);
      },
      getPromiseByName : function(name) {
        if (name == user.username) {
          return {
            success : function(fn) {fn(user);},
          };
        } else {
          return $http.get('/user/' + name + '/');
        }
      },
      getLevelInfo : function(user) {
        var levelEnd = 0;
        var levelRange = 30;
        var rangeIncrease = 0;
        for (var i = 1; true; i++) {
          levelEnd += levelRange;
          if (user.points < levelEnd) {
            return {
              level : i,
              form : levelEnd - levelRange,
              to : levelEnd,
              range : levelRange,
              points : user.points - (levelEnd - levelRange),
            };
          }
          levelRange += rangeIncrease;
          rangeIncrease += 10;
        }
        
      },
      save : function(user) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        return $http.post('/user/save/', user).success(updateUser); 
      }
    };
    return that;
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
        var typeName = places.getPlaceTypeName(route.params.place_type);
        if (typeName) {
          title += typeName + ' - ';
        }
      } else if (route.controller == "AppUser") {
        title = route.params.user + ' - ';
      } else {
        title = titles[route.templateUrl] || '';
      }
      return title;
    };
  }])

  .factory('goal',['$http', '$cookies', 'confirmModal', 'gettext',
      function($http, $cookies, confirmModal, gettext) {
    
    var goalDict = {};
    var goals = [];
    function updateGoal(g){
      if (goalDict[g.id]) {
        angular.copy(g, goalDict[g.id]);
      } else {
        goalDict[g.id] = g;
        goals.unshift(g);
      }
    }
    var goalsPromise = $http.get("/goal/");

    var that = {
      update : function(newGoals) {
        for (var i = 0; i < newGoals.length; i++) {
          updateGoal(newGoals[i]);
        }
      },
      get : function(user) {
        if (user) {
          return $http.get("/goal/" + user);
        } else {
          return {
            success : function(fn) {
              goalsPromise.success(function() {
                fn(goals);
              });
            }
          };
        }
      },
      getForMap : function(mapCode, typeSlug) {
        for (var i = 0; i < goals.length; i++) {
          var g = goals[i];
          if (g.map.code == mapCode && g.type.slug == typeSlug) {
            return g;
          }
        }
      },
      remove : function(goal) {
        var question = gettext("Opravdu chcete cíl smazat?");
        confirmModal.open(question, function() {
          goal.deleting = true;
          $http.get("/goal/delete/" + goal.id).success(function() {
            for (var i = 0; i < goals.length; i++) {
              if (goals[i].id == goal.id) {
                goals.splice(i, 1);
                break;
              }
            }
            delete goalDict[goal.id];
          });
        });
      },
      add : function(goal) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        var promise = $http.post('/goal/', goal);
        promise.success(function(data) {
          updateGoal(data);
        });
        return promise;
      }
    };

    goalsPromise.success(function(data) {
      that.update(data.reverse());
    });

    return that;
  }])

  .factory('params', ["$routeParams", "$location",
      function ($routeParams, $location) {
    var keys = ['limit'];
    var params = {}; 
    var that =  {
      get: function (key) {
        if (params[key] && ! $routeParams[key]) {
          $location.search(key, params[key]);
        }   
        if ($routeParams[key]) {
          params[key] = $routeParams[key];
        }   
        return params[key];
      },  
      all : function() {
        for (var i = 0; i < keys.length; i++) {
          that.get(keys[i]);
        }
        return params;
      },  
      queryString : function() {
        that.all();
        var string = keys.map(function(key) {
          return that.get(key) ? '&' + key + '=' + that.get(key) : ''; 
        }).join('');
        return string;
      }   
    };  
    return that;
  }])

  .factory('loginModal', ["$modal", function ($modal) {
    var ModalLoginCtrl = ['$scope', '$modalInstance', 
        function ($scope, $modalInstance) {
      $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
      };
    }];

    return {
      open : function(user) {
        if (!user.username) {
          $modal.open({
            templateUrl: 'static/tpl/login_modal.html',
            controller: ModalLoginCtrl,
            size: 'sm',
          });
        }
      }
    };
  }])

  .factory('confirmModal', ["$modal", function ($modal) {
    var ModalConfirmCtrl = ['$scope', '$modalInstance', 'question', 'confirm',
        function ($scope, $modalInstance, question, confirm) {
      $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
      };
      $scope.confirm = confirm;
      $scope.question = question;
    }];

    return {
      open : function(question, callback) {
        $modal.open({
          templateUrl: 'static/tpl/confirm_modal.html',
          controller: ModalConfirmCtrl,
          resolve: {
            confirm: function () {
              return  callback;
            },
            question: function () {
              return  question;
            },
          },
        });
      }
    };
  }]);
}());
