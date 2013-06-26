
var GOOD = "#26bf00";
var BAD = "#ff0000";

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
    
    map.loadCSS('static/css/map.css', function() {
        map.loadMap('static/img/'+ config.name + '.svg', function() {
            var statesLayer = {styles: {
                    'fill' : '#fff',
                    'stroke-width': 0.2
                }
            }
            if (config.click) {
                statesLayer.click = function(data, path, event) {
                    config.click(data.name);
                }
            }
            if (config.showTooltips) {
                statesLayer.tooltips = function(d) {
                    var name = '<span class="label">' + (config.states[d.name] ? '<i class="flag-'+d.name+'"></i> ' + config.states[d.name]: d.name) + '</span>'; 
                    return [name, ''];
                }
            }
            map.addLayer('states', statesLayer )
           /* 
            .addLayer('states', {
                name: 'bg'
            })

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
            var color = color || "#ccc"
            var layer = map.getLayer('states');
            statePath = layer.getPaths({ name: state })[0];
            if (statePath) {
                statePath.svgPath.attr('fill', color);
            }
        },
        clearHighlights : function () {
            var layer = map.getLayer('states');
            layer.style('fill', "#fff");
        }
    }
    return myMap; 
}

function inputKeyUp(e) {
    e.which = e.which || e.keyCode;
    if(e.which == 13) {
        var ngView = $("#ng-view").children().scope();
        if (!ngView.select && ngView.question && ngView.question.type == 1) {
            $("select.select2").select2("open");
        }
        $('.btn-primary:not([disabled="disabled"])').click();
    }
}

