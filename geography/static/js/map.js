var STROKE_WIDTH = 1.5;
var RIVER_WIDTH = STROKE_WIDTH * 2;
var RESERVOIR_WIDTH = STROKE_WIDTH * 4;
var ANIMATION_TIME_MS = 500;
var hash = function(x) {
  if (window.mapFileHashes) {
    return window.mapFileHashes[x] || x;
  }
  return x;
};

angular.module('proso.geography.map', [])

  .value('chroma', chroma)

  .value('$', jQuery)

  .value('$K', Kartograph)

  .value('bboxCache', bboxCache)

  .value('colors', {
    'GOOD': '#0d0',
    'BAD': '#e23',
    'NEUTRAL': '#777',
    'BRIGHT_GRAY' : '#ddd',
    'BRIGHTER_GRAY' : '#eee',
    'WATER_COLOR' : '#73c5ef'
  })

  .value('stateAlternatives', [
    "region",
    "province",
    "region_cz",
    "region_it",
    "bundesland",
    "autonomous_comunity",
  ])

  .factory('colorScale', ['colors', 'chroma', function(colors, chroma) {
    var scale = chroma.scale([
        colors.BAD,
        '#f40',
        '#fa0',
        '#fe3',
        colors.GOOD
      ]);
    return scale;
  }])

  .factory('getLayerConfig', ['$log', 'colors', 'colorScale', 'citySizeRatio',
      'stateAlternatives', 'highlighted',
      function($log, colors, colorScale, citySizeRatio, stateAlternatives, highlighted) {
    'use strict';
    return function(config) {
      var layerConfig = {};
      layerConfig.bg = {
        'styles' : {
          'fill' : colors.BRIGHT_GRAY,
          'stroke-width' : STROKE_WIDTH,
          'transform' : ''
        }
      };

      layerConfig.border = {
        'styles' : {
          'fill' : colors.BRIGHTER_GRAY,
          'stroke-width' : STROKE_WIDTH,
          'transform' : ''
        }
      };

      layerConfig.state = {
        'styles' : {
          'fill' : function(d) {
            var flashcard = config.places && config.places[d.code];
            return flashcard && flashcard.practiced ?
              colorScale(flashcard.prediction).hex() :
              '#fff';
          },
          'stroke-width' : STROKE_WIDTH,
          'stroke' : '#000',
          'transform' : ''
        },
        'click' : function(data) {
          $log.log(data.code);
          if (config.click !== undefined) {
            config.click(data.code);
          }
        }
      };

      angular.forEach(stateAlternatives.concat('island', 'mountains', 'surface'), function(sa){
        layerConfig[sa] = angular.copy(layerConfig.state);
      });

      layerConfig.river = angular.extend(angular.extend({}, layerConfig.state), {
        'styles' : {
          'stroke-width' : RIVER_WIDTH,
          'stroke' : function(d) {
            var flashcard = config.places && config.places[d.code];
            return flashcard && flashcard.practiced ?
              colorScale(flashcard.prediction).hex() :
              colors.WATER_COLOR;
          },
          'transform' : ''
        },
        'mouseenter' : function(data, path) {
          var zoomRatio = 4;
          var animAttrs = { 'stroke-width' : zoomRatio * RIVER_WIDTH };
          path.animate(animAttrs, ANIMATION_TIME_MS / 2, '>');
        },
        'mouseleave' : function(data, path) {
          var animAttrs = { 'stroke-width' : RIVER_WIDTH };
          path.animate(animAttrs, ANIMATION_TIME_MS / 2, '>');
        }
      });

      layerConfig.city = angular.extend(angular.extend({},layerConfig.state), {
        'mouseenter' : function(data, path) {
          if (!highlighted.isHighlighted(data.code)) {
            return;
          }
          path.toFront();
          var zoomRatio = 2.5 / citySizeRatio(data.population);
          var animAttrs = {
              'transform' : 's' + zoomRatio,
              'stroke-width' : zoomRatio * STROKE_WIDTH
            };
          path.animate(animAttrs, ANIMATION_TIME_MS / 2, '>');
        },
        'mouseleave' : function(data, path) {
          var animAttrs = {
              'transform' : '',
              'stroke-width' : STROKE_WIDTH
            };
          path.animate(animAttrs, ANIMATION_TIME_MS / 2, '>');
        }
      });

      layerConfig.lake = angular.copy(layerConfig.state, {});
      layerConfig.lake.styles.fill = function(d) {
        var flashcard = config.places && config.places[d.code];
        return flashcard && flashcard.practiced ?
          colorScale(flashcard.prediction).hex() :
          colors.WATER_COLOR;
      };
      layerConfig.sea = angular.copy(layerConfig.lake, {});

      layerConfig.reservoir = angular.copy(layerConfig.river, {
        'mouseenter' : function(data, path) {
          var zoomRatio = 4;
          var animAttrs = { 'stroke-width' : zoomRatio * RESERVOIR_WIDTH };
          path.animate(animAttrs, ANIMATION_TIME_MS / 2, '>');
        },
        'mouseleave' : function(data, path) {
          var animAttrs = { 'stroke-width' : RESERVOIR_WIDTH };
          path.animate(animAttrs, ANIMATION_TIME_MS / 2, '>');
        }
      });
      layerConfig.reservoir.styles['stroke-width'] = RESERVOIR_WIDTH;
      layerConfig.reservoir.styles.fill = layerConfig.lake.styles.fill;

      return layerConfig;
    };
  }])

  .factory('initLayers', ['getLayerConfig', 'stateAlternatives', function(getLayerConfig, stateAlternatives) {

    function _hideLayer(layer){
      var paths = layer ? layer.getPaths({}) : [];
      angular.forEach(paths, function(path) {
        path.svgPath.hide();
      });
    }

    return function(map, config) {
      var layersConfig = getLayerConfig(config);
      var layersArray = [];
      for (var i in layersConfig) {
        map.addLayer(i, layersConfig[i]);
        var l = map.getLayer(i);
        if (l && l.id != 'bg' && l.id != 'border') {
          layersArray.push(l);
          _hideLayer(l);
        }
      }
      var that = {
        hideLayer : function(layer) {
          _hideLayer(layer);
        },
        showLayer : function(layer) {
          var paths = layer ? layer.getPaths({}) : [];
          angular.forEach(paths, function(path) {
            path.svgPath.show();
          });
        },
        getLayerBySlug: function(slug) {
          var ret;
          angular.forEach(layersArray, function(l) {
            if (l.id == slug) {
              ret = l;
            }
          });
          return ret;
        },
        getAll : function(){
          return layersArray;
        },
        getConfig : function(layer){
          return layersConfig[layer.id];
        },
        getStateAlternative : function() {
          var ret;
          angular.forEach(stateAlternatives.concat(['state']), function(alternative){
            l = that.getLayerBySlug(alternative);
            if (l) {
              ret = l;
            }
          });
          return ret;
        }
      };
      return that;
    };
  }])

  .factory('mapFunctions', ['$timeout', '$', 'stateAlternatives', 'bboxCache',
      function($timeout, $, stateAlternatives, bboxCache){
    var that = {
      getZoomRatio : function(placePath) {
        if (!bboxCache.get(placePath.data.code)) {
          bboxCache.set(placePath.data.code, placePath.svgPath.getBBox());
        }
        bboxCache.setKey(placePath.svgPath.node.id, placePath.data.code);
        var bbox = placePath.svgPath.getBBox();
        var bboxArea = bbox.width * bbox.height;
        var zoomRatio = Math.max(4, 140 / Math.sqrt(bboxArea));
        return zoomRatio;
      },
      initMapZoom : function(paper) {
        var panZoom = paper.panzoom({});
        panZoom.enable();

        $('#zoom-in').click(function(e) {
          panZoom.zoomIn(1);
          e.preventDefault();
        });

        $('#zoom-out').click(function(e) {
          panZoom.zoomOut(1);
          e.preventDefault();
        });
        return panZoom;
      },
      getHighlightAnimationAttributes : function(placePath, layer, origStroke, color) {
        var animAttrs = { };
        if (color) {
          if (layer.id == 'river') {
            animAttrs.stroke = color;
          } else if (layer.id == 'reservoir') {
            animAttrs.stroke = color;
            animAttrs.fill = color;
          } else {
            animAttrs.fill = color;
          }
        }
        return animAttrs;
      },
      isStateAlternative : function (id) {
        var ret;
        angular.forEach(stateAlternatives.concat(['state']), function(alternative){
          if (id == alternative) {
            ret = alternative;
          }
        });
        return ret;
      }
    };
    return that;
  }])

  .factory('getTooltipGetter', ['$filter', 'colorScale', 'gettextCatalog',
      function($filter, colorScale, gettextCatalog){

    function getAttributes(d, place) {
        return (d.population ? gettextCatalog.getString('Počet obyvatel') + ': ' +
          '<span class="badge badge-default">' +
            $filter('number')(d.population) +
          '</span><br><br>' : '') +
        (place['state-by-city'] ? gettextCatalog.getString('Hlavní město') + ': ' +
          '<span class="label label-default">' +
           place['state-by-city']  +
          '</span><br><br>' : '') +
        (place['city-by-state'] ? gettextCatalog.getString('Stát') + ': ' +
          '<span class="label label-default">' +
           place['city-by-state']  +
          '</span><br><br>' : '');
    }

    return function(places) {
      return function(d) {
        var place = places && places[d.code];
        var name = ( place ?
          '<div class="label label-default label-title">' +
            '<i class="flag-' + d.code + '"></i> ' +
            place.term.name +
            '</div>' :
          '');
        var description = (place && place.practiced ?
          '<div>' +
            gettextCatalog.getString('Odhad znalosti') + ': ' +
              '<span class="badge badge-default">' +
                '<i class="color-indicator" style="background-color :' +
                colorScale(place.prediction).hex() + '"></i>' +
                Math.round(10 * place.prediction) + ' / 10 ' +
              '</span><br><br>' +
            getAttributes(d, place) +
          '</div>' :
            (place && place.summary ?
            '' :
            '<br>' + gettextCatalog.getString('Neprocvičováno') + '<br><br>'));
        return [
          name + description,
          place ? place.name : ''
        ];
      };
    };
  }])

  .service('citySizeRatio', function(){
    var min_pop_ratios = [
      [5000000, 1.8],
      [1000000, 1.4],
      [500000, 1.2],
      [100000, 1],
      [30000, 0.8],
      [0, 0.6]
    ];

    return function (population) {
      for (var i = 0; i < min_pop_ratios.length; i++) {
        if (population > min_pop_ratios[i][0]) {
          return min_pop_ratios[i][1];
        }
      }
      return min_pop_ratios[2][1];
    };
  })

  .factory('highlighted', function(){
    var places = [];
    return {
      clear: function() {
        places = [];
      },
      isHighlighted: function(code) {
        return places.length === 0 || places.indexOf(code) != -1;
      },
      setHighlighted: function(codes) {
        places = angular.copy(codes);
      }
    };
  })

  .service('getMapResizeFunction', ['$', 'citySizeRatio', '$window',
      function($, citySizeRatio, $window){

    function getNewHeight(mapAspectRatio, isPractise, holderInitHeight) {
      angular.element('#ng-view').removeClass('horizontal');
      var newHeight;
      if (isPractise) {
        var screenAspectRatio = $window.innerHeight / $window.innerWidth;
        if (screenAspectRatio < mapAspectRatio) {
          angular.element('#ng-view').addClass('horizontal');
          newHeight = $window.innerHeight;
        } else {
          var controlsHeight = $window.innerWidth > 767 ? 290 : 150;
          newHeight = $window.innerHeight - controlsHeight;
        }
      } else if (holderInitHeight / mapAspectRatio >= $window.innerWidth) {
        newHeight = Math.max(holderInitHeight / 2, mapAspectRatio * $window.innerWidth);
      } else {
        newHeight = holderInitHeight;
      }
      return newHeight;
    }

    var initCitySizes = {};

    function setCitiesSize(layer, currZoom) {
      if (!layer) {
        return;
      }
      currZoom = currZoom || 0;
      var paths = layer.paths;
      angular.forEach(paths, function(path) {
        var initSize = initCitySizes[path.data.code] || path.svgPath.attr("r");
        initCitySizes[path.data.code] = initSize;
        var newRadius = initSize * citySizeRatio(path.data.population) * (1 - (currZoom * 0.08));
        path.svgPath.attr({r: newRadius});
      });
    }

    return function(m, holder, practice) {
      var holderInitHeight = holder.height();
      var panZoom = m.panZoom;
      var map = m.map;
      var mapAspectRatio = map.viewAB.height / map.viewAB.width;

      return function () {
        var newHeight = getNewHeight(mapAspectRatio, practice, holderInitHeight);
        holder.height(newHeight);
        map.resize();
        if (panZoom) {
          panZoom.zoomIn(1);
          panZoom.zoomOut(1);
          panZoom.onZoomChange(function(currZoom) {
            setCitiesSize(map.getLayer("city"), currZoom);
          });
        }
        if (practice) {
          $("html, body").animate({ scrollTop: ($('.navbar').height() - 8) + "px" });
        }
        setCitiesSize(map.getLayer("city"));
      };
    };
  }])

  .service('singleWindowResizeFn', ['$window', function($window){
    var fn = function(){};
    angular.element($window).bind('resize', function() {
      fn();
    });
    return function(newFn) {
      fn = newFn;
    };
  }])

  .factory('mapControler', ['$', '$K', 'mapFunctions', 'initLayers', '$filter',
      'getTooltipGetter', 'highlighted',
      function($, $K, mapFunctions, initLayers, $filter, getTooltipGetter, highlighted) {
    $.fn.qtip.defaults.style.classes = 'qtip-dark';

    return function(mapCode, showTooltips, holder, callback) {
      var config = { state : [] };
      var layers;
      var _placesByTypes;

      config.showTooltips = showTooltips;
      config.isPractise = !showTooltips;
      config.places = [];

      var myMap = {
        map :  $K.map(holder),
        panZoom : undefined,
        onClick : function(clickFn) {
          config.click = function(code) {
            if (!myMap.panZoom.isDragging()) {
              clickFn(code);
            }
          };
        },
        highlightItems : function(states, color, zoomRatio) {
          var state = states.pop();
          var layer = this.getLayerContaining(state);
          var placePath = layer ? layer.getPaths({ code : state })[0] : undefined;
          if (placePath) {
            placePath.svgPath.toFront();
            var origStroke = layers.getConfig(layer).styles['stroke-width'];
            var animAttrs = mapFunctions.getHighlightAnimationAttributes(placePath, layer,
                origStroke, color);
            placePath.svgPath.animate(animAttrs, ANIMATION_TIME_MS / 2, '>', function() {
              myMap.highlightItems(states, color);
            });

            if (!bboxCache.get(placePath.data.code)) {
              bboxCache.set(placePath.data.code, placePath.svgPath.getBBox());
            }
            bboxCache.setKey(placePath.svgPath.node.id, placePath.data.code);
            var bbox = placePath.svgPath.getBBox();
            var highlightEllipse = myMap.map.paper.circle(
              bbox.x + bbox.width / 2,
              bbox.y + bbox.height / 2,
              Math.max(bbox.width, bbox.height) / 2);
            highlightEllipse.attr({
              'stroke-width' : STROKE_WIDTH * 4,
              'stroke' : color,
              'transform' : 's ' + mapFunctions.getZoomRatio(placePath),
            });
            var ellAnimAttrs = {
              transform : '',
            };
            highlightEllipse.animate(ellAnimAttrs, ANIMATION_TIME_MS, '>', function() {
              highlightEllipse.remove();
            });
          } else if (states.length > 0) {
            myMap.highlightItems(states, color);
          }
        },
        highlightItem : function(state, color, zoomRatio) {
          myMap.highlightItems([state], color, zoomRatio);
        },
        clearHighlights : function() {
          highlighted.clear();
          angular.forEach(layers.getAll(), function(layer) {
            layer.style(layers.getConfig(layer).styles);
            layers.showLayer(layer);
          });
        },
        updateItems : function(placesByTypes) {
          if (layers === undefined) {
            _placesByTypes = placesByTypes;
            return;
          }
          angular.forEach(placesByTypes, function(type) {
            var l = layers.getLayerBySlug(type.identifier);
            if (type.hidden) {
              layers.hideLayer(l);
            } else {
              layers.showLayer(l);
            }
          });

          var places = $filter('StatesFromPlaces')(placesByTypes);
          config.places = places;
          angular.forEach(layers.getAll(), function(layer) {
            var layerConfig = layers.getConfig(layer);
            layer.style('fill', layerConfig.styles.fill);
            layer.style('stroke', layerConfig.styles.stroke);
            if (config.showTooltips) {
              layer.tooltips(getTooltipGetter(places));
            }
          });
        },
        showSummaryTooltips : function(questions) {
          var places = {};
          questions.map(function(q){
            places[q.description] = {
              'code' : q.description,
              'term' : q.term,
              'summary' : true,
            };
          });
          angular.forEach(layers.getAll(), function(layer) {
            layer.tooltips(getTooltipGetter(places));
          });
        },
        getLayerContaining : function(placeCode) {
          var ret;
          angular.forEach(layers.getAll(), function(layer) {
            if (layer.getPaths({ code : placeCode }).length >= 1) {
              ret = layer;
            }
          });
          return ret;
        },
        showLayerContaining : function(placeCode) {
          var l = myMap.getLayerContaining(placeCode);
          layers.showLayer(l);
          if (l && l.id == "city") {
            layers.showLayer(layers.getStateAlternative());
          } else if (l && l.id == "reservoir") {
            layers.showLayer(layers.getLayerBySlug('river'));
          }
        },
        highLightLayer : function(layer) {
          angular.forEach(layers.getAll(), function(l) {
            if (l == layer || 
                (layer && layer.id == 'city' &&
                  mapFunctions.isStateAlternative(l.id)) ||
                (layer && layer.id == 'reservoir' && l.id == 'river')) {
              layers.showLayer(l);
              if (layer && layer.id == 'reservoir' && l.id == 'river') {
                reservoirRiverHack(l);
              }
            }
            else {
              layers.hideLayer(l);
            }
          });
        },
        hideLayers : function() {
          angular.forEach(layers.getAll(), function(l) {
            layers.hideLayer(l);
          });
        },
        placeToFront : function(placeCode) {
          angular.forEach(layers.getAll(), function(layer) {
            var place = layer.getPaths({ code : placeCode })[0];
            if (place) {
              place.svgPath.toFront();
            }
          });
        }
      };

      function reservoirRiverHack(l) {
        l.style('stroke-width', STROKE_WIDTH);
        var hoverFn = function(data, path) {
          path.animate({
            'stroke-width' : STROKE_WIDTH,
            'cursor' : 'default',
          }, ANIMATION_TIME_MS, '>');
        };
        l.on('mouseenter', hoverFn);
        l.on('mouseleave', hoverFn);
      }

      myMap.map.loadCSS(hash('/static/dist/css/map.css'), function() {
        myMap.map.loadMap(hash('/static/map/' + mapCode + '.svg'), function() {
          highlighted.clear();
          layers = initLayers(myMap.map, config);
          if (_placesByTypes !== undefined) {
            myMap.updateItems(_placesByTypes);
          }
          myMap.panZoom = mapFunctions.initMapZoom(myMap.map.paper);
          callback(myMap);
        });
      });
      return myMap;
    };
  }]);
