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
  
  .directive('blindMap', function () {
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
        $scope.name = attrs.name;
        $scope.practice = attrs.practice;
        //TODO: call initMap service from here and not from controlers.
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
  
  

