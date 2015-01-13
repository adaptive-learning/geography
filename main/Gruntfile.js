module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    sass: {
      options: {
        sourcemap: true,
        style: "compressed"
      },
      dist: {
          files: [{
            expand: true,
            cwd: 'geography/static/sass',
            src: ['*.sass'],
            dest: 'geography/static/css',
            ext: '.css'
          }]
      }
    },
    concat: {
      app: {
        src: [
          'geography/static/dist/js/hash.js',
          'geography/static/dist/js/bbox.js',
          'proso_auth/static/js/app.js',
          'proso_feedback/static/js/app.js',
          'proso_goals/static/js/app.js',
          'proso_mnemonics/static/js/app.js',
          'geography/static/js/app.js',
          'geography/static/js/controllers.js',
          'geography/static/js/services.js',
          'geography/static/js/filters.js',
          'geography/static/js/map.js',
          'geography/static/js/directives.js',
          'geography/static/dist/js/templates.js',
          'proso_auth/static/dist/js/templates.js',
          'proso_goals/static/dist/js/templates.js',
        ],
        dest: 'geography/static/dist/js/<%= pkg.name %>.min.js'
      },
    },
    shell: { 
        hashes: {
            command: './manage.py static_hashes "(css|svg)" > geography/static/dist/hashes.json'
        },
        runserver: {
            command: './manage.py runserver'
        }
    },
    'string-replace': {
      homepage: {
        options: {
          replacements: [
            {
                pattern: /\{\{\s*(("[^"]+")|('[^']+'))\s*\|\s*trans\s*\}\}/g,
                replacement: '{% trans $1 %}'
            }
          ]
        },
        src: ['geography/static/tpl/homepage.html'],
        dest: 'templates/generated/homepage.html',
      },
      'tpl-gettext-hack': {
        options: {
          replacements: [
            {
                pattern: /\{\{\s*(("[^"]+")|('[^']+'))\s*\|\s*trans\s*\}\}/g,
                replacement: '\ngettext($1);\n  '
            }, {
                pattern: /(  |<).*\n/g,
                replacement: ''
            }
          ]
        },
        files: [{
          expand: true,
          src: [
            'geography/static/tpl/*',
            'proso_auth/static/tpl/*',
            'proso_feedback/static/tpl/*',
            'proso_goals/static/tpl/*',
          ],
          dest: 'geography/static/hack/',
          ext: '.js'
        }]
      },
      hashes: {
        options: {
          replacements: [
            {
                pattern: '{{hashes}}',
                replacement: "<%= grunt.file.read('geography/static/dist/hashes.json') %>"
            }
          ]
        },
        src: ['geography/static/jstpl/hash.js'],
        dest: 'geography/static/dist/js/hash.js',
      },
      bboxcache: {
        options: {
          replacements: [
            {
                pattern: '{{bboxes}}',
                replacement: "<%= grunt.file.read('geography/static/hack/bboxcache.json') %>"
            }
          ]
        },
        src: ['geography/static/jstpl/bbox.js'],
        dest: 'geography/static/dist/js/bbox.js',
      }
    },
    ngtemplates:    {
      blindMaps:          {
        cwd: 'geography',
        src: [
          'static/tpl/*.html',
        ],
        dest: 'geography/static/dist/js/templates.js',
        options:    {
          htmlmin:  { collapseWhitespace: true, collapseBooleanAttributes: true }
        }
      },
      'proso.feedback':          {
        cwd: 'proso_feedback',
        src: [
          'static/tpl/*.html',
        ],
        dest: 'proso_feedback/static/dist/js/templates.js',
        options:    {
          htmlmin:  { collapseWhitespace: true, collapseBooleanAttributes: true }
        }
      },
      'proso.goals':          {
        cwd: 'proso_goals',
        src: [
          'static/tpl/*.html',
        ],
        dest: 'proso_goals/static/dist/js/templates.js',
        options:    {
          htmlmin:  { collapseWhitespace: true, collapseBooleanAttributes: true }
        }
      },
      'proso.auth':          {
        cwd: 'proso_auth',
        src: [
          'static/tpl/*.html',
        ],
        dest: 'proso_auth/static/dist/js/templates.js',
        options:    {
          htmlmin:  { collapseWhitespace: true, collapseBooleanAttributes: true }
        }
      }
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
        sourceMap: true
      },
      app: {
        src: [
          'geography/static/dist/js/hash.js',
          'geography/static/dist/js/bbox.js',
          'proso_auth/static/js/app.js',
          'proso_feedback/static/js/app.js',
          'proso_goals/static/js/app.js',
          'proso_mnemonics/static/js/app.js',
          'geography/static/js/app.js',
          'geography/static/js/controllers.js',
          'geography/static/js/services.js',
          'geography/static/js/filters.js',
          'geography/static/js/map.js',
          'geography/static/js/directives.js',
          'geography/static/dist/js/templates.js',
          'proso_auth/static/dist/js/templates.js',
          'proso_feedback/static/dist/js/templates.js',
          'proso_goals/static/dist/js/templates.js',
        ],
        dest: 'geography/static/dist/js/<%= pkg.name %>.min.js'
      },
      fallbacks: {
        src: [
          'geography/static/lib/js/fallbacks.js',
        ],
        dest: 'geography/static/dist/js/fallbacks.min.js'
      },
      libs: {
        src: [
        /*
          'geography/static/lib/angular-1.2.9/i18n/angular-locale_cs.js',
          */
          'geography/static/lib/js/jquery-1.11.0.js',
          'geography/static/lib/angular-1.2.9/angular.js',
          'geography/static/lib/js/raphael.js',
          'geography/static/lib/js/raphael.pan-zoom.js',
          'geography/static/lib/js/kartograph.js',
          'geography/static/lib/js/chroma.js',
          'geography/static/lib/js/bootstrap.js',
          'geography/static/lib/js/ui-bootstrap-tpls-0.11.0.js',
          'geography/static/lib/angular-1.2.9/angular-route.js',
          'geography/static/lib/angular-1.2.9/angular-cookies.js',
          'geography/static/lib/angular-1.2.9/angular-animate.js',
          'geography/static/lib/js/jquery.qtip.min.js',
          'geography/static/lib/js/angulartics.min.js',
          'geography/static/lib/js/angulartics-ga.min.js',
          'geography/static/lib/js/xeditable.js',
        ],
        dest: 'geography/static/dist/js/libs.min.js'
      }
    },
    jshint: {
      options: {
          "undef": true,
          "unused": true,
          "browser": true,
          "globals": { 
              "angular": false
          },
          "maxcomplexity": 6,
          "indent": 2,
          "maxstatements": 12,
          "maxdepth" : 3,
          "maxparams": 12,
          "maxlen": 110
      },
      build: {
        src: 'geography/static/js/',
      }
    },
    watch: {
      options: {
        interrupt: true,
      },
      styles: {
        files: ['geography/static/sass/*.sass'],
        tasks: ['styles'],
      },
      hashes: {
        files: ['geography/static/map/*.svg', 'geography/static/sass/*.sass'],
        tasks: ['hashes'],
      },
      jstpl: {
        files: ['geography/static//jstpl/*.js'],
        tasks: ['string-replace'],
      },
      templates: {
        files: [
          'geography/static/tpl/*.html',
          'proso_auth/static/tpl/*.html',
          'proso_feedback/static/tpl/*.html',
          'proso_goals/static/tpl/*.html',
        ],
        tasks: ['templates', 'concat:app'],
      },
      jsapp: {
        files: [
          'geography/static/js/*.js',
          'proso_feedback/static/js/*.js',
          'proso_goals/static/js/*.js',
          'proso_mnemonics/static/js/*.js',
        ],
        tasks: ['concat:app'],
      },
      jslibs: {
        files: ['geography/static/lib/js/*.js', 'geography/static/lib/angular-1.2.9/*.js'],
        tasks: ['uglify:libs'],
      },
    },
    rename: {
        moveAboveFoldCss: {
            src: 'geography/static/css/above-fold.css',
            dest: 'templates/generated/above-fold.css'
        },
        moveReminderEmailCss: {
            src: 'geography/static/css/reminder-email.css',
            dest: 'templates/generated/reminder-email.css'
        },
    },
    bboxcache: {
      default: {
        files: {
          'geography/static/hack/bboxcache.json': ['geography/static/map/*.svg'],
        },
      },
    },
    protractor: {
      options: {
        configFile: "geography/static/test/spec.js", // Default config file
        keepAlive: true, // If false, the grunt process stops when the test fails.
        noColor: false, // If true, protractor will not use colors in its output.
        args: {
          // Arguments passed to the command
        }
      },
      tests: {
        options: {
          args: {} // Target-specific arguments
        }
      },
    },
  });

  // Load plugins.
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-notify');
  grunt.loadNpmTasks('grunt-rename');
  grunt.loadNpmTasks('grunt-newer');
  grunt.loadNpmTasks('grunt-angular-templates');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-string-replace');
  grunt.loadNpmTasks('grunt-shell');
  grunt.loadNpmTasks('grunt-protractor-runner');

  // Default task(s).
  grunt.registerTask('styles', ['sass','rename']);
  grunt.registerTask('runserver', ['shell:runserver','watch']);
  grunt.registerTask('hashes', ['shell:hashes', 'string-replace:hashes']);
  grunt.registerTask('bboxcacheall', ['bboxcache', 'string-replace:bboxcache']);
  grunt.registerTask('templates', ['string-replace:homepage', 'ngtemplates', 'string-replace:tpl-gettext-hack']);
  grunt.registerTask('minifyjs', ['hashes', 'templates', 'uglify']);
  grunt.registerTask('default', ['styles', 'jshint', 'bboxcache', 'minifyjs']);
  grunt.registerTask('deploy', ['styles', 'string-replace:bboxcache', 'minifyjs']);

  grunt.registerMultiTask('bboxcache', 'Precompute bbox of svg paths.', function() {

    var raphael = require('node-raphael');
    var DomJS = require("dom-js").DomJS;
    var RANDOM_CONST = 42;

    function mapNameFromFilepath (filepath) {
        var splittedPath = filepath.split('/');
        var filename = splittedPath[splittedPath.length -1];
        return filename.split('.')[0];
    }

    // Iterate over all specified file groups.
    this.files.forEach(function(f) {
      
      var cache = {
          bboxes : {},
          maps : {},
      };

      f.src.filter(function(filepath) {
        // Warn on and remove invalid source files (if nonull was set).
        if (!grunt.file.exists(filepath)) {
          grunt.log.warn('Source file "' + filepath + '" not found.');
          return false;
        } else {
          return true;
        }
      }).map(function(filepath) {

        var domjs = new DomJS();

        domjs.parse(grunt.file.read(filepath), function(err, dom) {
            var mapName = mapNameFromFilepath(filepath);
            var map = {
                width :  parseInt(dom.attributes.width),
                height :  parseInt(dom.attributes.height),
            };
            cache.maps[mapName] = map;

            raphael.generate(RANDOM_CONST, RANDOM_CONST, function draw(paper) { 
                dom.children.filter(function(e){
                    return e.name == 'g';
                }).map(function (e) {
                    return e.children.filter(function(ch){
                        return ch.name == 'path' && ch.attributes['data-code'];
                    }).map(function(ch){
                    var d = ch.attributes.d;
                    var code = ch.attributes['data-code'];
                    if (code) {
                        var path = paper.path(d);
                        var bbox =  path.getBBox();
                        var keys = ['x', 'y', 'cx', 'cy', 'x2', 'y2', 'width', 'height'];
                        for (var j = 0; j < keys.length; j++) {
                            bbox[keys[j]] = Math.round(bbox[keys[j]]);
                        }
                        bbox.map = mapName;
                        if (!cache.bboxes[code]) {
                            cache.bboxes[code] = bbox;
                        }
                    }
                    });
                });
            });

        });
        return; 
      });

      // Write the destination file.
      grunt.file.write(f.dest, JSON.stringify(cache));

      // Print a success message.
      grunt.log.writeln('File "' + f.dest + '" created.');
    });
  });
};
