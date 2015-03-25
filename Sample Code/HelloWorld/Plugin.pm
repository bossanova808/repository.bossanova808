package Plugins::HelloWorld::Plugin;

# HelloWorld tutorial plugin by Mitch Gerdisch
# Meant to be a way of figuring out and understanding how plugins need to be written for SC7.
# There are 4 basic components that need to be written for SC7 plugins:
#	Plugin.pm - This is the main processing bit of the plugin and not much different than pre-SC7 plugin code.
#				But, there are differences.
#	Settings.pm - This file contains perl code for processing the web page used to set the settings for the plugin.
#	strings.txt - Where all the strings are stored - including their various lanuage equivalents.
#	basic.html - This is a file under HTML/<language abbrev.>/plugins/<plugin name>/settings/. It contains 
#				 HTML-like stuff for displaying the plugin's web user interface.

# This code is derived from code with the following copyright message:
#
# SqueezeCenter Copyright 2001-2007 Logitech.
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.

# required bit
use strict;

# required bit
use base qw(Slim::Plugin::Base);

# Plugin specific bit - put name of plugin where HelloWorld is.
# This points to the Settings.pm file that you also need to create/update for the plugin.
use Plugins::HelloWorld::Settings;

# Might be required. At least it's not bad to include it.
use Scalar::Util qw(blessed);

# Might be required. Not sure, but again it doesn't hurt.
use Slim::Control::Request;

# MUST HAVE: This log bit is new and allows one to use nicer logging facilities than were available pre-SC7
use Slim::Utils::Log;

# MUST HAVE: magical preferences getting stuff
use Slim::Utils::Prefs;

# MUST HAVE: provides the strings functionality that uses the strings.txt file to present the correct language
use Slim::Utils::Strings qw(string);

# So, get the data related to this plugin.
# The call to preferences() will be "plugin.<plugin name in lowercase>
# Something that might be interesting, there's actually a prefs file for each plugin.
# On Windows its stored in documents and settings/all users/application data/squeezecenter/prefs.
# You can look at it (it's a text file) and see what is being currently stored.
# However, there seems to be a lag between doing a set and it actually showing up in the file, fyi.
my $prefs = preferences('plugin.helloworld');

# Any global variables? Go ahead and declare and/or set them here
our @browseMenuChoices;

# used for logging
# To debug, run squeezecenter.exe from the command prompt as follows:
# squeezecenter.exe --debug plugin.<plugin name>=<logging level in caps>
# Log levels are DEBUG, INFO, WARN, ERROR, FATAL where a level will include messages for all levels to the right.
# So, squeezecenter.exe --debug plugin.helloworld=INFO,persist will show all messages fro INFO, WARN, ERROR, and FATAL.
# The "persist" bit of text allows the system to remember that logging level between invocations of squeezecenter.
my $log = Slim::Utils::Log->addLogCategory({
	'category'     => 'plugin.helloworld',
	'defaultLevel' => 'INFO',
#	'defaultLevel' => 'DEBUG',
	'description'  => getDisplayName(),
});

# This is an old friend from pre-SC7 days
# It returns the name to display on the squeezebox
sub getDisplayName {
	return 'PLUGIN_HELLOWORLD';
}

# I have my own debug routine so that I can add the *** stuff easily.
sub myDebug {
	my $msg = shift;
	my $lvl = shift;
	
	if ($lvl eq "")
	{
		$lvl = "debug";
	}

	
	$log->$lvl("*** Hello World *** $msg");
}

# Another old friend from pre-SC7 days.
# This is called when SC loads the plugin.
# So use it to initialize variables and the like.
sub initPlugin {
	my $class = shift;
	
	myDebug("Initializing");
		
	# These next two appear to be things that have to be done when initializing the plugin in SC7.
	# Not sure what they do.
	$class->SUPER::initPlugin();
	# Note the plugin-specific field here. This may instantiate the web interface for the plugin.
	Plugins::HelloWorld::Settings->new;
	
	# I'm using the Input modes capability of slimserver to control the menues.
	# Believe it or not, this stuff is documented rather well in the slimserver help pages.
	# So fire up the slimserver and select help and then select technical information.
	
	# Anyway check if the name field is populated in the plugin's preferences store and if not, set it to a default
	if ($prefs->get('helloname') eq '') {	
		myDebug("initializing helloname");
		$prefs->set('helloname', " World");
	}
	my $helloname = $prefs->get('helloname');
	myDebug("helloname is $helloname");

}

