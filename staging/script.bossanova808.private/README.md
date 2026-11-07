Bossanova808 Private
===================================

`script.bossanova808.private`

**Testing only - this add-on may break your system - DON'T INSTALL!**

A private add-on for Bossanova808's own Kodi systems. When it is installed and enabled, the Bossanova808 Confluence skins (Omega and Piers) switch on household-specific behaviour: a custom TV Shows sub-menu, fast profile switching, family birthday backgrounds, and skin utilities.

The skins check for it with `System.AddonIsEnabled(script.bossanova808.private)`, exposed as `$EXP[IsBossanova808]`. Add-ons are installed per Kodi install, so the add-on being enabled is what switches the behaviour on; disabling or uninstalling it returns the skins to their standard behaviour. Which profile gets what is then set per profile, in the add-on's settings:

- **Profile Switching** - the profile the skin's profile button fast-switches to (chosen with a picker). Leave empty for a normal log-off.
- **TV Shows menu** - an optional custom TV Shows sub-menu of up to 5 buttons, each with a label and a target (a library node, playlist or `videodb://` path). A button with no label is hidden.

A small service copies these settings into skin strings, which are saved per profile and available as the skin loads, so the skins show the right menus immediately rather than waiting for the service to start.

If you have installed this by accident, please uninstall it.
