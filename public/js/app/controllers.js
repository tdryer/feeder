(function(angular) {

  var controllers = angular.module('feeder.controllers', []);

  controllers.controller('TestCtrl', function($scope, Restangular) {

    var feeds = Restangular.all('feeds')
      , entries = Restangular.several('entries', [1, 2, 3, 4]);

    feeds.getList().then(function(data) {
      $scope.testApi = data.feeds;
    });

    $scope.addFeed = {};
    $scope.addFeed.add = function() {
      feeds.post({
        url: this.url
      });
    }

    entries.getList().then(function(data) {
      $scope.entries = data.entries;
    });

  });

}).call(this, angular);
