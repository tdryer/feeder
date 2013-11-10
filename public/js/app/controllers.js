(function(angular) {

  var controllers = angular.module('feeder.controllers', []);

  controllers.controller('TestCtrl', function($scope, Restangular) {

    var feeds = Restangular.all('feeds');

    feeds.getList().then(function(data) {
      $scope.testApi = data.feeds;
    });

    $scope.addFeed = {};
    $scope.addFeed.add = function() {
      feeds.post({
        url: this.url
      });
    }

  });

}).call(this, angular);
