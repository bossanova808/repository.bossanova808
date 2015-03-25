package Slim::Plugin::XBMCTime::Plugin;

# SqueezeCenter Copyright (c) 2001-2007 Logitech.
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.

use strict;
use base qw(Slim::Plugin::Base);
use Slim::Utils::DateTime;
use Slim::Utils::Prefs;

use Slim::Control::Command;

use Slim::Utils::Misc;
use Slim::Utils::Strings qw(string);
use IO::Socket;

use Slim::Plugin::XBMCTime::Settings;

my $prefs = preferences('plugin.XBMCTime');

sub getDisplayName {
	return 'PLUGIN_SCREENSAVER_XBMCTime';
}

sub setMode {
	my $class  = shift;
	my $client = shift;

	$client->lines(\&lines);

	# setting this param will call client->update() frequently
	$client->modeParam('modeUpdateInterval', 1); # seconds
}

sub getXBMCStatus {

        if ($succCounter < 60) {
          $succCounter++;
          return "";
        }

         my $sock = new IO::Socket::INET (
                                          PeerAddr => '192.168.0.100',
                                          PeerPort => '80',
                                          Proto => 'tcp',
                                          Timeout => '0'
                                         );
         if (not defined $sock) {
           $::d_plugins && msg("Could not create socket.\n");
          $succCounter = 0;
          undef $sock;
          return "";
         }

         close($sock);

	my $client = shift;
	my $content = "None";
	my $time = "";
	my $duration = "";

       	my $http = Slim::Player::Protocols::HTTP->new({
        	'url'    => 'http://192.168.0.100/scripts/nowplaying.asp',
	        'timeout' => 1,
       	});

        if (not defined $http) {
          $::d_plugins && msg("HTTP undefined. Exiting.\n");
          $succCounter = 0;
          return "";
        }

	$content = $http->content();
	$http->close();
	undef $http;

        if ($content =~ /Time:(.*)\n/i) {
           $time = $1;
        }

	if ($time eq "") {
          $::d_plugins && msg("Unable to parse time.\n");
          $succCounter = 0;
          return "";
        }

        if ($content =~ /Duration:(.*)\n/i) {
           $duration = $1;
        }

        $succCounter = 100;
	return $time . " (" . $duration . ")";
}

sub initPlugin {
	my $class = shift;

	$class->SUPER::initPlugin();

	Slim::Plugin::XBMCTime::Settings->new;

	Slim::Buttons::Common::addSaver(
		'SCREENSAVER.XBMCTime',
		getScreensaverXBMCTime(),
		\&setScreensaverXBMCTimeMode,
		undef,
		getDisplayName(),
	);
}

our %functions = (
	'up' => sub  {
		my $client = shift;
		my $button = shift;
		$client->bumpUp() if ($button !~ /repeat/);
	},
	'down' => sub  {
	    my $client = shift;
		my $button = shift;
		$client->bumpDown() if ($button !~ /repeat/);;
	},
	'left' => sub  {
		my $client = shift;
		Slim::Buttons::Common::popModeRight($client);
	},
	'right' => sub  {
		my $client = shift;
		
		my $saver = Slim::Player::Source::playmode($client) eq 'play' ? 'screensaver' : 'idlesaver';
		
		if ($prefs->client($client)->get($saver) ne 'SCREENSAVER.XBMCTime') {
			$prefs->client($client)->set($saver,'SCREENSAVER.XBMCTime');
		} else {
			$prefs->client($client)->set($saver, $Slim::Player::Player::defaultPrefs->{$saver});
		}
	},
	'stop' => sub {
		my $client = shift;
		Slim::Buttons::Common::pushMode($client, 'SCREENSAVER.XBMCTime');
	}
);

