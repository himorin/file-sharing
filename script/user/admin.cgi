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

my $c_tenant = $obj_cgi->param('tn');
my $ret = {};

# check access
my $is_ok = 0;
my $sth;
if (defined $obj_cgi->cookie($c_tenant)) {
  $sth = $dbh->prepare('SELECT * FROM tenants WHERE tid = ? AND adminkey = ?');
  $sth->execute($c_tenant, $obj_config->secret_to_int($obj_cgi->cookie($c_tenant)));
  if ($sth->rows > 0) { $is_ok = 1; }
}
if ($is_ok == 0) {
  $obj_cgi->send_error(503, 'invalid parameter');
  exit;
}

$ret->{$c_tenant} = $sth->fetchrow_hashref();
$ret->{$c_tenant}->{'adminkey'} = $obj_config->int_to_secret($ret->{$c_tenant}->{'adminkey'});

# groups
$sth = $dbh->prepare('SELECT * FROM labels WHERE tid = ?');
$sth->execute($c_tenant);
$ret->{'groups'} = {};
$ret->{'labels'} = {};
while (my $ref = $sth->fetchrow_hashref) {
  my $cv = {};
  $cv->{'lid'} = $ref->{'lid'};
  $cv->{'name'} = $ref->{'name'};
  $cv->{'memo'} = $ref->{'memo'};
  if (defined($ref->{'gid'})) {
    $cv->{'gid'} = $ref->{'gid'};
    $ret->{'groups'}->{$cv->{'name'}} = $cv;
  } else {
    $ret->{'labels'}->{$cv->{'name'}} = $cv;
  }
}


# files


print $obj_cgi->header(200);
print to_json(\%$ret);

exit;
