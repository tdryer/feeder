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
    $routeProvider

    .when('/', {
      controller: 'IndexCtrl',
      template: ' '
    })

    .when('/home', {
      controller: 'HomeCtrl',
      templateUrl: 'partials/home.html'
    })

    .when('/home/:feed', {
      controller: 'FeedCtrl',
      templateUrl: 'partials/feed.html'
    })

    .when('/home/:feed/:article', {
      controller: 'HomeCtrl',
      templateUrl: 'partials/home.html'
    })

    .when('/login', {
      controller: 'LoginCtrl',
      templateUrl: 'partials/login.html'
    })

    .when('/logout', {
      controller: 'LogoutCtrl',
      template: ' '
    })

    .when('/register', {
      controller: 'RegisterCtrl',
      templateUrl: 'partials/register.html'
    })

    .otherwise({
      redirectTo: '/'
    });
  });

  app.config(function(RestangularProvider) {
    RestangularProvider.setBaseUrl('api');
  });

}).call(this, angular);
