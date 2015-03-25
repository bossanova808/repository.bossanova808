# Plugin.pm
#
# This code is derived from code with the following copyright message:
#
# SliMP3 Server Copyright (C) 2001 Sean Adams, Slim Devices Inc.
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.

use strict;

package Plugins::XSqueezeDisplay::Plugin;
use base qw(Slim::Plugin::Base);

use vars qw($VERSION);
use Slim::Utils::Strings qw (string);
use Slim::Utils::Prefs;
use Plugins::XSqueezeDisplay::Settings;

$VERSION = substr(q$Revision: 1.1$, 10);

use constant XSQUEEZEDISPLAY_MENU => 'XSqueezeDisplay.XSqueezeDisplayMenu';


# A logger we will use to write plugin-specific messages. 
my $log = Slim::Utils::Log->addLogCategory( 
 { 
     'category'     => 'plugin.xsqueezedisplay', 
     'defaultLevel' => 'WARN',
     'description'  => 'PLUGIN_XSQUEEZEDISPLAY' 
 }
);

my $fvPrefs = preferences('plugin.XSqueezeDisplay');
my $DEFAULT_FOLDER = "DefaultFolder";

sub getDisplayName { return 'PLUGIN_XSQUEEZEDISPLAY'; }

sub initPlugin {
	my $class = shift;
	$class->SUPER::initPlugin(shift);
	Plugins::XSqueezeDisplay::Settings->new;
}

sub setMode {
	my $class  = shift;
	my $client = shift;
	my $method = shift;

	if ($method eq 'pop') {
		Slim::Buttons::Common::popMode($client);
		return;
	}

	DisplayFileList($client);
}

my %fileitems = ();


sub DisplayFileList
{
	my $client = shift;

	%fileitems = (); 
 
	my $folder = $fvPrefs->get('basedir');
	my $folder = $fvPrefs->get('basedir');
	my $folder = $fvPrefs->get('basedir');
	my $folder = $fvPrefs->get('basedir');

	if (!defined $folder) {
		$folder = DEFAULT_FOLDER;
	}

	# find all text files within the folder. 
	FindFiles($folder);

	my @names = sort keys %fileitems;

	my %params =
	(
		# The header (first line) to display whilst in this mode.
		header => '{PLUGIN_FILESVIEWER} {count}',

		# A reference to the list of items to display.
		listRef => \@names,

		# A unique name for this mode that won't actually get displayed anywhere.
		modeName => FILESVIEWER_MENU,

		parentMode => Slim::Buttons::Common::mode($client),

		onPlay => sub {
			my ($client, $name) = @_;
			DisplayFile($client, $folder, $name);
		},

		# An anonymous function that is called every time the user presses the RIGHT button.
		onRight => sub {
			my ($client, $name) = @_;
			DisplayFile($client, $folder, $name);
		},

		# These are all menu items and so have a right-arrow overlay
		overlayRef => sub {
         my $client = shift; 
         return [ undef, $client->symbols('rightarrow') ];
      }
	);

	Slim::Buttons::Common::pushModeLeft($client, 'INPUT.Choice', \%params);
}

sub FindFiles
{
	my $rootdir = shift;
	my $subdir = shift;

	my $dir = (defined $subdir) ? "$rootdir/$subdir" : "$rootdir";

	opendir DIR, $dir or $log->error("Couldn't open folder $dir");
	my @files = readdir DIR;

	foreach my $item (@files)
	{
		next if ($item =~ /^\./);

		my $p = "$dir/$item";

		if (-d $p)
		{
			my $searchdir = (defined $subdir) ? "$subdir/$item" : "$item";
			 
			$log->debug("search subfolder $searchdir in $rootdir");

			FindFiles($rootdir, $searchdir);
		}
		elsif ($item =~ /(.*)(\.txt)$/)
		{
			my $name = $1;

			$log->debug("Found $name in $item");

			$fileitems{$name} = (defined $subdir) ? "$subdir/$item" : "$item";
		}
	}
	closedir DIR;
}

sub DisplayFile
{
	my ($client, $folder, $name) = @_;

	$log->info("FilesViewer: Display $name");

	my $file = $folder . '/' . $fileitems{$name};
 	my @lines = ReadFile($client, $file);

	my $item = {
		title        => $name,
		description  => join("\n\r", @lines)
	};

	Slim::Buttons::XMLBrowser::displayItemDescription($client, $item);
}


sub ReadFile {
	my ($client, $filepath) = @_;
	
	my @lines;

	$log->info("FilesViewer: Read File $filepath");

	if (open MYFILE, $filepath) {
		@lines = <MYFILE>;
		close MYFILE;
	}
	else {
		push @lines, $client->string('PLUGIN_FILESVIEWER_NOFILE') . ": $filepath";
	}

	return @lines;
}

my %FilesViewerFunctions = (
	'done' => sub {
		my ( $client, $funct, $functarg ) = @_;
		Slim::Buttons::Common::popMode($client);
		$client->update();

		# pass along ir code to new mode if requested
		if (defined $functarg && $functarg eq 'passback') {
			Slim::Hardware::IR::resendButton($client);
		}
	}
);

sub getFunctions {
	return \%FilesViewerFunctions;
}

1;
