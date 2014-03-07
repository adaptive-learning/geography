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
        places, mapTitle) {
    $scope.part = $routeParams.part;
    var user = $routeParams.user || '';
    $scope.typeCategories = places.getCategories();

    places.get($scope.part, user, updatePlaces);

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
  })

  .controller('AppPractice', function($scope, $routeParams, $timeout, $filter,
      question, user, events, colors, places, $) {
    $scope.part = $routeParams.part;
    $scope.placeType = $routeParams.place_type;
    
    // To fetch names of all places on map and be able to show name of wrongly answered place
    places.getPlaces($scope.part);

    $scope.highlight = function() {
      var active = $scope.question;
      $scope.layer = $scope.map.getLayerContaining(active.asked_code);
      $scope.map.highLightLayer($scope.layer);
      $scope.map.placeToFront(active.asked_code);
      if ($filter('isPickNameOfType')($scope.question)) {
        $scope.map.highlightState(active.asked_code, colors.NEUTRAL);
      }
      if ($filter('isFindOnMapType')($scope.question) && active.options) {
        $scope.map.highlightStates(active.options.map(function(option) {
          return option.code;
        }), colors.NEUTRAL);
      }
    };

    $scope.checkAnswer = function(selected) {
      var asked = $scope.question.asked_code;
      highlightAnswer(asked, selected);
      $scope.question.answered_code = selected;
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
        $scope.map.highlightState(asked, colors.GOOD);
      }
      $scope.map.highlightState(selected, asked == selected ? colors.GOOD : colors.BAD);
      if ($filter('isPickNameOfType')($scope.question)) {
        highlightOptions(selected);
      }
    }

    function setupSummary() {
      $scope.layer = undefined;
      // prevents additional points gain. issue #38
      $scope.summary = question.summary();
      $scope.showSummary = true;
      $scope.map.clearHighlights();
      $scope.map.hideLayers();
      angular.forEach($scope.summary.questions, function(q) {
        var correct = q.asked_code == q.answered_code;
        $scope.map.showLayerContaining(q.asked_code);
        $scope.map.highlightState(q.asked_code, correct ? colors.GOOD : colors.BAD, 1);
      });
      $("html, body").animate({ scrollTop: "0px" });
      events.emit('questionSetFinished', user.getUser().points);
    }

    function setQuestion(active) {
      $scope.question = active;
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
        setQuestion(q);
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
  });
}());
