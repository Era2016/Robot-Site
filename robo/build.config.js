/**
 * This file/module contains all configuration for the build process.
 */
module.exports = {
  /**
   * The `build_dir` folder is where our projects are compiled during
   * development and the `compile_dir` folder is where our app resides once it's
   * completely built.
   */
  build_dir: 'build',
  compile_dir: 'bin',
  assets_dir: 'src/assets',
  /**
   * This is a collection of file patterns that refer to our app code (the
   * stuff in `src/`). These file paths are used in the configuration of
   * build tasks. `js` is all project javascript, less tests. `ctpl` contains
   * our reusable components' (`src/common`) template HTML files, while
   * `atpl` contains the same, but for our app's code. `html` is just our
   * main HTML file, `less` is our main stylesheet, and `unit` contains our
   * app's unit tests.
   */
  app_files: {
    js: [ 'src/**/*.js', '!src/**/*.spec.js', '!src/assets/**/*.js' ],
    jsunit: [ 'src/**/*.spec.js' ],
    
    atpl: [ 'angular/src/app/**/*.tpl.html' ],
    ctpl: [ 'angular/src/common/**/*.tpl.html' ],

    html: [ 'src/index.html' ],
    less: ['angular/src/less/*.less', '!angular/src/less/partials/_*.less','angular/src/app/**/*.less']
  },

  /**
   * This is a collection of files used during testing only.
   */
  test_files: {
    js: [
      'vendor/angular-mocks/angular-mocks.js'
    ]
  },

  /**
   * This is the same as `app_files`, except it contains patterns that
   * reference vendor code (`vendor/`) that we need to place into the build
   * process somewhere. While the `app_files` property ensures all
   * standardized files are collected for compilation, it is the user's job
   * to ensure non-standardized (i.e. vendor-related) files are handled
   * appropriately in `vendor_files.js`.
   *
   * The `vendor_files.js` property holds files to be automatically
   * concatenated and minified with our project source files.
   *
   * The `vendor_files.css` property holds any CSS files to be automatically
   * included in our app.
   *
   * The `vendor_files.assets` property holds any assets to be copied along
   * with our app's assets. This structure is flattened, so it is not
   * recommended that you use wildcards.
   */

  vendor_files: {
    js: [
      'vendor/moment/min/moment.min.js',
      'vendor/jquery/dist/jquery.min.js',
      //'vendor/jquery/dist/jquery.min.js.map',
      'vendor/angular/angular.min.js',
      //'vendor/angular/angular.min.js.map',
      'vendor/angular-ui-router/release/angular-ui-router.min.js',
      'vendor/angular-cookies/angular-cookies.min.js',
      //'vendor/angular-cookies/angular-cookies.min.js.map',
      'vendor/angular-inflector/dist/angular-inflector.min.js',
      'vendor/angular-mocks/angular-mocks.js',
      'vendor/angular-moment/angular-moment.min.js',
      //'vendor/angular-moment/angular-moment.min.js.map',
      'vendor/angular-restmod/dist/angular-restmod.min.js',
      'vendor/angular-restmod/dist/styles/ams.min.js',
      'vendor/angular-resource/angular-resource.min.js',
      //'vendor/angular-resource/angular-resource.min.js.map',
      'vendor/angular-route/angular-route.min.js',
      'vendor/angular-toArrayFilter/toArrayFilter.js',
      'vendor/angular-ui-router/angular-ui-router.min.js',
      'vendor/placeholders/angular-placeholders-0.0.1-SNAPSHOT.min.js',
      'vendor/angular-ui-utils/modules/route/route.js',
      'vendor/angularUtils-pagination/dirPagination.js',
      'vendor/ng-file-upload-shim/ng-file-upload-all.min.js',
      //'vendor/wow/dist/wow.min.js',
      //'vendor/modernizr-custom.js',

      'vendor/ngstorage/ngStorage.min.js',

      'vendor/angular-animate/angular-animate.min.js',
      'vendor/angular-material/angular-material.min.js',
      'vendor/angular-aria/angular-aria.min.js',
      // Medium Editor and Angular Medium Editor Directive
      'vendor/medium-editor/dist/js/medium-editor.min.js',
      'vendor/angular-medium-editor/dist/angular-medium-editor.min.js',
      'vendor/angular-loading-bar/build/loading-bar.min.js',
      // UI Calendar
      'vendor/angular-ui-calendar/src/calendar.js',
      'vendor/fullcalendar/dist/fullcalendar.min.js',
      'vendor/fullcalendar/dist/gcal.js',
      // Input Mask
      'vendor/angular-input-masks/angular-input-masks-standalone.min.js',
      // Angular NLP Compromise 
      'vendor/angular-nlp-compromise/dist/angular-nlp-compromise.min.js',
      // Infinite Scroll
      'vendor/ngInfiniteScroll/build/ng-infinite-scroll.min.js'

      // Jquery File Upload Plugin
      //'vendor/blueimp-file-upload/js/vendor/jquery.ui.widget.js',
      //'vendor/blueimp-file-upload/js/jquery.iframe-transport.js',
      //'vendor/blueimp-file-upload/js/jquery.fileupload.js',
      //'vendor/medium-editor-insert-plugin/dist/js/medium-editor-insert-plugin.min.js',
    ],
    css: [
      'vendor/fullcalendar/dist/fullcalendar.min.css',
      'vendor/animate.css/animate.min.css',
      'vendor/medium-editor/dist/css/medium-editor.min.css',
      //'vendor//medium-editor-insert-plugin/dist/css/medium-editor-insert-plugin.min.css',
      //'vendor/components-font-awesome/css/font-awesome.min.css',
      'vendor/angular-material/angular-material.min.css',
      'vendor/angular-loading-bar/build/loading-bar.min.css',
    ],
    assets: [ 
      //'vendor/components-font-awesome/fonts/fontawesome-webfont.eot',
      //'vendor/components-font-awesome/fonts/fontawesome-webfont.svg',
      //'vendor/components-font-awesome/fonts/fontawesome-webfont.ttf',
      //'vendor/components-font-awesome/fonts/fontawesome-webfont.woff',
      //'vendor/components-font-awesome/fonts/fontawesome-webfont.woff2',
      //'vendor/components-font-awesome/fonts/FontAWesome.otf',

    ]
  }
};
