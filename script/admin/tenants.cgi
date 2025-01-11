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

# add or update
if ($obj_cgi->request_method() eq 'POST') {

  exit;
}

my $ret = {};

my $sth = $dbh->prepare('SELECT * FROM tenants');
$sth->execute($c_tenant);
while (my $ref = $sth->fetchrow_hashref) {
  $ret->{$ref->{'tenant'}} = $ret;
}

print $obj_cgi->header(200);
print to_json(\%$ret);

exit;
