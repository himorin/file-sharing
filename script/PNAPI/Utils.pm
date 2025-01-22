# -*- Mode: perl; indent-tabs-mode: nil -*-
#
# Module for misc Utils
#

package PNAPI::Utils;

use strict;

use base qw(Exporter);
use Data::UUID;
use Encode;

use PNAPI::Constants;
use PNAPI::CGI;

@PNAPI::Utils::EXPORT = qw(
  generate_id
  fix_zipname
);


# generate id string using UUID
sub generate_id {
  my ($num) = @_;
  my @arr;
  if (! defined($num)) { $num = 1; }
  my $obj_uuid = Data::UUID->new;
  while ($num > 0) {
    my $cur = $obj_uuid->to_hexstring($obj_uuid->create());
    if (substr($cur, 0, 2) == '0x') { $cur = substr($cur, 2); }
    push(@arr, $cur);
    $num--;
  }
  return \@arr;
}

# convert encoding based on target device
sub fix_zipname {
  my ($obj_cgi, $name) = @_;
  my $ret = $name;
  if ($obj_cgi->user_agent() =~ /Windows/) {
    $ret = Encode::encode(PNAPI::Constants::ZIP_WIN_ENC, $name);
  } else {
    # nothing specific
  }
  return $ret;
}



1;

__END__
