'use strict';

/* Controllers */

angular.module('blindMaps.controllers', [])
  .controller('AppCtrl', function($scope, $rootScope, $timeout, $cookies, user) {
    $rootScope.topScope = $rootScope;

    var updateUser = function(data) {
        $rootScope.user = data;
        $cookies.points = $rootScope.user;
    };
    user.getUser(updateUser);

    $('.atooltip').tooltip({"placement" : "bottom"});

    $rootScope.logout = function(){
        $rootScope.user = user.logout(updateUser);
    };

    $rootScope.addPoint = function(){
        $rootScope.user.points++;
        $cookies.points = $rootScope.user;
        if ($rootScope.user.points == 1) {
            $timeout(function(){
                $('#points').tooltip("show");
            },0);
        }
    };

    $scope.vip = function() {
        return $scope.user && ($scope.user.username == 'Verunka');
    };
  })

  .controller('AppView', function($scope, $routeParams, $filter, $timeout, 
        usersplaces, question, placeName, mapControler) {
    $scope.part = $routeParams.part;
    $scope.user = $routeParams.user || "";
    $scope.name = placeName($scope.part);

    usersplaces.get($scope.part, $scope.user, function(data) {
        $scope.placesTypes = data;
        $scope.$parent.placesTypes = data;
        var states = $filter("StatesFromPlaces")(data);
        mapControler.updatePlaces(states);
        $scope.name = placeName($scope.part);
    });

    $scope.hover = function(place, isHovered) {
        place.isHovered = isHovered;
        if (isHovered) {
            $timeout(function(){
                if (place.isHovered){
                    mapControler.highlightState(place.code);
                }
            }, 200);
        }
    };
    
    mapControler.registerCallback(function() {
    });
  })

  .controller('AppPractice', function($scope, $routeParams, $timeout, 
          question, placeName, mapControler) {
    $scope.part = $routeParams.part;
    $scope.name = placeName($scope.part);

    $scope.highlight = function() {
        var active = $scope.question;
        $scope.layer = mapControler.getLayerContaining(active.code);
        mapControler.highLightLayer($scope.layer);
        if ($scope.isPickNameOfType()) {
            mapControler.highlightState(active.code, NEUTRAL);
        }
        if ($scope.isFindOnMapType() && active.options) {
            mapControler.highlightStates(active.options.map(function(option) {
                return option.code;
            }), NEUTRAL);
        }
    };

    $scope.setQuestion = function(active) {
        $scope.question = active;
        mapControler.clearHighlights();
        $scope.highlight();
        $scope.canNext = false;
        $scope.select = undefined;
        $scope.starterLetters = undefined;
    };

    $scope.check = function(selected) {
       var correct = (selected == $scope.question.code);
       if ($scope.isFindOnMapType()) {
           mapControler.highlightState($scope.question.code, GOOD);
       }
       mapControler.highlightState(selected, correct ? GOOD : BAD);
       if ($scope.isPickNameOfType()) {
           $scope.highlightOptions(selected);
       }
       $scope.question.answer = selected;
       $scope.progress = question.answer($scope.question);
       if (correct) {
           $scope.$parent.addPoint();
           $timeout(function(){
            $scope.next();
           },700);
       } else {
           $scope.canNext = true;
       }
    };

    $scope.next = function() {
        if($scope.progress < 100) {
            question.next($scope.part, $routeParams.place_type, function(q) {
                $scope.setQuestion(q);
            });
        } else {
            $scope.summary = question.summary();
            $scope.showSummary = true;
            mapControler.clearHighlights();
            angular.forEach($scope.summary.questions, function(q){
                var correct = q.code == q.answer;
                mapControler.highlightState(q.code, correct ? GOOD : BAD, 1);
            });
        }
    };

    $scope.highlightOptions = function(selected) {
        $scope.question.options.map(function(o) {
            o.correct = o.code == $scope.question.code;
            o.selected = o.code == selected;
            o.disabled = true;
            return o;
        });

    };

    $scope.isFindOnMapType = function() {
        return $scope.question && $scope.question.type < 20;
    };

    $scope.isPickNameOfType = function() {
        return $scope.question && $scope.question.type >= 20;
    };

    $scope.isAllowedOption = function(code) {
        return !$scope.question.options || 1 == $scope.question.options.filter(function(place){
            return place.code == code;
        }).length;
    };
    $scope.isInActiveLayer = function(code) {
        return $scope.layer == mapControler.getLayerContaining(code);
    };

    mapControler.onClick(function  (code) {
        if ($scope.isFindOnMapType()
                && !$scope.canNext
                && $scope.isAllowedOption(code)
                && $scope.isInActiveLayer(code)) {
            $scope.check(code);
            $scope.$apply();
        }
    });
    
    mapControler.registerCallback(function() {
        question.first($scope.part, $routeParams.place_type, function(q) {
            $scope.setQuestion(q);
        });
    });

  });

