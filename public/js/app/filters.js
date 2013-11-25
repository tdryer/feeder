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
  })

  /**
   * Parse through an HTML text locating all anchor tags and setting their
   * target attribute.
   *
   * @filter
   * @param {*} text The HTML text to parse.
   * @param {String} value The value to set target to.
   * @return {String} Returns the new HTML text with modified anchor tags.
   */
  .filter('anchorTarget', function() {
    return function(text, value) {
      // Remove new-lines
      var dom = angular.element(String(text).replace(/(\r\n|\r|\n)/gm, ''));
      value || (value = '_blank');

      dom.find('a').attr('target', '_blank');

      return (angular.element('<div>').append(dom)).html();
    }
  });

}).call(this, angular, _);
