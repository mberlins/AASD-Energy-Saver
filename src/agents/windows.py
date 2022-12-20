import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import json


class WindowsAgent(Agent):

    def __init__(self, *args, room_id, regulate_temp, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = room_id
        self.regulate_temp = regulate_temp
        with open('config.json') as conf:
            conf = json.load(conf)
            self.pref_temp = conf['preferred_temp']

    class RecvTemp(CyclicBehaviour):

        def receive_plan(self):
            if not self.agent.regulate_temp:
                return
            if self.temp != self.agent.pref_temp:
                if self.window_state == 'OPEN':
                    if (self.out_temp > self.agent.pref_temp and self.agent.pref_temp < self.temp) or (
                            self.out_temp < self.agent.pref_temp > self.temp):
                        self.window_state = 'CLOSED'
                        print("Closed windows in room {}".format(self.agent.room_id))
                elif self.window_state == 'CLOSED':
                    if (self.out_temp > self.temp and self.agent.pref_temp > self.temp) or (
                            self.out_temp < self.temp > self.agent.pref_temp):
                        self.window_state = 'OPEN'
                        print("Opened windows in room {}".format(self.agent.room_id))

        async def on_start(self):
            print("Starting behaviour [WindowsAgent {}]. . .".format(self.agent.room_id))
            self.window_state = 'OPEN'
            self.temp = 0
            self.out_temp = 0

        async def run(self):
            recv_message = await self.receive(timeout=10)
            if recv_message:
                if recv_message.metadata["sensor_type"] == "THERM":
                    self.temp = int(recv_message.body)
                elif recv_message.metadata["sensor_type"] == "OUT_THERM":
                    self.out_temp = int(recv_message.body)

                print("Windows agent for room {}: inside temp {}, outside temp {}".format(self.agent.room_id, self.temp,
                                                                                          self.out_temp))

                sent_message = Message(to="repo@localhost")
                sent_message.set_metadata("msg_type", "ASK")
                sent_message.set_metadata("room_id", self.agent.room_id)
                sent_message.body = ''
                await self.send(sent_message)

                self.receive_plan()

            else:
                print("Did not receive any messages")

            await asyncio.sleep(0.5)

    async def setup(self):
        self.recv_temp = self.RecvTemp()
        template = Template()
        template.set_metadata("msg_type", "INF")
        template.set_metadata("sensor_id", self.room_id)
        self.add_behaviour(self.recv_temp, template)