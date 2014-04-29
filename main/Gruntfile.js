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
      homepage: {
        src: ['geography/static/tpl/homepage.html'],
        dest: 'templates/generated/homepage.html',
      },
    },
    shell: { 
        hashes: {
            command: './manage.py static_hashes "(css|svg)" > geography/static/dist/hashes.json'
        }
    },
    'string-replace': {
      hashes: {
        options: {
          replacements: [
            {
                pattern: '{{ hashes|safe }}',
                replacement: "<%= grunt.file.read('geography/static/dist/hashes.json') %>"
            }
          ]
        },
        src: ['geography/static/jstpl/hash.js'],
        dest: 'geography/static/dist/js/hash.js',
      }
    },
    ngtemplates:    {
      blindMaps:          {
        cwd: 'geography',
        src: [
          './../templates/home/how_it_works.html',
          'static/tpl/*.html',
        ],
        dest: 'geography/static/dist/js/templates.js',
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
          'geography/static/js/app.js',
          'geography/static/js/controllers.js',
          'geography/static/js/services.js',
          'geography/static/js/filters.js',
          'geography/static/js/map.js',
          'geography/static/js/directives.js',
          'geography/static/dist/js/templates.js',
        ],
        dest: 'geography/static/dist/js/<%= pkg.name %>.min.js'
      },
      libs: {
        src: [
        /*
          'geography/static/lib/js/fallbacks.js',
          'geography/static/lib/js/jquery-1.11.0.js',
          'geography/static/lib/angular-1.2.9/angular.js',
          'geography/static/lib/angular-1.2.9/i18n/angular-locale_cs.js',
          */
          'geography/static/lib/js/raphael.js',
          'geography/static/lib/js/raphael.pan-zoom.js',
          'geography/static/lib/js/kartograph.js',
          'geography/static/lib/js/chroma.js',
          'geography/static/lib/js/bootstrap.js',
          'geography/static/lib/angular-1.2.9/angular-route.js',
          'geography/static/lib/angular-1.2.9/angular-cookies.js',
          'geography/static/lib/angular-1.2.9/angular-animate.js',
          'geography/static/lib/js/jquery.qtip.min.js',
          'geography/static/lib/js/angulartics.min.js',
          'geography/static/lib/js/angulartics-google-analytics.min.js',
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
          "maxcomplexity": 5,
          "indent": 2,
          "maxstatements": 12,
          "maxdepth" : 2,
          "maxparams": 11,
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
      jsapp: {
        files: ['geography/static/js/*.js', 'geography/static/tpl/*.html'],
        tasks: ['quickminifyjs'],
      },
      styles: {
        files: ['geography/static/sass/*.sass'],
        tasks: ['styles'],
      },
      jslibs: {
        files: ['geography/static/lib/js/*.js', 'geography/static/lib/angular-1.2.9/*.js'],
        tasks: ['uglify:libs'],
      },
    },
    rename: {
        moveAboveFoldCss: {
            src: 'geography/static/css/above-fold.css',
            dest: 'templates/home/above-fold.css'
        },
    }
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

  // Default task(s).
  grunt.registerTask('styles', ['sass','rename']);
  grunt.registerTask('hashes', ['shell:hashes', 'string-replace:hashes']);
  grunt.registerTask('templates', ['newer:concat', 'ngtemplates']);
  grunt.registerTask('minifyjs', ['hashes', 'templates', 'uglify']);
  grunt.registerTask('quickminifyjs', ['hashes', 'templates', 'newer:uglify:app']);
  grunt.registerTask('default', ['styles', 'jshint', 'quickminifyjs']);
  grunt.registerTask('deploy', ['styles', 'minifyjs']);

};
