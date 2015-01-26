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
      link: function ($scope, elem, attrs) {
        $scope.deleteGoal = goal.remove;
        
        goal.get(attrs.user).success(function(goals) {
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
          $scope.minFinish = new Date();
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
  }])

  .factory('goal',['$http', '$cookies', 'confirmModal', 'gettext',
      function($http, $cookies, confirmModal, gettext) {
    
    var goalDict = {};
    var goals = [];
    function updateGoal(g){
      if (goalDict[g.id]) {
        angular.copy(g, goalDict[g.id]);
      } else {
        goalDict[g.id] = g;
        goals.unshift(g);
      }
    }
    var goalsPromise = $http.get("/goal/");

    var that = {
      update : function(newGoals) {
        for (var i = 0; i < newGoals.length; i++) {
          updateGoal(newGoals[i]);
        }
      },
      get : function(user) {
        if (user) {
          return $http.get("/goal/" + user);
        } else {
          return {
            success : function(fn) {
              goalsPromise.success(function() {
                fn(goals);
              });
            }
          };
        }
      },
      getForMap : function(mapCode, typeSlug) {
        for (var i = 0; i < goals.length; i++) {
          var g = goals[i];
          if (g.map.code == mapCode && g.type.slug == typeSlug) {
            return g;
          }
        }
      },
      remove : function(goal) {
        var question = gettext("Opravdu chcete cíl smazat?");
        confirmModal.open(question, function() {
          goal.deleting = true;
          $http.get("/goal/delete/" + goal.id).success(function() {
            for (var i = 0; i < goals.length; i++) {
              if (goals[i].id == goal.id) {
                goals.splice(i, 1);
                break;
              }
            }
            delete goalDict[goal.id];
          });
        });
      },
      add : function(goal) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        var promise = $http.post('/goal/', goal);
        promise.success(function(data) {
          updateGoal(data);
        });
        return promise;
      }
    };

    goalsPromise.success(function(data) {
      that.update(data.reverse());
    });

    return that;
  }]);


})();

