#! /usr/bin/perl

use strict;
use lib '../';

use JSON;
use Encode;

use PNAPI::Constants;
use PNAPI::Config;
use PNAPI::CGI;
use PNAPI::DB;
use PNAPI::Utils;

my $obj_cgi = new PNAPI::CGI;
my $obj_config = new PNAPI::Config;
my $obj_db = new PNAPI::DB;
my $dbh = $obj_db->dbh();

if ($obj_cgi->request_method() ne 'POST') {
  $obj_cgi->send_error(503, 'not POST');
  exit;
}

my $postdata = $obj_cgi->param('POSTDATA');
utf8::encode($postdata);
my $cdat = decode_json $postdata;

my $sth;
my $ret = {};

# check access
my $is_ok = 0;
if (defined $obj_cgi->cookie($cdat->{'tid'})) {
  $sth = $dbh->prepare('SELECT * FROM tenants WHERE tid = ? AND adminkey = ?');
  $sth->execute($cdat->{'tid'}, $obj_config->secret_to_int($obj_cgi->cookie($cdat->{'tid'})));
  if ($sth->rows > 0) { $is_ok = 1; }
}
if ($is_ok == 0) {
  $obj_cgi->send_error(503, 'invalid parameter');
  exit;
}

$sth = $dbh->prepare('SELECT * FROM labels WHERE tid = ? AND name = ?');
$sth->execute($cdat->{'tid'}, $cdat->{'name'});
if ($sth->rows > 0) {
  $obj_cgi->send_error(503, 'duplicated name');
  exit;
}

# gen UUID
my $ids;
if ($cdat->{'mode'} eq 'group') { $ids = PNAPI::Utils::generate_id(2); }
else { $ids = PNAPI::Utils::generate_id(1); }
$sth = $dbh->prepare('SELECT * FROM labels WHERE lid = ? OR gid = ?');
foreach my $cid (@$ids) {
  $sth->execute($cid, $cid);
  if ($sth->rows > 0) {
    $obj_cgi->send_error(503, 'id generation failed');
    exit;
  }
}

my $nrow;
$sth = $dbh->prepare('INSERT INTO labels (tid, lid, gid, name, memo) VALUES (?, ?, ?, ?, ?)');
if ($cdat->{'mode'} eq 'group') { $nrow = $sth->execute($cdat->{'tid'}, $ids->[0], $ids->[1], $cdat->{'name'}, $cdat->{'memo'}); }
else { $nrow = $sth->execute($cdat->{'tid'}, $ids->[0], undef, $cdat->{'name'}, $cdat->{'memo'}); }
if (! defined($nrow)) {
  $obj_cgi->send_error(503, 'add failed');
  exit;
}

$sth = $dbh->prepare('SELECT * FROM labels WHERE tid = ? AND name = ?');
$sth->execute($cdat->{'tid'}, $cdat->{'name'});
if ($sth->rows != 1) {
  $obj_cgi->send_error(503, 'registration error');
  exit;
}
my $ref = $sth->fetchrow_hashref();
$ret->{$ref->{'name'}} = $ref;

print $obj_cgi->header(200);
print to_json(\%$ret);

exit;
