global.timer = ((get_timer() - 34000) + global.lastReloadTimer)
global.timerstring = string(global.timer)
comment = "This will start out equal but will eventually drift to be slightly late"
time += 1
if (jt == 0)
{
    if (j_ch != 2)
    {
        if joystick_exists(1)
            j_ch = 1
        else if (j_ch == 1)
            j_ch = 0
    }
}
if (jt == 4)
{
    if (j_ch != 1)
    {
        if joystick_exists(2)
            j_ch = 2
        else if (j_ch == 2)
            j_ch = 0
    }
}
jt += 1
if (jt >= 8)
    jt = 0
if (j_ch > 0)
{
    j_prev[0] = j_on[0]
    j_on[0] = joystick_check_button(j_ch, global.button0)
    if (j_on[0] == 1 && j_prev[0] != j_on[0])
        keyboard_key_press(ord("Z"))
    if (j_on[0] == 0 && j_prev[0] != j_on[0])
        keyboard_key_release(ord("Z"))
    j_prev[1] = j_on[1]
    j_on[1] = joystick_check_button(j_ch, global.button1)
    if (j_on[1] == 1 && j_prev[1] != j_on[1])
        keyboard_key_press(ord("X"))
    if (j_on[1] == 0 && j_prev[1] != j_on[1])
        keyboard_key_release(ord("X"))
    j_prev[2] = j_on[2]
    j_on[2] = joystick_check_button(j_ch, global.button2)
    if (j_on[2] == 1 && j_prev[2] != j_on[2])
        keyboard_key_press(ord("C"))
    if (j_on[2] == 0 && j_prev[2] != j_on[2])
        keyboard_key_release(ord("C"))
    j_fr_p = j_fr
    j_fl_p = j_fl
    j_fu_p = j_fu
    j_fd_p = j_fd
    j_fr = 0
    j_fl = 0
    j_fu = 0
    j_fd = 0
    if (global.joy_dir == 0 || global.joy_dir == 1)
    {
        j_xpos = joystick_xpos(j_ch)
        j_ypos = joystick_ypos(j_ch)
    }
    j_dir = joystick_direction(j_ch)
    if (global.joy_dir == 0 || global.joy_dir == 1)
    {
        if (j_dir == 101)
        {
            if (j_xpos >= global.analog_sense)
                j_fr = 1
            if (j_xpos <= (-global.analog_sense))
                j_fl = 1
            if (j_ypos >= global.analog_sense)
                j_fd = 1
            if (j_ypos <= (-global.analog_sense))
                j_fu = 1
        }
    }
    if (j_dir != 101)
    {
        if (j_dir == 100)
            j_fl = 1
        if (j_dir == 98)
            j_fd = 1
        if (j_dir == 102)
            j_fr = 1
        if (j_dir == 104)
            j_fu = 1
        if (j_dir == 99)
        {
            j_fr = 1
            j_fd = 1
        }
        if (j_dir == 97)
        {
            j_fd = 1
            j_fl = 1
        }
        if (j_dir == 103)
        {
            j_fu = 1
            j_fl = 1
        }
        if (j_dir == 105)
        {
            j_fu = 1
            j_fr = 1
        }
    }
    if (global.joy_dir == 0 || global.joy_dir == 2)
    {
        j_pov = joystick_pov(j_ch)
        if (j_pov == 0)
            j_fu = 1
        if (j_pov == 270)
            j_fl = 1
        if (j_pov == 90)
            j_fr = 1
        if (j_pov == 180)
            j_fd = 1
        if (j_pov == 315)
        {
            j_fu = 1
            j_fl = 1
        }
        if (j_pov == 45)
        {
            j_fu = 1
            j_fr = 1
        }
        if (j_pov == 225)
        {
            j_fd = 1
            j_fl = 1
        }
        if (j_pov == 135)
        {
            j_fd = 1
            j_fr = 1
        }
    }
    if (j_fr != j_fr_p && j_fr == 1)
        keyboard_key_press(vk_right)
    if (j_fl != j_fl_p && j_fl == 1)
        keyboard_key_press(vk_left)
    if (j_fd != j_fd_p && j_fd == 1)
        keyboard_key_press(vk_down)
    if (j_fu != j_fu_p && j_fu == 1)
        keyboard_key_press(vk_up)
    if (j_fr != j_fr_p && j_fr == 0)
        keyboard_key_release(vk_right)
    if (j_fl != j_fl_p && j_fl == 0)
        keyboard_key_release(vk_left)
    if (j_fd != j_fd_p && j_fd == 0)
        keyboard_key_release(vk_down)
    if (j_fu != j_fu_p && j_fu == 0)
        keyboard_key_release(vk_up)
}
up = 0
down = 0
left = 0
right = 0
if keyboard_check(vk_up)
    try_up = 1
if keyboard_check_released(vk_up)
    try_up = 0
if keyboard_check(vk_down)
    try_down = 1
if keyboard_check_released(vk_down)
    try_down = 0
if keyboard_check(vk_right)
    try_right = 1
if keyboard_check_released(vk_right)
    try_right = 0
if keyboard_check(vk_left)
    try_left = 1
if keyboard_check_released(vk_left)
    try_left = 0
if (global.osflavor == 1)
{
    if try_up
        up = keyboard_check_direct(vk_up)
    if try_down
        down = keyboard_check_direct(vk_down)
    if try_left
        left = keyboard_check_direct(vk_left)
    if try_right
        right = keyboard_check_direct(vk_right)
}
else
{
    if try_up
        up = keyboard_check(vk_up)
    if try_down
        down = keyboard_check(vk_down)
    if try_left
        left = keyboard_check(vk_left)
    if try_right
        right = keyboard_check(vk_right)
}
if keyboard_check_released(vk_up)
    up = 0
if keyboard_check_released(vk_down)
    down = 0
if keyboard_check_released(vk_left)
    left = 0
if keyboard_check_released(vk_right)
    right = 0
if keyboard_multicheck(2)
{
    if (global.flag[28] == 1)
    {
        if (instance_exists(OBJ_WRITER) && (!instance_exists(obj_choicer)))
        {
            if (h_skip == 0)
            {
                keyboard_key_press(ord("X"))
                keyboard_key_press(ord("Z"))
            }
            if (h_skip == 1)
            {
                keyboard_key_release(ord("Z"))
                keyboard_key_release(ord("X"))
            }
            if (h_skip == 0)
                h_skip = 1
            else
                h_skip = 0
        }
    }
}
if (global.debug == true)
{
    if keyboard_check_pressed(ord("F"))
        room_speed = 200
}
if (global.debug == true)
{
    if keyboard_check_pressed(ord("W"))
        room_speed = 10
}
if keyboard_check_pressed(vk_f4)
{
    if window_get_fullscreen()
        window_set_fullscreen(false)
    else
        window_set_fullscreen(true)
}
if (canquit == 1)
{
    if (global.debug == true)
    {
        if (keyboard_check_pressed(ord("R")) && instance_exists(obj_essaystuff) == 0)
        {
            debug_r += 1
            if (debug_r > 5)
                game_restart()
            spec_rtimer = 1
        }
    }
    spec_rtimer += 1
    if (spec_rtimer >= 6)
        debug_r = 0
    if keyboard_check(vk_escape)
    {
        quit += 1
        if (instance_exists(obj_quittingmessage) == 0)
            instance_create(0, 0, obj_quittingmessage)
    }
    else
        quit = 0
}
