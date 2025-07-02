import asyncio
from pymodbus.client import AsyncModbusTcpClient
from main import log

class ModbusClient:
    def __init__(self, client_id, ip, port, interval, operation, unit_id=1):
        self.client_id = client_id
        self.ip = ip
        self.port = port
        self.unit_id = unit_id
        self.interval = interval
        self.operation = operation
        self.value = None
        self.status = "Not started"
        self._running = True

    async def start(self):
        client = AsyncModbusTcpClient(self.ip, port=self.port)
        await client.connect()

        if not client.connected:
            self.status = "Connection failed"
            log(f"[{self.client_id}] Connection failed")
            return

        self.status = "Connected"
        log(f"[{self.client_id}] Connected")

        try:
            while self._running:
                if self.operation == "read":
                    result = await client.read_holding_registers(0, 2, unit=self.unit_id)
                    if not result.isError():
                        self.value = result.registers
                        self.status = "OK"
                        log(f"[{self.client_id}] Registers: {self.value}")
                    else:
                        self.status = "Read error"
                        log(f"[{self.client_id}] ERROR reading")
                elif self.operation == "write":
                    result = await client.write_register(0, 123, unit=self.unit_id)
                    if not result.isError():
                        self.value = "Wrote 123"
                        self.status = "OK"
                        log(f"[{self.client_id}] Wrote 123 to register 0")
                    else:
                        self.status = "Write error"
                        log(f"[{self.client_id}] ERROR writing")
                await asyncio.sleep(self.interval)
        finally:
            await client.close()
            self.status = "Stopped"
            log(f"[{self.client_id}] Stopped")

    def stop(self):
        self._running = False

class ClientManager:
    def __init__(self):
        self.clients = []
        self.tasks = []

    def start_clients(self, count, ip, port, interval, operation):
        for i in range(count):
            client = ModbusClient(i, ip, port, interval, operation)
            self.clients.append(client)
            task = asyncio.create_task(client.start())
            self.tasks.append(task)

    def stop_all(self):
        for client in self.clients:
            client.stop()

manager = ClientManager()
