# FileViewer::Plugin.pm by mh 2005-2007
#
# This code is derived from code with the following copyright message:
#
# SliMP3 Server Copyright (C) 2001 Sean Adams, Slim Devices Inc.
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.
#
# Changelog
# 1.5 - SqueezeCenter 7.0 compatibility
# 1.0 - initial release

use strict;

package Plugins::FileViewer::Plugin;
use base qw(Slim::Plugin::Base);

use vars qw($VERSION);
use Plugins::FileViewer::Settings;
use Slim::Utils::Strings qw (string);
use Slim::Utils::Prefs;

my $prefs = preferences('plugin.fileviewer');

my ($delay, $lines);

sub getDisplayName { return 'PLUGIN_FILEVIEWER'; }

sub initPlugin {
	my $class = shift;
	$class->SUPER::initPlugin(shift);

	$VERSION = $class->_pluginDataFor('version');

	Plugins::FileViewer::Settings->new;

	Slim::Buttons::Common::addSaver( 'SCREENSAVER.fileviewer',
		getFunctions(), \&setScreenSaverMode,
		undef, getDisplayName() );

	$delay = $prefs->get('plugin_fileviewer_updateinterval') + 1;
}

sub setMode {
	my $class  = shift;
	my $client = shift;
	my $method = shift;

	if ($method eq 'pop') {
		Slim::Buttons::Common::popMode($client);
		return;
	}

	my $lines = _readFile($client);

	my %params = (
		stringHeader => 1,
		header => 'PLUGIN_FILEVIEWER',
		headerAddCount => 1,
		listRef => $lines,
		parentMode => Slim::Buttons::Common::mode($client),		  
	);

	Slim::Buttons::Common::pushMode($client, 'INPUT.List', \%params);
}

my %fileViewerFunctions = (
	'done' => sub {
		my ( $client, $funct, $functarg ) = @_;
		Slim::Buttons::Common::popMode($client);
		$client->update();

		# pass along ir code to new mode if requested
		if ( defined $functarg && $functarg eq 'passback' ) {
			Slim::Hardware::IR::resendButton($client);
		}
	}
);

sub getFunctions {
	return \%fileViewerFunctions;
}

sub setScreenSaverMode {
	my $client = shift;
	$client->modeParam('modeUpdateInterval', 1);
	$client->lines(\&screensaverFileviewerLines);
}

sub screensaverFileviewerLines {
	my $client = shift;

	if (++$delay > $prefs->get('plugin_fileviewer_updateinterval')) {
		$lines = join(' ', @{_readFile($client)});
		$delay = 0;
	}

	return {
		'line1' => string('PLUGIN_FILEVIEWER'),
		'line2' => $lines
	};
}

sub _readFile {
	my $client = shift;
	my @lines;

	if (open MYFILE, $prefs->get('plugin_fileviewer_filename')) {
		@lines = <MYFILE>;
		close MYFILE;
	}
	else {
		push @lines, $client->string('PLUGIN_FILEVIEWER_NOFILE');
	}	

	return \@lines;
}

1;
