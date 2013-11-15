(function(angular) {

  var app = angular.module('feeder', [
    'ngCookies',
    'ngRoute',
    'ngSanitize',
    'restangular',
    'feeder.controllers',
    'feeder.directives',
    'feeder.filters',
    'feeder.services'
  ]);

  app.config(function($locationProvider) {
    $locationProvider.html5Mode(false);
  });

  app.config(function($routeProvider) {
    $routeProvider.when('/', {
      controller: 'IndexCtrl',
      template: ' '
    });

    $routeProvider.when('/home', {
      controller: 'HomeCtrl',
      templateUrl: 'partials/home.html'
    });

    $routeProvider.when('/home/:feed', {
      controller: 'HomeCtrl',
      templateUrl: 'partials/home.html'
    });

    $routeProvider.when('/home/:feed/:article', {
      controller: 'HomeCtrl',
      templateUrl: 'partials/home.html'
    });

    $routeProvider.when('/login', {
      controller: 'LoginCtrl',
      templateUrl: 'partials/login.html'
    });

    $routeProvider.when('/register', {
      controller: 'RegisterCtrl',
      templateUrl: 'partials/register.html'
    });

    $routeProvider.otherwise({
      redirectTo: '/'
    });
  });

  app.config(function(RestangularProvider) {
    RestangularProvider.setBaseUrl('/api');
  });

}).call(this, angular);
