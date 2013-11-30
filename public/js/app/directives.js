(function() {

  /**
   * Implements awesome konami code goodness.
   *
   * @directive
   * @restrict attribute
   */
  this.directive('konami', function($http) {
    var konami = '38,38,40,40,37,39,37,39,66,65'
      , konami_class = 'konami-easter-egg'
      , konami_len = 10;

    return {
      restrict: 'A',
      link: function(scope, elem$) {
        var document$ = angular.element(document)
          , keys = [];

        document$.on('keydown', function(event) {
          keys.push(event.keyCode);

          if (keys.toString().indexOf(konami) === 0) {
            keys = [];
            document$.off('keydown');
            elem$.addClass(konami_class);
          }

          if (keys.length > konami_len) {
            keys.shift();
          }
        });
      }
    }
  });

  /**
   * Overlays the entire screen if the application is loading.
   *
   * @directive
   * @restrict element
   */
  this.directive('loading', function() {
    return {
      restrict: 'E',
      controller: function($scope, State) {
        $scope.State = State;
      }
    }
  });

  /**
   * The header houses the breadcrumbs, a greeting to the user if he or she is
   * authenticated, and various buttons.
   *
   * @directive
   * @restrict element
   */
  this.directive('header', function() {
    return {
      restrict: 'E',
      controller: function($scope, User, Feeds, ArticleList, Article) {
        $scope.User = User;
        $scope.Feeds = Feeds;
        $scope.ArticleList = ArticleList;
        $scope.Article = Article;
      },
      templateUrl: '/partials/header.html'
    }
  });

  /**
   * Displays the content of an article.
   *
   * @directive
   * @restrict element
   */
  this.directive('content', function() {
    return {
      restrict: 'E',
      link: function(scope, elem$, attrs) {
        elem$.ready(function() {
          elem$.find('a').attr('target', '_blank');
        });
      }
    }
  });

}).call(angular.module('feeder.directives', []));
