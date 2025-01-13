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
my $cgid = $obj_cgi->param('gid');
my $clid = $obj_cgi->param('lid');
my $ret = {};
my $sth;

my $tid;
if (defined($cfid)) {
  $sth = $dbh->prepare('SELECT * FROM files WHERE fid = ?');
  $sth->execute($cfid);
  if ($sth->rows != 1) {
    $obj_cgi->send_error(503, 'fid not found');
    exit;
  }
  $ret->{'info'} = $sth->fetchrow_hashref();
} elsif (defined($cgid)) {
  $sth = $dbh->prepare('SELECT * FROM labels WHERE gid = ?');
  $sth->execute($cgid);
  if ($sth->rows != 1) {
    $obj_cgi->send_error(503, 'gid not found');
    exit;
  }
  my $cur = $sth->fetchrow_hashref();
  $tid = $cur->{'tid'};
  $ret->{'info'} = {};
  $ret->{'info'}->{'name'} = $cur->{'name'};
  $ret->{'info'}->{'memo'} = $cur->{'memo'};
} elsif (defined($clid)) {
  $sth = $dbh->prepare('SELECT * FROM labels WHERE lid = ?');
  $sth->execute($clid);
  if ($sth->rows != 1) {
    $obj_cgi->send_error(503, 'lid not found');
    exit;
  }
  $tid = $cur->{'tid'};
  $ret->{'info'} = {};
  $ret->{'info'}->{'name'} = $cur->{'name'};
  $ret->{'info'}->{'memo'} = $cur->{'memo'};
  if (defined($cur->{'gid'})) { $ret->{'info'}->{'type'} = 'group'; }
  else { $ret->{'info'}->{'type'} = 'label'; }
  # file info
  $sth = $dbh->prepare('SELECT * FROM files WHERE gid = ?');
  $sth->execute($clid);
  $ret->{'files'} = [];
  my %garr;
  my $gsth = $dbh->prepare('SELECT * FROM labels WHERE lid = ?');
  while (my $cf = $sth->fetchrow_hashref) {
    delete $cf->{'tid'};
    if (exists($garr{$cf->{'gid'}})) {
      $cf->{'gid'} = $garr{$cf->{'gid'}};
    } else {
      $gsth->execute($cf->{'gid'});
      my $cur = $gsth->fetchrow_hashref();
      $garr{$cur->{'gid'}} = $cur;
    }
    push(@{$ret->{'files'}}, $cf);
  }
  # gen group name -> memo
  $ret->{'groups'} = {};
  foreach my $cid (keys(%garr)) {
    $ret->{'groups'}->{$garr{$cid}->{'name'}} = $garr{$cid}->{'memo'};
  }
} else {
  $obj_cgi->send_error(503, 'invalid parameter');
  exit;
}

$sth = $dbh->prepare('SELECT * FROM tenants WHERE tid = ?');
$sth->execute($tid);
if ($sth->rows != 1) {
  $obj_cgi->send_error(503, 'invalid tenant'); # should not happen...
  exit;
}
my $cv = $sth->fetchrow_hashref();
$ret->{'tenant'} = {};
$ret->{'tenant'}->{'name'} = $cv->{'name'};
$ret->{'tenant'}->{'memo'} = $cv->{'memo'};

if (defined($cgid) && (defined($cginfo->{'redirect'}) || ($cginfo->{'noup'} != 0))) {
  $obj_cgi->send_error(503, 'upload closed'):
  exit;
}

print $obj_cgi->header(200);
print to_json(\%$ret);

exit;
