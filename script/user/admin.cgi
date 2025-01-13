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

# groups


# files


print $obj_cgi->header(200);
print to_json(\%$ret);

exit;
