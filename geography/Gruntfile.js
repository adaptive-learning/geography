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
                dest: 'static/bower-libs.js',
                dependencies: {
                    'kartograph.js': ['jquery']
                }
            }
        },
        concat: {
            libs: {
                options: {
                    separator: ';',
                },
                src: [
                    'bower_components/dist/angular.js',
                    'bower_components/dist/angular-*.js',
                    'bower_components/dist/**/*.js'
                ],
                dest: 'static/bower-libs.js'
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
                    sourceMapName: 'static/bower-libs.min.js.map'
                },
                src: 'static/bower-libs.js',
                dest: 'static/bower-libs.min.js'
            }
        }
    });

    grunt.loadNpmTasks('grunt-bower-concat');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-shell');
    grunt.loadNpmTasks('grunt-string-replace');

    grunt.registerTask('bboxcache-all', ['bboxcache', 'string-replace:bboxcache']);
    grunt.registerTask('collect-libs', ['bower_concat:all', 'uglify:libs']);
    grunt.registerTask('prepare-libs', ['shell:bower_install', 'collect-libs']);

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
