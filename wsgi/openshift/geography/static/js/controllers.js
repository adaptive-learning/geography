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

  .controller('AppView', function($scope, $routeParams, 
        places, mapTitle, $filter) {
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
      updatePlaces($scope.placesTypes)
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

    $scope.mapCallback = function() {
      var data = places.getCached($scope.part, user);
      updatePlaces(data);
    };
  })

  .controller('AppPractice', function($scope, $routeParams, $timeout, $filter,
      question, user, events, colors) {
    $scope.part = $routeParams.part;
    $scope.placeType = $routeParams.place_type;

    $scope.highlight = function() {
      var active = $scope.question;
      $scope.layer = $scope.map.getLayerContaining(active.code);
      $scope.map.highLightLayer($scope.layer);
      if ($filter('isPickNameOfType')($scope.question)) {
        $scope.map.highlightState(active.code, colors.NEUTRAL);
      }
      if ($filter('isFindOnMapType')($scope.question) && active.options) {
        $scope.map.highlightStates(active.options.map(function(option) {
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
      angular.forEach($scope.summary.questions, function(q) {
        var correct = q.code == q.answer;
        $scope.map.highlightState(q.code, correct ? colors.GOOD : colors.BAD, 1);
      });
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
        o.correct = o.code == $scope.question.code;
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
