'use strict';

/* Controllers */

angular.module('myApp.controllers', [])
  .controller('AppCtrl', function($scope, $rootScope, $http, $cookies, $route, $location, $timeout) {
    $rootScope.topScope = $rootScope;
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] =  'application/x-www-form-urlencoded';

    $rootScope.getUser = function(callback) {
        $http.get('user/').success(function(data) {
            $rootScope.user = data;
            callback && callback(data);
        });
    };

    $rootScope.getUser();

    $('.atooltip').tooltip({"placement" : "bottom"});
    //$('a#fdbk_tab').colorbox();

    $rootScope.logout = function(){
        $rootScope.user = {
            'username' : '',
            'points' :  0
        };
        $http.get('user/logout/').success(function(data) {
            $rootScope.user = data;
        });
    };

    $rootScope.addPoint = function(){
        $rootScope.user.points++;
        if ($rootScope.user.points == 1) {
            $timeout(function(){
                $('#points').tooltip("show");
            },0);

        }
    };

    $scope.vip = function() {
        return $scope.user && ($scope.user.username == 'Verunka');
    };

    $scope.getActiveClass = function(path) {
        if ($location.path().substr(0, path.length) == path) {
          return "active";
        } else {
          return "";
        }
    };

    var emailAddress = $("#footer .email").html();
    emailAddress = emailAddress.replace("{zavinac}", "@");
    emailAddress = '<a href="mailto:'+emailAddress+'">'+ emailAddress+ '</a>';
    $("#footer .email").html(emailAddress);

  })

  .controller('AppView', function($scope, $routeParams, $filter, $timeout, usersplaces, question, placeName) {
    $scope.part = $routeParams.part;
    $scope.user = $routeParams.user || "";
    $scope.name = placeName($scope.part);

    var mapConfig = {
        name : $scope.part.toLowerCase(),
        showTooltips : true,
        states : []
    };

    $scope.placesTypes = usersplaces($scope.part, $scope.user, function(data) {
        $scope.placesTypes = data;
        $scope.$parent.placesTypes = data;
        var states = $filter("StatesFromPlaces")(data);
        $scope.map.updatePlaces(states);
        $scope.name = placeName($scope.part);
    });
    mapConfig.states = $filter("StatesFromPlaces")($scope.placesTypes);
    $scope.map = initMap(mapConfig);

    $scope.hover = function(place, isHovered) {
        place.isHovered = isHovered;
        if (isHovered) {
            $timeout(function(){
                if (place.isHovered){
                    $scope.map.highlightState(place.code);
                }
            }, 200);
        }
    };

//    question.availableCount($scope.part, function(count) {
//        $scope.practiceCount = count;
//    })
    $scope.colNum = function (colsCount) {
        return Math.floor(12/colsCount);
    };

  })

  .controller('AppPractice', function($scope, $routeParams, $timeout, $location, question, placeName) {
    $scope.part = $routeParams.part;
    $scope.name = placeName($scope.part);

    $scope.highlight = function() {
        var active = $scope.question;
        $scope.layer = $scope.map.getLayerContaining(active.code);
        $scope.map.highLightLayer($scope.layer);
        if ($scope.isPickNameOfType()) {
            $scope.map.highlightState(active.code, NEUTRAL);
        }
        if ($scope.isFindOnMapType() && active.options) {
            $scope.map.highlightStates(active.options.map(function(option) {
                return option.code;
            }), NEUTRAL);
        }
    };

    $scope.setQuestion = function(active) {
        $scope.question = active;
        $scope.map.clearHighlights();
        $scope.highlight();
        $scope.canNext = false;
        $scope.select = undefined;
        $scope.starterLetters = undefined;
    };

    $scope.check = function(selected) {
       var correct = (selected == $scope.question.code);
       if ($scope.isFindOnMapType()) {
           $scope.map.highlightState($scope.question.code, GOOD);
       }
       $scope.map.highlightState(selected, correct ? GOOD : BAD);
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
            question.next($scope.part, function(q) {
                $scope.setQuestion(q);
            });
        } else {
            $scope.summary = question.summary();
            $scope.showSummary = true;
            $scope.map.clearHighlights();
            angular.forEach($scope.summary.questions, function(q){
                var correct = q.code == q.answer;
                $scope.map.highlightState(q.code, correct ? GOOD : BAD, 1);
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

    $scope.isAllowedOpion = function(code) {
        return !$scope.question.options || 1 == $scope.question.options.filter(function(place){
            return place.code == code;
        }).length;
    };
    $scope.isInActiveLayer = function(code) {
        return $scope.layer == $scope.map.getLayerContaining(code);
    };

    var mapConfig = {
        name : $scope.part.toLowerCase(),
        click : function  (code) {
            if ($scope.isFindOnMapType()
                    && !$scope.canNext
                    && $scope.isAllowedOpion(code)
                    && $scope.isInActiveLayer(code)) {
                $scope.check(code);
                $scope.$apply();
            }
        }
    };
    $scope.map = initMap(mapConfig, function() {
        question.first($scope.part, function(q) {
            if(q) $scope.setQuestion(q);
            else {
                $scope.showSummary = true;
                $scope.errorMessage = 'Žádný stát ještě není potřeba znovu procvičovat.';
            }
        });
    });

  });

