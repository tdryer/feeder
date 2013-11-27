(function() {

  this.config(function($locationProvider) {
    $locationProvider.html5Mode(true);
  });

  this.config(function($routeProvider) {
    $routeProvider.when('/', {
      controller: 'IndexCtrl',
      templateUrl: '/partials/index.html'
    });

    $routeProvider.when('/404', {
      controller: '404Ctrl',
      templateUrl: '/partials/404.html'
    });

    $routeProvider.when('/login', {
      controller: 'LoginCtrl',
      templateUrl: '/partials/login.html'
    });

    $routeProvider.when('/logout', {
      controller: 'LogoutCtrl',
      template: ' '
    });

    $routeProvider.when('/register', {
      controller: 'RegisterCtrl',
      templateUrl: '/partials/register.html'
    });

    $routeProvider.when('/home', {
      controller: 'HomeCtrl',
      templateUrl: '/partials/home.html'
    })

    .when('/home/:feed', {
      controller: 'FeedCtrl',
      templateUrl: '/partials/feed.html',
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
      templateUrl: '/partials/article.html',
      resolve: {
        data: function($route, $q, Article) {
          return Article.get($route.current.params.article).then(function(result) {
            return result.entries[0];
          }, $q.reject);
        }
      }
    })

    .otherwise({
      redirectTo: '/404'
    });
  });

  this.config(function(RestangularProvider) {
    RestangularProvider.setBaseUrl('/api');
  });

  this.run(function($rootScope, State) {
    $rootScope.$on('$routeChangeStart', function() {
      State.loading = true;
      State.error = false;
    });

    $rootScope.$on('$routeChangeError', function() {
      State.loading = false;
      State.error = true;
    });

    $rootScope.$on('$routeChangeSuccess', function() {
      State.loading = false;
      State.error = false;
    });
  });

}).call(angular.module('feeder', [
  'ngCookies',
  'ngRoute',
  'ngSanitize',
  'restangular',
  'feeder.controllers',
  'feeder.directives',
  'feeder.filters',
  'feeder.services'
]));
