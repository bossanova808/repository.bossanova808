#
# This code is derived from code with the following copyright message:
#
# SliMP3 Server Copyright (C) 2001 Sean Adams, Slim Devices Inc.
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.
#
use strict;

package Plugins::XSqueezeDisplay::Plugin;

use base qw(Slim::Plugin::Base);
use vars qw($VERSION);
use Plugins::XSqueezeDisplay::Settings;
use Slim::Utils::Strings qw (string);
use Slim::Utils::Prefs;
use Slim::Utils::Log;
use LWP::UserAgent;
use POSIX qw(strftime);
use JSON;

use constant CONNECTION_ATTEMPTS_BEFORE_SLEEP => 2;
use constant SLEEP_PERIOD => 10;

my $ua = LWP::UserAgent->new;

my $log = Slim::Utils::Log->addLogCategory({
	'category'     => 'plugin.xsqueezedisplay',
	'defaultLevel' => 'INFO',
	'description'  => getDisplayName(),
});

my $prefs = preferences('plugin.xsqueezedisplay');

my ($delay, $lines, $line1, $line2, $server_endpoint, $state, $timeRemaining, $failed_connects, $retry_timer);


# Video properties
my ($duration,
	$totaltime, 
	$time, 
	$time_remaining, 
	$percentage, 
	$title, 
	$album, 
	$artist, 
	$season, 
	$episode, 
	$showtitle, 
	$tvshowid, 
	$thumbnail, 
	$file, 
	$fanart, 
	$streamdetails, 
	$resume);

# Audio properties
# Pictures properties

sub getDisplayName { return 'PLUGIN_XSQUEEZEDISPLAY'; }

sub myDebug {
	my $msg = shift;
	my $lvl = shift;	
	if ($lvl eq "")
	{
		$lvl = "debug";
	}
	$log->$lvl("*** XSqueezeDisplay *** $msg");
}

sub initPlugin {
	my $class = shift;
	$class->SUPER::initPlugin(shift);

	$VERSION = $class->_pluginDataFor('version');

	Plugins::XSqueezeDisplay::Settings->new;

	Slim::Buttons::Common::addSaver( 'SCREENSAVER.xsqueezedisplay',
		getFunctions(), \&setScreenSaverMode,
		undef, getDisplayName() );

	# $delay = $prefs->get('plugin_fileviewer_updateinterval') + 1;
	$delay = 1;
	if ($prefs->get('plugin_xsqueezedisplay_kodijsonuser') eq ""){
		$server_endpoint = join('', 'http://', $prefs->get('plugin_xsqueezedisplay_kodiip'),':',$prefs->get('plugin_xsqueezedisplay_kodijsonport'), '/jsonrpc');
	}
	else{
		$server_endpoint = 'http://' . $prefs->get('plugin_xsqueezedisplay_kodijsonuser') . ':' . $prefs->get('plugin_xsqueezedisplay_kodijsonpassword') . '@' . $prefs->get('plugin_xsqueezedisplay_kodiip') . ':' . $prefs->get('plugin_xsqueezedisplay_kodijsonport') . '/jsonrpc';
	}
	myDebug(join("","Kodi endpoint is ", $server_endpoint));
	$state = "Stopped";
	$timeRemaining = "";
	$failed_connects = 0;
	$retry_timer = SLEEP_PERIOD;
}

sub setMode {
	my $class  = shift;
	my $client = shift;
	my $method = shift;

	if ($method eq 'pop') {
		Slim::Buttons::Common::popMode($client);
		return;
	}

	my %params = (
		stringHeader => 1,
		header => 'PLUGIN_XSQUEEZEDISPLAY',
		headerAddCount => 1,
		listRef => $lines,
		parentMode => Slim::Buttons::Common::mode($client),		  
	);

	Slim::Buttons::Common::pushMode($client, 'INPUT.List', \%params);
}

my %xSqueezeDisplayFunctions = (
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
	return \%xSqueezeDisplayFunctions;
}

sub setScreenSaverMode {
	my $client = shift;
	$client->modeParam('modeUpdateInterval', 1);
	$client->lines(\&screensaverXSqueezeDisplayLines);
}