# Another old friend from pre-SC7.
# This is called when the plugin is selected by the user.
# So, initPlugin is called when the server starts up and is loading the plugins.
# setMode is called when the user navigates to the plugin on the squeezebox and navigates in or out of it.
sub setMode {
	my $class  = shift;
	my $client = shift;
	my $method = shift;
	
	myDebug("In setmode");
	
	# Handle requests to exit this mode/plugin by going back to where the user was before they came
	# here.  If you don't this, pressing LEFT will just put you straight back to where you already
	# are! (try commenting out the following if statement) 
	if ($method eq 'pop') {
		# Pop the current mode off the mode stack and restore the previous one
		Slim::Buttons::Common::popMode($client);
		return;
	}
	
	
	

	# Upon entering the plugin, we'll provide a menu of options.
	@browseMenuChoices = (
		'PLUGIN_HELLOWORLD_SEE_MESSAGE',
		'PLUGIN_HELLOWORLD_ENTER_NAME',
	);


		my %params = (
			'listRef'        => \@browseMenuChoices, # this isn't actually necessary since 'externRef' is set.
			'externRef'		 => \@browseMenuChoices, # the main reason I'm using this is to use stringExternRef.
			'stringExternRef' => 1, # setting this to true runs the menu option names through string() so it displays correctly.
			'externRefArgs'  => 'CV',
			'header'         => 'PLUGIN_HELLOWORLD', # This is displayed on the topline of the display
			'headerAddCount' => 1, # This tells the server to add an (x of y) thing to the header to indicate which item in the menu is being seen at that time. 
			'stringHeader'   => 1, # This tells the server to run the header through the strings function which uses strings.txt to figure out which language to display.
			'callback'       => \&helloworldMainMenu, # CRITICAL bit. This is a function that gets called when something happens - like a button press
			'onChange'       => \&helloworldOnChange, # OK, I'm having a bit of fun here, but thought I would play with this onChange capability which let's me do stuff as the menu is scrolled up and down.
			'onChangeArgs'	 => 'CVI', # This passes the client pointer, the internal value of the client? and the index in the menu

		);
	
		myDebug("Calling pushMode");
		
		# this is the fancy-pants stuff that is provided by the system to scroll through the options.
		Slim::Buttons::Common::pushMode($client, 'INPUT.List', \%params);
		
		myDebug("Post pushMode call");
}


# currently this does nothing. But, if I wanted to do something each time a the user scrolled up or down,
# this is where I would do it.
sub helloworldOnChange {
	myDebug("in helloworldOnChange");
}

