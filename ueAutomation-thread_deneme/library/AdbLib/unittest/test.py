import time
import unittest
from unittest.mock import patch
import ADBShellViaSSH
import paramiko
import appium
import io
import os
import threading
import SpeedTest
import datetime

# If side_effect is an iterable then each call to the mock will return the next value from the iterable.
ui_counter = 0  # 0-x speedtest, 10-11 airplane settings


class MChnnl:
    status = False
    in_buffer = None

    def __init__(self, buffer):
        self.status = False
        self.in_buffer = buffer

    def exit_status_ready(self):
        return self.status


class MStrIO(io.StringIO):

    def __init__(self, *args):
        super().__init__(*args)
        self.channel = MChnnl(self)

    def __len__(self):
        temp = self.tell()
        self.seek(0, os.SEEK_END)
        pos = self.tell()
        self.seek(temp)
        return pos


class MBytIO(io.BytesIO):

    def __init__(self, *args):
        super().__init__(*args)
        self.channel = MChnnl(self)

    def __len__(self):
        temp = self.tell()
        self.seek(0, os.SEEK_END)
        pos = self.tell()
        self.seek(temp)
        return pos

    def readlines(self, __hint: int = ...):
        lines = super().readlines()
        lines2 = []
        for line in lines:
            lines2.append(line.decode("utf8"))
        return lines2


