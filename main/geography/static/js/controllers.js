(function() {
  'use strict';
  /* Controllers */
  angular.module('blindMaps.controllers', [])

  .controller('AppCtrl', ['$scope', '$rootScope', '$location', '$modal',
      '$window', 'user', 'pageTitle', 'places', 'signupModal', 'loginModal',
      function($scope, $rootScope, $location, $modal,
        $window, user, pageTitle, places, signupModal, loginModal) {
    $rootScope.topScope = $rootScope;
    $rootScope.location = $location;
    $rootScope.loginModal = loginModal;
    $rootScope.signupModal = signupModal;
    
    $rootScope.initTitle = function (title) {
      $rootScope.initialTitle = title;
      $rootScope.title = title;
    };
    
    $rootScope.$on("$routeChangeStart", function(event, next) {
      $rootScope.title = pageTitle(next) + $rootScope.initialTitle;
    });
    
    var updateUser = function(data) {
      $rootScope.user = data;
    };
    
    $scope.initLanguageCode = function (code) {
      $rootScope.LANGUAGE_CODE = code;
    };

    $scope.initUser = function (data) {
      $rootScope.user = user.initUser(data);
    };

    $scope.setPlaceTypeNames = function (obj) {
      places.setPlaceTypeNames(obj);
    };

    $rootScope.logout = function() {
      $rootScope.user = user.logout(updateUser);
    };

    $scope.vip = function() {
      return $scope.user && $scope.user.username == 'Verunka';
    };

  }])

  .controller('AppView', ['$scope', '$routeParams', '$filter', 'places', 'mapTitle', 'gettext',
      function($scope, $routeParams, $filter, places, mapTitle, gettext) {
    $scope.part = $routeParams.part;
    var user = $routeParams.user || '';
    $scope.typeCategories = places.getCategories($scope.part);
    

    places.get($scope.part, user, updatePlaces).
      error(function(){
        $scope.error = gettext("V aplikaci bohužel nastala chyba.");
      });

    $scope.placeClick = function(place) {
      $scope.map.highlightState(place.code);
    };
    
    $scope.updateMap = function(type) {
      type.hidden = !type.hidden; 
      $scope.map.updatePlaces($scope.placesTypes);
    };
    
    $scope.updateCat = function(category) {
      var newHidden = !category.hidden;
      angular.forEach($scope.typeCategories, function(type) {
        type.hidden = true;
      });
      angular.forEach($scope.placesTypes, function(type) {
        type.hidden = true;
      });
      category.hidden = newHidden;
      updatePlaces($scope.placesTypes);
    };

    function updatePlaces(data) {
      $scope.placesTypes = data;
      angular.forEach($scope.typeCategories, function(category) {
        var filteredTypes = $filter('isTypeCategory')($scope.placesTypes, category);
        angular.forEach(filteredTypes, function(type) {
          type.hidden = category.hidden;
        });
      });
      $scope.map.updatePlaces($scope.placesTypes);
      $scope.name = mapTitle($scope.part, user);
    }
  }])

  .controller('AppPractice', ['$scope', '$routeParams', '$timeout', '$filter',
      'question', 'user', 'events', 'colors', 'places', '$', 'highlighted', 'gettext',
      function($scope, $routeParams, $timeout, $filter,
      question, user, events, colors, places, $, highlighted, gettext) {
    $scope.part = $routeParams.part;
    $scope.placeType = $routeParams.place_type;
    
    places.practicing($scope.part, $scope.placeType);

    $scope.highlight = function() {
      var active = $scope.question;
      $scope.layer = $scope.map.getLayerContaining(active.asked_code);
      $scope.map.highLightLayer($scope.layer);
      $scope.map.placeToFront(active.asked_code);
      if ($filter('isPickNameOfType')($scope.question)) {
        $scope.map.highlightState(active.asked_code, colors.NEUTRAL);
      }
      if ($filter('isFindOnMapType')($scope.question) && active.options) {
        var codes = active.options.map(function(option) {
          return option.code;
        });
        highlighted.setHighlighted(codes);
        $scope.map.highlightStates(codes, colors.NEUTRAL);
      }
    };

    $scope.checkAnswer = function(selected) {
      var asked = $scope.question.asked_code;
      highlightAnswer(asked, selected);
      $scope.question.answered_code = selected;
      $scope.progress = question.answer($scope.question);
      user.addAnswer(asked == selected);
      if (asked == selected) {
        $timeout(function() {
          $scope.next();
        }, 700);
      } else {
        $scope.canNext = true;
      }
    };

    $scope.next = function() {
      if ($scope.progress < 100) {
        question.next($scope.part, $routeParams.place_type, setQuestion);
      } else {
        setupSummary();
      }
    };

    function highlightAnswer (asked, selected) {
      if ($filter('isFindOnMapType')($scope.question)) {
        $scope.map.highlightState(asked, colors.GOOD);
      }
      $scope.map.highlightState(selected, asked == selected ? colors.GOOD : colors.BAD);
      if ($filter('isPickNameOfType')($scope.question)) {
        highlightOptions(selected);
      }
    }

    function setupSummary() {
      $scope.question.slideOut = true;
      $scope.layer = undefined;
      // prevents additional points gain. issue #38
      $scope.summary = question.summary();
      $scope.showSummary = true;
      $scope.map.clearHighlights();
      $scope.map.hideLayers();
      $scope.map.showSummaryTooltips($scope.summary.questions);
      angular.forEach($scope.summary.questions, function(q) {
        var correct = q.asked_code == q.answered_code;
        $scope.map.showLayerContaining(q.asked_code);
        $scope.map.highlightState(q.asked_code, correct ? colors.GOOD : colors.BAD, 1);
      });
      $("html, body").animate({ scrollTop: "0px" });
      events.emit('questionSetFinished', user.getUser().answered_count);
    }

    function setQuestion(active) {
      if ($scope.question) {
        $scope.question.slideOut = true;
      }
      $scope.question = active;
      $scope.questions.push(active);
      $scope.map.clearHighlights();
      $scope.highlight();
      $scope.canNext = false;
    }

    function highlightOptions(selected) {
      $scope.question.options.map(function(o) {
        o.correct = o.code == $scope.question.asked_code;
        o.selected = o.code == selected;
        o.disabled = true;
        return o;
      });
    }

    function isInActiveLayer(code) {
      return $scope.layer == $scope.map.getLayerContaining(code);
    }
    
    $scope.mapCallback = function() {
      question.first($scope.part, $routeParams.place_type, function(q) {
        $scope.questions = [];
        setQuestion(q);
      }).error(function(){
        $scope.error = gettext("V aplikaci bohužel nastala chyba.");
      });
      $scope.map.onClick(function(code) {
        if ($filter('isFindOnMapType')($scope.question) && 
            !$scope.canNext && 
            $filter('isAllowedOption')($scope.question, code) &&
            isInActiveLayer(code)) {
          $scope.checkAnswer(code);
          $scope.$apply();
        }
      });
    };
  }])

  .controller('AppUser', ['$scope', 'user', '$routeParams', '$location', 
      '$timeout', 'gettext',
      function($scope, user, $routeParams, $location, $timeout, gettext) {

    $scope.profileUrl = $location.absUrl();
    $scope.user = {username: $routeParams.user};
    user.getPromiseByName($routeParams.user).success(function(data){
      $scope.user = data;
      $scope.editRights = data.username == user.getUser().username;

      if ($routeParams.edit !== undefined && $scope.editRights) {
        $timeout(function() {
          $scope.editableForm.$show();
        },10);
      }
    });

    $scope.saveUser = function() {
      // $scope.user already updated!
      return user.save($scope.user).error(function(err) {
        if(err.field && err.msg) {
          // err like {field: "name", msg: "Server-side error for this username!"} 
          $scope.editableForm.$setError(err.field, err.msg);
        } else { 
          // unknown error
          $scope.editableForm.$setError('name', gettext("V aplikaci bohužel nastala chyba."));
        }
      });
    };

  }])

  .controller('AppOverview', ['$scope', 'places', '$http', '$routeParams',
      function($scope, places, $http, $routeParams) {

    var mapSkills = {};

    $scope.user = $routeParams.user || '';
    $scope.places = places;
    $http.get('/mapskill/' + $scope.user).success(function(data){
      angular.forEach(data, function(p){
        mapSkills[p.code] = mapSkills[p.code] || {};
        mapSkills[p.code][p.type] = p;
      });
      $scope.mapSkillsLoaded = true;
    });
    places.getOverview().success(function(data){
      $scope.mapCategories = data;
    });

    $scope.mapSkills = function(code, type) {
      if (!$scope.mapSkillsLoaded) {
        return;
      }
      var defalut = {
        count : 0
      };
      if (!type) {
        return avgSkills(mapSkills[code]);
      }
      return (mapSkills[code] && mapSkills[code][type]) || defalut;
    };
    
    function avgSkills(skills) {
      var learned = 0;
      var practiced = 0;
      for (var i in skills){
        var p = skills[i];
        learned += p.learned;
        practiced += p.practiced;
      }
      var avg = {
        learned : learned,
        practiced : practiced,
      };
      return avg;
    }
  }])

  .controller('AppConfused', ['$scope', '$http', 'gettext',
      function($scope, $http, gettext){
    $http.get('/confused/').success(function(data){
      angular.forEach(data, function(p){
        p.wrongRatio = p.mistake_count / p.asked_count;
      });
      $scope.confused = data;
      $scope.loaded = true;
    }).error(function(){
      $scope.loaded = true;
      $scope.error = gettext("V aplikaci bohužel nastala chyba.");
    });
  }])
  
  .controller('ReloadController', ['$window', function($window){
    $window.location.reload();
  }]);
}());
