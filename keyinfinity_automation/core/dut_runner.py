import json
import paramiko

# Toggle: True = Local VS Code Mocking (No sudo/no board needed)
#         False = Real Physical VVDN Board via SSH
USE_LOCAL_EMULATOR = True


class DUTRunner:
    """Handles execution on physical board via SSH or simulates commands locally."""

    def __init__(self, ip="192.168.1.100", username="root", password="root"):
        self.ip = ip
        self.username = username
        self.password = password
        self.ssh = None
        self.mock_state = {
            "can0_state": "UP",
            "can1_state": "UP",
            "last_dump": "",
            "can0_bitrate": "500000",
            "can1_bitrate": "500000",
        }

    def connect(self):
        if not USE_LOCAL_EMULATOR:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.ip, username=self.username, password=self.password, timeout=10)

    def disconnect(self):
        if self.ssh:
            self.ssh.close()

    def run(self, command):
        """Executes shell commands on physical board or simulates them locally."""
        if not USE_LOCAL_EMULATOR:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            return stdout.read().decode('utf-8').strip(), stderr.read().decode('utf-8').strip(), exit_code

        # =====================================================================
        # LOCAL NO-SUDO MOCK ENGINE
        # Intercepts Linux CLI calls and provides accurate return values
        # =====================================================================

        # 1. Mock `ip link show` / `ip -d link show`
        if "ip link show" in command or "ip -d link show" in command:
            iface = "can0" if "can0" in command else "can1"
            state = self.mock_state[f"{iface}_state"]
            bitrate = self.mock_state[f"{iface}_bitrate"]
            output = f"3: {iface}: <NOARP,UP,LOWER_UP> mtu 16 qdisc pfifo_fast state {state} mode DEFAULT\n"
            output += f"    link/can  bitrate {bitrate} sample-point 0.750"
            return output, "", 0

        # 2. Mock `ip link set` state and bitrate switches
        elif "ip link set" in command:
            if "can0 down" in command:
                self.mock_state["can0_state"] = "DOWN"
            elif "can0 up" in command:
                self.mock_state["can0_state"] = "UP"
            if "can1 down" in command:
                self.mock_state["can1_state"] = "DOWN"
            elif "can1 up" in command:
                self.mock_state["can1_state"] = "UP"

            if "bitrate" in command:
                parts = command.split()
                if "bitrate" in parts:
                    idx = parts.index("bitrate") + 1
                    if "can0" in command:
                        self.mock_state["can0_bitrate"] = parts[idx]
                    elif "can1" in command:
                        self.mock_state["can1_bitrate"] = parts[idx]
            return "", "", 0

        # 3. Mock CAN-FD Frame Transmit (`cansend`)
        elif command.startswith("cansend"):
            parts = command.split()
            if len(parts) >= 3:
                iface, raw = parts[1], parts[2]
                if "##" in raw:
                    can_id, payload_raw = raw.split("##")
                    payload = payload_raw[1:] if len(payload_raw) > 0 and payload_raw[0].isdigit() else payload_raw
                else:
                    can_id = raw[:3]
                    payload = raw[3:]

                fmt_bytes = " ".join([payload[i:i+2] for i in range(0, len(payload), 2)])
                self.mock_state["last_dump"] = f"  {iface}  {can_id}   [{len(payload)//2}]  {fmt_bytes}"
            return "", "", 0

        # 4. Mock Log Files Output (`cat /tmp/can_dump.log`)
        elif "cat /tmp/" in command:
            return self.mock_state["last_dump"], "", 0

        # 5. Mock Process Check (`ps aux`)
        elif "ps aux" in command:
            return "root 1234 0.0 0.1 2456 800 ? S 10:00 0:00 candump", "", 0

        # 6. Mock File Stats (`stat`)
        elif command.startswith("stat"):
            return "1024", "", 0

        # Default fallback for cleanup calls (killall, rm, etc.)
        return "", "", 0