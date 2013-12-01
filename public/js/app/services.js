(function() {

  /**
   * The `State` model represents the overall state and status of the entire
   * application.
   *
   * @factory
   * @var {Boolean} [error=false] Has the application encountered an error?
   * @var {Boolean} [loading=false] Is the application is loading something?
   * @var {Number} [requests=0] The number of outstanding requests.
   */
  this.factory('State', function() {
    var error = false
      , loading = false
      , requests = 0;

    return {
      error: error,
      loading: loading,
      requests: requests
    };
  });

  /**
   * The `Cookie` service is a cookie service.
   *
   * @service
   * @var {Function} get Fetchs the value of a cookie.
   * @var {Function} has Check to see if a cookie exists.
   * @var {Function} remove Deletes a cookie.
   * @var {Function} set Stores a cookie.
   */
  this.service('Cookie', function() {
    var defaultOptions = {
      path: '/',
      expires: 9001
    };

    /**
     * Returns the value of a cookie identified by `key`.
     *
     * @param {String} key The key of the cookie.
     * @returns {String|Object} Returns the value of the cookie.
     */
    function get(key) {
      var value = cookie.get(key);
      return value ? angular.fromJson(value) : value;
    }

    /**
     * Checks to see if a cookie has been set.
     *
     * @param {String} key The key of the cookie.
     * @returns {Boolean} Returns whether or not a cookie exists.
     */
    function has(key) {
      return angular.isDefined(this.get(key));
    }

    /**
     * Deletes a cookie.
     *
     * @param {String} key The key of the cookie.
     * @returns {Model} Returns the current `Cookie` instance.
     */
    function remove(key) {
      cookie.remove(key);
      return this;
    }

    /**
     * Stores a cookie.
     *
     * @param {String} key The key of the cookie.
     * @param {String|Object} value The value of the cookie.
     * @param {Object} [options={}] Any additional parameters of storage.
     * @returns {Model} Returns the current `Cookie` instance.
     */
    function set(key, value, options) {
      options = _.extend(defaultOptions, options);
      cookie.set(key, angular.toJson(value), options);
      return this;
    }

    return {
      get: get,
      has: has,
      remove: remove,
      set: set
    };
  });

  /**
   * The `User` model represents the current visitor.
   *
   * @factory
   * @var {Boolean} authenticated Is the visitor authenticated?
   * @var {String} authorization The authorization token of the current user.
   * @var {Function} call Returns an authenticated `Restangular` instance.
   * @var {Function} getAuthHeader Creates the header needed to make API calls.
   * @var {Function} login Logs the current visitor in.
   * @var {Function} logout Logs the current visitor out.
   * @var {Function} register Creates a user for the current visitor.
   * @var {String} username The username of the user.
   */
  this.factory('User', function($q, Restangular, Cookie) {
    var endpoint = Restangular.one('users')
      , authKey = 'auth'
      , usernameKey = 'username'
      , authenticated = Cookie.has(authKey)
      , authorization = Cookie.get(authKey)
      , username = Cookie.get(usernameKey);

    /**
     * Returns an authenticated `Restangular` instance.
     *
     * @returns {Object} Returns a `Restangular` object.
     */
    function call() {
      return Restangular.withConfig(_.bind(function(configurer) {
        function interceptor(element, operation, route, url, headers, params) {
          return {
            element: element,
            params: params,
            headers: _.extend(headers, this.getAuthHeader())
          };
        }

        configurer.setFullRequestInterceptor(_.bind(interceptor, this));
      }, this));
    }

    /**
     * Generates a header object that needs to be used by every other service to
     * make their API calls.
     *
     * @param {String} [auth=this.authorization] The authorization token.
     * @returns {Object} Returns the header object.
     */
    function getAuthHeader(auth) {
      auth || (auth = this.authorization);

      return {
        Authorization: 'xBasic ' + auth
      };
    }

    /**
     * Logs in a visitor by checking the server to see if the he or she exists
     * and if the username and password pair matches.
     *
     * @param {String} username The username of the visitor.
     * @param {String} password The password of the visitor.
     * @returns {Promise} Returns the promise of the login API hit.
     */
    function login(username, password) {
      var auth = btoa(username + ':' + password)
        , header = getAuthHeader(auth);

      return endpoint.get({}, header).then(_.bind(function() {
        this.authenticated = true;
        this.authorization = auth;
        this.username = username;
        Cookie.set(authKey, auth).set(usernameKey, username);
      }, this), $q.reject);
    }

    /**
     * Registers a new user.
     *
     * @param {String} username The username of the new user.
     * @param {String} password The password of the new user.
     * @returns {Promise} Returns the promise of the registration API hit.
     */
    function register(username, password) {
      var auth = btoa(username + ':' + password);

      return endpoint.all('').post({
        username: username,
        password: password
      }).then(_.bind(function() {
        this.authenticated = true;
        this.authorization = auth;
        this.username = username;
        Cookie.set(authKey, auth).set(usernameKey, username);
      }, this), $q.reject);
    }

    /**
     * Logs out a user by deleting the session cookie.
     */
    function logout() {
      this.authenticated = false;
      this.username = '';
      Cookie.remove(authKey).remove(usernameKey);
    }

    return {
      authenticated: authenticated,
      authorization: authorization,
      call: call,
      getAuthHeader: getAuthHeader,
      login: login,
      logout: logout,
      register: register,
      username: username
    };
  });

  /**
   * The `Feeds` model represents all the subscribed feeds of the user.
   *
   * @factory
   * @var {Function} update Fetches and stores the subscribed feeds of the user.
   * @var {Array|Boolean} [feeds=false] The feeds of the current user.
   * @var {Function} id Returns a feed with a specific id.
   * @var {Number} [unreads=0] The total number of unreads in all the feeds.
   * @var {Function} update Fetches and stores the subscribed feeds of the user.
   * @var {Function} remove Unsubscribes a feed.
   */
  this.factory('Feeds', function($q, User) {
    var endpoint = User.call().one('feeds')
      , feeds = false
      , unreads = 0;

    /**
     * Adds a new feed to the list of subscribed feeds of the current user.
     *
     * @param {String} url The url of the feed.
     * @returns {Promise} Returns the promise of the add feed API hit.
     */
    function add(url) {
      return endpoint.all('').post({
        url: url
      }).then(_.bind(function() {
        return this.update();
      }, this));
    }

    /**
     * Adds a bunch of new feeds to the list of subscribed feeds.
     *
     * @param {Array} urls The urls of the feed.
     * @returns {Promise} Returns the promise of all the add feed API hit.
     */
    function batchAdd(urls) {
      urls = _.map(urls, function(url) {
        return endpoint.all('').post({
          url: url
        });
      });

      return $q.all(urls).then(_.bind(function() {
        return this.update();
      }, this), _.bind(function() {
        return this.update();
      }, this));
    }

    /**
     * Returns the feed object with id `id`.
     *
     * @param {String|Number} id The id of the feed.
     * @returns {Object} Returns the feed object with id `id`.
     */
    function id(id) {
      id = parseInt(id, 10);

      if (!this.feeds) {
        return;
      }

      return _.find(this.feeds, {
        id: id
      });
    }

    /**
     * Removes a feed from the list of subscribed feeds of the current user.
     *
     * @returns {Promise} Returns the promise of the remove feed API hit.
     */
    function remove(id) {
      return endpoint.one(id).remove().then(_.bind(function() {
        return this.update();
      }, this), $q.reject);
    }

    /**
     * Fetches the list of subscribed feeds of the current user, and stores it
     * within the current `Feeds` model.
     *
     * @returns {Promise} Returns the promise of the update feeds API hit.
     */
    function update() {
      return endpoint.get().then(_.bind(function(result) {
        var feeds = result.feeds;

        this.feeds = feeds;
        this.unreads = _.reduce(feeds, function(unreads, feed) {
          return unreads + feed.unreads;
        }, 0);

        return result;
      }, this), $q.reject);
    }

    return {
      add: add,
      batchAdd: batchAdd,
      feeds: feeds,
      id: id,
      remove: remove,
      unreads : unreads,
      update: update
    };
  });

  /**
   * The `ArticleList` model represents the list of articles for the feed that
   * the user is currently viewing.
   *
   * @factory
   * @var {Number} [id=0] The id of the feed parent of the article list.
   * @var {Array|Boolean} [list=false] The list of articles.
   * @var {Function} push Adds to the article list, or update an article in it.
   * @var {Function} update Fetches and stores the article ids of a feed.
   * @var {Function} updateFilter Changes the filter of the article list view.
   */
  this.factory('ArticleList', function($q, Cookie, User, Article) {
    var endpoint = User.call().one('feeds')
      , filterKey = 'filter'
      , filter = Cookie.has(filterKey) ? Cookie.get(filterKey) : {
          read: false
        }
      , id = 0
      , list = false
      , unreads = 0;

    /**
     * Either adds a new article to the article list, or updates an already
     * existing article. The article to push or update comes from the `Article`
     * model.
     */
    function push() {
      var list = this.list
        , updatedArticle = Article.article;

      if (!updatedArticle) {
        return;
      }

      list = _.each(list, function(article, key) {
        if (article.id === updatedArticle.id) {
          list[key].read = updatedArticle.read;
        }
      });

      this.list = list;
    }

    /**
     * Fetches all the articles belonging to a feed identified by `id`. These
     * articles will not have their full content. Instead, a truncated version
     * will be requested for the purposes of a short preview in the article
     * list view.
     *
     * @param {Number} id The id of the feed.
     * @returns {Promise} Returns the promise of the fetch articles API hit.
     */
    function update(id) {
      return endpoint.one(id).getList('entries').then(_.bind(function(result) {
        if (!result.entries.length) {
          this.id = id;
          this.list = [];
          return;
        }

        return Article.get(result.entries, {
          truncate: 300
        }).then(_.bind(function(result) {
          this.id = id;
          this.list = result.entries;
        }, this), $q.reject);
      }, this), $q.reject);
    }

    /**
     * Updates the filter for the article list view. This setting persists on a
     * per browser basis due to cookie usage.
     *
     * @param {Null|Object} filter The filter object.
     */
    function updateFilter(filter) {
      if (_.isBoolean(filter)) {
        this.filter = {
          read: filter
        };
      } else {
        this.filter = null;
      }

      Cookie.set(filterKey, this.filter);
    }

    return {
      filter: filter,
      id: id,
      list: list,
      push: push,
      update: update,
      updateFilter: updateFilter
    };
  });

  /**
   * The `Article` model represents the list of articles for the feed that
   * the user is currently viewing.
   *
   * @factory
   * @var {Object|Boolean} [article=false] The article.
   * @var {Function} get Fetches an article.
   * @var {Function} read Reads an article.
   * @var {Function} unread Unreads an article.
   * @var {Function} update Fetches and stores the article ids of a feed.
   */
  this.factory('Article', function($q, User) {
    var endpoint = User.call().one('entries')
      , article = false;

    /**
     * Fetches an article.
     *
     * @param {Array|Number} id The id(s) of the feed.
     * @param {Object} [queryParams={}] Any query parameters.
     * @returns {Promise} Returns the promise of the fetch article API hit.
     */
    function get(id, queryParams) {
      queryParams || (queryParams = {});
      return endpoint.getList(id, queryParams);
    }

    /**
     * Sets an article as read.
     *
     * @param {Number} id The id of the feed.
     * @returns {Promise} Returns the promise of the read article API hit.
     */
    function read(id) {
      return endpoint.one(id).patch({
        read: true
      }).then(_.bind(function(result) {
        this.article.read = true;
      }, this), $q.reject);
    }

    /**
     * Sets an article as unread.
     *
     * @param {Number} id The id of the feed.
     * @returns {Promise} Returns the promise of the unread article API hit.
     */
    function unread(id) {
      return endpoint.one(id).patch({
        read: false
      }).then(_.bind(function(result) {
        this.article.read = false;
      }, this), $q.reject);
    }

    /**
     * Fetches and stores an article.
     *
     * @param {Array|Number} id The id(s) of the feed.
     * @returns {Promise} Returns the promise of the fetch article API hit.
     */
    function update(id) {
      return this.get(id).then(_.bind(function(result) {
        this.article = result.entries.pop();
      }, this), $q.reject);
    }

    return {
      article: article,
      get: get,
      read: read,
      unread: unread,
      update: update
    };
  });

}).call(angular.module('feeder.services', []));
