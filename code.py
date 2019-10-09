#  Launch Deck Trellis M4
#  USB HID button box for launching applications, media control, camera switching and more
#  Use it with your favorite keyboard controlled launcher, such as Quicksilver and AutoHotkey

import time  
import random
import adafruit_trellism4
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
random.seed(time.monotonic_ns())

# Rotation of the trellis. 0 is when the USB is upself.
# The grid coordinates used below require portrait mode of 90 or 270
ROTATION = 270
# button behavior - whether pressing that macro key PRESSes (and immediately releases)
# a key combo, or PRESS_HOLD, where the key combo is held as long as the macro key is,
# or TOGGLE_HOLD, where a key combo is held until the macro key is pressed a second time
# and finally, TOGGLE_REP, wherre the key combo is repeatedly pressed and released until
# the macro key is pressed a second time
PRESS = 0
PRESS_HOLD = 1
TOGGLE_HOLD = 2
TOGGLE_REP = 3

# maximum brightness when an LED is lit
ACTIVE_BRIGHTNESS = 0.5
INACTIVE_BRIGHTNESS = 0.1

# the two command types -- MEDIA for ConsumerControlCodes, KEY for Keycodes
# this allows button press to send the correct HID command for the type specified
MEDIA = 1
KEY = 2

# button mappings
# customize these for your desired postitions, colors, and keyboard combos
# specify:
#         (button coordinate): (color hex value,
#                               Button behavior,     # PRESS, PRESS_HOLD, TOGGLE_HOLD, or TOGGLE_REP
#                               Delay/debounce time, # generally 0.01 unless TOGGLE_REP
#                               command type,        # MEDIA or KEY
#                               command/keycodes)    # single keys must within parens, with ending comma
macro_config_LUT = {
    (0,0): (0x002200, PRESS, 0.1, MEDIA, ConsumerControlCode.PLAY_PAUSE),
    # (1,0): (0x110011, MEDIA, HOLD, ConsumerControlCode.SCAN_PREVIOUS_TRACK),
    # (2,0): (0x110011, MEDIA, HOLD, ConsumerControlCode.SCAN_NEXT_TRACK),
    # (3,0): (0x000033, MEDIA, HOLD, ConsumerControlCode.VOLUME_INCREMENT),

    # (0,1): (0x110000, MEDIA, HOLD, ConsumerControlCode.MUTE),
    # # intentional blank button
    # # intentional blank button
    # (3,1): ((0,0,10), MEDIA, HOLD, ConsumerControlCode.VOLUME_DECREMENT),

    (0,2): (0x551100, PRESS_HOLD, 0.01, KEY, (Keycode.SHIFT, )),
    # (1,2): (0x221100, KEY, HOLD, (Keycode.CONTROL, Keycode.SHIFT, Keycode.TAB)),  # back cycle tabs
    # (2,2): (0x221100, KEY, HOLD, (Keycode.CONTROL, Keycode.TAB)),  # cycle tabs
    # (3,2): (0x333300, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.TWO)),

    # (0,3): (0x001155, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.THREE)),
    # # intentional blank button
    # # intentional blank button
    # (3,3): (0x330000, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.FOUR)),

    # (0,4): (0x005511, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.FIVE)),
    # (1,4): (0x440000, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.SIX)),
    # # intentional blank button
    # (3,4): (0x003300, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.EIGHT)),

    # (0,5): (0x222222, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.W)),
    (1,5): (0x0000ff, TOGGLE_HOLD, 0.01, KEY, (Keycode.SHIFT, )),
    # # intentional blank button
    # (3,5): (0x332211, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.T)),

    # (0,6): (0x001133, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.C)),
    # (1,6): (0x331100, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.V)),
    # (2,6): (0x111111, KEY, HOLD, (Keycode.GUI, Keycode.SHIFT, Keycode.FOUR)),  # screen shot
    # (3,6): (0x110000, KEY, HOLD, (Keycode.GUI, Keycode.ALT, Keycode.CONTROL, Keycode.N)),

    # (0,7): (0x060606, KEY, HOLD, (Keycode.GUI, Keycode.H)),  # hide front app, all windows
    # (1,7): (0x222200, KEY, HOLD, (Keycode.GUI, Keycode.GRAVE_ACCENT)),  # cycle windows of app
    # (2,7): (0x010001, KEY, HOLD, (Keycode.GUI, Keycode.SHIFT, Keycode.TAB)),  # cycle apps backards
    (3,7): (0x510051, TOGGLE_REP, 0.05, KEY, (Keycode.R, ))}  # mash 'r' as fast as possible



###----------------NOT USED CURRENTLY
# # Time in seconds to stay lit before sleeping.
# TIMEOUT = 90
# # Time to take fading out all of the keys.
# FADE_TIME = 1
# # Once asleep, how much time to wait between "snores" which fade up and down one button.
# SNORE_PAUSE = 0.5
# # Time in seconds to take fading up the snoring LED.
# SNORE_UP = 2
# # Time in seconds to take fading down the snoring LED.
# SNORE_DOWN = 1
# TOTAL_SNORE = SNORE_PAUSE + SNORE_UP + SNORE_DOWN

