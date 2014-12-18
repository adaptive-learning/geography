(function() {
  'use strict';
  /* Controllers */
  angular.module('proso.goals', ['ui.bootstrap'])

  .value('gettext', gettext)

  .directive('goalProgress', ['goal', function (goal) {
    return {
      restrict: 'A',
      templateUrl : 'static/tpl/goal-progress_tpl.html',
      link: function ($scope, element, attrs) {
        if(attrs.map && attrs.placeType) {
          $scope.goal = goal.getForMap(attrs.map, attrs.placeType);
        }
      }
    };
  }])

  .directive('personalGoals', ['$modal', 'goal', function ($modal, goal) {
    return {
      restrict: 'A',
      templateUrl : 'static/tpl/personal-goals_tpl.html',
      link: function ($scope) {
        $scope.deleteGoal = goal.remove;
        
        goal.get().success(function(goals) {
          $scope.loaded = true;
          $scope.goals = goals;
        });

        $scope.addGoal = function () {
          $modal.open({
            templateUrl: 'add_goal_modal.html',
            controller: ModalAddGoalCtrl,
            resolve: {
              goals: function () {
                return $scope.goals;
              }
            }
          });
        };

        var ModalAddGoalCtrl = ['$scope', '$modalInstance', 
              '$location', 'goals', 'gettext', 'places', 'goal',
            function ($scope, $modalInstance, 
              $location, goals, gettext, places, goal) {

          $scope.goal = {
            finish_date: new Date(new Date().getTime() + 1000 * 60 * 60 * 24 * 14),
          };
          $scope.minFinish = new Date(new Date().getTime() + 1000 * 60 * 60 * 24 * 7);
          $scope.alerts = [];
          $scope.datePopup = {};

          function filterGoals(maps, goals) {
            maps.forEach(function(map){
              var disabledCounter = 0;
              map.placesTypes.forEach(function(l) {
                goals.forEach(function(g){
                  if (l.slug == g.type.slug && map.slug == g.map.code) {
                    l.disabled = true;
                    disabledCounter++;
                  }
                });
              });
              map.disabled = disabledCounter == map.placesTypes.length;
            });
          }

          function firstGoal(maps) {
            for (var i = 0; i < maps.length; i++) {
              var map = maps[i];
              for (var j = 0; j < map.placesTypes.length; j++) {
                if (!map.placesTypes[j].disabled) {
                  return {
                    finish_date : new Date(new Date().getTime() + 1000 * 60 * 60 * 24 * 14),
                    map : map.slug,
                    layer : map.placesTypes[j].slug,
                  };
                }
              }
            }
          }

          function getMaps(mapCategories) {
            var maps = [];
            mapCategories.forEach(function(cat){
              maps = maps.concat(cat.maps);
            });
            return maps;
          }

          places.getOverview().success(function(data){
            $scope.maps = getMaps(data);
            filterGoals($scope.maps, goals);
            $scope.mapCategories = data;
            $scope.goal = firstGoal($scope.maps);
          });

          $scope.openDatePopup = function($event) {
            $event.preventDefault();
            $event.stopPropagation();

            $scope.datePopup.isOpen = true;
          };

          $scope.send = function() {
            goal.add($scope.goal).success(function(){
              $scope.alerts.push({
                type : 'success',
                msg : gettext("Cíl byl vytvořen"),
              });
              $scope.sending = false;
              $scope.cancel();
            }).error(function(){
              $scope.alerts.push({
                type : 'danger',
                msg : gettext("V aplikaci bohužel nastala chyba."),
              });
              $scope.sending = false;
            });
            $scope.sending = true;
          };

          $scope.closeAlert = function(index) {
            $scope.alerts.splice(index, 1);
          };

          $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
          };
        }];

      }
    };
  }]);

})();

