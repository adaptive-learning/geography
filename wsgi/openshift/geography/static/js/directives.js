'use strict';

/* Directives */


angular.module('blindMaps.directives', [])

  .directive('placeLabel', function () {
    return {
      restrict: 'E',
      template: '<span class="label label-default">' +
                  '<i class="flag-{{place.code}}"></i> {{place.name}}' +
                '</span>' ,
      link: function ($scope, elem, attrs) {
        $scope.place = attrs.place;
      }
    };
  })
  
  .directive('blindMap', function ($filter, mapControler, usersplaces) {
    return {
      restrict: 'E',
      template: '<center class="map-container">' +
                  '<div id="map-holder">' +
                      '<div class="loading-indicator"></div>' +
                  '</div>' +
                  '<h1 ng-bind="name"></h1>' +
                  '<a  ng-show="practice"' +
                      'href="#/practice/{{part}}"' +
                      'class="btn btn-primary btn-lg btn-practice" >' +
                    'Procvičovat' +
                  '</a>' +
                '</center>',
      link: function ($scope, elem, attrs) {
        $scope.practice = attrs.practice;
        var showTooltips = attrs.practice !== undefined;
        mapControler.init($scope.part, showTooltips);
        if (showTooltips) {
          var places = usersplaces.getCached($scope.part, "");
          mapControler.updatePlaces($filter("StatesFromPlaces")(places));
        }
      }
    };
  })
  
  .directive('email', function () {
    return {
      restrict: 'C',
      link: function ($scope, elem, attrs) {
        var emailAddress = elem.html();
        emailAddress = emailAddress.replace("{zavinac}", "@");
        emailAddress = '<a href="mailto:'+emailAddress+'">'+ emailAddress+ '</a>';
        elem.html(emailAddress);
      }
    };
  });
  
  