# def Snore(time, up=SNORE_UP, dwn= SNORE_DOWN, pause=SNORE_PAUSE, chirp=0.0):
  # brightness = 0.0
  # if time < up:
    # brightness = ACTIVE_BRIGHTNESS * ( time / up )
  # elif time < (up + dwn):
    # brightness = ACTIVE_BRIGHTNESS * 
    # ( 1 - (time-up)/dwn + chirp * (time % 0.13))
  # return brightness

# snore_new = True
# snore_start = 0
###----------------END NOT USED

# global state variables
# buttons refers to the actual buttons on the trellis,  
button_set = {(i,j) for i in range(0,4) for j in range(0,8)}
button_timers = {key:0.0 for key in button_set}
running_set = set()
toggled_set = set()
prev_press = set()

def add_to_running(key_location):
  running_set.add(key_location)
  
def toggle(key_location):
  toggled_set.discard(key_location) if key_location in toggled_set else toggled_set.add(key_location )
  
def add_and_toggle(key_location):
  add_to_running(key_location)
  toggle(key_location)

def nothing(key_location):
  pass

phys_press_funcs = {0:add_to_running, 
                    1:add_and_toggle,
                    2:add_and_toggle,
                    3:add_and_toggle}
                    
phys_release_funcs = {0:nothing,
                      1:add_and_toggle,
                      2:nothing, 
                      3:nothing}
                      
def press(button, time_interval):
  # NOTE; NEVER USE kbd.send, it is just press(*keys) followed by release_ALL
  color = macro_config_LUT[button][0] # the hex value

  # on the first loop time_interval == 0, but float
  if time_interval < 0.001:    
    # change brightness to full
    trellis.pixels[button] = scale_hex(color, ACTIVE_BRIGHTNESS)
    
    # do the pressing
    if macro_config_LUT[button][3] == KEY:
          kbd.press(*macro_config_LUT[button][4])
          kbd.release(*macro_config_LUT[button][4])
    else:
      cc.send(macro_config_LUT[button][4])
    
  # change brightness back
  if time_interval > macro_config_LUT[button][2]:
    trellis.pixels[button] = scale_hex(color, INACTIVE_BRIGHTNESS)
    running_set.discard(button)  # done running, remove button from set

def hold(button, time_interval):
  # this is the case where we want to hold a key as long as the button is depressed
  # whenever the state is set to run, it checks the toggle state, then either presses or
  # releases and flips the toggle, and turns off run
  
  color = macro_config_LUT[button][0] # the hex value
  if time_interval < 0.001: 
    if button not in toggled_set:  # turn it off
      if macro_config_LUT[button][3] == KEY:
        kbd.release(*macro_config_LUT[button][4])
      #else:
      #  pass # there is no equivalent for cc keys
      # dim the pixel color
      trellis.pixels[button] = scale_hex(color, INACTIVE_BRIGHTNESS)
    else: # turn it on
      # brighten the pixel color
      trellis.pixels[button] = scale_hex(color, ACTIVE_BRIGHTNESS)
      if macro_config_LUT[button][3] == KEY:
        kbd.press(*macro_config_LUT[button][4])
      else:
        cc.send(macro_config_LUT[button][4])
  
  if time_interval > macro_config_LUT[button][2]: # delay timeout/debounce
    running_set.discard(button)  # done running, remove button from set

def press_repeat(button, time_interval):
  color = macro_config_LUT[button][0] # the hex value
  if time_interval < 0.001:
    # change brightness to full
    trellis.pixels[button] = scale_hex(color, ACTIVE_BRIGHTNESS)
    
    # do the pressing
    if macro_config_LUT[button][3] == KEY:
          kbd.press(*macro_config_LUT[button][4])
          kbd.release(*macro_config_LUT[button][4])
    else:
      cc.send(macro_config_LUT[button][4])
  elif time_interval > macro_config_LUT[button][2]: # the repeat delay
    trellis.pixels[button] = scale_hex(color, INACTIVE_BRIGHTNESS)
    if button in toggled_set:  # we start over
      button_timers[button] = time.monotonic()
    else:
      running_set.discard(button)  # done running, remove button from set
  else:  # fadeout in the middle time
    delay = macro_config_LUT[button][2]
    scale = ((ACTIVE_BRIGHTNESS-INACTIVE_BRIGHTNESS) * (1 - time_interval/delay)) + INACTIVE_BRIGHTNESS
    trellis.pixels[button] = scale_hex(color, scale)

run_funcs = {0:press,
             1:hold,
             2:hold,
             3:press_repeat }


