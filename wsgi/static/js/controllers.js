'use strict';

/* Controllers */

angular.module('myApp.controllers', [])
  .controller('AppCtrl', function($scope, $rootScope, $http, $cookies, $route) {
    $rootScope.topScope = $rootScope;
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] =  'application/x-www-form-urlencoded'
    $http.get('user/').success(function(data) {
        $rootScope.user = data;
    })

    $('.atooltip').tooltip({"placement" : "bottom"});
    $('.input-tooltip').tooltip({"placement" : "bottom", trigger: "focus"});
    $('.dropdown-menu li input').click(function(event){
        // hack to prevent login dropdown from premature closing on mobile platforms
        var dropdown = $(this).parents('ul.dropdown-menu')
        setTimeout(function(){
            if (!dropdown.is(":visible")) {
            	dropdown.css("display", "block");
            }
        },200);
        event.stopPropagation();
    });
    
    $('a#fdbk_tab').colorbox();

    $rootScope.login = function(){
        var credentials = {
            'username' : $scope.getUsername ? $scope.getUsername() : $scope.username,
            'password' : $scope.getPassword ? $scope.getPassword() : $scope.password
        }
        $http.post('user/login/', credentials).success(function(data) {
            $rootScope.loginResponse = data;
            if (data.success) {
                //$route.reload();
                document.location.reload(true)
            }
        }).error(function(data) {
            $rootScope.loginResponse = {'messgae' : "Přihllášení se nezdařilo"};
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

  .controller('AppView', function($scope, $routeParams, usersplaces, question) {
    $scope.part = $routeParams.part;
    $scope.user = $routeParams.user || "";
    $scope.placesTypes = [];

    usersplaces($scope.part, $scope.user, function(data) {
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

    question.availableCount($scope.part, function(count) {
        $scope.practiceCount = count;
    })

  })

  .controller('AppPractice', function($scope, $routeParams, $timeout, $location, places, question) {
    $scope.part = $routeParams.part;

    $scope.setQuestion = function(active) {
        $scope.question = active;
        $scope.map.clearHighlights();
        if (active.type == 1) {
            $scope.map.blink(active.code);
        }
        $scope.canNext = false;
        $scope.select = undefined;
        $("select.select2").select2("val", $scope.select);
    }

    $scope.check = function(selected) {
       var correct = (selected == $scope.question.code);
       $scope.map.highlightState($scope.question.code);
       $scope.map.highlightState(selected, correct ? GOOD : BAD);
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
            $scope.summary = question.summary();
            $scope.showSummary = true;
            $scope.map.clearHighlights();
            angular.forEach($scope.summary.questions, function(q){
                var correct = q.code == q.answer;
                $scope.map.highlightState(q.code, correct ? GOOD : BAD);
            })
        }
    }

    $scope.openPlacesSelect = function() {
        $timeout(function() {
            $("select.select2").select2("open");
        },100);
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
            $("select.starters").select2({
                placeholder: "Počáteční písmeno",
                width : '100px'
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
                if(q) $scope.setQuestion(q);
                else {
                    $scope.showSummary = true;
                    $scope.errorMessage = 'Žádný stát není potřeba procvičovat.';
                }
            })
        })
    })
    
  })

