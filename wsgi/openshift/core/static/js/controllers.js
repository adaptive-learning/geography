'use strict';

/* Controllers */

angular.module('myApp.controllers', [])
  .controller('AppCtrl', function($scope, $rootScope, $http, $cookies, $route, $location) {
    $rootScope.topScope = $rootScope;
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] =  'application/x-www-form-urlencoded';
    	
    $rootScope.getUser = function(callback) {
        $http.get('user/').success(function(data) {
            $rootScope.user = data;
            callback && callback(data);
        })
	}

    $rootScope.getUser();

    $('.atooltip').tooltip({"placement" : "bottom"});
    //$('a#fdbk_tab').colorbox();

    $rootScope.logout = function(){
        $rootScope.user = {
            'username' : '',
            'points' :  0 
        }
        $http.get('user/logout/').success(function(data) {
            $rootScope.user = data;
        })
    }

    $rootScope.addPoint = function(){
        $rootScope.user.points++;
    }
    
    $scope.vip = function() {
        return $scope.user && ($scope.user.username == 'Verunka')
    }
    
    $scope.getActiveClass = function(path) {
        if ($location.path().substr(0, path.length) == path) {
          return "active"
        } else {
          return ""
        }
    }
    
  })

  .controller('AppView', function($scope, $routeParams, $filter, usersplaces, question, placeName) {
    $scope.part = $routeParams.part;
    $scope.user = $routeParams.user || "";
    $scope.name = placeName($scope.part);

    var mapConfig = {
        name : $scope.part.toLowerCase(),
        showTooltips : true,
        states : []
    }
    
    $scope.placesTypes = usersplaces($scope.part, $scope.user, function(data) {
        $scope.placesTypes = data;
        $scope.$parent.placesTypes = data;
        var states = $filter("StatesFromPlaces")(data);
        $scope.map.updateStates(states);
    });
    mapConfig.states = $filter("StatesFromPlaces")($scope.placesTypes);
    $scope.map = initMap(mapConfig);

//    question.availableCount($scope.part, function(count) {
//        $scope.practiceCount = count;
//    })
    $(".btn-practice").focus()

  })

  .controller('AppPractice', function($scope, $routeParams, $timeout, $location, question, placeName) {
	$scope.FIND_ON_MAP_QUESTION_TYPE = 0;
	$scope.PICK_NAME_OF_6_OPTIONS_QUESTION_TYPE = 1;
    $scope.PICK_NAME_OF_4_OPTIONS_QUESTION_TYPE = 2;
    $scope.FIND_ON_MAP_OF_OPTIONS_QUESTION_TYPE = 3
    $scope.PICK_NAME_OF_2_OPTIONS_QUESTION_TYPE = 4;
    $scope.FIND_ON_MAP_OF_2_OPTIONS_QUESTION_TYPE = 5
	
    $scope.part = $routeParams.part;
    $scope.name = placeName($scope.part);

    $scope.setQuestion = function(active) {
        $scope.question = active;
        $scope.map.clearHighlights();
        if ($scope.isPickNameOfType()) {
            $scope.map.highlightState(active.code, NEUTRAL);
        }
        if (active.type == $scope.FIND_ON_MAP_OF_OPTIONS_QUESTION_TYPE || active.type == $scope.FIND_ON_MAP_OF_2_OPTIONS_QUESTION_TYPE) {
        	$scope.map.highlightStates(active.options.map(function(option) {
        		return option.code;
			}), NEUTRAL)
        }
        $scope.canNext = false;
        $scope.select = undefined;
        $scope.starterLetters = undefined;
    }

    $scope.check = function(selected) {
       var correct = (selected == $scope.question.code);
       if ($scope.isFindOnMapType()) {
           $scope.map.highlightState($scope.question.code, GOOD);
       }
       $scope.map.highlightState(selected, correct ? GOOD : BAD);
       if ($scope.isPickNameOfType()) {
           $scope.highlightOptions(selected);
       }
       $scope.canNext = true;
       if (correct) {
           $scope.$parent.addPoint();
       }
       $scope.question.answer = selected;
       $scope.progress = question.answer($scope.question);
       $timeout(function(){
        $(".btn-continue").focus()
       },100)
    }

    $scope.next = function() {
        if($scope.progress < 100) {
            question.next($scope.part, function(q) {
                $scope.setQuestion(q);
            })
        } else {
            $scope.summary = question.summary();
            $scope.showSummary = true;
            $scope.map.clearHighlights();
            angular.forEach($scope.summary.questions, function(q){
                var correct = q.code == q.answer;
                $scope.map.highlightState(q.code, correct ? GOOD : BAD, 1);
            })
        }
    }

    $scope.highlightOptions = function(selected) {
    	$scope.question.options.map(function(o) {
			o.correct = o.code == $scope.question.code;
			o.selected = o.code == selected;
			o.disabled = true;
			return o;
		})

    }
    
    $scope.isFindOnMapType = function() {
        return $scope.question &&
               ($scope.question.type == $scope.FIND_ON_MAP_QUESTION_TYPE 
             || $scope.question.type == $scope.FIND_ON_MAP_OF_OPTIONS_QUESTION_TYPE
             || $scope.question.type == $scope.FIND_ON_MAP_OF_2_OPTIONS_QUESTION_TYPE)
    }
    
    $scope.isPickNameOfType = function() {
        return $scope.question &&
               ($scope.question.type == $scope.PICK_NAME_OF_6_OPTIONS_QUESTION_TYPE 
             || $scope.question.type == $scope.PICK_NAME_OF_4_OPTIONS_QUESTION_TYPE
             || $scope.question.type == $scope.PICK_NAME_OF_2_OPTIONS_QUESTION_TYPE)
    }
    
    $scope.isAllowedOpion = function(code) {
        return !$scope.question.options || 1 == $scope.question.options.filter(function(place){
            return place.code == code;
        }).length
    }

    var mapConfig = {
        name : $scope.part.toLowerCase(),
        click : function  (code) {
            if ($scope.isFindOnMapType() && !$scope.canNext && $scope.isAllowedOpion(code)) {
                $scope.check(code);
                $scope.$apply();
            }
        }
    }
    $scope.map = initMap(mapConfig, function() {
        question.first($scope.part, function(q) {
            if(q) $scope.setQuestion(q);
            else {
                $scope.showSummary = true;
                $scope.errorMessage = 'Žádný stát není potřeba procvičovat.';
            }
        })
    })
    
  })

