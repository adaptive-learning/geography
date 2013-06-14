
var GOOD = "#26bf00";
var BAD = "#ff0000";
var ANIMAT_TIME = 200;
var BORDER_WIDTH = 0.5;

Raphael.fn.map = function(coastline, controller) {
    var coastline = paper.path(coastline);
    coastline.attr({"fill": "white", "stroke-width" : BORDER_WIDTH});
    
    var map = {
        coastline : coastline,
        states : paper.set(),
        addState : function (description) {
            var state = paper.state(description, controller);
            this.states.push(state);
        },
        highlightState : function (code, color) {
            this.states.forEach(function(state){
                if (state.code == code) {
                    state.highlight(color);
                }
            });
        },
        clearHighlights : function () {
            this.states.forEach(function(state){
                state.clearHighlights();
            });
        }
    }
    return map;

}
    var STATE_COLOR = "#f9f9f9";

Raphael.fn.state = function(description, controller) {
    var state = paper.path(description.border);
    state.code = description.code;
    state.attr({"fill": STATE_COLOR, "stroke-width": BORDER_WIDTH, "cursor": "pointer"});
    state.hover(function() {
        if (!this.highlighted) {
            this.attr({"fill": "#ddd"});
            if (controller.highlight) {
                controller.highlight(state.code, true);
                controller.$apply();
            }
        }
    }, function() {
        if (!this.highlighted) {
            this.attr({"fill": STATE_COLOR});
            if (controller.highlight) {
                controller.highlight(state.code, false);
                controller.$apply();
            }
        }
    })
    state.highlight = function (color) {
        var color = color || "#ccc"
        this.animate({"fill": color},ANIMAT_TIME);
        this.highlighted = true;
    }
    state.clearHighlights = function () {
        this.highlighted = false;
        this.animate({"fill": STATE_COLOR}, ANIMAT_TIME);
    }
    state.click(function () {
        if (controller.question.type == 0 && !controller.canNext) {
            controller.check(this.code);
            controller.$apply();
        }
    })
    return state;
}

function initMap(data, controller) {
    /*
    paper = Raphael("map-holder", 700, 500);
    paper.setViewBox(10, 10, 200, 190)
    var map = paper.map(data.coastline, controller);
    angular.forEach(data.states, function(state, key){
        map.addState(state);
    });
    return map;
    */
    var map = $K.map('#map-holder'); 

        var resize = function() {
            var c = $('#map-holder');
            var ratio = map.viewAB.width / map.viewAB.height;
            c.height( c.width() / ratio );
            map.resize();
        };

        $(window).resize(resize);

$.fn.qtip.defaults.style.classes = 'qtip-dark';

    map.loadMap('img/usa.svg', function() {
        map.addLayer('usa', {
                tooltips: function(d) {
                    return [d.name, ''];
                }
            }).addLayer('usa', {
                    name: 'bg'
                }).addLayer('usa', {
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
            resize();
    })
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

