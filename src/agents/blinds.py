import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import json

class BlindsAgent(Agent):

    def __init__(self, *args, room_id, regulate_temp, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = room_id
        self.regulate_temp = regulate_temp
        with open('config.json') as conf:
            conf = json.load(conf)
            self.pref_temp = conf['preferred_temp']

    class RecvTemp(CyclicBehaviour):

        def recv_plan(self):
            if self.temp is None or self.uv is None:
                return
            if self.agent.regulate_temp and self.uv >= 50:
                if self.temp < self.agent.pref_temp:
                    if self.blinds_state == 'DOWN':
                        self.blinds_state = 'UP'
                        print("Blinds exposed in room {}".format(self.agent.room_id))
                else:
                    if self.blinds_state == 'UP':
                        self.blinds_state = 'DOWN'
                        print("Blinds drawn in room {}".format(self.agent.room_id))

        async def on_start(self):
            print("Starting behaviour [BlindsAgent{}]. . .".format(self.agent.room_id))
            self.blinds_state = 'DOWN'
            self.temp = None
            self.uv = None


        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if msg.metadata["sensor_type"] == "TERM":
                    self.temp = int(msg.body)
                elif msg.metadata["sensor_type"] == "UV":
                    self.uv = int(msg.body)
                else:
                    print("Unknown sensor type {}".format(msg.metadata["sensor_type"]))
                print("Blinds agent for room {}: inside temp {}, UV {}".format(self.agent.room_id, self.temp, self.uv))

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
        self.add_behaviour(self.rcv_temp, template)