(function(angular) {

  var services = angular.module('feeder.services', []);

  services.factory('UserService', function($q, $cookieStore, Restangular) {
    var User = angular.noop
      , cookieKey = 'auth';

    User.prototype.register = function(username, password) {
      return Restangular.all('users').post({
        username: username,
        password: password
      });
    }

    User.prototype.login = function(username, password) {
      var auth = btoa(username + ':' + password);

      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders({
          Authorization: 'xBasic ' + auth
        });
      });

      return Restangular.one('').get().then(function(result) {
        $cookieStore.put(cookieKey, auth);
      }, function(reason) {
        return $q.reject(reason);
      });
    };

    User.prototype.logout = function() {
      $cookieStore.remove(cookieKey);
    }

    User.prototype.isLoggedIn = function() {
      return !!$cookieStore.get(cookieKey);
    }

    return new User;
  });

}).call(this, angular);
