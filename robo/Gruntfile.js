// This Gruntfile automates different tasks for front-end development
// Type "grunt" to see a list of commands

// Required for image optimization
var pngquant = require('imagemin-pngquant');
var mozjpeg  = require('imagemin-mozjpeg');
var gifsicle = require('imagemin-gifsicle');

module.exports = function (grunt) {

var userConfig = require('./build.config.js');
var appConfig = grunt.file.readJSON('package.json');

// Load grunt tasks automatically
// see: https://github.com/sindresorhus/load-grunt-tasks

require('load-grunt-tasks')(grunt);

// Time how long tasks take. Can help when optimizing build times
// see: https://npmjs.org/package/time-grunt
// require('time-grunt')(grunt);

var taskConfig = {
    pkg: appConfig,
    meta: {
      banner: 
        '/**\n' +
        ' * <%= pkg.name %> - v<%= pkg.version %> - <%= grunt.template.today("yyyy-mm-dd") %>\n' +
        ' * <%= pkg.homepage %>\n' +
        ' *\n' +
        ' * Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author %>\n' +
        ' */\n'
    },

// Increments the version number, etc.
    bump: {
      options: {
        files: [
          "package.json", 
          "bower.json"
        ],
        commit: false,
        commitMessage: 'chore(release): v%VERSION%',
        commitFiles: [
          "package.json", 
          "client/bower.json"
        ],
        createTag: false,
        tagName: 'v%VERSION%',
        tagMessage: 'Version %VERSION%',
        push: false,
        pushTo: 'origin'
      }
    },   

// The directories to delete when `grunt clean` is executed.
    
    clean: [ 'angular/<%= build_dir %>', 'angular/<%= compile_dir %>'],

// The `copy` task just copies files from A to B. We use it here to copy
// our project assets (images, fonts, etc.) and javascripts into
// `build_dir`, and then to copy the assets to `compile_dir`.

    copy: {
      build_app_assets: {
        files: [
          { 
            src: [ '**' ],
            dest: 'angular/<%= build_dir %>/assets/',
            cwd: 'angular/src/assets/',
            expand: true
          }
       ]   
      },
      build_vendor_assets: {
        files: [
          { 
            src: [ '<%= vendor_files.assets %>' ],
            dest: 'angular/<%= build_dir %>/assets/',
            cwd: 'angular/',
            expand: true,
            flatten: true
          }
       ]   
      },
      build_appjs: {
        files: [
          {
            src: [ '<%= app_files.js %>' ],
            dest: 'angular/<%= build_dir %>/',
            cwd: 'angular/',
            expand: true
          }
        ]
      },
      build_vendorjs: {
        files: [
          {
            src: [ '<%= vendor_files.js %>' ],
            dest: 'angular/<%= build_dir %>/',
            cwd: 'angular/',
            expand: true
          }
        ]
      },
      build_vendorcss: {
        files: [
          {
            src: [ '<%= vendor_files.css %>' ],
            dest: 'angular/<%= build_dir %>/',
            cwd: 'angular/',
            expand: true
          }
        ]
      },
      compile_assets: {
        files: [
          {
            src: [ '**','!site.js','!README.md'],
            dest: 'angular/<%= compile_dir %>/assets',
            cwd: 'angular/<%= build_dir %>/assets',
            expand: true
          },
          {
            src: [ '<%= vendor_files.css %>' ],
            dest: 'angular/<%= compile_dir %>/',
            cwd: 'angular/',
            expand: true
          }
        ]
      }
    },


// 'grunt concat' concatenates multiple source files into a single file.

    concat: {

// The 'build_css' target concatenates compiled CSS and vendor CSS together.
      build_css: {
        src: [
          '<%= vendor_files.css %>',
          'angular/<%= build_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css'
        ],
        dest: 'angular/<%= build_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css'
      },

// The 'compile_js' target is the concatenation of our application source
// code and all specified vendor source code into a single file.

      compile_js: {
        options: {
          stripBanners: true,
          banner: '<%= meta.banner %>'
        },
        dest: 'angular/<%= compile_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.js',
        src: (function(){
            var cwd = 'angular/';
            var files = userConfig.vendor_files.js;

            files = files.map(function (file){
                return cwd + file;
            });
            files.push('angular/build/assets/site.js');
            files.push('module.prefix');
            files.push('angular/build/src/**/*.js');
            files.push('angular/build/templates-app.js');
            files.push('angular/build/templates-common.js');
            files.push('module.suffix');
          return files;
        }())
      }
    },

// 'ngAnnotate' annotates the sources before minifying. That is, it allows us
//  to code without the array syntax.

    ngAnnotate: {
      compile: {
        files: [
          {
            src: [ '<%= app_files.js %>' ],
            cwd: 'angular/<%= build_dir %>',
            dest: 'angular/<%= build_dir %>',
            expand: true
          }
        ]
      }
    },



// Minify the sources

    uglify: {
      compile: {
        options: {
          stripBanners: true,
          banner: '<%= meta.banner %>'
        },
        src:'angular/<%= compile_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.js',
        //dest:'angular/<%= compile_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.js',
        expand: true
        },
      sitejs: {
        options: {
          stripBanners: true,
          banner: '<%= meta.banner %>'
        },
        src:'angular/<%= compile_dir %>/assets/site.js',
        expand: true
      }
    },

    less: {      
      build: {
        options: {
            cleancss: true,
            compress: true,
            paths: 'angular/src/less',
            sourceMap: true,
            sourceMapFilename: 'angular/<%= build_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css.map',
            sourceMapURL: 'angular/<%= build_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css.map'
        },
          files: {
            'angular/<%= build_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css': '<%= app_files.less %>'
          }      
        },
      compile: {
          options: {
              cleancss: true,
              compress: true,
              paths: 'angular/src/less',
              sourceMap: true,
              sourceMapFilename: 'angular/<%= compile_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css.map',
              sourceMapURL: 'angular/<%= compile_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css.map'
          },
          files: {
            'angular/<%= compile_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css': '<%= app_files.less %>'
          }
      },
      staticLess: {
          options: {
              paths: 'robotics/static/less',
              sourceMap: true,
              sourceMapFilename: 'robotics/static/css/site.css.map',
              sourceMapURL: 'robotics/static/css/site.css.map',
              compress: true
          },
          files: {
              "robotics/static/css/site.css": ["robotics/static/less/*.less", "!robotics/static/less/_*.less"]
          }
      }
    },

    /**
     * `jshint` defines the rules of our linter as well as which files we
     * should check. This file, all javascript sources, and all our unit tests
     * are linted based on the policies listed in `options`. But we can also
     * specify exclusionary patterns by prefixing them with an exclamation
     * point (!); this is useful when code comes from a third party but is
     * nonetheless inside `src/`.
     */
    jshint: {
      src: [ 
        '<%= app_files.js %>'
      ],
      test: [
        '<%= app_files.jsunit %>'
      ],
      gruntfile: [
        'Gruntfile.js'
      ],
      options: {
        curly: true,
        immed: true,
        newcap: true,
        noarg: true,
        sub: true,
        boss: true,
        eqnull: true
      },
      globals: {}
    },



// post process the css to add in vendor prefixes if they don't already exist.
    postcss: {
      options: {
        map: true, // inline sourcemaps

        processors: [
          require('pixrem')(), // add fallbacks for rem units
          require('autoprefixer-core')({browsers: [
            'Android 2.3',
            'Android >= 4',
            'Chrome >= 20',
            'Firefox >= 24',
            'Explorer >= 8',
            'iOS >= 6',
            'Opera >= 12',
            'Safari >= 6'
          ]}), // add vendor prefixes
          require('cssnano')() // minify the result
        ]
      },
      dist: {
        src: 'angular/<%= build_dir %>/assets/*.css'
      }
    },

// HTML2JS is a Grunt plugin that takes all of your template files and
// places them into JavaScript files as strings that are added to
// AngularJS's template cache. This means that the templates too become
// part of the initial payload as one JavaScript file. Neat!

    html2js: {
      /**
       * These are the templates from `src/app`.
       */
      app: {
        options: {
          base: 'angular/src/app'
        },
        src: [ '<%= app_files.atpl %>' ],
        dest: 'angular/<%= build_dir %>/templates-app.js'
      },

      /**
       * These are the templates from `src/common`.
       */
      common: {
        options: {
          base: 'angular/src/common'
        },
        src: [ '<%= app_files.ctpl %>' ],
        dest: 'angular/<%= build_dir %>/templates-common.js'
      }
    },

// The Karma configurations.
    karma: {
      options: {
        configFile: 'angular/<%= build_dir %>/karma-unit.js'
      },
      unit: {
        port: 9019,
        background: true
      },
      continuous: {
        singleRun: true
      }
    },

// The `index` task compiles the `index.html` file as a Grunt template. CSS
// and JS files co-exist here but they get split apart later.
    index: {

      /**
       * During development, we don't want to have wait for compilation,
       * concatenation, minification, etc. So to avoid these steps, we simply
       * add all script files directly to the `<head>` of `index.html`. The
       * `src` property contains the list of included files.
       */

      build: {
        dir: '<%= build_dir %>',
        cwd: 'angular/',
        src: [
          '<%= vendor_files.js %>',
          'src/**/*.js',
          '!src/**/*.spec.js',
          '!src/assets/**/*.js',
          '<%= build_dir %>/templates-app.js',
          '<%= build_dir %>/templates-common.js',
          '<%= vendor_files.css %>',
          '<%= build_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css',
          '<%= build_dir %>/assets/site.js'
        ]
      },

      /**
       * When it is time to have a completely compiled application, we can
       * alter the above to include only a single JavaScript and a single CSS
       * file. Now we're back!
       */
      compile: {
        dir: '<%= compile_dir %>',
        cwd: 'angular/',
        src: [
          '<%= compile_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.js',
          '<%= vendor_files.css %>',
          '<%= compile_dir %>/assets/<%= pkg.name %>-<%= pkg.version %>.css'
        ]
      }
    },

    /**
     * This task compiles the karma template so that changes to its file array
     * don't have to be managed manually.
     */
    karmaconfig: {
      unit: {
        dir: '<%= build_dir %>',
        cwd: 'angular/',
        src: [ 
          '<%= vendor_files.js %>',
          '<%= html2js.app.dest %>',
          '<%= html2js.common.dest %>',
          '<%= test_files.js %>'
        ]
      }
    },

    /**
     * And for rapid development, we have a watch set up that checks to see if
     * any of the files listed below change, and then to execute the listed 
     * tasks when they do. This just saves us from having to type "grunt" into
     * the command-line every time we want to see what we're working on; we can
     * instead just leave "grunt watch" running in a background terminal. Set it
     * and forget it, as Ron Popeil used to tell us.
     *
     * But we don't need the same thing to happen for all the files. 
     */
    delta: {
      /**
       * By default, we want the Live Reload to work for all tasks; this is
       * overridden in some tasks (like this file) where browser resources are
       * unaffected. It runs by default on port 35729, which your browser
       * plugin should auto-detect.
       */
      options: {
        livereload: true
      },

      /**
       * When the Gruntfile changes, we just want to lint it. In fact, when
       * your Gruntfile changes, it will automatically be reloaded!
       */
      gruntfile: {
        files: 'Gruntfile.js',
        tasks: [ 'jshint:gruntfile' ],
        options: {
          livereload: true
        }
      },

      /**
       * When our JavaScript source files change, we want to run lint them and
       * run our unit tests.
       */
      jssrc: {
        files: [ 
          'angular/src/**/*.js'
        ],
        // tasks: [ 'jshint:src', 'karma:unit:run', 'copy:build_appjs' ]
        tasks: [ 'jshint:src', 'copy:build_appjs' ]
      },

      /**
       * When assets are changed, copy them. Note that this will *not* copy new
       * files, so this is probably not very useful.
       */
      assets: {
        files: [ 
          'angular/src/assets/**/*'
        ],
        tasks: [ 'copy:build_app_assets', 'copy:build_vendor_assets' ]
      },

      /**
       * When index.html changes, we need to compile it.
       */
      html: {
        files: [ 'angular/src/index.html' ],
        tasks: [ 'index:build' ]
      },

      /**
       * When our templates change, we only rewrite the template cache.
       */
      tpls: {
        files: [ 
          '<%= app_files.atpl %>', 
          '<%= app_files.ctpl %>'
        ],
        tasks: [ 'html2js' ]
      },

      /**
       * When the CSS files change, we need to compile and minify them.
       */
      less: {
        files: [ 'angular/src/**/*.less' ],
        tasks: [ 'less:build' ]
      },

      /**
       * If any of the static less or django template files are changed, we update as well.
       */
      staticLess: {
        files: [ 'robotics/static/less/**/*.less', 'robotics/templates/**/*.html' ],
        tasks: [ 'less:staticLess' ]
      },



      /**
       * When a JavaScript unit test file changes, we only want to lint it and
       * run the unit tests. We don't want to do any live reloading.
       */
      jsunit: {
        cwd: 'angular/',
        files: [
          '<%= app_files.jsunit %>'
        ],
        // tasks: [ 'jshint:test', 'karma:unit:run' ],
        tasks: [ 'jshint:test'],
        options: {
          livereload: false
        }
      }
    },

    // lets us run django commands too
    // see: https://npmjs.org/package/grunt-bg-shell
    bgShell: {
      _defaults: {
        bg: true
      },
      runDjango: {
        cmd: 'python manage.py runserver'
      },
      runScript: {
        cmd: './clear_migrations.sh'
      },
      runMailDump: {
        cmd: 'maildump -p mailserver.pid'
      },
      stopMailDump: {
        cmd: 'maildump -p mailserver.pid --stop'
      }
    },
    // optimize image
    imagemin: {                          // Task
      dynamic: {                         // Another target
        options: {                       // Target options
          optimizationLevel: 7,
          progressive:true,
          svgoPlugins: [{ removeViewBox: false }],
          use: [pngquant(), mozjpeg(), gifsicle()]
          },
        files: [{
          expand: true,                  // Enable dynamic expansion
          cwd: 'angular/<%= build_dir %>/assets/img/',                   // Src matches are relative to this path
          src: ['**/*.{png,jpg,jpeg,gif}'],   // Actual patterns to match
          dest: 'angular/<%= compile_dir %>/assets/img/'                  // Destination path prefix
        }]
      }
    },
    sass: {
      dist:{
            options: {
                style: 'expanded',
                lineNumbers: true, // 1
                sourcemap: 'none'
            },
            files: [{
                expand: true, // 2
                cwd: 'angular/vendor/angular-material',
                src: ['angular-material.scss'],
                dest: 'angular/vendor/angular-material',
                ext: '.css'
            }]
          }
        },
      cssmin: {
        target:{
            files: [{
                expand: true,
                cwd: 'angular/vendor/angular-material',
                src: ['angular-material.css'], // 1
                dest: 'angular/vendor/angular-material',
                ext: '.min.css'
            }]
          }
        }
  }; //initConfig

grunt.initConfig( grunt.util._.extend( taskConfig, userConfig ) );

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-conventional-changelog');
  grunt.loadNpmTasks('grunt-bump');
  grunt.loadNpmTasks('grunt-coffeelint');
  grunt.loadNpmTasks('grunt-karma');
  grunt.loadNpmTasks('grunt-ng-annotate');
  grunt.loadNpmTasks('grunt-html2js');
  grunt.loadNpmTasks("grunt-contrib-watch");
  grunt.loadNpmTasks("grunt-contrib-less");
  grunt.loadNpmTasks('grunt-contrib-htmlmin');
  //grunt.loadNpmTasks('grunt-contrib-compress');
  //grunt.loadNpmTasks('grunt-newer');
  //grunt.loadNpmTasks('grunt-git');
  //grunt.loadNpmTasks('grunt-ftp-deploy');
  grunt.loadNpmTasks('grunt-contrib-imagemin');
  //grunt.loadNpmTasks('grunt-aws-s3');

  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-cssmin');


  grunt.renameTask( 'watch', 'delta' );
  grunt.registerTask( 'watch', [ 'build','karma:unit','bgShell:runDjango','delta'] );
  grunt.registerTask( 'serve', [ 'build','bgShell:runDjango','delta'] );
  grunt.registerTask( 'db', ['bgShell:runScript']);
  grunt.registerTask( 'default', [ 'build','compile'] );
  grunt.registerTask( 'build', [
    'clean', 'html2js', 'jshint','sass','cssmin','less:build','less:staticLess',
    'concat:build_css', 'copy:build_app_assets', 'copy:build_vendor_assets',
    'copy:build_appjs', 'copy:build_vendorjs', 'copy:build_vendorcss','postcss','index:build'
  ]);

  // grunt.registerTask( 'build', [
  //   'clean', 'html2js', 'jshint', 'less:build',
  //   'concat:build_css', 'copy:build_app_assets', 'copy:build_vendor_assets',
  //   'copy:build_appjs', 'copy:build_vendorjs', 'copy:build_vendorcss','postcss','index:build', 'karmaconfig',
  //   'karma:continuous' 
  // ]);

  grunt.registerTask( 'compile', ['less:compile', 'copy:compile_assets', 'ngAnnotate', 'concat:compile_js','imagemin', 'uglify', 'index:compile']);
  grunt.registerTask( 'prod', ['bgShell:runDjango','delta']);
  grunt.registerTask( 'robotics', [ 'build', 'compile' ] );



  grunt.registerTask("default", "Prints usage", function () {
      grunt.log.writeln("");
      grunt.log.writeln("Grunt Tasks for CoSpaceRobot");
      grunt.log.writeln("----------------------------------------------");
      grunt.log.writeln("");
      grunt.log.writeln("* run 'grunt --help' to get an overview of all commands.");
      grunt.log.writeln("* run 'grunt db' to run the script to clear out the migrations and db.");
      grunt.log.writeln("* run 'grunt build' for development and testing.");
      grunt.log.writeln("* run 'grunt delta' or 'grunt serve' to track changes and reload");
      grunt.log.writeln("* run 'grunt compile' for deployment by concatenating and minifying your code.");
      grunt.log.writeln("* run 'grunt prod' to run production. ** Note you must change to PROD_SPA in common.py **");
      grunt.log.writeln("* run 'grunt bolt' to build and compile.");

  });

  /**
   * A utility function to get all app JavaScript sources.
   */
  function filterForJS ( files ) {
    return files.filter( function ( file ) {
      return file.match( /\.js$/ );
    });
  }

  /**
   * A utility function to get all app CSS sources.
   */
  function filterForCSS ( files ) {
    return files.filter( function ( file ) {
      return file.match( /\.css$/ );
    });
  }

 /** 
   * The index.html template includes the stylesheet and javascript sources
   * based on dynamic names calculated in this Gruntfile. This task assembles
   * the list into variables for the template to use and then runs the
   * compilation.
   */

  grunt.registerMultiTask( 'index', 'Process index.html template', function () {
    //grunt.log.write('this file src: ',this);
    var dirRE = new RegExp( '^('+'angular\/'+grunt.config('build_dir')+'|'+'angular\/'+grunt.config('compile_dir')+'|'+grunt.config('build_dir')+'|'+grunt.config('compile_dir')+')\/', 'g' );
    //grunt.log.write('this dirRE: ',dirRE);

    var jsFiles = filterForJS( this.filesSrc ).map( function ( file ) {
      return file.replace( dirRE, '' );
    });
    var cssFiles = filterForCSS( this.filesSrc ).map( function ( file ) {
      return file.replace( dirRE, '' );
    });
    //grunt.log.write(cssFiles);
    //grunt.log.write('JSfiles ',jsFiles);

    grunt.file.copy('angular/src/index.html', 'angular/'+this.data.dir+'/index.html', { 
      process: function ( contents, path ) {
        return grunt.template.process( contents, {

          data: {
            scripts: jsFiles,
            styles: cssFiles,
            version: grunt.config( 'pkg.version' )
          }
        });
      }
    });
  });

  /**
   * In order to avoid having to specify manually the files needed for karma to
   * run, we use grunt to manage the list for us. The `karma/*` files are
   * compiled as grunt templates for use by Karma. Yay!
   */
  grunt.registerMultiTask( 'karmaconfig', 'Process karma config templates', function () {
    var jsFiles = filterForJS( this.filesSrc );
    
    grunt.file.copy( 'angular/karma/karma-unit.tpl.js','angular/' + grunt.config( 'build_dir' ) + '/karma-unit.js', { 
      process: function ( contents, path ) {
        return grunt.template.process( contents, {
          data: {
            scripts: jsFiles
          }
        });
      }
    });
  });
};
