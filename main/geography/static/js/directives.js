(function() {
  'use strict';
  /* Directives */
  angular.module('blindMaps.directives', [])

  .directive('placeLabel', ['colorScale', 'gettext', function(colorScale, gettext) {
    return {
      restrict : 'A',
      template : '<i class="flag-{{place.code}}"></i> {{place.name}}',
      link : function($scope, elem) {
        elem.addClass('label');
        elem.addClass('label-default');
        elem.tooltip({
          html : true,
          placement: 'bottom',
          container: 'body',
          title : '<div class="skill-tooltip">' +
                gettext('Odhad znalosti') + 
                ' <span class="badge badge-default">' +
                  '<i class="color-indicator" style="background-color :' +
                  colorScale($scope.place.probability).hex() + '"></i>' +
                  10 * $scope.place.probability + ' / 10 ' +
                '</span>' +
               '</div>'
        });
      }
    };
  }])

  .directive('blindMap', ['mapControler', 'places', 'singleWindowResizeFn', 
        'getMapResizeFunction', '$parse', 'gettext',
      function(mapControler, places, singleWindowResizeFn, 
        getMapResizeFunction, $parse, gettext) {
    return {
      restrict : 'E',
      template : '<div class="map-container">' +
                  '<div id="map-holder">' +
                      '<div class="loading-indicator" ng-show="loading"></div>' +
                  '</div>' +
                  '<h1 ng-bind="name" ng-show="!practice"></h1>' +
                  '<div class="btn-group-vertical map-switch" data-toggle="buttons" ng-show="!practice" >' +
                    '<a class="btn btn-default" href="#/view/{{part}}/"' +
                        'ng-class="\'/view/\'+part+\'/\'|isActive"' +
                        'tooltip-append-to-body="true"' +
                        'tooltip-placement="right"' +
                        'tooltip="' + gettext('Moje znalosti') + '">' +
                      '<i class="glyphicon glyphicon-user"></i>' +
                    '</a>' +
                    '<a class="btn btn-default" href="#/view/{{part}}/average"' +
                        'ng-class="\'/view/\'+part+\'/average\'|isActive"' +
                        'tooltip-append-to-body="true"' +
                        'tooltip-placement="right"' +
                        'tooltip="' + gettext('Průměrný nový uživatel') + '">' +
                      '<i class="glyphicon glyphicon-globe"></i> ' +
                    '</a>' +
                  '</div>' +
                  '<div class="zoom-buttons"></div>'+
                '</div>',
      link : function($scope, elem, attrs) {
        $scope.loading = true;
        $scope.name = places.getName($scope.part);
        $scope.practice = !attrs.showTooltips;
        var showTooltips = attrs.showTooltips !== undefined;

        var map = mapControler($scope.part, showTooltips, elem, function(m) {
          $scope.loading = false;
          var resize = getMapResizeFunction(m, elem, $scope.practice);
          singleWindowResizeFn(resize);
          resize();
          $scope.$eval(attrs.callback);
          $scope.$digest();
        });
        var model = $parse(attrs.map);
        //Set scope variable for the map
        model.assign($scope, map);
      },
      replace : true
    };
  }])

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
        emailAddress = '<a href="mailto:' + emailAddress + 
  '">' + emailAddress + 
  '</a>';
        elem.html(emailAddress);
      }
    };
  })

  .directive('atooltip', function() {
    return {
      restrict : 'C',
      link : function($scope, elem, attrs) {
        elem.tooltip({ 
          'placement' : attrs.placement || 'bottom',
          'container' : attrs.container,
        });
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

  .directive('points', ['$timeout', 'events', function($timeout, events) {
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
  }])

  .directive('dropLogin',['$timeout', 'events', function($timeout, events) {
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
  }])

  .directive('mapProgress', ['gettext', function(gettext) {
    return {
      restrict : 'C',
      template : '<div class="progress overview-progress">' +
                    '<div class="progress-bar progress-bar-learned" style="' +
                        'width: {{(skills.learned / count)|percent}};">' +
                    '</div>' +
                    '<div class="progress-bar progress-bar-practiced" style="' +
                        'width: {{(skills.practiced / count)|percent}};">' +
                    '</div>' +
                  '</div>',
      link : function($scope, elem, attrs) {
        $scope.count = attrs.count;
        attrs.$observe('skills', function(skills) {
          if(skills !== '') {
            $scope.skills = angular.fromJson(skills);
            elem.tooltip({
              html : true,
              placement: 'bottom',
              container: 'body',
              title : '<div class="skill-tooltip">' +
                     gettext('Naučeno') + ' ' +
                     '<span class="badge badge-default">' +
                       '<i class="color-indicator learned"></i>' +
                       $scope.skills.learned + ' / ' + $scope.count +
                     '</span>' +
                   '</div>' +
                   '<div class="skill-tooltip">' +
                     gettext('Procvičováno') + ' ' +
                     '<span class="badge badge-default">' +
                       '<i class="color-indicator practiced"></i>' +
                       $scope.skills.practiced + ' / ' + $scope.count +
                     '</span>' +
                   '</div>'
            });
          }
        });
      }
    };
  }])

  .directive('levelProgressBar',['user', '$timeout', 'gettext',
      function(user, $timeout, gettext) {
    
    function getLevelInfo(points) {
      var levelEnd = 0;
      var levelRange = 30;
      var rangeIncrease = 0;
      for (var i = 1; true; i++) {
        levelEnd += levelRange;
        if (points < levelEnd) {
          return {
            level : i,
            form : levelEnd - levelRange,
            to : levelEnd,
            range : levelRange,
            points : points - (levelEnd - levelRange),
          };
        }
        levelRange += rangeIncrease;
        rangeIncrease += 10;
      }
      
    }
    return {
      restrict : 'C',
      template : '<span class="badge level-start" ' +
                   'ng-bind="level.level" tooltip="' + gettext('Aktuální úroveň') + '">' +
                 '</span>' +
                 '<div class="progress level-progress" ' +
                     'tooltip="{{level.points}} / {{level.range}} ' + 
                     gettext('bodů') + '">' +
                   '<div class="progress-bar progress-bar-warning" ' +
                        'style="width: {{(level.points/level.range)|percent}};">' +
                   '</div>' +
                 '</div>' +
                 '<span class="badge level-goal" ' +
                       'ng-bind="level.level+1" tooltip="' + gettext('Příští úroveň') + '">' +
                 '</span>',
      link : function($scope) {
        $scope.level = getLevelInfo(user.getUser().points);
      }
    };
  }]);
}());
