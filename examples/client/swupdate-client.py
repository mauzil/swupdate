#!/usr/bin/env python3
# Copyright (c) 2018 Stefano Babic <sbabic@denx.de>
#
# SPDX-License-Identifier:     GPL-2.0-or-later
#

import asyncio
import json
import os
import requests
import websockets
import sys

class SWUpdater:
    "" " Python helper class for SWUpdate " ""

    url_upload = 'http://{}:8080/upload'
    url_status = 'ws://{}:8080/ws'

    def __init__ (self, path_image, host_name):
        self.__image = path_image
        self.__host_name = host_name


    async def wait_update_finished(self, timeout = 300):
        print ("Wait update finished")
        async def get_finish_messages ():
            async with websockets.connect(self.url_status.format(self.__host_name)) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if data ["type"] != "message":
                        continue

                    print (data["text"])
                    if data ["text"] == "SWUPDATE successful !":
                        return

        await asyncio.wait_for(get_finish_messages(), timeout = timeout)

    def update (self, timeout = 300):
        print ("Start uploading image...")
        try:
            response = requests.post(self.url_upload.format(self.__host_name), files = { 'file':open (self.__image, 'rb') })

            if response.status_code != 200:
                raise Exception ("Cannot upload software image: {}".  format (response.status_code))

            print ("Software image uploaded successfully. Wait for installation to be finished...\n")
            asyncio.sleep(10)
            asyncio.get_event_loop().run_until_complete(self.wait_update_finished(timeout = timeout))

        except ValueError:
            print("No connection to host, exit")


if __name__ == "__main__":
    sys.path.append (os.getcwd ())

    if len (sys.argv) != 3:
       print ("Usage: swupdate.py <path to image> <hostname>")
       exit (0)


    SWUpdater (sys.argv[1], sys.argv[2]).update ()
