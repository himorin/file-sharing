# -*- Mode: perl; indent-tabs-mode: nil -*-
#
# Module for misc Utils
#

package PNAPI::Utils;

use strict;

use base qw(Exporter);
use Data::UUID;

@PNAPI::Utils::EXPORT = qw(
  generate_id
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




1;

__END__
