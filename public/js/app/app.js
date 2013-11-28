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
      templateUrl: '/partials/home.html',
      resolve: {
        fetchFeeds: function(Feeds) {
          return Feeds.update();
        }
      }
    });

    $routeProvider.when('/home/:feed', {
      controller: 'FeedCtrl',
      templateUrl: '/partials/feed.html',
      resolve: {
        fetchFeeds: function(Feeds) {
          if (Feeds.feeds === false) {
            return Feeds.update();
          }
        },
        fetchArticleList: function($route, ArticleList) {
          var id = parseInt($route.current.params.feed, 10);
          if (ArticleList.list === false || ArticleList.id !== id) {
            return ArticleList.update(id);
          } else {
            return ArticleList.list;
          }
        }
      }
    });

    $routeProvider.when('/home/:feed/:article', {
      controller: 'ArticleCtrl',
      templateUrl: '/partials/article.html',
      resolve: {
        fetchArticle: function($route, Article) {
          return Article.update($route.current.params.article);
        }
      }
    });

    $routeProvider.otherwise({
      redirectTo: '/404'
    });
  });

  this.config(function(RestangularProvider) {
    RestangularProvider.setBaseUrl('/api');
  });

  this.config(function($httpProvider) {
    $httpProvider.interceptors.push(function($q, State) {
      return {
        request: function(config) {
          State.loading = true;
          return config;
        },
        requestError: function(rejection) {
          State.loading = false;
          return $q.reject(rejection);
        },
        response: function(response) {
          State.loading = false;
          return response;
        },
        responseError: function(rejection) {
          State.loading = false;
          return $q.reject(rejection);
        }
      };
    });
  });

  this.run(function($rootScope, $location, State) {
    $rootScope.$on('$routeChangeStart', function() {
      State.loading = true;
      State.error = false;
    });

    $rootScope.$on('$routeChangeError', function() {
      State.loading = false;
      State.error = true;
      $location.path('/404');
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
