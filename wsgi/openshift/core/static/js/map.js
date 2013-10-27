var GOOD = "#0d0";
var BAD = "#ff0000";
var NEUTRAL = "#bbb";
var HOLDER = '#map-holder';

var times = {};
function profile(message) {
    if (!times[message]) {
        times[message] = new Date().getTime();
    } else {
        time = new Date().getTime() - times[message];
        console.log(message, time, "ms");
        times[message] = undefined;
    }
}

function initMap(config, callback) {

    var map = $K.map(HOLDER);
    var HOLDER_INIT_HEIGHT = $(HOLDER).height();
    
    var resize = function() {
        var c = $(HOLDER);
        var ratio = map.viewAB.height / map.viewAB.width;
        if (c.height() / ratio >= $(window).width()) {
            c.width($(window).width());
            c.height(ratio * c.width());
        } else {
            c.height(HOLDER_INIT_HEIGHT);
            c.width(c.height() / ratio);
        }
        map.resize();
    };

    $(window).resize(resize);

    $.fn.qtip.defaults.style.classes = 'qtip-dark';

    var scale = chroma.scale([BAD, "#ff4500", "#ffa500", "#ffff00", GOOD]);

    var isPracticeView = config.click != undefined;

    var statesLayerConfig = {};
    statesLayerConfig.styles = {
        'fill' : function(d) {
            var state = config.states && config.states[d.name];
            return state ? (scale(state.skill).brighten((1 - state.certainty) * 80).hex()) : '#fff';
        },
        'stroke-width' : 1
    }
    if (config.click) {
        clickFn = function(data, path, event) {
            config.click(data.name);
        }
        statesLayerConfig.click = clickFn
        statesLayerConfig.styles['stroke-width'] = 1.5;
    }
    if (config.showTooltips) {
        statesLayerConfig.tooltips = function(d) {
            var state = config.states && config.states[d.name];
            var name = ( state ? '<span class="label">' + '<i class="flag-' + d.name + '"></i> ' + state.name + '</span>' : '<br>Neprozkoumané území<br><br>');
            var description = state ? '<div> <i class="color-indicator" style="background-color:' + scale(state.skill).hex() + '"></i> Úspěšnost: ' + Math.round(100 * state.skill) + '%</div>' : "";
//             TODO: find a better word than "Jistota"
//            description += ( state ? '<div> <i class="color-indicator" style="background-color:' + chroma.color("#000").brighten((1 - state.certainty) * 130).hex() + '"></i>  Jistota: ' + Math.round(100 * state.certainty) + '%</div> ' : "");

            return [name + description, config.states[d.name] ? config.states[d.name].name : ""];
        }
    }

    map.loadCSS(Hash('static/css/map.css'), function() {
        map.loadMap(Hash('static/map/' + config.name + '.svg'), function() {
            profile("Map loading takes:");

            profile("Add layer takes:");
            map.addLayer('states', statesLayerConfig);
            profile("Add layer takes:");
            profile("resize takes:");
            resize();
            profile("resize takes:");
            
            /*
            var layer = map.getLayer('states');
            var statePaths = layer.getPaths({});
            var animation_ms = 500;
            for (var i = statePaths.length - 1; i >= 0; i--){
              var state = statePaths[i];
              var bbox = state.svgPath.getBBox()
              if (bbox.width < 10 || bbox.height < 10) {
                  var c = layer.paper.circle( bbox.x + bbox.width/2, bbox.y + bbox.height/2, 10);
                  c.attr({"stroke-width": 3, stroke: "red", fill: "transparent"})
                  c.click(function(event){
                      var name = state.data.name
                      var transform = "S2"//, 2, "+ event.x-bbox.x + ", -" + event.y-bbox.y;
                      state.svgPath.animate({transform: transform}, animation_ms/2, "<");
                      console.log(name)
                      console.log(event)
                  })
                  c.hover(function(){
                      this.attr({stroke: "red"});
                  }, function(){
                      this.attr({stroke: "red"});
                  })
              }
            };*/
           
            
            callback && callback();

            $('#map-holder').find(".loading-indicator").hide();
            
            profile("Map loading takes:");
        })
    });
    function getZoomRatio(bboxArea) {
        if (bboxArea > 10000) {
            return 1.2;
        } else if (bboxArea > 1000) {
            return 2.5;
        }
        return 4;
    }

    var myMap = {
        map : map,
        highlightStates : function(states, color, zoomRatio) {
            var animation_ms = 500;
            var layer = map.getLayer('states');
            var state = states.pop();
            var statePath = layer.getPaths({ name: state })[0];
            if (statePath) {
                statePath.svgPath.toFront();
                var bbox = statePath.svgPath.getBBox()
                var bboxArea = bbox.width * bbox.height;
                var zoomRatio = zoomRatio || getZoomRatio(bboxArea);
                var aminAttrs = {transform: "s"+zoomRatio, 'stroke-width': zoomRatio};
                if (color) {
                    aminAttrs['fill'] = color;
                }
                statePath.svgPath.animate(aminAttrs, animation_ms/2, ">", function(){
                    if (bboxArea > 100 || color != NEUTRAL) {
                        statePath.svgPath.animate({transform: "", 'stroke-width': 1}, animation_ms/2, "<");
                    }
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
            var layer = map.getLayer('states');
            layer.style({'fill': "#fff", transform: "", 'stroke-width': 1});
        },
        updateStates : function(states) {
            var time = new Date().getTime();
            config.states = states;
            var statesLayer = map.getLayer('states')
            if (statesLayer) {
                statesLayer.style('stroke', statesLayerConfig.styles.stroke);
                statesLayer.style('stroke-width', statesLayerConfig.styles['stroke-width'], 0.1);
                statesLayer.style('fill', statesLayerConfig.styles.fill, 2);
                statesLayer.tooltips(statesLayerConfig.tooltips);
            }
            time = new Date().getTime() - time;
            console.log("updateStates takes:", time, "ms");
        }
    }
    return myMap;
}
