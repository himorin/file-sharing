#! /usr/bin/perl

use strict;
use lib './';

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

# check parameter
if (! defined($c_tenant)) {
  print $obj_cgi->header(404);
  exit;
}
my $sth = $dbh->prepare('SELECT * FROM tenants WHERE tid = ?');
$sth->execute($c_tenant);
if ($sth->rows != 1) {
  print $obj_cgi->header(404);
  exit;
}

my $c_dat = $sth->fetchrow_hashref();

$ret->{'tenant'} = $c_dat->{'tid'};
$ret->{'name'} = $c_dat->{'name'};
$ret->{'memo'} = $c_dat->{'memo'};
$ret->{'archived'} = 0;
if (defined($c_dat->{'redirect'})) {
  $ret->{'archived'} = 1;
}

print $obj_cgi->header(200);
print to_json(\%$ret);

exit;
