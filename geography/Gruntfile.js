module.exports = function(grunt) {
    'use strict';

    grunt.initConfig({
        bboxcache: {
            default: {
                files: {
                    'static/hack/bboxcache.json': ['static/map/*.svg'],
                },
            },
        },
        bower_concat: {
            all: {
                dest: 'static/dist/js/bower-libs.js',
                cssDest: 'static/dist/css/bower-libs.css',
                dependencies: {
                    'kartograph.js': ['jquery']
                },
                mainFiles: {
                    'angular-i18n': 'angular-locale_cs-cz.js'
                }
            }
        },
        concat: {
            geography: {
                src: ['static/js/*.js'],
                dest: 'static/dist/js/geography.js'
            }
        },
        copy: {
            'above-fold': {
                src: 'static/dist/css/above-fold.css',
                dest: 'templates/dist/above-fold.css'
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
        sass: {
            options: {
                sourcemap: "inline",
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
                command: 'bower install -f'
            }
        },
        'string-replace': {
            bboxcache: {
                options: {
                    replacements: [{
                        pattern: '{{bboxes}}',
                        replacement: "<%= grunt.file.read('static/hack/bboxcache.json') %>"
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
                        except: ['Kartograph']
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

        }
    });

    grunt.loadNpmTasks('grunt-bower-concat');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-shell');
    grunt.loadNpmTasks('grunt-string-replace');
    grunt.loadNpmTasks('grunt-html2js');

    grunt.registerTask('bboxcache-all', ['bboxcache', 'string-replace:bboxcache']);
    grunt.registerTask('collect-libs', ['bower_concat:all', 'uglify:libs']);
    grunt.registerTask('prepare-libs', ['shell:bower_install', 'collect-libs']);
    grunt.registerTask('prepare', ['html2js:geography', 'concat:geography', 'uglify:geography', 'sass:geography', 'copy:above-fold']);
    grunt.registerTask('default', ['bboxcache-all', 'prepare-libs', 'prepare']);

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
}
