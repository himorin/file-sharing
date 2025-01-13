#! /usr/bin/perl

use strict;
use lib '../';

use JSON;
use MIME::Types;

use PNAPI::Constants;
use PNAPI::Config;
use PNAPI::CGI;
use PNAPI::DB;

my $obj_cgi = new PNAPI::CGI;
my $obj_config = new PNAPI::Config;
my $obj_db = new PNAPI::DB;
my $dbh = $obj_db->dbh();
my $sth;

my $c_fid = $obj_cgi->param('fid');
my $c_lid = $obj_cgi->param('lid');

# check fid
if (defined($c_fid)) {
  $sth = $dbh->prepare('SELECT * FROM files WHERE fid = ?');
  $sth->execute($c_fid);
  if ($sth->rows != 1) {
    $obj_cgi->send_error(503, 'fid not found');
    exit;
  }
  # file download
  my $finfo = $sth->fetchrow_hashref();
  my $fname = $obj_config->GetHashFilename($c_fid, 0, $finfo->{'tid'}, 1);
  if (! (-f $fname)) {
    $obj_cgi->send_error(503, 'internal file store error');
    exit;
  }
  my $mime = MIME::Types->new();
  my $fmime = $mime->mimeTypeOf($finfo->{'mimetype'});
  # should this be all replaced with DEF_MIMETYPE?? (for download)
  if (defined($fmime)) { $fmime = lc($fmime); }
  else { $fmime = DEF_MIMETYPE; }
  my $fdl = $finfo->{'name'} . '.' . $finfo->{'mimetype'};
  print $obj_cgi->header(200,
    -type => "$fmime; name=\"$fdl\"",
    -content_disposition => "attachment; filename=\"$fdl\"",
    -content_length => $finfo->{'size'},
  );
  binmode STDOUT, ':bytes';
  open(INDAT, $fname);
  print <INDAT>;
  close(INDAT);
  exit;
}

if (! defined($c_lid)) {
  $obj_cgi->send_error(503, 'invalid parameter');
  exit;
}

$sth = $dbh->prepare('SELECT * FROM labels WHERE lid = ?');
if ($sth->rows != 1) {
  $obj_cgi->send_error(503, 'lid not found');
  exit;
}
my $tgt = $sth->fetchrow_hashref();
if (defined($tgt->{'gid'})) {
  # single group mode
} else {
  # label mode
}


exit;
