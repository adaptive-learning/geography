'use strict';

var GOOD = "#0d0";
var BAD = "#ff0000";
var NEUTRAL = "#bbb";
var HOLDER = '#map-holder';
var STROKE_WIDTH = 1.5;
var RIVER_WIDTH = STROKE_WIDTH * 2;
var WATER_COLOR = "#73c5ef";
var ANIMATION_TIME_MS = 500;

(function(window, $K, undefined){

var times = {};
var time;
function profile(message) {
    if (!times[message]) {
        times[message] = new Date().getTime();
    } else {
        time = new Date().getTime() - times[message];
        console.log(message, time, "ms");
        times[message] = undefined;
    }
}

window.initMap = function(config, callback) {

    var map = $K.map(HOLDER);
    var panZoom;
    var layers;

    var holderInitHeight = $(HOLDER).height();
    var mapAspectRatio;

    $.fn.qtip.defaults.style.classes = 'qtip-dark';

    var scale = chroma.scale([BAD, "#ff4500", "#ffa500", "#ffff00", GOOD]);

    var layerConfig = {};
    layerConfig.bg = {
        'styles' : {
            'fill' : NEUTRAL,
            'stroke-width' : STROKE_WIDTH,
            'transform' : ""
        }
    };

    layerConfig.states = {
        'styles' : {
            'fill' : function(d) {
                var state = config.states && config.states[d.name];
                return (state
                    ? (scale(state.probability).brighten((1 - state.certainty) * 80).hex())
                    : '#fff');
            },
            'stroke-width' : STROKE_WIDTH,
            'transform' : ""
        },
        'click' : function(data, path, event) {
            console.log(data["name"]);
            if (config.click != undefined) {
                config.click(data.name);
            }
        }
    };

    if (config.showTooltips) {
        layerConfig.states.tooltips = function(d) {
            var state = config.states && config.states[d.name];
            var name = ( state
                ? '<span class="label">'
                    + '<i class="flag-' + d.name + '"></i> '
                    + state.name
                    + '</span>'
                : '<br>Zatím neprocvičováno<br><br>');
            var description = (state
                ? '<div>'
                    + '<i class="color-indicator" style="background-color:'
                    + scale(state.probability).hex() + '"></i>'
                    + ' Odhad znalosti: ' + Math.round(100 * state.probability) + '%</div>'
                : "");
            return [
                name + description,
                config.states[d.name] ? config.states[d.name].name : ""
            ];
        };
    }

    layerConfig.provinces = jQuery.extend({}, layerConfig.states);
    layerConfig.cities = jQuery.extend(jQuery.extend({}, layerConfig.states), {
        'mouseenter' : function(data, path, event) {
            path.toFront();
            var zoomRatio = 2;
            var aminAttrs = {
                'transform' : "s"+zoomRatio,
                'stroke-width' : zoomRatio * STROKE_WIDTH
            };
            path.animate(aminAttrs, ANIMATION_TIME_MS/2, ">");
        },
        'mouseleave' : function(data, path, event) {
            var aminAttrs = {
                'transform': "",
                'stroke-width': STROKE_WIDTH
            };
            path.animate(aminAttrs, ANIMATION_TIME_MS/2, ">");
        }
    });

    layerConfig.rivers = jQuery.extend(jQuery.extend({}, layerConfig.states), {
        'styles' : {
            'stroke-width' : RIVER_WIDTH,
            'stroke' : WATER_COLOR,
            'transform' : ""
        },
        'mouseenter' : function(data, path, event) {
            var zoomRatio = 4;
            var aminAttrs = {
                'stroke-width' : zoomRatio * RIVER_WIDTH
            };
            path.animate(aminAttrs, ANIMATION_TIME_MS/2, ">");
        },
        'mouseleave' : function(data, path, event) {
            var aminAttrs = {
                'stroke-width': RIVER_WIDTH
            };
            path.animate(aminAttrs, ANIMATION_TIME_MS/2, ">");
        }
    });

    layerConfig.lakes = jQuery.extend(true, {}, layerConfig.cities);
    layerConfig.lakes["styles"]["fill"] = function(d) {
        var state = config.states && config.states[d.name];
        return (state
            ? (scale(state.probability).brighten((1 - state.certainty) * 80).hex())
            : WATER_COLOR);
    };

    map.loadCSS(Hash('static/css/map.css'), function() {
        map.loadMap(Hash('static/map/' + config.name + '.svg'), function() {
            profile("Map loading takes:");

            layers = initLayers(map, layerConfig);

            $(window).resize(resize);
            profile("resize takes:");
            resize();
            profile("resize takes:");

            panZoom = initMapZoom(map.paper);

            callback && callback();

            $(HOLDER).find(".loading-indicator").hide();

            profile("Map loading takes:");
        });
    });

    function resize() {
        if (!mapAspectRatio) {
            mapAspectRatio = map.viewAB.height / map.viewAB.width;
        }

        var c = $(HOLDER);
        if (holderInitHeight/ mapAspectRatio >= $(window).width()) {
            var newHeight = Math.max(holderInitHeight/2, mapAspectRatio * $(window).width());
        } else {
            var newHeight = holderInitHeight;
        }
        c.height(newHeight);
        map.resize();
        if (panZoom) {
            panZoom.zoomIn(1);
            panZoom.zoomOut(1);
        }
    }

    function getZoomRatio(bboxArea) {
        var zoomRatio = Math.max(1.2, 70 / Math.sqrt(bboxArea));
        return zoomRatio;
    }

    function initMapZoom(paper) {
        var panZoom = paper.panzoom({ });
        panZoom.enable();

        var zoomButtons = ''+
        '<div class="btn-group zoom-btn">'+
        '    <a class="btn btn-default" id="zoom-out"><i class="glyphicon glyphicon-minus"></i></a>'+
        '    <a class="btn btn-default" id="zoom-in"><i class="glyphicon glyphicon-plus"></i></a>'+
        '</div>';
        $(HOLDER).after(zoomButtons);

        $("#zoom-in").click(function (e) {
            panZoom.zoomIn(1);
            e.preventDefault();
        });

        $("#zoom-out").click(function (e) {
            panZoom.zoomOut(1);
            e.preventDefault();
        });
        return panZoom;
    }

    var myMap = {
        map : map,
        highlightStates : function(states, color, zoomRatio) {
            var state = states.pop();
            var layer = this.getLayerContaining(state);
            if (layer) {
                var placePath = layer.getPaths({ name: state })[0];
            }

            if (placePath) {
                placePath.svgPath.toFront();
                var origStroke = layerConfig[layer.id].styles['stroke-width'];
                var bbox = placePath.svgPath.getBBox();
                var bboxArea = bbox.width * bbox.height;
                var zoomRatio = zoomRatio || getZoomRatio(bboxArea);
                var aminAttrs = {
                    transform: "s"+zoomRatio,
                    'stroke-width': Math.min(6, zoomRatio) * origStroke
                };
                if (color) {
                    if (layer.id == 'rivers') {
                        aminAttrs['stroke'] = color;
                    } else {
                        aminAttrs['fill'] = color;
                    }
                }
                placePath.svgPath.animate(aminAttrs, ANIMATION_TIME_MS/2, ">", function(){
                        placePath.svgPath.animate({transform: "", 'stroke-width': origStroke}, ANIMATION_TIME_MS/2, "<");
                    myMap.highlightStates(states, color);
                });
            } else if (states.length > 0) {
                myMap.highlightStates(states, color);
            }
        },
        highlightState : function(state, color, zoomRatio) {
            myMap.highlightStates([state], color, zoomRatio);
        },
        clearHighlights : function() {
            var layers = this.getAllLayers();
            angular.forEach(layers, function(layer){
                layer.style(layerConfig[layer.id].styles);
                myMap.showLayer(layer);
            });
            myMap.zoomOut();
        },
        zoomOut : function(i){
            var i = i || 10;
            if (panZoom) {
                panZoom.zoomOut(1);
            }
            i--;
            if (i > 0) {
                setTimeout(function(){
                    myMap.zoomOut(i);
                }, 25);
            }
        },
        updatePlaces : function(places) {
            config.states = places;
            var layers = myMap.getAllLayers();
            angular.forEach(layers, function(layer){
                var config = layerConfig[layer.id];
                layer.style('fill', config.styles.fill);
                layer.tooltips(config.tooltips);
            });
        },
        getAllLayers : function() {
            var layers = [];
            for (var l in layerConfig) {
                try {
                    var layer = map.getLayer(l);
                    if (layer) {
                        layers.push(layer);
                    }
                } catch (e) {
                    console.log(e);
                }
            }
            return layers;
        },
        getLayerContaining : function(placeCode) {
            var layers = myMap.getAllLayers();
            var ret;
            angular.forEach(layers, function(layer){
                if (layer.getPaths({ name: placeCode }).length >= 1) {
                    ret = layer;
                }
            });
            return ret;
        },
        highLightLayer : function(layer) {
            var layers = myMap.getAllLayers();
            angular.forEach(layers, function(l){
                if (l.id == "cities" && layer.id == "states") {
                    myMap.hideLayer(l);
                }
            });
        },
        hideLayer : function(layer) {
            var paths = layer ? layer.getPaths({}) : [];
            angular.forEach(paths, function(path){
                path.svgPath.hide();
            });
        },
        showLayer : function(layer) {
            var paths = layer ? layer.getPaths({}) : [];
            angular.forEach(paths, function(path){
                path.svgPath.show();
            });
        }
    };
    return myMap;
};

function initLayers(map, layerConfig) {
    var layersArray = [];

    for (var i in layerConfig) {
        profile("Add layer "+ i +" takes:");
        map.addLayer(i, layerConfig[i]);
        var l = map.getLayer(i);
        if (l) {
            layersArray.push(l);
        }
        profile("Add layer "+ i +" takes:");
    }

    var that = {

        getAll : function(){
            return layersArray;
        }
    };
    return that;
}
})(window, $K);
