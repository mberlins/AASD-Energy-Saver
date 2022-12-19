from spade import quit_spade

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

import asyncio
import json
import datetime
import getpass
import time
import random


class SensorsAgent(Agent):
    class SendTemperatureInformation(CyclicBehaviour):

        class SensorTemperatures:
            def __init__(self, name, temp):
                self.name = name
                self.temp = temp

        async def on_start(self):
            self.counter = 0

        async def on_end(self):
            print(f"Sensor agent stopping at {datetime.datetime.now().time()}: {self.counter}")
            await self.agent.stop()

        async def run(self):

            sensor_temps = list()
            # Create temperature map for all defined sensors
            for sensor in self.agent.sensors:
                if self.counter % sensor['interval'] == 0:
                    sensor_temps.append(
                        self.SensorTemperatures(sensor['name'], random.randint(sensor['min'], sensor['max'])))

            if len(sensor_temps) > 0:
                for room in self.agent.rooms:
                    print(f"\nRoom {room['id']}:")
                    for sensor_temp in sensor_temps:
                        msg = Message(to="windows{}@localhost".format(room['id']))
                        msg.set_metadata("msg_type", "INF")
                        msg.set_metadata("room_id", room['id'])
                        msg.set_metadata("sensor_name", sensor_temp.name)
                        msg.body = str(sensor_temp.temp)
                        await self.send(msg)
                        print(f"Sensor agent sent data to agent: {sensor_temp.name} with temp: {sensor_temp.temp}")

            self.counter += 1
            await asyncio.sleep(1)

    async def setup(self):
        with open('config.json') as conf:
            conf = json.load(conf)
            self.rooms = conf['rooms']
            self.sensors = conf['sensors']

        behaviour = self.SendTemperatureInformation()
        self.add_behaviour(behaviour)

        print(f"Sensor agent started at {datetime.datetime.now().time()}. Running updates...")


if __name__ == "__main__":
    sensors_agent = SensorsAgent("sensors@localhost", "password")
    future = sensors_agent.start()
    future.result()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sensors_agent.stop()
        print("Stopping...")