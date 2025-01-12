#! /usr/bin/perl

use strict;
use lib '../';

use JSON;
use Encode;

use PNAPI::Constants;
use PNAPI::Config;
use PNAPI::CGI;
use PNAPI::DB;

my $obj_cgi = new PNAPI::CGI;
my $obj_config = new PNAPI::Config;
my $obj_db = new PNAPI::DB;
my $dbh = $obj_db->dbh();
my $sth;

# add or update
if ($obj_cgi->request_method() eq 'POST') {
  my $postdata = $obj_cgi->param('POSTDATA');
  utf8::encode($postdata);
  my $cdat = decode_json $postdata;
  if (! defined($cdat->{'method'})) {
    $obj_cgi->send_error(503, 'invalid data');
    exit;
  }
  if ($cdat->{'tid'} !~ /^[a-z0-9]+$/) {
    $obj_cgi->send_error(503, 'invalid tid');
    exit;
  }
  if ($cdat->{'method'} eq 'add') {
    $sth = $dbh->prepare('SELECT * FROM tenants WHERE tid = ? OR name = ?');
    $sth->execute($cdat->{'tid'}, $cdat->{'name'});
    if ($sth->rows > 0) {
      $obj_cgi->send_error(503, 'duplicate tid/name');
      exit;
    }
    $sth = $dbh->prepare('INSERT INTO tenants (tid, adminkey, name, memo) VALUES (?, ?, ?, ?)');
    my $crand = int(rand(0xFFFFFFFF));
    my $nrow = $sth->execute($cdat->{'tid'}, $crand, $cdat->{'name'}, $cdat->{'memo'});
    if (! defined($nrow)) {
      $obj_cgi->send_error(503, 'registration failed');
      exit;
    }
  } elsif ($cdat->{'method'} eq 'update') {
    # check name conflict, try UPDATE - no tid if error
    $sth = $dbh->prepare('SELECT * FROM tenants WHERE name = ?');
    $sth->execute($cdat->{'name'});
    if ($sth->rows > 0) {
      $obj_cgi->send_error(503, 'duplicate name');
      exit;
    }
    $sth = $dbh->prepare('UPDATE tenants SET name = ?, memo = ? WHERE tid = ?');
    my $nrow = $sth->execute($cdat->{'name'}, $cdat->{'memo'}, $cdat->{'tid'});
    if (! defined($nrow)) {
      $obj_cgi->send_error(503, 'tid not found');
      exit;
    }
  } else {
    $obj_cgi->send_error(503, 'invalid method');
    exit;
  }
  $sth = $dbh->prepare('SELECT * FROM tenants WHERE tid = ?');
  $sth->execute($cdat->{'tid'});
  my $ret = $sth->fetchrow_hashref();
  $ret->{'adminkey'} = $obj_config->int_to_secret($ret->{'adminkey'});
  exit;
}

my $ret = {};

$sth = $dbh->prepare('SELECT * FROM tenants');
$sth->execute();
while (my $ref = $sth->fetchrow_hashref) {
  $ref->{'adminkey'} = $obj_config->int_to_secret($ref->{'adminkey'});
  $ret->{$ref->{'tenant'}} = $ref;
}

print $obj_cgi->header(200);
print to_json(\%$ret);

exit;
