var GOOD = "#0d0";
var BAD = "#ff0000";
var NEUTRAL = "#bbb";
var HOLDER = '#map-holder';

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

    var statesLayer = {};
    statesLayer.styles = {
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
        statesLayer.click = clickFn
        statesLayer.styles['stroke-width'] = 1.5;
    }
    if (config.showTooltips) {
        statesLayer.tooltips = function(d) {
            var state = config.states && config.states[d.name];
            var name = ( state ? '<span class="label">' + '<i class="flag-' + d.name + '"></i> ' + state.name + '</span>' : '<br>Neprozkoumané území<br><br>');
            var description = state ? '<div> <i class="color-indicator" style="background-color:' + scale(state.skill).hex() + '"></i> Znalost: ' + Math.round(100 * state.skill) + '%</div>' : "";
            description += ( state ? '<div> <i class="color-indicator" style="background-color:' + chroma.color("#000").brighten((1 - state.certainty) * 130).hex() + '"></i>  Jistota: ' + Math.round(100 * state.certainty) + '%</div> ' : "");

            return [name + description, config.states[d.name] ? config.states[d.name].name : ""];
        }
    }

    map.loadCSS('static/css/map.css', function() {
        map.loadMap('static/map/' + config.name + '.svg', function() {

            if (767 < $(window).width()) {
                map.addLayer('states', {
                    name : 'bg'
                });
                map.addFilter('outerglow', 'glow', {
                    size : 4,
                    color : '#333',
                    strength : 2,
                    inner : false
                });
                map.getLayer('bg').applyFilter('outerglow');
            }

            resize();
            map.addLayer('states', statesLayer);
            map.addLayer('cities', statesLayer);

            if (!isPracticeView) {
                map.addFilter('inner-state-glow', 'glow', {
                    size : 1,
                    strength : 1,
                    color : '#000',
                    opacity : 0.2,
                    inner : true
                });
                map.getLayer('states').applyFilter('inner-state-glow');
            }
            resize();
            callback && callback();

            $('#map-holder').find(".loading-indicator").hide();
        })
    });

    var myMap = {
        map : map,
        highlightStates : function(states, color, zoomRatio) {
            var animation_ms = 500;
            var zoomRatio = zoomRatio || 4;
            var layer = map.getLayer('states');
            var state = states.pop();
            var statePath = layer.getPaths({ name: state })[0];
            if (statePath) {
                statePath.svgPath.toFront();
                var aminAttrs = {transform: "s"+zoomRatio, 'stroke-width': zoomRatio};
                if (color) {
                    aminAttrs['fill'] = color;
                }
                var bbox = statePath.svgPath.getBBox()
                statePath.svgPath.animate(aminAttrs, animation_ms/2, ">", function(){
                    if ((bbox.width > 10 && bbox.height > 10) || color != NEUTRAL) {
                        statePath.svgPath.animate({transform: "", 'stroke-width': 1}, animation_ms/2, "<");
                    }
                    myMap.highlightStates(states, color);
                });
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
            if (!jQuery.isEmptyObject(config.states)) {
                var highlights = [];
                for (var code in states) {
                    var oldState = config.states[code]
                    states[code].diff = states[code].skill - (oldState && oldState.skill) || 0;
                    if (states[code].diff != 0) {
                        highlights.push(code);
                    }
                }
                myMap.highlightStates(highlights)
            }
            config.states = states;
            map.getLayer('states').style('stroke', statesLayer.styles.stroke);
            map.getLayer('states').style('stroke-width', statesLayer.styles['stroke-width'], 0.1);
            map.getLayer('states').style('fill', statesLayer.styles.fill, 2);
            map.getLayer('states').tooltips(statesLayer.tooltips);
        }
    }
    return myMap;
}
