var thisString, alphaGet;
draw_set_color(c_black)
draw_set_font(fnt_maintext)
alphaGet = draw_get_alpha()
draw_set_alpha(0.6)
thisString = ""
thisString += ("Current seed: " + string(global.seed))
thisString += ("#Current state index: " + string(global.stateIndex))
thisString += ("#Current seed's timer: " + string(global.lastTimer))
thisString += "#"
thisString += ("#Last seed: " + string(global.lastSeed))
thisString += ("#Last state index: " + string(global.lastState))
thisString += ("#Last seed's timer: " + string(global.otherLastTimer))
thisString += "#"
thisString += ("#Current time: " + global.timerstring)
draw_rectangle(0, 0, (string_width(thisString) + 20), (string_height(thisString) + 20), false)
draw_set_color(c_white)
draw_text(10, 10, thisString)
draw_set_alpha(alphaGet)
