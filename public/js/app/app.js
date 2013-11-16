(function(angular, _) {

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
      templateUrl: 'partials/feed.html',
      resolve: {
        Feed: function($route, $q, Feeds) {
          return Feeds.get().then(function(feeds) {
            return _.find(feeds, {
              id: +$route.current.params.feed
            });
          }, $q.reject);
        }
      }
    })

    .when('/home/:feed/:article', {
      controller: 'ArticleCtrl',
      templateUrl: 'partials/article.html',
      resolve: {
        data: function($route, $q, Article) {
          return Article.get($route.current.params.article).then(function(result) {
            return result.entries[0];
          }, $q.reject);
        }
      }
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

}).call(this, angular, _);
