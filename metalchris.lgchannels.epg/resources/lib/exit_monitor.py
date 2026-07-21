import xbmc

def main():
    monitor = xbmc.Monitor()
    
    # Run your main logic here
    while not monitor.abortRequested():
        # Wait for 10 seconds or until Kodi exits
        if monitor.waitForAbort(10):
            # Abort was requested while waiting
            break
        
        # Perform your periodic task here
        # xbmc.log("Working...", level=xbmc.LOGDEBUG)

    # --- TASK ON EXIT ---
    # Place your exit code here (e.g., saving state, stopping external processes)
    xbmc.log("Kodi is exiting, performing cleanup tasks...", level=xbmc.LOGDEBUG)

if __name__ == '__main__':
    main()
