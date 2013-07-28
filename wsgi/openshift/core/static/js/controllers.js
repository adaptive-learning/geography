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
    $scope.placesTypes = undefined;

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
    $(".btn-practice").focus()

  })

  .controller('AppPractice', function($scope, $routeParams, $timeout, $location, places, question) {
	$scope.FIND_ON_MAP_QUESTION_TYPE = 0;
	$scope.PICK_NAME_OF_QUESTION_TYPE = 1;
	$scope.PICK_NAME_OF_OPTIONS_QUESTION_TYPE = 2;
	$scope.FIND_ON_MAP_OF_OPTIONS_QUESTION_TYPE = 3
	
    $scope.part = $routeParams.part;

    $scope.setQuestion = function(active) {
        $scope.question = active;
        $scope.map.clearHighlights();
        if (active.type == $scope.PICK_NAME_OF_QUESTION_TYPE || active.type == $scope.PICK_NAME_OF_OPTIONS_QUESTION_TYPE) {
            $scope.map.blink(active.code);
        }
        if (active.type == $scope.FIND_ON_MAP_OF_OPTIONS_QUESTION_TYPE) {
        	active.options.map(function(option) {
        		$scope.map.blink(option.code);
			})
        }
        $("select.select2").select2("enable", true)
        $scope.canNext = false;
        $scope.select = undefined;
        $scope.starterLetters = undefined;
        $("select.places").select2("val", $scope.select);
        $("select.starters").select2("val", $scope.starterLetters);
        setTimeout(function() {
            $("select.places").select2('focus');
        },100)
    }

    $scope.check = function(selected) {
       var correct = (selected == $scope.question.code);
       if ($scope.isFindOnMapType()) {
           $scope.map.highlightState($scope.question.code, GOOD);
       }
       $scope.map.highlightState(selected, correct ? GOOD : BAD);
       if ($scope.question.type == $scope.PICK_NAME_OF_OPTIONS_QUESTION_TYPE) {
           $scope.highlightOptions(selected);
       }
       $scope.canNext = true;
       $("select.places").select2("val", $scope.question.code);
       $("select.select2").select2("enable", false)
       if (correct) {
           $scope.$parent.addPoint();
       }
       $scope.question.answer = selected;
       $scope.progress = question.answer($scope.question);
       setTimeout(function() {
       },100)
       $("#btn-continue").focus()
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
    	     || $scope.question.type == $scope.FIND_ON_MAP_OF_OPTIONS_QUESTION_TYPE)
    }
    
    $scope.openPlacesSelect = function() {
        $timeout(function() {
            $("select.places").select2("open");
        },100);
    }

    places($scope.part, function(placesTypes) {
        $scope.places = placesTypes[0].places;
        $timeout(function() {
            var format = function(state) {
            	if (!state) return "";
                if (!state.id) return state.text; // optgroup
                    return '<i class="flag-'+state.id+'"></i> ' + state.text;
            }
            $("select.places").select2({
                formatResult: format,
                formatSelection: format,
                escapeMarkup: function(m) { return m; }
            });
            $("select.starters").select2({
                width : '100px'
            });
        },100);

        var mapConfig = {
            name : $scope.part.toLowerCase(),
            click : function  (data) {
                if ($scope.isFindOnMapType() && !$scope.canNext) {
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

