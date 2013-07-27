
var GOOD = "#0d0";
var BAD = "#ff0000";
var NEUTRAL = "#bbb";

function initMap(config, callback) {

    var map = $K.map('#map-holder'); 

        var resize = function() {
            var c = $('#map-holder');
            var ratio = map.viewAB.width / map.viewAB.height;
            c.height( c.width() / ratio );
            map.resize();
        };

        $(window).resize(resize);

    $.fn.qtip.defaults.style.classes = 'qtip-dark';

    var scale = chroma.scale([BAD, "#ff4500", "#ffa500", "#ffff00", GOOD]);
    
    map.loadCSS('static/css/map.css', function() {
        map.loadMap('static/img/'+ config.name + '.svg', function() {

            var bgLayer = {
                name: 'bg'
            }

            var statesLayer = { 
	            styles : {
	                'fill' : function(d) { 
	                    return config.states && config.states[d.name] ? (scale(config.states[d.name].skill).hex()) :'#fff';
	                    }
	            }
	        }
            if (config.click) {
                clickFn = function(data, path, event) {
                    config.click(data.name);
                }
                statesLayer.click = clickFn 
                bgLayer.click = clickFn 
            }
            if (config.showTooltips) {
                statesLayer.tooltips = function(d) {
                    var name = (config.states[d.name] ? '<span class="label">' + '<i class="flag-'+d.name+'"></i> ' + config.states[d.name].name + '</span>' : '<br>Neprozkoumané území<br><br>'); 
                    var description = config.states[d.name] ? '<br><br> Úroveň znalosti: ' + Math.round(100 * config.states[d.name].skill) + '%' : "";

                    return [name + description, ''];
                }
            }
            map.addLayer('states', bgLayer)
            map.addLayer('states', statesLayer )

            if (!config.click) {
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

           /* 
            .addLayer('states', {
                name: 'bgback'
            });

            map.addFilter('oglow', 'glow', {
                size: 10,
                color: '#988',
                strength: 1,
                inner: false
            });
            map.getLayer('bgback').applyFilter('oglow');
            map.addFilter('myglow', 'glow', {
                size: 20,
                color: '#945C1B',
                inner: true
            });
            map.getLayer('bg').applyFilter('myglow');

            map.addFilter('myglow', 'glow', { size: 9, color: '#945C1B', inner: true });
            map.getLayer('bg').applyFilter('myglow');
            */
            resize();
            callback && callback();
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
        }
    }
    return myMap; 
}

