#! /usr/bin/perl

use strict;
use lib '../';

use JSON;

use PNAPI::Constants;
use PNAPI::Config;
use PNAPI::CGI;
use PNAPI::DB;

my $obj_cgi = new PNAPI::CGI;
my $obj_config = new PNAPI::Config;
my $obj_db = new PNAPI::DB;
my $dbh = $obj_db->dbh();

# check lid or fid
my $cfid = $obj_cgi->param('fid');
my $clid = $obj_cgi->param('lid');
my $ret = {};
my $sth;

if (defined($cfid)) {
  $sth = $dbh->prepare('SELECT * FROM files WHERE fid = ?');
  $sth->execute($cfid);
  if ($sth->rows != 1) {
    $obj_cgi->send_error(503, 'fid not found');
    exit;
  }
  $ret->{'info'} = $sth->fetchrow_hashref();
} elsif (defined($clid)) {
  $sth = $dbh->prepare('SELECT * FROM labels WHERE lid = ? OR gid = ?');
  $sth->execute($clid);
  if ($sth->rows != 1) {
    $obj_cgi->send_error(503, 'lid not found');
    exit;
  }
  my $cur = $sth->fetchrow_hashref();
  $ret->{'info'} = {};
  $ret->{'info'}->{'tid'} = $cur->{'tid'};
  $ret->{'info'}->{'name'} = $cur->{'name'};
  $ret->{'info'}->{'memo'} = $cur->{'memo'};
} else {
  $obj_cgi->send_error(503, 'invalid parameter');
  exit;
}

$sth = $dbh->prepare('SELECT * FROM tenants WHERE tid = ?');
$sth->execute($ret->{'info'}->{'tid'});
if ($sth->rows != 1) {
  $obj_cgi->send_error(503, 'invalid tenant'); # should not happen...
  exit;
}
my $cv = $sth->fetchrow_hashref();
$ret->{'tenant'} = {};
$ret->{'tenant'}->{'tid'} = $cv->{'tid'};
$ret->{'tenant'}->{'name'} = $cv->{'name'};
$ret->{'tenant'}->{'memo'} = $cv->{'memo'};

print $obj_cgi->header(200);
print to_json(\%$ret);

exit;
