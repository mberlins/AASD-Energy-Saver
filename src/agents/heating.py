import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import json

class FloorHeatingAgent(Agent):

    def __init__(self, *args, room_id, regulate_temp, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = room_id
        self.regulate_temp = regulate_temp
        with open('config.json') as conf:
            conf = json.load(conf)
            self.pref_temp = conf['preferred_temp']

    class RecvTemp(CyclicBehaviour):

        def recv_plan(self):
            if self.agent.regulate_temp:
                self.is_heating_on = self.temp < self.agent.pref_temp
                if self.is_heating_on:
                    print("Heating is on in room {}\n".format(self.agent.room_id))
                else:
                    print("Heating is off in room {}\n".format(self.agent.room_id))

        async def on_start(self) -> None:
            print("Starting behavior [FloorHeatingAgent{}]. . .".format(self.agent.room_id))
            self.is_heating_on = False
            self.temp = 0

        async def run(self) -> None:
            msg = await self.receive(timeout=10)
            if msg:
                self.temp = int(msg.body)

                print("Floor heating agent for room {}: inside temp {}".format(self.agent.room_id, self.temp))
                msg = Message(to="repo@localhost")
                msg.set_metadata("msg_type", "ASK")
                msg.set_metadata("room_id", self.agent.room_id)
                msg.body = ''
                await self.send(msg)

                self.recv_plan()
            else:
                print("Did not receive any message after 10 seconds")

            await asyncio.sleep(0.5)

    async def setup(self):
        self.rcv_temp = self.RecvTemp()
        template = Template()
        template.set_metadata("msg_type", "INF")
        template.set_metadata("sensor_id", self.room_id)
        template.set_metadata("sensor_type", "TERM")
        self.add_behaviour(self.rcv_temp, template)