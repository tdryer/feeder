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
    };
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
          clickable: false,
          url: '/opml-receiver'
        });

        OPMLReceiver.on('addedfile', function(file) {
          var reader = new FileReader();

          reader.onload = function(event) {
            var result = event.target.result
              , links = []
              , parser;

            try {
              parser = new DOMParser();
              result = parser.parseFromString(result, 'text/xml');
              result = angular.element(result).find('outline');
              angular.forEach(result, function(element) {
                var url = angular.element(element).attr('xmlUrl');
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
    };
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
    };
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
    };
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
    };
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
    };
  });

  /**
   * Outputs the content of an article.
   *
   * @directive
   * @restrict attribute
   */
  this.directive('articleAnchor', function() {
    return {
      restrict: 'A',
      link: function(scope, elem$, attrs) {
        elem$.on('click', function(event) {
          if (!scope.State.mobile) {
            event.preventDefault();
            scope.$apply(function() {
              elem$.parent().parent().children().removeClass('selected');
              elem$.parent().addClass('selected');
              if (scope.ArticleList.filter !== null &&
                _.indexOf(scope.ArticleList.filter.ids, attrs.articleAnchor) === -1) {
                  scope.ArticleList.filter.ids.push(parseInt(attrs.articleAnchor));
              }
              scope.Article.update(attrs.articleAnchor).then(function() {
                scope.Article.read(attrs.articleAnchor).then(function() {
                  scope.ArticleList.push();
                });
              });
            });
          }
        });
      }
    };
  });

  /**
   * Toggles the status of an Article on click.
   *
   * @directive
   * @restrict: attribute
   */
  this.directive('toggleArticleStatus', function() {
    return {
      restrict: 'A',
      link: function(scope, elem$) {
        elem$.on('click', function(event) {
          var id = scope.Article.article.id;
          if (scope.Article.article.read) {
            scope.Article.unread(id).then(function() {
              scope.ArticleList.push();
            });
          } else {
            scope.Article.read(id).then(function() {
              scope.ArticleList.push();
            });
          }
        });
      }
    }
  });

  /**
   * Outputs the content of an article.
   *
   * @directive
   * @restrict attribute
   */
  this.directive('articlePane', function() {
    var left = 37
      , right = 39
      , j = 74
      , k = 75;

    return {
      restrict: 'A',
      templateUrl: '/partials/article.html',
      controller: function($scope, Article) {
        $scope.Article = Article;
        $scope.swipe = false;
      },
      link: function(scope, elem$) {
        angular.element(document).on('keydown', function(event) {
          var id = scope.Article.article.id
            , list
            , index
            , prev
            , next;

          if (event.keyCode === left || event.keyCode === k) {
            list = scope.ArticleList.get();
            index = _.findIndex(list, {id: id});
            prev = scope.ArticleList.get(index - 1);
            if (prev) {
              if (scope.ArticleList.filter !== null &&
                _.indexOf(scope.ArticleList.filter.ids, prev.id) === -1) {
                  scope.ArticleList.filter.ids.push(prev.id);
              }
              scope.Article.update(prev.id).then(function() {
                var el = document.getElementById('article-anchor-' + prev.id);
                angular.element(el).parent().children().removeClass('selected');
                angular.element(el).addClass('selected');
                scope.Article.read(prev.id).then(function() {
                  scope.ArticleList.push();
                });
              });
            }
          }

          if (event.keyCode === right || event.keyCode === j) {
            list = scope.ArticleList.get();
            index = _.findIndex(list, {id: id});
            next = scope.ArticleList.get(index + 1);
            if (next) {
              if (scope.ArticleList.filter !== null &&
                _.indexOf(scope.ArticleList.filter.ids, next.id) === -1) {
                  scope.ArticleList.filter.ids.push(next.id);
              }
              scope.Article.update(next.id).then(function() {
                var el = document.getElementById('article-anchor-' + next.id);
                angular.element(el).parent().children().removeClass('selected');
                angular.element(el).addClass('selected');
                scope.Article.read(next.id).then(function() {
                  scope.ArticleList.push();
                });
              });
            }
          }
        });
      }
    };
  });

  this.directive('swipe', function() {
    function maxMagnitude(num) {
      if (num < -50) {
        return -50;
      } else if (num > 50) {
        return 50;
      }
      return num;
    }

    return {
      restrict: 'A',
      link: function(scope, elem$, attrs) {
        var id = parseInt(attrs.id)
          , list = scope.ArticleList.get()
          , index = _.findIndex(list, {id: id})
          , prev = scope.ArticleList.get(index - 1)
          , next = scope.ArticleList.get(index + 1)
          , delta
          , hammerInstance;

        if (scope.swipe === false) {
          return;
        }

        hammerInstance = Hammer(elem$[0]);
        hammerInstance.options.prevent_mouseevents = true;

        hammerInstance.on('dragleft dragright', function(event) {
          delta = maxMagnitude(event.gesture.deltaX * 10);
        }).on('dragend', function() {
          if (delta === -50 && next) {
            scope.$apply(function() {
              scope.goToArticle(next.feed_id, next.id);
            });
          } else if (delta === 50 && prev) {
            scope.$apply(function() {
              scope.goToArticle(prev.feed_id, prev.id);
            });
          }
        });
      }
    }
  });

}).call(angular.module('feeder.directives', []));
