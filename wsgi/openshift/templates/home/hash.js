;(function(window, undefined){
    var hashes = {{ hashes|safe }};
    function get_hash(filename) {
        return hashes[filename] ? hashes[filename] : "";
    }
    window.Hash = function(filename) {
        return filename + "?hash=" + get_hash(filename);
    }
})(window);
