import asyncio
from pymodbus.client import AsyncModbusTcpClient
from utils import log

class SessionClientManager:
    def __init__(self):
        self.clients = []
        self.tasks = []
        self.logs = []
        self.running = True

    async def start_clients(self, count, ip, port, interval, operation):
        for i in range(count):
            task = asyncio.create_task(self.run_client(i, ip, port, interval, operation))
            self.tasks.append(task)

    async def run_client(self, client_id, ip, port, interval, operation, unit_id=1):
        client = AsyncModbusTcpClient(ip, port=port)
        await client.connect()

        if not client.connected:
            self._log(client_id, "Connection failed")
            return

        self._log(client_id, "Connected")
        status = {"id": client_id, "status": "Connected", "value": None}
        self.clients.append(status)

        try:
            while self.running:
                if operation == "read":
                    result = await client.read_holding_registers(0, 2, unit=unit_id)
                    if not result.isError():
                        status["status"] = "OK"
                        status["value"] = result.registers
                        self._log(client_id, f"Registers: {result.registers}")
                    else:
                        status["status"] = "Read error"
                        self._log(client_id, "Read error")
                elif operation == "write":
                    result = await client.write_register(0, 123, unit=unit_id)
                    if not result.isError():
                        status["status"] = "OK"
                        status["value"] = "Wrote 123"
                        self._log(client_id, "Wrote 123 to register 0")
                    else:
                        status["status"] = "Write error"
                        self._log(client_id, "Write error")
                await asyncio.sleep(interval)
        finally:
            await client.close()
            status["status"] = "Stopped"
            self._log(client_id, "Stopped")

    async def stop_all(self):
        self.running = False
        await asyncio.gather(*self.tasks, return_exceptions=True)

    def _log(self, cid, msg):
        entry = f"[{cid}] {msg}"
        log(entry)
        self.logs.append(entry)
        if len(self.logs) > 100:
            self.logs.pop(0)
