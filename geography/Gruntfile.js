module.exports = function(grunt) {
    'use strict';

    grunt.initConfig({
        bboxcache: {
            default: {
                files: {
                    'static/dist/bboxcache.json': ['static/map/*.svg'],
                },
            },
        },
        bower_concat: {
            all: {
                dest: 'static/dist/js/bower-libs.js',
                cssDest: 'static/dist/css/bower-libs.css',
                dependencies: {
                    'kartograph.js': ['jquery'],
                    'qtip2': ['jquery'],
                    'raphael-pan-zoom': ['raphael'],
                },
                mainFiles: {
                    'raphael-pan-zoom': 'src/raphael.pan-zoom.js',
                    'angular-i18n': 'angular-locale_cs-cz.js'
                },
                exclude: ['proso-apps-js']
            }
        },
        concat: {
            geography: {
                src: [
                  'static/dist/js/bbox.js',
                  'static/js/*.js',
                  'static/dist/js/translations.js'
                ],
                dest: 'static/dist/js/geography.js'
            }
        },
        copy: {
            'above-fold': {
                src: 'static/dist/css/above-fold.css',
                dest: 'templates/dist/above-fold.css'
            },
            'images': {
                expand: true,
                cwd: 'static/img',
                src: ['**'],
                dest: 'static/dist/img/'
            },
            'fonts': {
                expand: true,
                cwd: 'bower_components/bootstrap/fonts/',
                src: ['**'],
                dest: 'static/dist/fonts/'
            },
            'proso-apps-js': {
                src: 'bower_components/proso-apps-js/proso-apps-all.js',
                dest: 'static/dist/js/proso-apps-all.js'
            }
        },
        html2js: {
            options: {
                base: '.',
                module: 'proso.geography.templates',
                singleModule: true,
                useStric: true
            },
            geography: {
                src: ['static/tpl/*.html'],
                dest: 'static/dist/js/geography.html.js',
            }
        },
        jshint: {
            options: {
                "undef": true,
                "unused": true,
                "browser": true,
                "globals": {
                    "angular": false,
                    "bboxCache": false,
                    "chroma": false,
                    "console": false,
                    "gettext": false,
                    "jQuery": false,
                },
                "maxcomplexity": 6,
                "maxstatements": 20,
                "maxdepth" : 3,
                "maxparams": 12,
                "predef": ["Kartograph"],
            },
            dist: {
                src: 'static/js/',
            }
        },
        nggettext_compile: {
            all: {
                src: ['static/po/*.po'],
                dest:'static/dist/js/translations.js',
            },
        },
        nggettext_extract: {
            pot: {
                src: [
                    'static/js/*.js',
                    'static/tpl/*.html'
                ],
                dest: 'static/dist/client.pot',
            },
        },
        sass: {
            options: {
                style: "compressed"
            },
            geography: {
                files: [{
                    expand: true,
                    cwd: 'static/sass',
                    src: ['*.sass'],
                    dest: 'static/dist/css',
                    ext: '.css'
                }]
            }
        },
        shell: {
            bower_install: {
                command: 'node_modules/bower/bin/bower install -f'
            },
            makemessages: {
                command: '../manage.py makemessages --all --ignore=node_modules/*  && ../manage.py makemessages --all --domain djangojs --ignore=node_modules/* --ignore=bower_components/* --ignore=static/dist/*'
            }
        },
        'string-replace': {
            bboxcache: {
                options: {
                    replacements: [{
                        pattern: '{{bboxes}}',
                        replacement: "<%= grunt.file.read('static/dist/bboxcache.json') %>"
                    }]
                },
                src: ['static/jstpl/bbox.js'],
                dest: 'static/dist/js/bbox.js',
            }
        },
        uglify: {
            libs: {
                options: {
                    mangle: {
                        except: ['Kartograph', 'Raphael', 'gettextCatalog']
                    },
                    sourceMap: true,
                    sourceMapIncludeSources: true,
                    sourceMapName: 'static/dist/js/bower-libs.min.js.map'
                },
                src: 'static/dist/js/bower-libs.js',
                dest: 'static/dist/js/bower-libs.min.js'
            },
            geography: {
                options: {
                    sourceMap: true,
                    sourceMapIncludeSources: true,
                    sourceMapName: 'static/dist/geography.min.js.map'
                },
                src: 'static/dist/js/geography.js',
                dest: 'static/dist/js/geography.min.js'
            },
            'geography-tpls': {
                options: {
                    sourceMap: true,
                    sourceMapIncludeSources: true,
                    sourceMapName: 'static/dist/geography-tpls.min.js.map'
                },
                src: 'static/dist/js/geography-tpls.js',
                dest: 'static/dist/js/geography-tpls.min.js'
            },

        },
        watch: {
            'geography-js': {
                files: 'static/js/*.js',
                tasks: ['concat:geography', 'uglify:geography']
            },
            'geography-css': {
                files: 'static/sass/*.sass',
                tasks: ['sass:geography', 'copy:above-fold']
            },
            'geography-tpls': {
                files: 'static/tpl/*.html',
                tasks: ['html2js:geography', 'concat:geography', 'uglify:geography']
            },
            'geography-nggettext_compile': {
                files: '<%= nggettext_compile.all.src %>',
                tasks: ['nggettext_compile']
            },
            'geography-nggettext_extract': {
                files: '<%= nggettext_extract.pot.src %>',
                tasks: ['nggettext_extract']
            }
        }
    });

    grunt.loadNpmTasks('grunt-bower-concat');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-shell');
    grunt.loadNpmTasks('grunt-string-replace');
    grunt.loadNpmTasks('grunt-html2js');
    grunt.loadNpmTasks('grunt-angular-gettext');

    grunt.registerTask('bboxcache-all', ['bboxcache', 'string-replace:bboxcache']);
    grunt.registerTask('makemessages', ['shell:makemessages']);
    grunt.registerTask('collect-libs', ['bower_concat:all', 'uglify:libs', 'copy:fonts', 'copy:proso-apps-js']);
    grunt.registerTask('prepare-libs', ['shell:bower_install', 'collect-libs']);
    grunt.registerTask('prepare', ['jshint', 'html2js:geography', 'concat:geography', 'uglify:geography', 'sass:geography', 'copy:above-fold', 'copy:images']);
    grunt.registerTask('default', ['bboxcache-all', 'nggettext_compile', 'prepare-libs', 'prepare']);

    /* CUSTOM TASKS */

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
                        dom.children.filter(function(e) {
                            return e.name == 'g';
                        }).map(function (e) {
                            return e.children.filter(function(ch) {
                                return ch.name == 'path' && ch.attributes['data-code'];
                            }).map(function(ch) {
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
