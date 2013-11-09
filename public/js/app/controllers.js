(function(angular) {

  var controllers = angular.module('feeder.controllers', []);

  controllers.controller('TestCtrl', function($scope, Restangular) {

    Restangular.all('').getList().then(function(data) {
      $scope.testApi = data.message;
    });

  });

}).call(this, angular);
