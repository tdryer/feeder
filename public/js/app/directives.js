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

}).call(angular.module('feeder.directives', []));
