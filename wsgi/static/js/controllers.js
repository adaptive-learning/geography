'use strict';

/* Controllers */

angular.module('myApp.controllers', [])
  .controller('AppCtrl', function($rootScope) {
    $rootScope.topScope = $rootScope;
    $rootScope.points = 0;
    $('#points').tooltip({"placement" : "bottom"})
    $('a#fdbk_tab').colorbox();
  })

  .controller('AppHomeCtrl', function($scope, $http, maps) {
      maps(undefined, function(data) {
        $scope.worldParts = data;
      });
  })

  .controller('AppView', function($scope, $http,  $routeParams, maps) {
    $scope.part = $routeParams.part;
    $scope.placesTypes = [];
    $scope.hover = function (code, isHovered) {
        if (isHovered ) {
            //$scope.map.highlightState(code);
        } else {
            //$scope.map.clearHighlights();
        }
    }

    $scope.getPlaceByCode = function (code) {
        var needle;
        angular.forEach($scope.placesTypes, function(type) {
            angular.forEach(type.places, function( place) {
                if (place.code == code) {
                    needle = place;
                }
            })

        })
        return needle;
    }

    $scope.highlight = function (code, isHovered) {
        var place = $scope.getPlaceByCode(code);
        place.highlight = isHovered;
    }


    $http.get('php/places.json').success(function(data) {
        $scope.placesTypes = data;
        $scope.$parent.placesTypes = data;
    });

    maps($scope.part, function(data) {
        $scope.map = initMap(data, $scope);
    });
  })

  .controller('AppPractice', function($scope, $http, $routeParams, $timeout, maps, places) {
    $scope.part = $routeParams.part;
    $scope.index = 0;

    $scope.update = function() {
        var questionTypes = [
            "Vyber na mapě stát",
            "Jak se jmenuje stát zvýrazněný na mapě?"
        ];
        var active = $scope.questions[$scope.index]
        $scope.question = active;
        var place = $scope.places[active.place]; 
        $scope.question.code = place.code;
        $scope.question.name = place.name;
        $scope.question.text = questionTypes[active.type];
        var mapPlace = (active.type == 1 ? place.code : "");
        //$scope.map.clearHighlights();
        //$scope.map.highlightState(mapPlace);
        $scope.canNext = false;
        $scope.select = undefined;
        $("select.select2").select2("val", $scope.select);
    }
    $scope.check = function(selected) {
       var correct = (selected == $scope.question.code);
       //$scope.map.highlightState(selected, correct ? GOOD : BAD);
       //$scope.map.highlightState($scope.question.code, selected ? GOOD : BAD);
       $scope.canNext = true;
       $scope.progress = 100 * ($scope.index+1) / $scope.questions.length;
       $("select.select2").select2("val", $scope.question.code);
       if (correct) {
           $scope.$parent.points++
       }
    }

    $scope.next = function() {
        $scope.index++;
        if($scope.index < $scope.questions.length) {
            $scope.update();
        } else {
            window.location.hash = "#/view/" + $scope.part;
        }
    }

    $scope.setPlaces = function(placesTypes) {
        $scope.places = placesTypes[0].places;
        $timeout(function() {
            var format = function(state) {
                if (!state.id) return state.text; // optgroup
                    return '<i class="flag-us-'+state.id+'"></i> ' + state.text;
            }
            $("select.select2").select2({
                placeholder: "Vyber stát",
                formatResult: format,
                formatSelection: format,
                escapeMarkup: function(m) { return m; }
            });
        },100);
    }

    $scope.init = function (mapData) {
        $scope.map = initMap(mapData, $scope);
        $http.get('php/questions.json').success(function(data) {
            $scope.questions = data;
            $scope.update();
        });
    }

    maps($scope.part, function(data) {
        $scope.init(data);
    });


    if ($scope.$parent.placesTypes) {
        $scope.setPlaces($scope.$parent.placesTypes);
    } else {
        $http.get('php/places.json').success(function(data) {
            $scope.setPlaces(data);
        });
    }
    
  })

