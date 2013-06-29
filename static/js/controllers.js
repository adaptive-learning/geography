'use strict';

/* Controllers */

angular.module('myApp.controllers', [])
  .controller('AppCtrl', function($scope, $rootScope, $http, $cookies) {
    $rootScope.topScope = $rootScope;
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] =  'application/x-www-form-urlencoded'
    $http.get('user/').success(function(data) {
        $rootScope.user = data;
    })

    $('.atooltip').tooltip({"placement" : "bottom"});
    $('.input-tooltip').tooltip({"placement" : "bottom", trigger: "focus"});
    $('.dropdown-menu').click(function(event){
         event.stopPropagation();
     });
    $('a#fdbk_tab').colorbox();

    $rootScope.login = function(){
        $scope.$apply();
        var credentials = {
            'username' : $scope.username,
            'password' : $scope.password
        }
        $http.post('user/login/', credentials).success(function(data) {
            $rootScope.user = data;
            $rootScope.loginFail = undefined;
        }).error(function(data) {
            $rootScope.loginFail = "Přihllášení se nezdařilo";
        });
    }

    $rootScope.logout = function(){
        $http.get('user/logout/').success(function(data) {
            $rootScope.user = data;
        })
    }

    $rootScope.addPoint = function(){
        $rootScope.user.points++;
    }
  })

  .controller('AppView', function($scope, $routeParams, usersplaces) {
    $scope.part = $routeParams.part;
    $scope.placesTypes = [];

    usersplaces($scope.part, function(data) {
        $scope.placesTypes = data;
        $scope.$parent.placesTypes = data;
        var places = {};
        angular.forEach(data[0].places, function(place) {
            places[place.code] = {
                name : place.name,
                skill : place.skill
            }
        });
        var mapConfig = {
            name : $scope.part.toLowerCase(),
            showTooltips : true,
            states : places
        }
        $scope.map = initMap(mapConfig);
    });

  })

  .controller('AppPractice', function($scope, $routeParams, $timeout, $location, places, question) {
    $scope.part = $routeParams.part;

    $scope.setQuestion = function(active) {
        $scope.question = active;
        $scope.map.clearHighlights();
        if (active.type == 1) {
            $scope.map.highlightState(active.code);
        }
        $scope.canNext = false;
        $scope.select = undefined;
        $("select.select2").select2("val", $scope.select);
    }

    $scope.check = function(selected) {
       var correct = (selected == $scope.question.code);
       $scope.map.highlightState(selected, correct ? GOOD : BAD);
       $scope.map.highlightState($scope.question.code, selected ? GOOD : BAD);
       $scope.canNext = true;
       $("select.select2").select2("val", $scope.question.code);
       if (correct) {
           $scope.$parent.addPoint();
       }
       $scope.question.answer = selected;
       $scope.progress = question.answer($scope.question);
    }

    $scope.next = function() {
        if($scope.progress < 100) {
            question.next($scope.part, function(q) {
                $scope.setQuestion(q);
            })
        } else {
            $location.path("/view/" + $scope.part);
        }
    }

    places($scope.part, function(placesTypes) {
        $scope.places = placesTypes[0].places;
        $timeout(function() {
            var format = function(state) {
                if (!state.id) return state.text; // optgroup
                    return '<i class="flag-'+state.id+'"></i> ' + state.text;
            }
            $("select.select2").select2({
                placeholder: "Vyber stát",
                formatResult: format,
                formatSelection: format,
                escapeMarkup: function(m) { return m; }
            });
        },100);

        var mapConfig = {
            name : $scope.part.toLowerCase(),
            click : function  (data) {
                if ($scope.question.type == 0 && !$scope.canNext) {
                    $scope.check(data);
                    $scope.$apply();
                }
            }
        }
        $scope.map = initMap(mapConfig, function() {
            question.first($scope.part, function(q) {
                $scope.setQuestion(q);
            })
        })
    })
    
  })