sub kodiJSON {
		my $post_data = shift;

		#set a very short timeout
		$ua->timeout(0.5);

		#assemble the JSON POST request
		my $req = HTTP::Request->new(POST => $server_endpoint);
		$req->header('content-type' => 'application/json');
		$req->content($post_data);

		#myDebug(join("", "JSON Request to: 	",$server_endpoint));
		#myDebug(join("", "JSON Request is: 	", $post_data));

		# submit the request
		my $resp = $ua->request($req);

		#  YAY! 
		if ($resp->is_success) {		    
	   	 	#myDebug("JSON Request Success: " . $resp->decoded_content ."\n");
		    return $resp;
		}
		#oh dear....
		else {
			#only log errors other than can't connect...
			if ($resp->code != 500){
			    myDebug(join("JSON Request error code: 		", $resp->code, "\n"));
			    myDebug(join("JSON Request error message: 	", $resp->message, "\n"));
			}
			return $resp;
		}	
	    
	    
}

sub screensaverXSqueezeDisplayLines {

	my $client = shift;

	#holds the lines to be resturned - default is to return the time
	my $state = "Inactive";
	$line1 = strftime "%A, %B %e, %Y", localtime;
	$line2 = strftime "%I:%M %p", localtime;
	$line2 =~ s/^0+//;

	#if we have more than 3 failed connections...
	if ($failed_connects > CONNECTION_ATTEMPTS_BEFORE_SLEEP){
		#if our retry timer is still above 0...
		if ($retry_timer > 0) {
			#myDebug("Sleeping for " . $retry_timer);
			$retry_timer--;
		}
		#retry timer has reached zero - reset the timer & connects counter
		else{
			#myDebug("Ok, trying to connect again");
			$failed_connects = 0;
			$retry_timer = SLEEP_PERIOD;
		}
	}
	#failed_connects is <3, so try and do stuff
	else {

		#debug - introspect test the kodi json API here
		#my $post_data = '{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "params": { "filter": { "id": "Player.GetItem", "type": "method" } }, "id": 1 }';
		# Get the active players
		my $post_data = '{
			"jsonrpc": "2.0", 
			"method": "Player.GetActivePlayers", 
			"id": 1
			}';

		my $resp = kodiJSON($post_data);
		
		if ($resp->is_success) {
			my $message = decode_json $resp->decoded_content;
			
			#A PLAYER IS ACTIVE
			if (@{$message->{result}}){

		    	#myDebug("Detected player activity - " . $resp->decoded_content);
		    	$state = "Playing";

		    	foreach my $player (@{$message->{result}}){
		    		#myDebug("Player ". $player->{'playerid'} . " is type " . $player->{'type'});

		    		if ($player->{'type'} == "video"){
			    		# Get the play progress time
						my $post_data = '{
						    "jsonrpc": "2.0",
						    "method": "Player.GetProperties",
						    "params": {
						        "properties": [
						            "percentage",
						            "time",
						            "totaltime"
						        ],
						        "playerid": 1
						    },
						    "id": 1
						}';

						$resp = kodiJSON($post_data);
						$message = decode_json $resp->decoded_content;

						my $duration = ($message->{'result'}{'totaltime'}{'minutes'} * 60) + $message->{'result'}{'totaltime'}{'seconds'};
						my $elapsed = ($message->{'result'}{'time'}{'minutes'} * 60) + $message->{'result'}{'time'}{'seconds'};
						my $difference = $duration - $elapsed;
						my $difference_hours = ($difference/(60*60))%24;
						my $difference_minutes = ($difference/60)%60;
						my $difference_seconds = $difference%60;
						#myDebug("Hours " . $hours . " Minutes " . $minutes . " Seconds " . $seconds);
						if ($difference_hours ne "0"){
							$timeRemaining = sprintf("-%02d:%02d:%02d", $difference_hours, $difference_minutes, $difference_seconds)
						}
						else {
							$timeRemaining = sprintf("-%02d:%02d", $difference_minutes, $difference_seconds);
						}

						$line1 = $state;
						$line2 = $line2 . "   [" . $timeRemaining . "]";
				    } #player == video	
				} # foreach $player
			} #there was a result in the json
		} #there was a resp->success
		#no response from Kodi
		else {
			#count failed connections.  If we get to 3, stop hammering the server for a while...(See top)
			if ($resp->code == 500){
				#myDebug("Failed to connect for " . $failed_connects);
				$failed_connects++;
			}
		}	

	} #failed_connects wwas less than 3


	#we've got here - package up the data and return it
	my $hash = {
	   'center' => [ $line1,
	                 $line2 ],
	};

	return $hash;

}


1;

