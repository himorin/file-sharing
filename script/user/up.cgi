#! /usr/bin/perl

use strict;
use lib '../';

use JSON;
use Encode;
use POSIX;

use PNAPI::Constants;
use PNAPI::Config;
use PNAPI::CGI;
use PNAPI::DB;
use PNAPI::Utils;

my $obj_cgi = new PNAPI::CGI;
my $obj_config = new PNAPI::Config;
my $obj_db = new PNAPI::DB;
my $dbh = $obj_db->dbh();
my $sth;
my $ret = {};

if ($obj_cgi->request_method() ne 'POST') {
  $obj_cgi->send_error(503, 'not POST');
  exit;
}

# options
my $c_gid = $obj_cgi->param('gid');
my $c_name = $obj_cgi->param('name');
my $c_memo = $obj_cgi->param('memo');
my $c_fsize = $obj_cgi->param('size');
my $c_fh = $obj_cgi->upload('target_file');
my $c_ext = $obj_cgi->param('target_file');
if (rindex($c_ext, '.') < 0) { $c_ext = 'dat'; }
else { $c_ext = substr($c_ext, rindex($c_ext, '.') + 1); }

# check gid
$sth = $dbh->prepare('SELECT * FROM labels LEFT JOIN tenants ON labels.tid = tenants.tid WHERE labels.gid = ?');
$sth->execute($c_gid);
if ($sth->rows != 1) {
  $obj_cgi->send_error(503, 'invalid gid');
  exit;
}
my $cginfo = $sth->fetchrow_hashref();
if (defined($cginfo->{'redirect'}) || ($cginfo->{'noup'} != 0)) {
  $obj_cgi->send_error(503, 'upload prohibited');
  exit;
}

my $fid = PNAPI::Utils::generate_id(1);
$sth = $dbh->prepare('INSERT INTO files (tid, gid, fid, name, mimetype, memo, size) VALUES (?, ?, ?, ?, ?, ?, ?)');
my $nrow = $sth->execute($cginfo->{'tid'}, $cginfo->{'lid'}, $fid[0], $c_name, $c_ext, $c_memo, $c_fsize);
if (! defined($nrow)) {
  $obj_cgi->send_error(503, 'id generation failed');
  exit;
}
$sth = $dbh->prepare('SELECT * FROM files WHERE fid = ?');
$sth->execute($fid);
if ($sth->rows != 1) {
  $obj_cgi->send_error(503, 'id registration failed');
  exit;
}
$ret = $sth->fetchrow_hashref();

my $rfname = $obj_config->GetHashFilename($fid[0], 0, $cginfo->{'tid'}, 1);
my $rfpath = substr($rfname, 0, rindex($rfname, '/'));
eval {
  File::Path::mkpath($rfpath);
};
open(ODAT, "> $rfname");
binmode(ODAT);
my $buf;
while (read($c_fh, $buf, 1024)) { print ODAT $buf; }
close(ODAT);

print $obj_cgi->header(200);
print to_json(\%$ret);

exit;

