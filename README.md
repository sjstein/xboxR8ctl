A quick proof-of-concept using a generic X-Box type controller (via the Windows Joystick API) to interface with Run8 via their "Custom USB Controller" interface (UDP)

D-Pad controls reverser : up = fwd, dwn = rev, left = throttle notch up, right = throttle notch down
Left stick controls air : up = auto brake apply, down = auto brake release, right = indy apply, left = indy release
right stick controls dynamic : up/down = in/out of setup, left = less dynamic, right = more dynamic

Various other functions for the buttons and triggers have also been added. See code for now.
