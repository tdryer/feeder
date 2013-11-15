(function(angular) {

  var services = angular.module('feeder.services', []);

  services.factory('UserService', function($q, $cookieStore, Restangular) {
    var User = angular.noop;

    User.prototype.login = function(username, password) {
      var auth = btoa(username + ':' + password);

      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders({
          Authorization: 'xBasic ' + auth
        });
      });

      return Restangular.one('').get().then(function(result) {
        $cookieStore.put('auth', auth);
        isLoggedIn = true;
      }, function(reason) {
        return $q.reject(reason);
      });
    };

    User.prototype.isLoggedIn = function() {
      return !!$cookieStore.get('auth');
    }

    return new User;
  });

}).call(this, angular);
