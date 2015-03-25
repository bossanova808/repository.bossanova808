# Settings.pm
#
# This code is derived from code with the following copyright message:
#
# SliMP3 Server Copyright (C) 2001 Sean Adams, Slim Devices Inc.
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.

use strict;

package Plugins::XSqueezeDisplay::Settings;
use base qw(Slim::Web::Settings);

use Slim::Utils::Prefs;

my $prefs = preferences('plugin.XSqueezeDisplay');

sub name {
	return Slim::Web::HTTP::protectName('PLUGIN_XSQUEEZEDISPLAY');
}

sub page {
	return Slim::Web::HTTP::protectURI('plugins/XSqueezeDisplay/settings/basic.html');
}

sub prefs {
	return ($prefs, qw(basedir));
}

1;
