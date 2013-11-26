(function(angular, _) {

  angular.module('feeder.filters', [])

  /**
   * Exposes the power of Moment.js parsing and formatting.
   *
   * @filter
   * @param {*} date The date to parse.
   * @param {String} [format='LLL'] The format to format `date` with.
   * @returns {String} Returns `date` in the format `format`.
   */
  .filter('moment', function() {
    return function(date, format) {
      format || (format = 'LLL');

      if (angular.isNumber(date)) {
        date = moment.unix(date);
      } else {
        date = moment(date);
      }

      if (format.toLowerCase() == 'relative') {
        return date.fromNow();
      } else {
        return date.format(format);
      }
    }
  })

  /**
   * Converts HTML to plain text by stripping all HTML tags off.
   *
   * @filter
   * @param {*} text The text to be stripped.
   * @returns {String} Returns `text` without any HTML tags.
   */
  .filter('htmlToPlainText', function() {
    return function(text) {
      return String(text).replace(/<(?:.|\n)*?>/gm, '');
    }
  });

}).call(this, angular, _);