sub lines {
	my $client = shift;
	
	my $saver = Slim::Player::Source::playmode($client) eq 'play' ? 'screensaver' : 'idlesaver';
	my $line2 = $client->string('SETUP_SCREENSAVER_USE');
	my $overlay2 = Slim::Buttons::Common::checkBoxOverlay($client, $prefs->client($client)->get($saver) eq 'SCREENSAVER.XBMCTime');
	
	return {
		'line'    => [ $client->string('PLUGIN_SCREENSAVER_XBMCTime'), $line2 ],
		'overlay' => [ undef, $overlay2 ]
	};
}

sub getFunctions {
	my $class = shift;

	return \%functions;
}

###################################################################
### Section 3. Your variables for your screensaver mode go here ###
###################################################################

our %screensaverXBMCTimeFunctions = (
	'done' => sub  {
		my ($client ,$funct ,$functarg) = @_;

		Slim::Buttons::Common::popMode($client);
		$client->update();

		# pass along ir code to new mode if requested
		if (defined $functarg && $functarg eq 'passback') {
			Slim::Hardware::IR::resendButton($client);
		}
	},
);

sub getScreensaverXBMCTime {
	return \%screensaverXBMCTimeFunctions;
}

sub setScreensaverXBMCTimeMode() {
	my $client = shift;
	$client->lines(\&screensaverXBMCTimelines);

	# setting this param will call client->update() frequently
	$client->modeParam('modeUpdateInterval', 1); # seconds
}

# following is a an optimisation for graphics rendering given the frequency XBMCTime is displayed
# by always returning the same hash for the font definition render does less work
my $fontDef = {
	'graphic-280x16'  => { 'overlay' => [ 'small.1'    ] },
	'graphic-320x32'  => { 'overlay' => [ 'standard.1' ] },
	'text'            => { 'displayoverlays' => 1        },
};

sub screensaverXBMCTimelines {
	my $client = shift;
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);

	# the alarm's days are sunday=7 based - 0 is daily

	my $alarm = preferences('server')->client($client)->get('alarm');

	my $alarmtime = preferences('server')->client($client)->get('alarmtime');
	my $currtime = $sec + 60*$min + 60*60*$hour;
	my $tomorrow = ($wday+1) % 7 || 7;

	my $alarmOn = $alarm->[ 0 ] 
			|| ($alarm->[ $wday ] && $alarmtime->[ $wday ] > $currtime)
			|| ($alarm->[ $tomorrow ] && $alarmtime->[ $tomorrow ] < $currtime);

	my $nextUpdate = $client->periodicUpdateTime();
	Slim::Buttons::Common::syncPeriodicUpdates($client, int($nextUpdate)) if (($nextUpdate - int($nextUpdate)) > 0.01);


	if ($xbmcPlaying eq "") {
        	return {
        		'center1' => Slim::Utils::Misc::longDateF(),
        		'center2' => Slim::Utils::Misc::timeF(),
        		'overlay1'=> ($alarmOn ? $client->symbols('bell') : undef),
        		'fonts'   => { 'graphic-280x16'  => { 'overlay1' => \ 'small.1' },
        					   'graphic-320x32'  => { 'overlay1' => \ 'standard.1' },
        					   'text' =>            { 'displayoverlays' => 1 },
        				   },
        	};
	}

	my $display = {
		'center' => [ Slim::Utils::XBMCTime::longDateF(undef, $prefs->get('dateformat')),
					  Slim::Utils::XBMCTime::timeF(undef, $prefs->get('timeformat')) ],
		'overlay'=> [ ($alarmOn ? $client->symbols('bell') : undef) ],
		'fonts'  => $fontDef,
	};

# BUG 3964: comment out until Dean has a final word on the UI for this.
# 	if ($client->display->hasScreen2) {
# 		if ($client->display->linesPerScreen == 1) {
# 			$display->{'screen2'}->{'center'} = [undef,Slim::Utils::XBMCTime::longDateF(undef,$prefs->get('dateformat'))];
# 		} else {
# 			$display->{'screen2'} = {};
# 		}
# 	}

	return $display;
}

1;

__END__
