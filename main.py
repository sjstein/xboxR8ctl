import pygame
import socket
import time

run8port = 7766
local_ip = '127.0.0.1'

# Run8 defined commands
cmd_alerter = 1
cmd_bell = 2
cmd_counter = 3
cmd_dyn_brake = 4
cmd_headlight_front = 5
cmd_headlight_rear = 6
cmd_mu_headlight = 7
cmd_horn = 8
cmd_indy_brake = 9
cmd_bail = 10
cmd_iso_switch = 11
cmd_park_break_set = 12
cmd_park_brake_rel = 13
cmd_reverser = 14
cmd_sand = 15
cmd_throttle = 16
cmd_t_motors = 17
cmd_auto_brake = 18
cmd_wiper = 19
cmd_dtmf_0 = 20
cmd_dtmf_1 = 21
cmd_dtmf_2 = 22
cmd_dtmf_3 = 23
cmd_dtmf_4 = 24
cmd_dtmf_5 = 25
cmd_dtmf_6 = 26
cmd_dtmf_7 = 27
cmd_dtmf_8 = 28
cmd_dtmf_9 = 29
cmd_dtmf_p = 30
cmd_dtmf_s = 31
cmd_radio_vol_up = 32
cmd_radio_vol_dwn = 33
cmd_radio_mute = 34
cmd_radio_ch_mode = 35
cmd_radio_dtmf_mode = 36
cmd_cktbrk_ctl = 37
cmd_cktbrk_dbrake = 38
cmd_cktbrk_engrun = 39
cmd_gktbrk_genfld = 40
cmd_cab_light = 41
cmd_step_light = 42
cmd_gauge_light = 43
cmd_emerg_stop = 44
cmd_auto_start = 45
cmd_auto_mu = 46
cmd_auto_cb = 47
cmd_auto_ab = 48
cmd_auto_eot = 49
cmd_eng_start = 50
cmd_eng_stop = 51
cmd_hep_switch = 52
cmd_tbrake_cutoff = 53
cmd_service_sel = 54
cmd_slow_speed_toggle = 55
cmd_slow_speed_inc = 56
cmd_slow_speed_dec = 57
cmd_on = 1
cmd_off = 0

throttle_idle = 152

r8_header_quiet = 96    # This message header tells Run8 not to play sounds in cab
r8_header_sound = 224   # This message header tells Run8 to play sound in cab

# Tuples which define dpad positions. These can also be added to form upper_right, lower_left, etc.
dpad_up = (0, 1)
dpad_dn = (0, -1)
dpad_rt = (1, 0)
dpad_lt = (-1, 0)


def crc(blist):
    # Generate CRC byte
    res = 0
    for i in blist:
        res = res ^ i
    return res


def form_msg(typ, cmd, data):
    # Form the message byte array
    msg_arr = bytes([typ, 0, cmd, data, crc([typ, cmd, data])])
    return msg_arr


