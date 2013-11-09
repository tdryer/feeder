(function(angular) {

  var app = angular.module('feeder', [
    'ngRoute',
    'restangular',
    'feeder.controllers',
    'feeder.directives',
    'feeder.filters',
    'feeder.services'
  ]);

  app.config(function($locationProvider) {
    $locationProvider.html5Mode(true);
  });

  app.config(function($routeProvider) {
    $routeProvider.when('/', {
      controller: 'TestCtrl',
      templateUrl: 'partials/test.html'
    });
  });

  app.config(function(RestangularProvider) {
    RestangularProvider.setBaseUrl('/api');

    RestangularProvider.setDefaultHeaders({
      Authorization: 'Basic ' + btoa('username:password')
    });
  });

}).call(this, angular);
