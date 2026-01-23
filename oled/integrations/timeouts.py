import asyncio
import settings
import time


from integrations.logging_config import *

logger = setup_logger(__name__)
#logger = setup_logger(__name__,lvlDEBUG)



class timeouts:

    def __init__(self,loop,windowmanager,nowplaying,usersettings):
        self.usersettings = usersettings
        self.loop = loop
        self.nowplaying = nowplaying
        self.windowmanager = windowmanager

        self.loop.create_task(self.__get_timeouts())



    async def __get_timeouts(self):
        while self.loop.is_running():
            #get_timeouts()
            try:

                if self.usersettings.startup < self.usersettings.shutdowntime:
                    shutdowntime = int(self.usersettings.shutdowntime - time.monotonic())
                    settings.job_t = shutdowntime

                    if self.usersettings.shutdowntime <= time.monotonic():
                        self.windowmanager.set_window("ende")
                else:
                    settings.job_t = -1

                logger.debug(f"get_timeouts  job_t is {settings.job_t}" )

            except Exception as error:
                settings.job_t = -1
                logger.error(f"get_timeouts job_t {error}")


            try:
                if self.usersettings.IDLE_POWEROFF > 0 and self.nowplaying._state != "play":
                    seconds_since_last_input = time.monotonic() - settings.lastinput
                    settings.job_i = self.usersettings.IDLE_POWEROFF * 60  - (seconds_since_last_input)
                    if seconds_since_last_input >= self.usersettings.IDLE_POWEROFF * 60:
                        self.windowmanager.set_window("ende")
                else:
                    settings.job_i = -1

                logger.debug(f"get_timeouts  job_i is {settings.job_i}" )

            except Exception as error:
                settings.job_i = -1
                logger.error(f"get_timeous job_i {error}")


            await asyncio.sleep(5)

