(function(angular, _) {

  var filters = angular.module('feeder.filters', []);

  /**
   * Exposes the power of Moment.js parsing and formatting.
   *
   * @filter
   * @param {*} date The date to parse.
   * @param {String} [format='LLL'] The format to format `date` with.
   * @returns {String} Returns `date` in the format `format`.
   */
  filters.filter('moment', function() {
    return function(date, format) {
      format || (format = 'LLL');

      if (angular.isNumber(date)) {
        date = moment.unix(date);
      } else {
        date = moment(date);
      }

      if (format.toUpperCase() == 'RELATIVE')
      {
          return date.fromNow();
      } else {
        return date.format(format);
      }
    }
  });

  filters.filter('htmlToPlainText', function() {
    return function(text) {
      return String(text).replace(/<(?:.|\n)*?>/gm, '');
    }
  });

  filters.filter('setAnchorTarget', function() {
    return function(text, value) {
      // Remove new-lines
      var dom = angular.element(String(text).replace(/(\r\n|\r|\n)/gm, ''));
      value || (value = '_blank');
      
      dom.find('a').attr('target', '_blank');

      return (angular.element('<div>').append(dom)).html();
    }
  });

}).call(this, angular, _);
