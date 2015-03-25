package Plugins::FileViewer::Settings;

# SqueezeCenter Copyright 2001-2007 Logitech.
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License, 
# version 2.

use strict;
use base qw(Slim::Web::Settings);

use Slim::Utils::Prefs;

my $prefs = preferences('plugin.fileviewer');

$prefs->setValidate({ 'validator' => 'file' }, 'plugin_fileviewer_filename');
$prefs->setValidate({ 'validator' => 'int' }, 'plugin_fileviewer_updateinterval');

sub new {
	my $class = shift;

	if (!defined $prefs->get('plugin_fileviewer_filename')) {
		$prefs->set('plugin_fileviewer_filename', '');
	}
	if (!defined $prefs->get('plugin_fileviewer_updateinterval')) {
		$prefs->set('plugin_fileviewer_updateinterval', 15);
	}

	return $class->SUPER::new();
}

sub name {
	return Slim::Web::HTTP::CSRF->protectName('PLUGIN_FILEVIEWER');
}

sub page {
	return Slim::Web::HTTP::CSRF->protectURI('plugins/FileViewer/settings.html');
}

sub prefs {
	return ($prefs, qw(plugin_fileviewer_filename plugin_fileviewer_updateinterval));
}

1;

__END__