class MyBlockingTestCases(unittest.TestCase):

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_airplane_mode_on_success(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        o = a.airplane_mode_on(ue_id="emulator-5554", blocking=True)

        self.assertTrue("Broadcast completed: result=0" in o["emulator-5554"])  # add assertion here

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_airplane_mode_off_success(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        o = a.airplane_mode_off(ue_id="emulator-5554", blocking=True)

        self.assertTrue("Broadcast completed: result=0" in o["emulator-5554"])  # add assertion here

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_sebeke_info_success(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        o = a.get_sebeke_kayit_info(ue_id="emulator-5554", blocking=True)

        self.assertTrue(("NR_SA" in o["emulator-5554"]) or ("HSPA" in o["emulator-5554"]) or
                        ("LTE" in o["emulator-5554"]) or ("EDGE" in o["emulator-5554"]))  # add assertion here

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_ping_success(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        o = a.send_ping(ue_id="emulator-5554", blocking=True)

        self.assertTrue("--- localhost ping statistics ---" in o["emulator-5554"])  # add assertion here

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_iperf_success(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        o = a.send_iperf(ip="23.251.106.210", ue_id="emulator-5554", blocking=True)

        self.assertTrue("iperf Done." in o["emulator-5554"])  # add assertion here


    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_nonexistent_ue_id_fail(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")

        with self.assertRaises(Exception):
            o = a.get_sebeke_kayit_info(ue_id="emulator-nonexistent", blocking=True)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_unspecified_ue_id_fail(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        with self.assertRaises(Exception):
            o = a.get_sebeke_kayit_info(blocking=True)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(ADBShellViaSSH.ADBShellViaSSH, 'refresh_device_list', autospec=True)
    def test_offline_ue_id_fail(self, mock_refresh_device_list, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success
        mock_refresh_device_list.side_effect = (
            lambda self, *args: {"emulator-5554": "offline", "emulator-5556": "offline"})

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")

        with self.assertRaises(Exception):
            o = a.get_sebeke_kayit_info(ue_id="emulator-5554", blocking=True)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(ADBShellViaSSH.ADBShellViaSSH, 'refresh_device_list', autospec=True)
    def test_empty_ue_id_list_fail(self, mock_refresh_device_list, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success
        mock_refresh_device_list.side_effect = (lambda self, *args: {})

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")

        with self.assertRaises(Exception):
            o = a.get_sebeke_kayit_info(ue_id="emulator-5554", blocking=True)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_all_ue_id_success(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")

        o = a.get_sebeke_kayit_info(ue_id="all", blocking=True)
        o = a.airplane_mode_on(ue_id="all", blocking=True)
        o = a.send_ping(ue_id="all", blocking=True)
        o = a.send_iperf(ip="23.251.106.210", ue_id="all", blocking=True)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_airplane_mode_no_su_access_fail(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_fail

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")

        with self.assertRaises(Exception):
            o = a.airplane_mode_on(ue_id="emulator-5554", blocking=True)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_sebeke_no_info_fail(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_fail

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")

        o = a.get_sebeke_kayit_info(ue_id="emulator-5554", blocking=True)
        self.assertFalse(("NR_SA" in o) or ("HSPA" in o) or ("LTE" in o) or ("EDGE" in o))  # add assertion here

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_ping_timeout_fail(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_fail

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")

        with self.assertRaises(Exception):
            o = a.send_ping(ue_id="emulator-5554", blocking=True)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_iperf_timeout_fail(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_fail

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")

        with self.assertRaises(Exception):
            o = a.send_iperf(ip="23.251.106.210", ue_id="emulator-5554", blocking=True)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(ADBShellViaSSH.ADBShellViaSSH, 'refresh_device_list', autospec=True)
    def test_one_offline_one_online_success(self, mock_refresh_device_list, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success
        mock_refresh_device_list.side_effect = (
            lambda self, *args: {"emulator-5554": "offline", "emulator-5556": "online"})

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")

        o = a.get_sebeke_kayit_info(ue_id="all", blocking=True)
        self.assertDictEqual(o, {"emulator-5554": "Device unreachable.", "emulator-5556": ["NR_SA"]})


class MyNonBlockingTestCases(unittest.TestCase):
    # Threadler job_id'de race condition yaşıyor. (Test için önemsiz bir hata)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_one_device_all_jobs_success(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        threads = [threading.Thread(target=a.airplane_mode_off, args=(None, "emulator-5554", False,)),
                   threading.Thread(target=a.send_iperf, args=(None, "emulator-5554", "23.251.106.210", 5201, 8192, 0,
                                                               1, 10, False, "/data/local/tmp/iperf", 20,)),
                   threading.Thread(target=a.get_sebeke_kayit_info, args=(None, "emulator-5554", False,)),
                   threading.Thread(target=a.send_ping, args=(None, "emulator-5554", "localhost", 10, False, 10,))]
        start_time = time.time()
        for t in threads:
            t.start()

        l = a.get_finished_jobs()
        i = 0
        while i < 4:
            x = a.refresh_active_jobs()
            time.sleep(1)
            for job in range(x):
                print(l[i].func)
                self.assertEqual(len(l[i].stderr), 0)
                i += 1

        end_time = time.time()
        for t in threads:
            t.join()

        self.assertGreater(28, end_time-start_time)

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_all_device_all_jobs_success(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        a.refresh_device_list()
        threads = [threading.Thread(target=a.airplane_mode_off, args=(None, "emulator-5554", False,)),
                   threading.Thread(target=a.send_iperf, args=(None, "emulator-5554", "23.251.106.210", 5201, 8192, 0,
                                                               1, 10, False, "/data/local/tmp/iperf", 20,)),
                   threading.Thread(target=a.get_sebeke_kayit_info, args=(None, "emulator-5554", False,)),
                   threading.Thread(target=a.send_ping, args=(None, "emulator-5554", "localhost", 10, False, 10,)),
                   threading.Thread(target=a.airplane_mode_off, args=(None, "emulator-5556", False,)),
                   threading.Thread(target=a.send_iperf, args=(None, "emulator-5556", "23.251.106.210", 5201, 8192, 0,
                                                               1, 10, False, "/data/local/tmp/iperf", 20,)),
                   threading.Thread(target=a.get_sebeke_kayit_info, args=(None, "emulator-5556", False,)),
                   threading.Thread(target=a.send_ping, args=(None, "emulator-5556", "localhost", 10, False, 10,))
                   ]

        for t in threads:
            t.start()

        l = a.get_finished_jobs()
        i = 0
        while i < 8:
            x = a.refresh_active_jobs()
            time.sleep(1)
            for job in range(x):
                print(l[i].func)
                self.assertEqual(len(l[i].stderr), 0)
                i+=1

        for t in threads:
            t.join()

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_one_device_one_job_fail(self, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_fail

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        a.refresh_device_list()
        threads = [threading.Thread(target=a.airplane_mode_off, args=(None, "emulator-5554", False,)),
                   ]
        start_time = time.time()
        for t in threads:
            t.start()
            time.sleep(1)

        while len(a.get_finished_jobs()) < 1:
            a.refresh_active_jobs()
            time.sleep(1)
        l = a.get_finished_jobs()
        for job in range(len(l)):
            with self.assertRaises(Exception):
                l.pop(0).print_all()

        end_time = time.time()
        for t in threads:
            t.join()

        self.assertGreater(25, end_time - start_time)


class MyUITestCases(unittest.TestCase):

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    def test_airplane_mode_on_ui_success(self, mock_exec_command, mock_connect):
        global ui_counter
        ui_counter = 10
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        o = a.airplane_mode_on_ui(ue_id="emulator-5554")
        self.assertTrue("1" in o["emulator-5554"])  # add assertion here

        o = a.airplane_mode_on_ui(ue_id="all")
        self.assertTrue("1" in o["emulator-5554"] and "1" in o["emulator-5556"])  # add assertion here

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(time, 'sleep', autospec=True)
    def test_speedtest_shell_success(self, mock_sleep, mock_exec_command, mock_connect):
        global ui_counter
        ui_counter = 0
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success
        mock_sleep.side_effect = (lambda self, *args : None)

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        o = SpeedTest.speedtest_shell(a, "emulator-5554")
        expectedout = {'emulator-5554': {'Server': 'Ridge Wireless -- Cupertino, CA', 'Time': '09/15/22, 4:28 PM', 'Download Speed': '14.9', 'Upload Speed': '9.19', 'Idle Ping': '248', 'Idle Jitter': '42', 'Idle Jitter Low': '206', 'Idle Jitter High': '310', 'Download Ping': '247', 'Download Jitter': '43', 'Download Jitter Low': '189', 'Download Jitter High': '1566', 'Upload Ping': '232', 'Upload Jitter': '40', 'Upload Jitter Low': '187', 'Upload Jitter High': '2120', 'Packet Loss': '0.0', 'Provider': 'Turkcell Superonline'}}
        self.assertEqual(o, expectedout)  # add assertion here

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(time, 'sleep', autospec=True)
    def test_wrong_ui_fail(self, mock_sleep, mock_exec_command, mock_connect):
        global ui_counter
        ui_counter = 15
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success
        mock_sleep.side_effect = (lambda self, *args: None)

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        with self.assertRaises(Exception):
            o = SpeedTest.speedtest_shell(a, "emulator-5554")

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(time, 'sleep', autospec=True)
    def test_ui_dump_fail(self, mock_sleep, mock_exec_command, mock_connect):
        def setup_fail(fail_part):
            global ui_counter
            ui_counter = 0

            def myf(self, cmd, timeout=None, *args):
                if fail_part in cmd:
                    return exec_command_fail(self, cmd, timeout, *args)
                return exec_command_success(self, cmd, timeout, *args)
            return myf

        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = setup_fail("uiautomator dump")
        mock_sleep.side_effect = (lambda self, *args: None)

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        with self.assertRaises(Exception) as ee:
            o = SpeedTest.speedtest_shell(a, "emulator-5554")
        self.assertTrue("Failed dumping UI" in str(ee.exception))

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(time, 'sleep', autospec=True)
    def test_invalid_xml_fail(self, mock_sleep, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = setup_fail("cat")
        mock_sleep.side_effect = (lambda self, *args: None)

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        with self.assertRaises(Exception) as ee:
            o = SpeedTest.speedtest_shell(a, "emulator-5554")
        self.assertTrue("No such file or directory" in str(ee.exception))

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(time, 'sleep', autospec=True)
    def test_get_date_fail(self, mock_sleep, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = setup_fail("date")
        mock_sleep.side_effect = (lambda self, *args: None)

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        with self.assertRaises(Exception) as ee:
            o = SpeedTest.speedtest_shell(a, "emulator-5554")
        self.assertTrue("Could not get device current date" in str(ee.exception))

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(time, 'sleep', autospec=True)
    def test_get_current_airplane_mode_fail(self, mock_sleep, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = setup_fail("settings get global airplane_mode_on")
        mock_sleep.side_effect = (lambda self, *args: None)

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        with self.assertRaises(Exception) as ee:
            o = a.airplane_mode_off_ui(ue_id="emulator-5554")
        self.assertTrue("Failed while getting airplane mode" in str(ee.exception))

    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(time, 'sleep', autospec=True)
    def test_data_from_result_pages_fail(self, mock_sleep, mock_exec_command, mock_connect):
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = setup_fail("settings get global airplane_mode_on")
        mock_sleep.side_effect = (lambda self, *args: None)

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        with self.assertRaises(Exception) as ee:
            o = a.airplane_mode_off_ui(ue_id="emulator-5554")
        self.assertTrue("Failed while getting airplane mode" in str(ee.exception))

    # TODO webdriver patchlenmedi, %100 exception
    @patch.object(paramiko.client.SSHClient, 'connect', autospec=True)
    @patch.object(paramiko.client.SSHClient, 'exec_command', autospec=True)
    @patch.object(SpeedTest.webdriver, 'Remote', autospec=True)
    @patch.object(SpeedTest.WebDriverWait, 'until', autospec=True)
    @patch.object(SpeedTest, 'click_by', autospec=True)
    @patch.object(appium.webdriver.webdriver.WebDriver, 'page_source', autospec=True)
    def test_speedtest_appium_success(self, mock_page_source, mock_click_by, mock_until, mock_Remote, mock_exec_command, mock_connect):
        global ui_counter
        ui_counter = 4
        mock_connect.side_effect = connect_success
        mock_exec_command.side_effect = exec_command_success
        mock_Remote.side_effect = (lambda self, *args: None)
        mock_until.side_effect = (lambda self, *args: None)
        mock_click_by.side_effect = (lambda self, *args: None)
        mock_page_source.side_effect = ui_chooser
        import xml.etree.ElementTree  # nedense burada importlamazsam test fail ediyor

        a = ADBShellViaSSH.ADBShellViaSSH("localhost", 22, "ulak", "123", cli="cmd")
        o = SpeedTest.speedtest_appium(a, "emulator-5554")
        # add assertion here


def setup_fail(fail_part):

    global ui_counter
    ui_counter = 0

    def myf(self, cmd, timeout=None, *args):
        if fail_part in cmd:
            return exec_command_fail(self, cmd, timeout, *args)
        return exec_command_success(self, cmd, timeout, *args)
    return myf


def ui_chooser():
    global ui_counter
    my_xml = ""
    if ui_counter == 0:
        f = open("go_12.xml", 'r')
    elif ui_counter == 1:
        f = open("go_12.xml", 'r')
    elif ui_counter == 2:
        f = open("sideresults_3.xml", 'r')
    elif ui_counter == 3:
        f = open("tablecell_4.xml", 'r')
    elif ui_counter == 4:
        f = open("result1_5.xml", 'r')
    elif ui_counter == 5:
        f = open("result2_6.xml", 'r')
    elif ui_counter == 10:
        f = open("off_e.xml", 'r')
    elif ui_counter == 11:
        f = open("on_e.xml", 'r')
    my_xml = f.read().replace('\n', '')
    my_xml = my_xml.replace('\r', '')
    f.close()
    return my_xml


def connect_success(self, *args):
    return None


def exec_command_success(self, cmd, timeout=None, *args):
    global ui_counter
    inn = MBytIO()
    out = MBytIO()
    err = MBytIO()

    if "su 0 settings put global airplane_mode_on" in cmd:
        out.write("Broadcasting: Intent { act=android.intent.action.AIRPLANE_MODE flg=0x400000 }\nBroadcast "
                  "completed: result=0\n".encode("utf8"))

    elif cmd.endswith("devices"):
        inn = MStrIO()
        out = MStrIO()
        err = MStrIO()
        out.write("List of devices attached\nemulator-5554\tdevice\nemulator-5556\tdevice\n\n")

    elif cmd.endswith("devices -l"):
        inn = MStrIO()
        out = MStrIO()
        err = MStrIO()
        out.write("List of devices attached\nemulator-5554\t\tdevice product:sdk_gphone64_x86_64 "
                  "model:sdk_gphone64_x86_64 device:emu64xa transport_id:6 \nemulator-5556\tdevice "
                  "product:sdk_gphone64_x86_64 model:sdk_gphone64_x86_64 device:emu64xa transport_id:7\n\n")

    elif "dumpsys telephony.registry" in cmd:
        out.write("NR_SA\n".encode("utf8"))

    elif "ping" in cmd:
        cmd_split = cmd.split()
        out.write(f"PING {cmd_split[9]} 56(84) bytes of data.".encode("utf8"))
        for i in range(int(cmd_split[8])):
            out.write(f"64 bytes from {cmd_split[9]}: icmp_seq={i + 1} ttl=?? time=0.123 ms\n".encode("utf8"))
            time.sleep(0.9)
        out.write(f"\n--- localhost ping statistics ---\n{cmd_split[8]} packets transmitted, {cmd_split[8]} received, "
                  f"0% packet loss, time {123 * int(cmd_split[8])}ms\nrtt min/avg/max/mdev = 0.123/0.123/0.123/0.123 "
                  f"ms\n".encode("utf8"))

    elif "iperf" in cmd:
        cmd_split = cmd.split()
        out.write(f"Connecting to host {cmd_split[6]}, port {cmd_split[8]}\n[  5] local 10.0.2.16 port 60748 "
                  f"connected to 23.251.106.210 port 5201\n[ ID] Interval           Transfer     Bitrate         Retr"
                  f"  Cwnd\n".encode("utf8"))
        for i in range(int(cmd_split[16])):
            out.write(f"[  5]   {i}.00-{i + 1}.00   sec   123 KBytes  1.23 Mbits/sec    0   12.3 KBytes\n".encode("utf8"))
            time.sleep(0.9)
        out.write(f"\n- - - - - - - - - - - - - - - - - - - - - - - - -\n[ ID] Interval           Transfer     "
                  f"Bitrate         Retr\n[  5]   0.00-{cmd_split[16]}.00  sec  12.3 MBytes  12.3 Mbits/sec    0      "
                  f"       sender\n[  5]   0.00-{cmd_split[16]}.15  sec  12.3 MBytes  12.3 Mbits/sec                  "
                  f"receiver\n\niperf Done.\n".encode("utf8"))

    elif "settings get global airplane_mode_on" in cmd:
        if ui_counter == 11:
            out.write("1\n".encode("utf8"))
        else:
            out.write("0\n".encode("utf8"))

    elif "am force-stop" in cmd:
        pass

    elif "input" in cmd:
        pass

    elif "am start" in cmd:
        out.write("Starting: Intent { something.something... }\n".encode("utf8"))

    elif "uiautomator dump" in cmd:
        out.write("UI hierchary dumped to: /sdcard/window_dump.xml\n".encode("utf8"))

    elif "cat /sdcard/window_dump.xml" in cmd:
        my_xml = ui_chooser()
        if ui_counter == 5:
            curtime = datetime.datetime.now().strftime("%m/%d/%y %I:%M %p")
            my_xml = my_xml.replace("09/15/22, 4:28 PM", curtime)
        out.write(my_xml.encode("utf8"))
        ui_counter += 1

    elif "date +'%D %I%:%M %p'" in cmd:
        out.write("09/15/22 01:06 PM".encode("utf8"))

    elif "rm" in cmd:
        pass

    elif cmd == "adb help":
        inn = MStrIO()
        out = MStrIO()
        err = MStrIO()
        out.write("MASS ADB HELP TEXT\n")
    else:
        inn = MStrIO()
        out = MStrIO()
        err = MStrIO()
        err.write("UNKNOWN_CASE\n")

    out.seek(0)
    err.seek(0)
    inn.channel.status = True
    out.channel.status = True
    err.channel.status = True
    return inn, out, err


def exec_command_fail(self, cmd, timeout=None, *args):
    inn = MBytIO()
    out = MBytIO()
    err = MBytIO()

    if "su 0 settings put global airplane_mode_on" in cmd:
        err.write("/system/bin/sh: su: inaccessible or not found\n".encode("utf8"))

    elif cmd.endswith("devices"):  # This is successfull, since we want devices to test failures on them
        inn = MStrIO()
        out = MStrIO()
        err = MStrIO()
        out.write("List of devices attached\nemulator-5554\tdevice\nemulator-5556\tdevice\n")

    elif cmd.endswith("devices -l"):  # This is successfull, since we want devices to test failures on them
        inn = MStrIO()
        out = MStrIO()
        err = MStrIO()
        out.write("List of devices attached\nemulator-5554\t\tdevice product:sdk_gphone64_x86_64 "
                  "model:sdk_gphone64_x86_64 device:emu64xa transport_id:6 \nemulator-5556\tdevice "
                  "product:sdk_gphone64_x86_64 model:sdk_gphone64_x86_64 device:emu64xa transport_id:7\n")

    elif "dumpsys telephony.registry" in cmd:
        out.write("\n".encode("utf8"))

    elif "ping" in cmd:
        cmd_split = cmd.split()
        out.write(f"PING {cmd_split[9]} 56(84) bytes of data.".encode("utf8"))
        time.sleep(timeout)
        raise paramiko.buffered_pipe.PipeTimeout

    elif "iperf" in cmd:
        cmd_split = cmd.split()
        out.write(f"Connecting to host {cmd_split[6]}, port {cmd_split[8]}\n[  5] local 10.0.2.16 port 60748 "
                  f"connected to 23.251.106.210 port 5201\n[ ID] Interval           Transfer     Bitrate         Retr"
                  f"  Cwnd\n".encode("utf8"))
        time.sleep(timeout)
        raise paramiko.buffered_pipe.PipeTimeout

    elif "settings get global airplane_mode_on" in cmd:
        out.write("null\n".encode("utf8"))

    elif "am force-stop" in cmd:
        err.write("SomeTestingException in force-stop\n".encode("utf8"))

    elif "input" in cmd:
        err.write("Exception in input".encode("utf8"))

    elif "am start" in cmd:
        out.write("Starting: Intent { something.something... }\n".encode("utf8"))
        err.write("Warning: am start something .....\n".encode("utf8"))

    elif "uiautomator dump" in cmd:
        pass
        #or err.write("ERROR: could not get idle state.\n".encode("utf8"))

    elif "cat /sdcard/window_dump.xml" in cmd:
        err.write("cat: /sdcard/window_dump.xml: No such file or directory\n".encode("utf8"))

    elif "date +'%D %I%:%M %p'" in cmd:
        pass

    elif "rm" in cmd:
        pass

    elif cmd == "adb help":
        inn = MStrIO()
        out = MStrIO()
        err = MStrIO()
        out.write("MASS ADB HELP TEXT\n")
    else:
        inn = MStrIO()
        out = MStrIO()
        err = MStrIO()
        err.write("UNKNOWN_CASE\n")

    out.seek(0)
    err.seek(0)
    inn.channel.status = True
    out.channel.status = True
    err.channel.status = True
    return inn, out, err


"""
    "settings get global airplane_mode_on"
        EX: out=['0'/'1'], ER: out=['null'] or err!=[]
    "am force-stop com.android.settings"
        EX: out=[]
    "input keyevent 3"
        EX: out=[]
    "am start -a android.settings.AIRPLANE_MODE_SETTINGS"
        EX: out=['Starting: Intent { act=android.settings.AIRPLANE_MODE_SETTINGS }'] err=[],
        ER: out=['Starting: Intent { act=android.settings.AIRPLANE_MODE_SETTINGS }'] and
            (err=['Warning: Activity not started, intent has been delivered to currently running top-most instance.'] or
            err=['Warning: Activity not started, its current task has been brought to the front'])
    "uiautomator dump --compressed"
        EX: out=['UI hierchary dumped to: /sdcard/window_dump.xml'],
        ER: err=['ERROR: could not get idle state.'] or
            out=[] err=[]
    "cat /sdcard/window_dump.xml"
        EX: out=['str_xml'], ER: err=['cat: /sdcard/winssdow_dump.xml: No such file or directory']
    "rm /sdcard/window_dump.xml" zaten try-except içinde
        EX: out=[], ER: err=[]
    "date +'%D %I%:%M %p'"
        EX: out=['09/15/22 01:06 PM']
"""
"""
    driver = webdriver.Remote('http://localhost:4723', capabilities)
        EX: <appium.webdriver.webdriver.WebDriver (session="2553e332-adb8-4e5d-b77f-b4a1b8d523d1")>,
        ER: Exception (MaxRetryError)(urllib3.exceptions.MaxRetryError) HERHANGI BIR CONNECTION LOSS
    waiter = WebDriverWait(driver=a, timeout=120)
        EX: <selenium.webdriver.support.wait.WebDriverWait (session="2553e332-adb8-4e5d-b77f-b4a1b8d523d1")>,
        ER: 
    waiter.until(lambda x: x.find_element(by=by, value=target))
        EX: <appium.webdriver.webelement.WebElement (session="0ed52c0c-c709-4293-9c64-304e0ac7e7a6", element="00000000-0000-00c3-ffff-ffff0000004c")>,
        ER: Exception (NoSuchElementError)
    driver.find_element(by=by, value=target).click()
        EX: None,
        ER: Exception (NoSuchElementError)
    source1 = driver.page_source
        EX: str_xml,
        ER: 
    """


if __name__ == '__main__':
    unittest.main()