# Trellis setup 
# and a function that I might reuse/reimplement for brightness control of
# individual NeoPixels
def scale_hex (color, scalar):
  # takes a hex formatted 3 byte color value, and scales it up or down by scalar,
  # capping at 255 and 0 ofc
  # Ex. 0xFF3700, 0.5 -> R,G,B (255, 55, 00)*0.5 -> (127, 27, 0) -> 0x7F1B00
  channel1 = (color >> 16) & 0xFF
  channel2 = (color >> 8) & 0xFF
  channel3 = color & 0xFF
  channel1 = (int(min(max(channel1 * scalar,0),255)) << 16) & 0xFF0000
  channel2 = (int(min(max(channel2 * scalar,0),255)) << 8) & 0xFF00
  channel3 = int(min(max(channel3 * scalar,0),255)) & 0xFF
  out = channel1 | channel2 | channel3
  return out
  
kbd = Keyboard()
cc = ConsumerControl()
trellis = adafruit_trellism4.TrellisM4Express(rotation=ROTATION)

###---------- FOR FUN
def rand_color(max_brightness):
  maxb = int(1.5*max_brightness)
  choice1 = random.randint(0, max(min(255, maxb),0))
  maxb -= choice1
  choice2 = random.randint(0, max(min(255, maxb),0))
  maxb -= choice2
  choice3 = random.randint(0, max(min(255, maxb),0))
  choice = (choice1 << 16) | (choice2 << 8) | (choice3)
  return choice

def pulse(button, time_interval, up = 3, hold = 0.2, dwn = 1.50, chirp = 5.0):
  if time_interval < 0:
    trellis.pixels[button] = (0,0,0)
  elif time_interval < up:
    trellis.pixels[button] = scale_hex(random_colors[button], time_interval / up )
  elif time_interval < (up+hold):
    trellis.pixels[button] = scale_hex(random_colors[button], 1.0 )
  elif time_interval < (up+hold+dwn):
    trellis.pixels[button] = scale_hex(random_colors[button], (1.0 - (time_interval - up - hold)/dwn) -chirp*(time_interval % 0.1))
  else:
    trellis.pixels[button] = (0,0,0)
    running_set.discard(button)

def wave():
  for loc_tot in range(0,11):
    now = time.monotonic()
    line = [ (i,loc_tot-i) for i in range(8) 
            if (i < 4 and
                i > -1 and
                (loc_tot-i) > -1 and
                (loc_tot-i) < 8 )]
    for button in line:
      button_timers[button] = now + 2
    time.sleep(0.15)  

def sparkle():
  running_list = list(running_set)
  while running_list:
    pick = random.randint(1,5)
    now = time.monotonic()
    for i in range(0,min(pick, len(running_list))):
      button = random.choice(running_list)
      button_timers[button] = now + 2
      running_list.remove(button)
    time.sleep(0.05)

running_set = {(i,j) for i in range(0,4) for j in range(0,8)}
random_colors = { button:rand_color(50) for button in button_set}

sparkle() # prefers pulse(button, now - button_timers[button], up = 3, hold = 0.2, dwn = 1.50, chirp = 5.0) (defaults)
# wave()    # prefers pulse(button, now - button_timers[button], up = 1.5, hold = 0.0, dwn = 0.50, chirp = 0.0)

while running_set:
  now = time.monotonic()
  for button in running_set:
    pulse(button, now - button_timers[button])

trellis.pixels.fill((0,0,0))
time.sleep(0.2)   

###------------- END FUN

for button in macro_config_LUT:
    trellis.pixels[button] = scale_hex(macro_config_LUT[button][0], INACTIVE_BRIGHTNESS)



#this is the main loop, assume whatever needed to be setup is setup
while True:
    now = time.monotonic()
    # sleep_time = now - last_press_time # no sleeping in this version
    # sleeping = sleep_time > TIMEOUT  # This also sets it so the first press on a sleeping board doesn't do anything but wake
    
    # Button presses are sorted into a set of newly pressed buttons, and a set of newly released buttons
    curr_press = set(trellis.pressed_keys) & set(macro_config_LUT.keys())  # only keep keys with a valid LookUp    
    new_press = curr_press - prev_press  # the set of newly pressed buttons
    new_release = prev_press - curr_press  # the set of newly released buttons
    prev_press = curr_press  # we are done with curr_press 
    
    
    # The above two sets are then used to modify the running/toggled sets which represent the global state
    # as well as record when they were pressed.
    for button in new_press:
      if button not in running_set: # if its running it already has a timer
        button_timers[button] = now
      phys_press_funcs[ macro_config_LUT[button][1] ](button)
      
    for button in new_release:
      if button not in running_set: # if its running it already has a timer
        button_timers[button] = now
      phys_release_funcs[ macro_config_LUT[button][1] ](button)
      
      
    # Now that we have handled new presses and releases properly (that was easy)
    #  we just need to deal with the timers and flags
    for button in running_set:
      run_funcs[ macro_config_LUT[button][1] ](button, now - button_timers[button] )

    
 
