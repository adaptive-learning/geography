(function() {
  'use strict';
  /* Directives */
  angular.module('blindMaps.directives', [])

  .directive('placeLabel', function() {
    return {
      restrict : 'A',
      template : '<i class="flag-{{place.code}}"></i> {{place.name}}',
      compile : function(element) {
        element.addClass('label');
        element.addClass('label-default');
      }
    };
  })

  .directive('blindMap', function(mapControler, places, singleWindowResizeFn, getMapResizeFunction) {
    return {
      restrict : 'E',
      template : '<div class="map-container">' +
                  '<div id="map-holder">' +
                      '<div class="loading-indicator" ng-show="loading"></div>' +
                  '</div>' +
                  '<h1 ng-bind="name"></h1>' +
                  '<div class="btn-group-vertical map-switch" data-toggle="buttons" ng-show="!practice" >' +
                    '<a class="btn btn-default" href="#/view/{{part}}/"' +
                        'ng-class="\'/view/\'+part+\'/\'|isActive">' +
                      'Moje znalosti' +
                    '</a>' +
                    '<a class="btn btn-default" href="#/view/{{part}}/average"' +
                        'ng-class="\'/view/\'+part+\'/average\'|isActive">' +
                      'Průměrný uživatel' +
                    '</a>' +
                  '</div>' +
                  '<a ng-show="!practice"' +
                      'href="#/practice/{{part}}/"' +
                      'class="btn btn-primary btn-lg btn-practice" >' +
                    'Procvičovat' +
                  '</a>' +
                  '<div class="zoom-buttons"></div>'+
                '</div>',
      link : function($scope, elem, attrs) {
        $scope.loading = true;
        $scope.name = places.getName($scope.part);
        $scope.practice = !attrs.practice;
        var showTooltips = attrs.practice !== undefined;

        mapControler.init($scope.part, showTooltips, elem, function(m) {
          $scope.loading = false;
          var resize = getMapResizeFunction(m, elem, $scope.practice);
          singleWindowResizeFn(resize);
          resize();
        });
      },
      replace : true
    };
  })

  .directive('zoomButtons', function() {
    return {
      restrict : 'C',
      template : '<div class="btn-group zoom-btn" ng-show="!loading">' +
                    '<a class="btn btn-default" id="zoom-out">' +
                      '<i class="glyphicon glyphicon-minus"></i></a>' +
                    '<a class="btn btn-default" id="zoom-in">' +
                      '<i class="glyphicon glyphicon-plus"></i></a>' +
                  '</div>'
    };
  })

  .directive('email', function() {
    return {
      restrict : 'C',
      compile : function(elem) {
        var emailAddress = elem.html();
        emailAddress = emailAddress.replace('{zavinac}', '@');
        emailAddress = '<a href="mailto :' + emailAddress + 
  '">' + emailAddress + 
  '</a>';
        elem.html(emailAddress);
      }
    };
  })

  .directive('atooltip', function() {
    return {
      restrict : 'C',
      compile : function(elem) {
        elem.tooltip({ 'placement' : 'bottom' });
      }
    };
  })

  .directive('dropLogin', function() {
    return {
      restrict : 'C',
      compile : function(elem) {
        elem.bind('click', function() {
          elem.tooltip('destroy');
          elem.parent().find('.tooltip').remove();
        });
      }
    };
  })

  .directive('points', function($timeout, events) {
    return {
      scope : true,
      restrict : 'C',
      link : function($scope, elem) {
        events.on('userUpdated', function(user) {
          $scope.user = user;
          if (user.points == 1) {
            $timeout(function() {
              elem.tooltip('show');
            }, 0);
          }
        });
      }
    };
  })

  .directive('dropLogin', function($timeout, events) {
    return {
      restrict : 'C',
      link : function($scope, elem) {
        events.on('questionSetFinished', function(points) {
          if (10 < points && points <= 20) {
            $timeout(function() {
              elem.tooltip('show');
            }, 0);
          }
        });
      }
    };
  });
}());
