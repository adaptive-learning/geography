(function() {
  'use strict';
  /* Controllers */
  angular.module('blindMaps.controllers', [])
  
  .controller('AppCtrl', function($scope, $rootScope, user) {
    $rootScope.topScope = $rootScope;

    var updateUser = function(data) {
      $rootScope.user = data;
    };
    user.getUser(updateUser);

    $rootScope.logout = function() {
      $rootScope.user = user.logout(updateUser);
    };

    $scope.vip = function() {
      return $scope.user && $scope.user.username == 'Verunka';
    };
  })

  .controller('AppView', function($scope, $routeParams, $filter, 
        places, mapTitle, mapControler) {
    $scope.part = $routeParams.part;
    var user = $routeParams.user || '';

    mapControler.registerCallback(function() {
      var data = places.getCached($scope.part, user);
      updatePlaces(data);
    });

    places.get($scope.part, user, updatePlaces);

    $scope.placeClick = function(place) {
      mapControler.highlightState(place.code);
    };

    function updatePlaces(data) {
      $scope.placesTypes = data;
      var states = $filter('StatesFromPlaces')($scope.placesTypes);
      mapControler.updatePlaces(states);
      $scope.name = mapTitle($scope.part, user);
    }
  })

  .controller('AppPractice', function($scope, $routeParams, $timeout, $filter,
      question, mapControler, user, events, colors) {
    $scope.part = $routeParams.part;

    $scope.highlight = function() {
      var active = $scope.question;
      $scope.layer = mapControler.getLayerContaining(active.code);
      mapControler.highLightLayer($scope.layer);
      if ($filter('isPickNameOfType')($scope.question)) {
        mapControler.highlightState(active.code, colors.NEUTRAL);
      }
      if ($filter('isFindOnMapType')($scope.question) && active.options) {
        mapControler.highlightStates(active.options.map(function(option) {
          return option.code;
        }), colors.NEUTRAL);
      }
    };

    $scope.checkAnswer = function(selected) {
      var asked = $scope.question.code;
      highlightAnswer(asked, selected);
      $scope.question.answer = selected;
      $scope.progress = question.answer($scope.question);
      if (asked == selected) {
        user.addPoint();
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
        mapControler.highlightState(asked, colors.GOOD);
      }
      mapControler.highlightState(selected, asked == selected ? colors.GOOD : colors.BAD);
      if ($filter('isPickNameOfType')($scope.question)) {
        highlightOptions(selected);
      }
    }

    function setupSummary() {
      $scope.layer = undefined;
      // prevents additional points gain. issue #38
      $scope.summary = question.summary();
      $scope.showSummary = true;
      mapControler.clearHighlights();
      angular.forEach($scope.summary.questions, function(q) {
        var correct = q.code == q.answer;
        mapControler.highlightState(q.code, correct ? colors.GOOD : colors.BAD, 1);
      });
      events.emit('questionSetFinished', user.getUser().points);
    }

    function setQuestion(active) {
      $scope.question = active;
      mapControler.clearHighlights();
      $scope.highlight();
      $scope.canNext = false;
    }

    function highlightOptions(selected) {
      $scope.question.options.map(function(o) {
        o.correct = o.code == $scope.question.code;
        o.selected = o.code == selected;
        o.disabled = true;
        return o;
      });
    }

    function isInActiveLayer(code) {
      return $scope.layer == mapControler.getLayerContaining(code);
    }
    mapControler.onClick(function(code) {
      if ($filter('isFindOnMapType')($scope.question) && 
          !$scope.canNext && 
          $filter('isAllowedOption')($scope.question, code) &&
          isInActiveLayer(code)) {
        $scope.checkAnswer(code);
        $scope.$apply();
      }
    });

    mapControler.registerCallback(function() {
      question.first($scope.part, $routeParams.place_type, function(q) {
        setQuestion(q);
      });
    });
  });
}());
