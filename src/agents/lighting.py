import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import json


class LightingAgent(Agent):

    def __init__(self, *args, room_id, if_detected_people, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = room_id
        # self.if_detected_people = if_detected_people

    class RecvDetectedPeople(CyclicBehaviour):
        def receive_plan(self):
            if not self.detected_people:
                return
            if self.detected_people == 0:
                if self.lighting_state == 'ON':
                    self.lighting_state = 'OFF'
                    print("Turned off the lights in room {}".format(self.agent.room_id))
            if self.detected_people > 0:
                if self.lighting_state == 'OFF':
                    self.lighting_state = 'ON'
                    print("Turned on the lights in room {}".format(self.agent.room_id))

        async def on_start(self):
            print("Starting behaviour [LightingAgent {}]. . .".format(self.agent.room_id))
            self.lighting_state = 'OFF'
            self.detected_people = 0

        async def run(self):
            recv_message = await self.receive(timeout=10)
            if recv_message:
                if recv_message.metadata["sensor_type"] == "PHOTOCELL":
                    self.detected_people = int(recv_message.body)
                else:
                    print("Received message from wrong sensor type")

                print("Lighting agent for room {}: , detected people: {}".format(self.agent.room_id, self.detected_people))

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
        self.recv_detected_people = self.RecvDetectedPeople()
        template = Template()
        template.set_metadata("msg_type", "INF")
        template.set_metadata("sensor_id", self.room_id)
        self.add_behaviour(self.recv_detected_people, template)