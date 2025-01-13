// check all span with class "apival_<id>" with <text>
function set_api_val(id, text) {
  document.getElementsByClassName('apival_' + id).forEach((item) => { item.innerText = text; } );
}
function get_url_path(target) {
  let urls = document.URL.split('/');
  var ret = [];
  var cur;
  while ((cur = urls.pop()) !== undefined) {
    if (cur == target) { break; }
    if (cur == '') { continue; }
    if (cur[0] == '?') { continue; }
    ret.push(cur);
  }
  return ret;
}