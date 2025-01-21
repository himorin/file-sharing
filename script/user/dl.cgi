#! /usr/bin/perl

use strict;
use lib '../';

use JSON;
use MIME::Types;
use Archive::Zip qw( :ERROR_CODES :CONSTANTS );

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
  $sth = $dbh->prepare('SELECT *, UNIX_TIMESTAMP(dt) AS dtunix FROM files WHERE fid = ?');
  $sth->execute($c_fid);
  if ($sth->rows != 1) {
    $obj_cgi->send_error(503, 'fid not found');
    exit;
  }
  # file download
  my $finfo = $sth->fetchrow_hashref();
  my $fname = $obj_config->GetHashFilename($c_fid, 0, $finfo->{'tid'});
  if (! defined($fname)) {
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
$sth->execute($c_lid);
if ($sth->rows != 1) {
  $obj_cgi->send_error(503, 'lid not found');
  exit;
}

my $files = {}; # files = { 'full-name.ext': { 'fid': 'unixtime', ...}, ... }
my $dirs = {}; # dirs = { 'dir1': { 'sdir1': {}, 'sdir2': { 'ssdir1': {}}, 'ssdir3': {}}, 'dir2': ....}
my $c_tid;

my $tgt = $sth->fetchrow_hashref();
$c_tid = $tgt->{'tid'};
if (defined($tgt->{'gid'})) {
  # single group mode
  $sth = $dbh->prepare('SELECT *, UNIX_TIMESTAMP(dt) AS dtunix FROM files WHERE gid = ?');
  $sth->execute($c_lid);
  while (my $cf = $sth->fetchrow_hashref) {
    # check files.name contains '/' or not
    if (index($cf->{'name'}, '/') > -1) { 
      # XXX to be implemented, register directories into $dirs
    }
    my $fname = $cf->{'name'} . '.' . $cf->{'mimetype'};
    if (! exists($files->{$fname})) {
      $files->{$fname} = {};
    }
    $files->{$fname}->{$cf->{'fid'}} = $cf->{'dtunix'};
  }
} else {
  # label mode
}

# build zip and send
my $DNAME = 'download.zip';
print("Content-type: application/zip\n");
print("Content-Disposition: attachment; filename=$DNAME\n");
print("\n");
my $ozip = Archive::Zip->new();
_add_dirs($ozip, '', $dirs);
my $clfile;
foreach my $fname (keys(%$files)) {
  if (scalar keys(%{$files->{$fname}}) > 1) {
    foreach my $tgt (keys(%{$files->{$fname}})) {
      $clfile = $obj_config->GetHashFilename($tgt, 0, $c_tid);
      if (defined($clfile)) { # just in case!
        $ozip->addFile($clfile, _build_fname_ut($fname, $files->{$fname}->{$tgt}));
      }
    }
  } else {
    foreach my $tgt (keys(%{$files->{$fname}})) {
      $clfile = $obj_config->GetHashFilename($tgt, 0, $c_tid);
      if (defined($clfile)) { # just in case!
        $ozip->addFile($clfile, $fname);
      }
    }
  }
}
$ozip->writeToFileHandle(*STDOUT);

exit;

sub _add_dirs {
  my ($ozip, $head, $hash) = @_;
  my $cadd;
  foreach my $cdir (keys(%$hash)) {
    $cadd = $head . '/' . $cdir;
    $ozip->addDirectory($cadd);
    _add_dirs($ozip, $cadd, $hash->{$cdir});
  }
}

sub _build_fname_ut {
  my ($fname, $ut) = @_;
  my $out = substr($fname, 0, rindex($fname, '.'));
  my @gt = gmtime($ut);
  $out .= sprintf('-%04d%02d%02dT%02d%02d%02d', $gt[5] + 1900, $gt[4] + 1, $gt[3], $gt[2], $gt[1], $gt[0]);
  $out .= substr($fname, rindex($fname, '.')); # contains '.'
  return $out;
}
