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
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
        sourceMap: true
      },
      build: {
        src: [
        /*
          'geography/static/lib/js/fallbacks.js',
          'geography/static/lib/js/jquery-1.11.0.js',
          'geography/static/lib/angular-1.2.9/angular.js',
          'geography/static/lib/angular-1.2.9/i18n/angular-locale_cs.js',
          'geography/static/lib/js/raphael.min.js',
          */
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
          'geography/static/js/app.js',
          'geography/static/js/controllers.js',
          'geography/static/js/services.js',
          'geography/static/js/filters.js',
          'geography/static/js/map.js',
          'geography/static/js/directives.js'
        ],
        dest: 'geography/static/dist/js/<%= pkg.name %>.min.js'
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
      scripts: {
        files: ['geography/static/js/*.js', 'geography/static/sass/*.sass'],
        tasks: ['default'],
        options: {
          interrupt: true,
        },
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

  // Default task(s).
  grunt.registerTask('styles', ['sass','rename']);
  grunt.registerTask('minify', ['newer:uglify:build']);
  grunt.registerTask('default', ['styles', 'jshint', 'minify']);
  grunt.registerTask('travis', ['jshint']);
  grunt.registerTask('deploy', ['styles', 'uglify']);

};
