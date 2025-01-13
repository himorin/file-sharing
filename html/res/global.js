// check all span with class "apival_<id>" with <text>
function set_api_val(id, text) {
  Array.from(document.getElementsByClassName('apival_' + id)).forEach((item) => { item.innerText = text; } );
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


// html generation
function htmlgen_disp_file_head(opt) {
  let hval = '<tr>';
  ['ファイル名', 'ファイルの説明', '拡張子', 'ファイルサイズ', 'アップロード日時', 'ラベル', opt, '備考'].forEach((item) => {
    hval += '<th>' + item + '</th>';
  });
  hval += '</tr>';
  return hval;
}
function htmlgen_disp_file_list(flist, opt, link) {
  let fhash = {};
  flist.forEach(item => {
    if (! (item['name'] in fhash)) { fhash[item['name']] = []; }
    fhash[item['name']].push(item);
  });
  let hval = '<tr>';
  Object.keys(fhash).sort().forEach((item) => {
    hval += '<td rowspan="' + fhash[item].length + '">' + item + '</td>';
    fhash[item].forEach(val => {
      hval += '<td>' + val['memo'] + '</td>';
      hval += '<td>' + val['mimetype'] + '</td>';
      hval += '<td>' + val['size'] + '</td>';
      hval += '<td>' + val['dt'] + '</td>';
      hval += '<td></td>'; // label
      if (link == null) { // opt
        hval += '<td></td>';
      } else {
        hval += '<td><a href="' + link + val['fid'] + '">' + opt + '</a></td>';
      }
      hval += '<td></td>'; // misc
      hval += '</tr><tr>';
    });
  });
  return hval.slice(0, -4);
}