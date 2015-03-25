package Plugins::HelloWorld::Settings;


# SqueezeCenter Copyright 2001-2007 Logitech.
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.

# Settings file.
# This file contains stuff generally applicable to the web interface used to set the settings for the plugin
# The HelloWorld plugin has a single text field in the settings screen used to enter a name to which to say "Hello."
# Anything in this file is required, except for anything that is clearly HelloWorld specific

# All good/required uses to have in here.
use strict;
use base qw(Slim::Web::Settings);
use Slim::Utils::Prefs;
use Slim::Utils::Log;

# Used for logging.
my $log = Slim::Utils::Log->addLogCategory({
	'category'     => 'plugin.helloworld',
	'defaultLevel' => 'INFO',
#	'defaultLevel' => 'DEBUG',
	'description'  => 'HelloWorld Settings',
});



# my own debug outputer
sub myDebug {
	my $msg = shift;
	
	$log->info("*** Hello World - Settings *** $msg");
}

# This gets the current preferences stored for the plugin.
# The stored preferences/settings for all plugins can be found on Windows under 
# documents and settings/all users/application data/squeezecenter/prefs.
# This call to "preferences" returns a pointer to that data that can then be read or set.
# At least that's how I think it works.
my $prefs = preferences('plugin.helloworld');

# This migrate method allows you to get the settings that were stored when the user had a pre-SC7 slimserver
# and was using the plug-in.
# You can then use those to populate the SC7-compatible attributes of preferences.
# Since HelloWorld is brand new to SC7, this call is unnecessary but left in you show how it works.
# The idea is as follows:
# 	helloname is the attribute in preferences that contains the name to which Hello is said.
# 	If there was a pre-SC7 version of HelloWorld, then the call to OldPrefs->get would return the value the user 
# 		had entered in the pre-SC7 slimserver.
#	Otherwise, the field is essentially initialized to "World."
$prefs->migrate(1, sub {
	$prefs->set('helloname',      Slim::Utils::Prefs::OldPrefs->get('helloname')      || 'World' );
	1;
});

# See strings.txt to see what PLUGIN_HELLOWORLD is expanded into.
sub name {
	return Slim::Web::HTTP::protectName('PLUGIN_HELLOWORLD');
}

# This points to the HTML page you wrote that is used to set the plugin's settings.
# If you look in this directory, you'll see a directory called HTML which if you follow it down
# you'll eventually find an html file called basic.html. I'm not convinced it has to be called basic.html but
# that seems to be what everyone calls it.
# Anyway, basic.html is in some funky HTML-like format that is used to display the settings page when you select
# "Settings->Extras->[plugin's settings box]" from the SC7 window.
sub page {
	return Slim::Web::HTTP::protectURI('plugins/HelloWorld/settings/basic.html');
}

# Required function used to process the web page input.
# This handler is called whenever the webpage is displayed as well as when a setting is "applied."
sub handler {
	my ($class, $client, $params) = @_;
	
	myDebug("in handler");

	# When "apply" is pressed on the settings page, this function gets called.
	# So, double check that the apply button was pressed and if so check that the field was populated.
	# If so, set that value into the prefs variable
	# It's easiest if you use the same name for the HTML field and the prefs field.
	# In this case everything is called helloname and if you look at basic.html 
	# you'll see the field is called helloname.
	if ($params->{'saveSettings'} && $params->{'helloname'}) {
		my $helloname = $params->{'helloname'};
		$prefs->set('helloname', " $helloname"); # add a leading space to make the message display nicely
	}

	# This puts the value on the webpage. 
	# If the page is just being displayed initially, then this puts the current value found in prefs on the page.
	$params->{'prefs'}->{'helloname'} = $prefs->get('helloname');

	# I have no idea what this does, but it seems important and it's not plugin-specific.
	return $class->SUPER::handler($client, $params);
}

1;

__END__
