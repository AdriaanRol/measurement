# control variables
kill_script = False

def script_killed():
    global kill_script
    
    if kill_script:
        kill_script = False
        return True
    else:
        return False

