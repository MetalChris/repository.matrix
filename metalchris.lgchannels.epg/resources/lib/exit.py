import xbmc

class AddonMonitor(xbmc.Monitor):
    def __init__(self):
        super().__init__()

    def onAbortRequested(self):
        # Called when Kodi or the add-on is exiting
        xbmc.log("Addon is exiting!", xbmc.LOGINFO)
        # Perform cleanup or reset here

# Run monitor
monitor = AddonMonitor()
while not monitor.abortRequested():
    if monitor.waitForAbort(1):
        break