def main():
    # Set up UDP
    out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Keep track of lever positions
    pos_indy_brake = 255
    pos_auto_brake = 0
    pos_dyn_brake = 0
    previous_indy = 255
    previous_auto = 0
    previous_dyn = 0
    pos_reverser = 'N'
    pos_throttle = 0
    active_dyn_brake = False
    alt_funct = False  # Designates an alternate function for specific button / axis
    wiper_value = 0
    headlight_value = 0

    # Keep track of direction levers are moving
    indy_brake_dir = 0
    auto_brake_dir = 0
    dyn_brake_dir = 0

    pygame.init()   # Initialize pygame
    pygame.joystick.init()  # Initialize the joystick module
    if pygame.joystick.get_count() == 0:    # Check if any joysticks are connected
        print("No controller detected.")
        return
    joystick = pygame.joystick.Joystick(0)      # Initialize the first joystick
    joystick.init()
    print(f"Controller detected: {joystick.get_name()}")
    try:
        # Main loop
        while True:
            for event in pygame.event.get():

                # Check for button pressed updates
                if event.type == pygame.JOYBUTTONDOWN:
                    # print(f"Button {event.button} pressed")
                    if event.button == 6:       # bail-off
                        out_sock.sendto(form_msg(r8_header_sound, cmd_bail, cmd_on), (local_ip, run8port))
                    elif event.button == 7:     # Wiper
                        wiper_value += 1
                        if wiper_value > 3:
                            wiper_value = 0
                        out_sock.sendto(form_msg(r8_header_sound, cmd_wiper, wiper_value), (local_ip, run8port))
                    elif event.button == 4:     # Front headlight
                        headlight_value += 1
                        if headlight_value > 2:
                            headlight_value = 0
                        out_sock.sendto(form_msg(r8_header_sound, cmd_headlight_front, headlight_value),
                                        (local_ip, run8port))
                    elif event.button == 5:      # Bell toggle
                        out_sock.sendto(form_msg(r8_header_sound, cmd_bell, cmd_on), (local_ip, run8port))
                    elif event.button == 3:     # counter up
                        out_sock.sendto(form_msg(r8_header_sound, cmd_counter, 1), (local_ip, run8port))
                    elif event.button == 0:     # counter down
                        out_sock.sendto(form_msg(r8_header_sound, cmd_counter, 2), (local_ip, run8port))
                    elif event.button == 2:     # Sand toggle
                        out_sock.sendto(form_msg(r8_header_sound, cmd_sand, cmd_on), (local_ip, run8port))
                    elif event.button == 1:     # Alerter
                        out_sock.sendto(form_msg(r8_header_sound, cmd_alerter, cmd_on), (local_ip, run8port))

                # Check for button released updates
                elif event.type == pygame.JOYBUTTONUP:
                    # print(f"Button {event.button} released")
                    if event.button == 6:       # bail-off release
                        out_sock.sendto(form_msg(r8_header_sound, cmd_bail, cmd_off), (local_ip, run8port))
                    # Are the below release messages even needed?
                    elif event.button == 5:
                        out_sock.sendto(form_msg(r8_header_sound, cmd_bell, cmd_off), (local_ip, run8port))
                    elif event.button == 2:
                        out_sock.sendto(form_msg(r8_header_sound, cmd_sand, cmd_off), (local_ip, run8port))
                    elif event.button == 3 or event.button == 0:
                        out_sock.sendto(form_msg(r8_header_sound, cmd_counter, 0), (local_ip, run8port))
                    elif event.button == 1:
                        out_sock.sendto(form_msg(r8_header_sound, cmd_alerter, cmd_off), (local_ip, run8port))

                # Check for analog stick updates
                elif event.type == pygame.JOYAXISMOTION:
                    # if event.axis < joystick.get_numaxes():
                    #     axis_value = joystick.get_axis(event.axis)
                    #     # print(f"Axis {event.axis} moved, Value: {axis_value}")

                    # horn toggle
                    if event.axis == 5:
                        if joystick.get_axis(event.axis) > 0.95:
                            out_sock.sendto(form_msg(r8_header_sound, cmd_horn, cmd_on), (local_ip, run8port))
                        if joystick.get_axis(event.axis) < 0.15:
                            out_sock.sendto(form_msg(r8_header_sound, cmd_horn, cmd_off), (local_ip, run8port))

                    # Left trigger - alt modifier
                    if event.axis == 4:
                        if joystick.get_axis(event.axis) > 0.95:
                            alt_funct = True
                        elif joystick.get_axis(event.axis) < -0.95:
                            alt_funct = False

                    # auto brake
                    if event.axis == 1:  # left stick
                        if joystick.get_axis(event.axis) < -0.5:   # Increase
                            auto_brake_dir = -1 * joystick.get_axis(event.axis)
                        elif joystick.get_axis(event.axis) > 0.5:   # Decrease
                            auto_brake_dir = -1 * joystick.get_axis(event.axis)
                        else:
                            auto_brake_dir = 0

                    # Indy brake
                    if event.axis == 0:
                        if joystick.get_axis(event.axis) > .2:   # Increase
                            indy_brake_dir = joystick.get_axis(event.axis)
                        elif joystick.get_axis(event.axis) < -.2:   # Decrease
                            indy_brake_dir = joystick.get_axis(event.axis)
                        else:
                            indy_brake_dir = 0

                    # Dyn brake - right stick (l/r)
                    if event.axis == 2:
                        if active_dyn_brake:    # Must at least be in setup
                            if joystick.get_axis(event.axis) > 0.05:   # Increase
                                dyn_brake_dir = joystick.get_axis(event.axis)
                            elif joystick.get_axis(event.axis) < -0.05:   # Decrease
                                dyn_brake_dir = joystick.get_axis(event.axis)
                            else:
                                dyn_brake_dir = 0

                    # Dyn brake setup - right stick (u/d)
                    if event.axis == 3:
                        # print(f'Joystick: {joystick.get_axis(event.axis)}')
                        if (joystick.get_axis(3) < -0.05 and pos_reverser != 'N' and pos_throttle == 0
                                and not active_dyn_brake):
                            active_dyn_brake = True     # Ok to go into dyn setup
                            pos_dyn_brake = 1

                        elif joystick.get_axis(3) > 0.05 and pos_dyn_brake <= 3 and active_dyn_brake:
                            active_dyn_brake = False    # Out of setup
                            pos_dyn_brake = 0

                # Check for D-Pad
                elif event.type == pygame.JOYHATMOTION:
                    dpad_value = joystick.get_hat(event.hat)
                    if dpad_value == dpad_dn and pos_throttle == 0:  # reverser reverse
                        if not active_dyn_brake:
                            if pos_reverser == 'F':
                                pos_reverser = 'N'
                                out_sock.sendto(form_msg(r8_header_sound, cmd_reverser, 100),
                                                (local_ip, run8port))
                            elif pos_reverser == 'N':
                                pos_reverser = 'R'
                                out_sock.sendto(form_msg(r8_header_sound, cmd_reverser, 0),
                                                (local_ip, run8port))

                    elif dpad_value == dpad_up:  # reverser fwd
                        if not active_dyn_brake and pos_throttle == 0:
                            if pos_reverser == 'N':
                                pos_reverser = 'F'
                                out_sock.sendto(form_msg(r8_header_sound, cmd_reverser, 255),
                                                (local_ip, run8port))
                            elif pos_reverser == 'R':
                                pos_reverser = 'N'
                                out_sock.sendto(form_msg(r8_header_sound, cmd_reverser, 100),
                                                (local_ip, run8port))

                    elif dpad_value == dpad_lt:  # Throttle up notch
                        if not active_dyn_brake:   # Only allow throttle movement when out of dynamic
                            pos_throttle += 1
                            if pos_throttle > 8:
                                pos_throttle = 8
                            out_sock.sendto(form_msg(r8_header_sound, cmd_throttle, pos_throttle),
                                            (local_ip, run8port))
                    elif dpad_value == dpad_rt:  # Throttle down notch
                        if not active_dyn_brake:  # Only allow throttle movement when out of dynamic
                            pos_throttle -= 1
                            if pos_throttle < 0:
                                pos_throttle = 0
                            # if pos_throttle <= 0:
                            #     out_sock.sendto(form_msg(r8_header_sound, cmd_throttle, throttle_idle),
                            #                     (local_ip, run8port))
                            # else:
                            out_sock.sendto(form_msg(r8_header_sound, cmd_throttle, pos_throttle), (local_ip, run8port))

            # Send updates to positions of levers
            if indy_brake_dir > 0:
                pos_indy_brake += 1
                if pos_indy_brake > 255:
                    pos_indy_brake = 255
                time.sleep((2.05-indy_brake_dir)/50)
            elif indy_brake_dir < 0:
                pos_indy_brake -= 1
                if pos_indy_brake < 0:
                    pos_indy_brake = 0
                time.sleep((2.05-abs(indy_brake_dir))/50)
            if pos_indy_brake != previous_indy:
                # print(f'Updating indy brake: {pos_indy_brake}')
                previous_indy = pos_indy_brake
                out_sock.sendto(form_msg(r8_header_sound, cmd_indy_brake, pos_indy_brake), (local_ip, run8port))

            if auto_brake_dir > 0:
                pos_auto_brake += 1
                if pos_auto_brake > 255:
                    pos_auto_brake = 255
                time.sleep((1.05-auto_brake_dir)/10)
            elif auto_brake_dir < 0:
                pos_auto_brake -= 1
                if pos_auto_brake < 0:
                    pos_auto_brake = 0
                time.sleep((1.05-abs(auto_brake_dir))/30)
            if pos_auto_brake != previous_auto:
                # print(f'Updating auto brake: {pos_auto_brake}')
                previous_auto = pos_auto_brake
                out_sock.sendto(form_msg(r8_header_sound, cmd_auto_brake, pos_auto_brake), (local_ip, run8port))

            if dyn_brake_dir > 0:
                pos_dyn_brake += 1
                if pos_dyn_brake > 255:
                    pos_dyn_brake = 255
                time.sleep((1.05-abs(dyn_brake_dir))/10)
            elif dyn_brake_dir < 0:
                pos_dyn_brake -= 1
                if pos_dyn_brake < 1:
                    pos_dyn_brake = 1
                time.sleep((1.05-abs(dyn_brake_dir))/10)
            if pos_dyn_brake != previous_dyn:
                # print(f'Updating dynamic brake: {pos_dyn_brake}')
                previous_dyn = pos_dyn_brake
                out_sock.sendto(form_msg(r8_header_sound, cmd_dyn_brake, pos_dyn_brake), (local_ip, run8port))

    except KeyboardInterrupt:
        # Quit pygame and clean up
        pygame.quit()


if __name__ == "__main__":
    main()
