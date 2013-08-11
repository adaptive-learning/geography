
var GOOD = "#0d0";
var BAD = "#ff0000";
var NEUTRAL = "#bbb";

function initMap(config, callback) {
	
    var map = $K.map('#map-holder'); 

        var resize = function() {
            var c = $('#map-holder');
            var ratio =  map.viewAB.height / map.viewAB.width;
            c.width( c.height() / ratio );
            map.resize();
        };

        $(window).resize(resize);

    $.fn.qtip.defaults.style.classes = 'qtip-dark';

    var scale = chroma.scale([BAD, "#ff4500", "#ffa500", "#ffff00", GOOD]);
    
    var statesLayer = {};
    
    map.loadCSS('static/css/map.css', function() {
        map.loadMap('static/img/'+ config.name + '.svg', function() {
        	var isPracticeView = config.click != undefined;

            var bgLayer = {
                name: 'bg'
            }

            statesLayer.styles = {
                'fill' : function(d) { 
                	var state = config.states && config.states[d.name];
                    return state ? (scale(state.skill).brighten((1-state.certainty)*80).hex()) :'#fff';
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
                    var name = (state ? '<span class="label">' + '<i class="flag-'+d.name+'"></i> ' + state.name + '</span>' : '<br>Neprozkoumané území<br><br>'); 
                    var description = state ? '<div> <i class="color-indicator" style="background-color:'+scale(state.skill).hex()+'"></i> Znalost: ' + Math.round(100 * state.skill) + '%</div>' : "";
                    description += (state ? '<div> <i class="color-indicator" style="background-color:'+chroma.color("#000").brighten((1-state.certainty)*130).hex()+'"></i>  Jistota: ' + Math.round(100 * state.certainty) + '%</div> ' : "");

                    return [name + description, config.states[d.name] ? config.states[d.name].name : ""];
                }
            }
            map.addLayer('states', bgLayer)
            resize();
            map.addLayer('states', statesLayer )

            if (!isPracticeView) {
	            map.addFilter('inner-state-glow', 'glow', {
	                size: 1,
	                strength: 1,
	                color: '#000',
	                opacity: 0.2,
	                inner: true
	            });
	            map.getLayer('states').applyFilter('inner-state-glow');
            }
            map.addFilter('outerglow', 'glow', {
                size: 4,
                color: '#333',
                strength: 2,
                inner: false
            });
            map.getLayer('bg').applyFilter('outerglow');

            resize();
            callback && callback();

        	$('#map-holder').find(".loading-indicator").hide();
        })
    })
    var myMap = {
        map: map,
        highlightState : function(state, color) {
            var color = color || NEUTRAL;
            var layer = map.getLayer('states');
            statePath = layer.getPaths({ name: state })[0];
            if (statePath) {
                statePath.svgPath.attr('fill', color);
            }
        },
        blink : function(state, count) {
            var count = count || 0;
            var that = this
            if (count < 6) {
                color = count % 2 == 0 ? "white" : NEUTRAL;
                that.highlightState(state, color);
                setTimeout(function(){
                    that.blink(state, ++count)
                }, 50)
            }
        },
        clearHighlights : function () {
            var layer = map.getLayer('states');
            layer.style('fill', "#fff");
        },
        updateStates : function(states) {
        	config.states = states;
        	map.getLayer('states').style('fill', statesLayer.styles.fill, 1);
        	map.getLayer('states').tooltips(statesLayer.tooltips);
		}
    }
    return myMap; 
}

