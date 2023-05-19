if (canquit == 1)
{
    if (quit > 20)
        game_end()
}
if ((((global.seed * 214013) + 2531011) >> 16) != global.stateIndex)
{
    global.otherLastState = global.lastState
    global.lastState = global.stateIndex
    global.stateIndex = (((global.seed * 214013) + 2531011) >> 16)
    global.otherLastTimer = global.lastTimer
    global.lastTimer = global.timer
    appendFile = file_text_open_append("states.txt")
    file_text_write_string(appendFile, ((((string(global.stateIndex) + ",") + global.timerstring) + ",") + string(global.seed)))
    file_text_writeln(appendFile)
    file_text_close(appendFile)
}