# This subroutine is called when the user does something other than up or down through the main menu.
# But, this plugin only cares about LEFT and RIGHT presses.
# LEFT bumps you back to the main menu.
# RIGHT either displays the message or lets the user enter a new name
# any other key (e.g. play) is ignored with a simple bumpright animation.
sub helloworldMainMenu {
	my ($client,$exittype) = @_;
	
	$exittype = uc($exittype);
	
	myDebug("in hellowworldMainMenu with exittype: $exittype");
	
	
	# If the button is the left arrow, then just pop back up the previous menu.
	# In this case that's the main menu.
	# But, if I had pushed down to a lower menu, then it would pop up to a higher level menu of this plugin.
	if ($exittype eq 'LEFT') {

		Slim::Buttons::Common::popModeRight($client);

	} elsif ($exittype eq 'RIGHT') {
		# The right arrow button was pressed so, do whatever should be done if the right arrow is pressed
		# Since this callback function was set from the initial menu (see setmode above) it handles the top
		# most menu options. If one of those menu options has sub menues, then I  push on another menu
		# and it would have it's own callback function to handle button presses.
			
		# This appears to return a reference to the current menu option being displayed.
		# That's why you'll see the $$valueref when actually checking the value below
		my $valueref = $client->modeParam('valueRef');
		
		myDebug("Processing RIGHT - current menu item is: $$valueref");
	
		# This option is selected to actually display the hello <whatever> message.
		if ($$valueref eq 'PLUGIN_HELLOWORLD_SEE_MESSAGE')
		{
			
			# So get the value stored by the user for the hello message
			my $hello_target = $prefs->get('helloname');
			
			# build the message
			my @message = (
				"Hello" . $hello_target, # the helloname string should have a leading space on it already
			);
			
			# and push the message on as a single item menu and then handle inputs 
			# As you'll see when you look at doneShowingMsg, any key press passed to the handler will send the user 
			# back to the main menu.
			my %params = (
			'header'		 => '',
			'listRef'        => \@message,
			'callback'       => \&doneShowingMsg, # CRITICAL bit. This is a function that gets called when something happens - like a button press
			);
	
			# So this will put up the message built above and wait for input which will be processed by doneShowingMsg
			Slim::Buttons::Common::pushMode($client, 'INPUT.List', \%params);
			
			$client->update; # refresh the client and move into displaying the message
			
	
		} elsif ($$valueref eq 'PLUGIN_HELLOWORLD_ENTER_NAME') {
			# This option is selected if the user wants to change the <whatever> of the hello <whatever> message.
			# FYI: the user can also change the <whatever> via the plugin's settings web interface. 
			
			# For this option, we'll use the text input mode.
			
			# So get the current value stored by the user for the hello message
			my $hello_target = $prefs->get('helloname');
			
			my %params = (
				'callback'	=> \&enterNewName, # function to process the user's input.
				'valueRef' 	=> \$hello_target, # initialize with the current name
				'charsRef'	=> "both", # allows both upper and lower case letters.
				);
	
			Slim::Buttons::Common::pushMode($client, 'INPUT.Text', \%params);
			
			$client->update; # refresh the display and move into the input mode
		}
	

	}
	else
	{
		# just indicate nothing was done with a bump right
		$client->bumpRight();
		
		my $valueref = $client->modeParam('valueRef');
	}
}

# Handler function for key press after showing message.
# Basically, any key press will pop you back to the previous menu.
sub doneShowingMsg {
	my ($client,$exittype) = @_;
	
	myDebug("in doneShowingMsg");
	
	Slim::Buttons::Common::popModeRight($client);
}
	
# Handler for entering new name
# This gets called once the right arrow is showing on the SB and the user presses the RIGHT key.
# And it gets called when the user backspaces (LEFT keys) all the way to the left and out.
# But, if the user backspaces all the way out I don't end up changing the stored hello target.
# So, if you go to the squeezebox and select the option to change the name and then left key all the way out
# and then go back into the change name option you'll see the previous name is still there unchanged.
sub enterNewName {
	my ($client,$exittype) = @_;
	
	$exittype = uc($exittype);
	
	myDebug("in enterNewName with exittype: $exittype");
	
	# If the user RIGHT keyed past the name, then this handler is called with "NEXTCHAR" and we want to store 
	# whatever the user has entered.
	if ($exittype eq 'NEXTCHAR') {
		
		my $valueref = $client->modeParam('valueRef');
		$$valueref =~ s/^\s+//; # get rid of leading spaces if any since one is always added. 
		$$valueref = " $$valueref";
		$prefs->set('helloname', $$valueref);
	}
		
	# Whether the user RIGHT keyed out or LEFT keyed/backspaced out, we are done with the change name option.
	# So, pop back out to the main menu. 
	Slim::Buttons::Common::popModeRight($client);

}
	
# Everything is handled by the input modes stuff
# So, just return and empty hash - NOTE THE CURLY BRACES with the return call! 
# I spent a while debugging a "bogus function" error because I had return() and not return{}.
# Normally this would return a reference to a functions hash that hashes button presses with actions.
sub getFunctions {

	return{};
}


# Always end with a 1 to make Perl happy
1;
