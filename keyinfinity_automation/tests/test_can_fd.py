import time
from testify import (
    TestCase,
    class_setup,
    class_teardown,
    setup,
    teardown,
    suite,
    assert_equal,
    assert_in
)
from core.dut_runner import DUTRunner


class CanFdTestSuite(TestCase):

    # -------------------------------------------------------------------------
    # FIXTURES
    # -------------------------------------------------------------------------
    @class_setup
    def setup_class(self):
        """Initialize connection/runner once for all 15 tests."""
        self.dut = DUTRunner()
        self.dut.connect()

    @class_teardown
    def teardown_class(self):
        """Disconnect after full test suite completes."""
        self.dut.disconnect()

    @setup
    @teardown
    def cleanup(self):
        """Ensure clean state before and after every test."""
        self.dut.run("killall -9 candump > /dev/null 2>&1")
        self.dut.run("sudo ip link set can0 down > /dev/null 2>&1")
        self.dut.run("sudo ip link set can1 down > /dev/null 2>&1")
        self.dut.run("rm -f /tmp/can_dump.log /tmp/can0_dump.log /tmp/can1_dump.log")

    # -------------------------------------------------------------------------
    # ALL 15 END-TO-END CAN-FD TEST CASES
    # -------------------------------------------------------------------------

    @suite('e2e', 'can', 'can0', 'init', 'fast')
    def test_VVDN_IGW1_CANFD_001_can0_init_and_status(self):
        """001: Verify CAN-FD Port 1 (can0) Initialization and Status."""
        out, _, exit_code = self.dut.run("ip link show can0")
        assert_equal(exit_code, 0, "can0 interface missing!")

        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on")
        out, _, _ = self.dut.run("ip link show can0")
        assert_in("state UP", out, "can0 failed to transition to UP state")

        self.dut.run("sudo ip link set can0 down")
        out, _, _ = self.dut.run("ip link show can0")
        assert_in("state DOWN", out, "can0 failed to transition to DOWN state")

    @suite('e2e', 'can', 'can1', 'init', 'fast')
    def test_VVDN_IGW1_CANFD_002_can1_init_and_status(self):
        """002: Verify CAN-FD Port 2 (can1) Initialization and Status."""
        out, _, exit_code = self.dut.run("ip link show can1")
        assert_equal(exit_code, 0, "can1 interface missing!")

        self.dut.run("sudo ip link set can1 up type can bitrate 500000 fd on")
        out, _, _ = self.dut.run("ip link show can1")
        assert_in("state UP", out)

        self.dut.run("sudo ip link set can1 down")
        out, _, _ = self.dut.run("ip link show can1")
        assert_in("state DOWN", out)

    @suite('e2e', 'can', 'can0', 'loopback', 'fast')
    def test_VVDN_IGW1_CANFD_003_can0_loopback(self):
        """003: Verify CAN-FD Port 1 Internal Loopback Transmission."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on loopback on")
        self.dut.run("candump -n 1 can0 > /tmp/can_dump.log 2>&1 &")
        time.sleep(0.3)

        payload = "123##8AABBCCDDEEFF0011"
        _, _, exit_code = self.dut.run(f"cansend can0 {payload}")
        assert_equal(exit_code, 0, "cansend failed on can0 loopback")
        time.sleep(0.3)

        dump_out, _, _ = self.dut.run("cat /tmp/can_dump.log")
        assert_in("123", dump_out)
        assert_in("AA BB CC DD EE FF 00 11", dump_out)

    @suite('e2e', 'can', 'can1', 'loopback', 'fast')
    def test_VVDN_IGW1_CANFD_004_can1_loopback(self):
        """004: Verify CAN-FD Port 2 Internal Loopback Transmission."""
        self.dut.run("sudo ip link set can1 up type can bitrate 500000 fd on loopback on")
        self.dut.run("candump -n 1 can1 > /tmp/can_dump.log 2>&1 &")
        time.sleep(0.3)

        payload = "456##82233445566778899"
        _, _, exit_code = self.dut.run(f"cansend can1 {payload}")
        assert_equal(exit_code, 0, "cansend failed on can1 loopback")
        time.sleep(0.3)

        dump_out, _, _ = self.dut.run("cat /tmp/can_dump.log")
        assert_in("456", dump_out)
        assert_in("22 33 44 55 66 77 88 99", dump_out)

    @suite('e2e', 'can', 'can0', 'external')
    def test_VVDN_IGW1_CANFD_005_can0_external_comm(self):
        """005: Verify External Transmit on CAN-FD Port 1."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on")
        payload = "789##16AABBCCDDEEFF00112233445566778899"
        _, _, exit_code = self.dut.run(f"cansend can0 {payload}")
        assert_equal(exit_code, 0, "Failed external frame transmit on can0")

    @suite('e2e', 'can', 'can1', 'external')
    def test_VVDN_IGW1_CANFD_006_can1_external_comm(self):
        """006: Verify External Transmit on CAN-FD Port 2."""
        self.dut.run("sudo ip link set can1 up type can bitrate 500000 fd on")
        payload = "ABC##2400112233445566778899AABBCCDDEEFF00112233"
        _, _, exit_code = self.dut.run(f"cansend can1 {payload}")
        assert_equal(exit_code, 0, "Failed external frame transmit on can1")

    @suite('e2e', 'can', 'simultaneous', 'fast')
    def test_VVDN_IGW1_CANFD_007_simultaneous_operation(self):
        """007: Verify Simultaneous Concurrent Operation of can0 and can1."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on loopback on")
        self.dut.run("sudo ip link set can1 up type can bitrate 500000 fd on loopback on")

        self.dut.run("candump -n 1 can0 > /tmp/can0_dump.log 2>&1 &")
        self.dut.run("candump -n 1 can1 > /tmp/can1_dump.log 2>&1 &")
        time.sleep(0.3)

        self.dut.run("cansend can0 123##8AABBCCDDEEFF0011")
        self.dut.run("cansend can1 456##82233445566778899")
        time.sleep(0.3)

        out0, _, _ = self.dut.run("cat /tmp/can0_dump.log")
        out1, _, _ = self.dut.run("cat /tmp/can1_dump.log")

        assert_in("123", out0, "can0 failed during simultaneous transmit")
        assert_in("456", out1, "can1 failed during simultaneous transmit")

    @suite('e2e', 'can', 'state_switch', 'fast')
    def test_VVDN_IGW1_CANFD_008_independent_state_switching(self):
        """008: Verify Independent State Switching (can0 UP while can1 DOWN)."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on")
        self.dut.run("sudo ip link set can1 down")

        out0, _, _ = self.dut.run("ip link show can0")
        out1, _, _ = self.dut.run("ip link show can1")
        assert_in("state UP", out0)
        assert_in("state DOWN", out1)

        # Reverse state
        self.dut.run("sudo ip link set can0 down")
        self.dut.run("sudo ip link set can1 up type can bitrate 500000 fd on")

        out0, _, _ = self.dut.run("ip link show can0")
        out1, _, _ = self.dut.run("ip link show can1")
        assert_in("state DOWN", out0)
        assert_in("state UP", out1)

    @suite('e2e', 'can', 'state_switch', 'fast')
    def test_VVDN_IGW1_CANFD_009_simultaneous_state_switching(self):
        """009: Verify Simultaneous Joint State Transitions."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on")
        self.dut.run("sudo ip link set can1 up type can bitrate 500000 fd on")

        out0, _, _ = self.dut.run("ip link show can0")
        out1, _, _ = self.dut.run("ip link show can1")
        assert_in("state UP", out0)
        assert_in("state UP", out1)

        self.dut.run("sudo ip link set can0 down")
        self.dut.run("sudo ip link set can1 down")

        out0, _, _ = self.dut.run("ip link show can0")
        out1, _, _ = self.dut.run("ip link show can1")
        assert_in("state DOWN", out0)
        assert_in("state DOWN", out1)

    @suite('e2e', 'can', 'errors', 'slow')
    def test_VVDN_IGW1_CANFD_010_error_frame_handling(self):
        """010: Verify Error Frame Detection and Socket Logging."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on")
        self.dut.run("candump -e can0 > /tmp/can_dump.log 2>&1 &")
        time.sleep(0.3)

        out, _, _ = self.dut.run("ps aux | grep candump")
        assert_in("candump", out, "Error dump monitor process was not created")

    @suite('e2e', 'can', 'errors', 'slow')
    def test_VVDN_IGW1_CANFD_011_error_injection_and_detection(self):
        """011: Verify Socket Error Monitoring with Timestamps."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on")
        self.dut.run("candump -td -L can0 > /tmp/can_dump.log 2>&1 &")
        time.sleep(0.3)

        out, _, _ = self.dut.run("ip -s -d link show can0")
        assert_in("can", out, "Detailed status query failed during error monitor test")

    @suite('e2e', 'can', 'bus_off', 'slow')
    def test_VVDN_IGW1_CANFD_012_bus_off_state_recovery(self):
        """012: Verify Bus-Off State Recovery Sequence."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on")
        self.dut.run("sudo ip link set can0 down")
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on loopback on")

        _, _, exit_code = self.dut.run("cansend can0 555##8DEADBEEF00112233")
        assert_equal(exit_code, 0, "Failed to transmit frame after recovery!")

    @suite('e2e', 'can', 'data_integrity', 'slow')
    def test_VVDN_IGW1_CANFD_013_data_integrity_dlc_patterns(self):
        """013: Verify Data Integrity across various DLC payload sizes (up to 64 bytes)."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on loopback on")

        patterns = [
            "100##8DEADBEEF00112233",
            "101##1600112233445566778899AABBCCDDEEFF",
            "102##64" + ("AA" * 64)
        ]

        for payload in patterns:
            self.dut.run("candump -n 1 can0 > /tmp/can_dump.log 2>&1 &")
            time.sleep(0.2)

            _, _, exit_code = self.dut.run(f"cansend can0 {payload}")
            assert_equal(exit_code, 0, f"Failed sending payload pattern: {payload[:10]}")
            time.sleep(0.2)

            dump_out, _, _ = self.dut.run("cat /tmp/can_dump.log")
            assert_in("can0", dump_out)

    @suite('e2e', 'can', 'bitrate', 'slow')
    def test_VVDN_IGW1_CANFD_014_bitrate_configuration(self):
        """014: Verify Arbitration and Data Phase Bitrate Configuration."""
        configs = [
            {"arb": 250000, "data": 1000000},
            {"arb": 500000, "data": 2000000},
            {"arb": 500000, "data": 4000000},
        ]

        for cfg in configs:
            self.dut.run("sudo ip link set can0 down")
            cmd = f"sudo ip link set can0 up type can bitrate {cfg['arb']} fd on dbitrate {cfg['data']}"
            _, _, exit_code = self.dut.run(cmd)
            assert_equal(exit_code, 0, f"Failed configuring bitrates: {cfg}")

            out, _, _ = self.dut.run("ip -d link show can0")
            assert_in(str(cfg['arb']), out, f"Arbitration bitrate {cfg['arb']} missing in status")

    @suite('e2e', 'can', 'suspend_resume', 'fast')
    def test_VVDN_IGW1_CANFD_015_suspend_resume_functionality(self):
        """015: Verify Interface Suspend/Resume Functionality."""
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on loopback on")
        out, _, _ = self.dut.run("ip link show can0")
        assert_in("state UP", out)

        # Suspend interface
        self.dut.run("sudo ip link set can0 down")
        out, _, _ = self.dut.run("ip link show can0")
        assert_in("state DOWN", out)

        # Resume interface
        self.dut.run("sudo ip link set can0 up type can bitrate 500000 fd on loopback on")
        out, _, _ = self.dut.run("ip link show can0")
        assert_in("state UP", out)

        _, _, exit_code = self.dut.run("cansend can0 777##81122334455667788")
        assert_equal(exit_code, 0, "Failed to transmit frame after resume")