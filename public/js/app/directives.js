(function() {

  /**
   * Implements awesome konami code goodness.
   *
   * @directive
   * @restrict attribute
   */
  this.directive('konami', function() {
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
   * Accepts OPML.
   *
   * @directive
   * @restrict attribute
   */
  this.directive('opmlReceiver', function(Feeds) {
    return {
      restrict: 'A',
      link: function(scope, elem$) {
        var OPMLReceiver;

        if (!window.FileReader) {
          return;
        }

        OPMLReceiver = new Dropzone(elem$[0], {
          autoProcessQueue: false,
          url: '/opml-receiver'
        });

        OPMLReceiver.on('addedfile', function(file) {
          var reader = new FileReader();

          reader.onload = function(event) {
            var result = event.target.result
              , links = [];

            try {
              result = angular.element(result).children().find('outline');
              angular.forEach(result, function(element) {
                var url = angular.element(element).attr('xmlurl');
                if (url) {
                  links.push(url);
                }
              });
              Feeds.batchAdd(links);
            } catch (error) {}
          }

          reader.readAsText(file);
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

  /**
   * Solves autocomplete issues with AngularJS and browsers by forcing an
   * update of the view value for forms when a form is submitted.
   *
   * @directive
   * @restrict attribute
   */
  this.directive('autocomplete', function() {
    return {
      restrict: 'A',
      priority: -10,
      link: function(scope, elem$, attrs) {
        if (attrs.autocomplete !== 'on') {
          return;
        }

        elem$.on('submit', function() {
          angular.forEach(elem$.find('input'), function(element) {
            var element$ = angular.element(element)
              , type = element$.attr('type');

            if (!element$.attr('ng-model')) {
              return;
            }

            if (type === 'text' || type === 'password') {
              element$.controller('ngModel').$setViewValue(element$.val());
            }
          });
        });
      }
    }
  });

  this.directive('keepscroll', function(ArticleList, $timeout, $window) {
    return {
      restrict: 'A',
      link: function(scope) {
        scope.$on('$routeChangeStart', function() {
          ArticleList.scrollYPos = $window.scrollY;
        });

        scope.$on('$routeChangeSuccess', function() {
          // Wait until the page has fully loaded to update scroll position
          $timeout(function() {
            $window.scrollTo(0, ArticleList.scrollYPos);
          }, 0)
        });
      }
    }
  })

}).call(angular.module('feeder.directives', []));
