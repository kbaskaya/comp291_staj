import time
import paramiko
import threading
from ui_helper import dump_find_click


class ADBShellViaSSH:
    """
    Hold the SSH connection to a remote server, which has ADB and UEs connected.
    """
    """client = None
    _cli = -1  # 0 for "shell", 1 for "cmd.exe"
    adb_path = "adb"
    device_list = {}
    active_list = []
    finished_list = []
    _job_counter = -1"""

    def __init__(self, hostname, port=paramiko.config.SSH_PORT, username=None, password=None,
                 pkey=None, key_filename=None, timeout=None, allow_agent=True, look_for_keys=True,
                 compress=False, sock=None, gss_auth=False, gss_kex=False, gss_deleg_creds=True,
                 gss_host=None, banner_timeout=None, auth_timeout=None, gss_trust_dns=True,
                 passphrase=None, disabled_algorithms=None, cli=None, path_to_adb=None):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        self.device_list = {}
        self.active_list = []
        self.finished_list = []
        self._job_counter = -1
        self.my_lock = threading.Lock()
        self.adb_path = "adb"
        if path_to_adb:
            self.adb_path = path_to_adb
        self.set_cli(cli)
        self.client.connect(hostname, port, username, password, pkey, key_filename, timeout,
                            allow_agent, look_for_keys, compress, sock, gss_auth, gss_kex, gss_deleg_creds, gss_host,
                            banner_timeout, auth_timeout, gss_trust_dns, passphrase, disabled_algorithms)
        #  self.my_transport = self.client.get_transport()
        if self._cli == 0:
            stdin, stdout, stderr = self.client.exec_command("adb help")
        else:
            stdin, stdout, stderr = self.client.exec_command("adb help")
        stdout.readlines()
        err = stderr.readlines()
        if len(err):
            self.client.close()
            enum = ["Linux", "Windows"]
            raise Exception(f"Couldn't execute {enum[self._cli]} command at remote.")

    def __del__(self):
        self.client.close()

    def set_cli(self, cli=None):
        if cli == "shell":
            self._cli = 0
        elif cli == ("cmd" or "cmd.exe"):
            self._cli = 1
        while not (-1 < self._cli < 2):
            try:
                x = int(input("Pick 0 for Linux, 1 for Windows: "))
            except ValueError:
                print("Enter a valid integer.")
            else:
                self._cli = x

    @staticmethod
    def fix_output(out_err) -> list:
        """input should be list of lines"""
        lines = out_err
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
        return lines

    def clear_finished_jobs(self):
        self.finished_list = []

    def get_finished_jobs(self):
        return self.finished_list

    def get_active_jobs(self):
        return self.active_list

    def refresh_active_jobs(self, verbose=1) -> int:
        counter = 0
        for job in self.active_list:
            if job.check_finish():
                self.finished_list.append(job)
                self.active_list.remove(job)
                counter += 1
        if verbose:
            print(counter, "new jobs finished.")
        return counter

    def refresh_device_list(self) -> dict:
        self.device_list.clear()
        stdin, stdout, stderr = self.client.exec_command(f"{self.adb_path} devices")
        lines = stdout.readlines()
        err = self.fix_output(stderr.readlines())
        for i in range(1, len(lines) - 1):
            lines[i] = lines[i].strip()
            x = lines[i].split()
            if x[1] == "device":
                x[1] = "online"
            self.device_list[x[0]] = x[1]
        if err:
            raise Exception(err)
        return self.device_list

    def execute_adb(self, adb_command: str = "devices -l", device: str = "", func_id: object = "execute_adb",
                    verbose: object = 1, blocking: object = True, timeout: object = 30) -> list:
        """
        Execute adb commands, in series. Does NOT support device="all".
        :param func_id: function that called this, for debugging
        :param adb_command:  adb command
        :param device: device id for ADB ("all" does not work!)
        :param verbose: prints the stdout/output of command, used only when commanding single device
        :param blocking: Set as "false" to run in background
        :param timeout: timeout
        :return: stdout/output of command as a list of lines, None if nonblocking
        """
        return self._execute_adb(adb_command, device, func_id, verbose, blocking, timeout)

    # blocking check
    def _execute_adb(self, adb_command: str = "devices -l", device: str = "", func_id="execute_adb",
                    verbose=1, blocking=True, timeout=30, dic=None) -> list:
        """
        Execute adb commands, in series. Does NOT support device="all".
        :param func_id: function that called this, for debugging
        :param adb_command:  adb command
        :param device: device id for ADB ("all" does not work!)
        :param verbose: prints the stdout/output of command, used only when commanding single device
        :param blocking: Set as "false" to run in background
        :param timeout: timeout
        :param dic: Only used to pass outputs of threads, DO NOT USE
        :return: stdout/output of command as a list of lines, None if nonblocking
        """
        out = None
        if device:
            adb_command = "-s " + device + " " + adb_command
        try:
            self.my_lock.acquire()
            self._job_counter += 1
            stdin, stdout, stderr = self.client.exec_command(self.adb_path + " " + adb_command, timeout=timeout)
            if blocking:  # blocking, print output now
                self.my_lock.release()
                out = self.fix_output(stdout.readlines())
                err = self.fix_output(stderr.readlines())
                if dic:
                    dic[device] = out + err
                if verbose:
                    for line in out:
                        print(line)
                if err:
                    raise Exception(err)
            else:  # nonblocking, fill buffer for later
                self.active_list.append(self.ParamikoContainer(device, func_id, self._job_counter, stdin, stdout, stderr))
                self.my_lock.release()
        except Exception as e:
            if self.my_lock.locked():
                self.my_lock.release()
            raise e
        return out

    # devices "all" check
    def execute_adb_shell(self, shell_command: str = "ls", device: str = "", func_id="execute_adb_shell",
                          verbose=1, blocking=True, timeout=30) -> dict:
        """
        Execute shellcode on devices, in series
        :param shell_command: shell command
        :param device: device id for ADB ("all" runs for all connected devices)
        :param func_id: function that called this, for debugging
        :param verbose: prints the stdout/output of command, used only when commanding single device
        :param blocking: Set as "false" to run in background
        :param timeout: timeout
        :return: stdout/output of command as a list of lines
        """
        devices = self.refresh_device_list()
        output = {}
        if len(devices) == 0:
            raise Exception("Could not find any devices.")
        # "ALL" DEVICES
        elif device.casefold() == "all":
            threads = []
            for device_id in devices:
                if devices[device_id] == "online":
                    try:
                        j = threading.Thread(target=self._execute_adb, args=("shell "+shell_command, device_id, func_id, 0, blocking, timeout, output,))
                        threads.append(j)
                        output[device_id] = ""
                        """BU KISIM ESKİ, THREAD OLMAYAN HALİ. ÜST "3 SATIR", ÜSTTE "threads = []" VE ALTTA "threads start ve joinler" SİLİNİP BU EKLENEBİLİR
                        m_output = self.execute_adb("shell " + shell_command, device_id, func_id, 0, blocking, timeout)
                        print(f"{device_id}: {m_output}")
                        output[device_id] = m_output"""
                    except Exception as e:
                        if verbose:
                            print(f"Failed {func_id} for device: {device_id}")
                            print(repr(e))
                        # raise e
                else:
                    output[device_id] = "Device unreachable."
                    # raise Exception(f"Cannot reach device {device_id}.")
            for j in threads:
                j.start()
            for j in threads:
                j.join()
        # SINGLE DEVICE
        else:
            if not device and len(devices) == 1:  # device is not given
                device = list(devices.keys())[0]
            elif not device:
                raise Exception("There are multiple devices. Choose one device.")
            if device in devices and devices[device] == "online":
                try:
                    output[device] = self.execute_adb("shell " + shell_command, device, func_id, verbose, blocking, timeout)
                except Exception as e:
                    output[device] = e
                    if verbose:
                        print(f"Failed {func_id} for device: {device}")
                        print(repr(e))
                    raise e
            else:
                output[device] = f"Cannot reach device {device}."
                raise Exception(f"Cannot reach device {device}.")
        return output

    def airplane_mode_on(self, connection=None, ue_id="", blocking=True):
        """ Assumes device is rooted, or has Android 7 or below """
        output = self.execute_adb_shell("\"su 0 settings put global airplane_mode_on 1 && su 0 am broadcast -a "
                                        "android.intent.action.AIRPLANE_MODE\"", ue_id, "airplane_mode_on",
                                        blocking=blocking)
        if ue_id == "all":
            return output
        o = list(output.values())[0]
        if blocking and (len(o) != 2 or "result=0" not in o[1]):
            raise Exception("Error while turning on airplane mode.")
        """if blocking:
            for device in output.keys():
                if len(output[device]) != 2 or "result=0" not in output[device][1]:
                    raise Exception("Error while turning on airplane mode.")"""
        return output

    def airplane_mode_off(self, connection=None, ue_id="", blocking=True):
        """ Assumes device is rooted, or has Android 7 or below """
        output = self.execute_adb_shell("\"su 0 settings put global airplane_mode_on 0 && su 0 am broadcast -a "
                                        "android.intent.action.AIRPLANE_MODE\"", ue_id, "airplane_mode_off",
                                        blocking=blocking)
        if ue_id == "all":
            return output
        o = list(output.values())[0]
        if blocking and (len(o) != 2 or "result=0" not in o[1]):
            raise Exception("Error while turning on airplane mode.")
        """if blocking:
            for device in output.keys():
                if len(output[device]) != 2 or "result=0" not in output[device][1]:
                    raise Exception("Error while turning on airplane mode.")"""
        return output

    def airplane_mode_on_ui(self, connection=None, ue_id=""):
        """ Turns airplane mode on through UI """
        return self._airplane_mode_toggle_settings_ui(None, ue_id, None, '0')

    def airplane_mode_off_ui(self, connection=None, ue_id=""):
        """ Turns airplane mode off through UI """
        return self._airplane_mode_toggle_settings_ui(None, ue_id, None, '1')

    def _airplane_mode_toggle_settings_ui(self, connection=None, ue_id="", dic=None, on='1'):
        """ Turns airplane mode off through UI """
        devices = self.refresh_device_list()
        if ue_id == "":
            if len(devices) == 1:
                ue_id = list(devices.keys())[0]
            else:
                raise Exception("Specify a device")
        if ue_id.casefold() == "all":
            jobs = []
            returns = {}
            for d in devices:
                j = threading.Thread(target=self._airplane_mode_toggle_settings_ui, args=(None, d, returns, on,))
                jobs.append(j)
                returns[d] = ""
            for j in jobs:
                j.start()
            for j in jobs:
                j.join()
            return returns
        airmode = self.execute_adb_shell("settings get global airplane_mode_on", ue_id, "airplane_mode_settings_ui")[ue_id][0]
        if airmode == on:
            try:
                self.execute_adb_shell("rm /sdcard/window_dump.xml", device=ue_id)
            except Exception:
                pass
            self.execute_adb_shell("am force-stop com.android.settings", ue_id, "airplane_mode_settings_ui")
            time.sleep(0.5)
            self.execute_adb_shell("input keyevent 3", ue_id, "airplane_mode_settings_ui")
            self.execute_adb_shell("am start -a android.settings.AIRPLANE_MODE_SETTINGS", ue_id, "airplane_mode_settings_ui")
            dump_find_click(self, ue_id, 'resource-id', "switch_widget")
            self.execute_adb_shell("am force-stop com.android.settings", ue_id, "airplane_mode_settings_ui")
            time.sleep(0.5)
            self.execute_adb_shell("input keyevent 3", ue_id, "airplane_mode_settings_ui")
        r = self.execute_adb_shell("settings get global airplane_mode_on", ue_id, "airplane_mode_settings_ui")[ue_id][0]
        if dic is not None:
            dic[ue_id] = r
        if airmode == 'null' or r == 'null':
            raise Exception("Failed while getting airplane mode.")
        return {ue_id: r}

    # TODO Iperf timeout, mesaj için değil, bütün komut için bitmesi gereken süre olarak çalışıyor
    def send_iperf(self, connection=None, ue_id="", ip="localhost", port=5201, buffer_bytes_length=8192, bandwidth=0,
                   periodic_bandwidth=1, time=10, blocking=True, path_to_iperf="/data/local/tmp/iperf", timeout=20):
        """ Assumes iperf executable is at "/data/local/tmp/iperf" """
        if timeout < time:
            timeout = time * 1.5
        output = self.execute_adb_shell(
            f"{path_to_iperf} -c {ip} -p {port} -l {buffer_bytes_length} -b {bandwidth} -i {periodic_bandwidth} -t {time}",
            ue_id, "send_iperf", blocking=blocking, timeout=timeout)
        return output

    def send_ping(self, connection=None, ue_id="", ip="localhost", count=10, blocking=True, timeout=10):
        output = self.execute_adb_shell(f"ping -W {timeout} -c {count} {ip}", ue_id, "send_ping", blocking=blocking,
                                        timeout=timeout)
        return output

    def get_sebeke_kayit_info(self, connection=None, ue_id="", blocking=True):
        data_command = "\"dumpsys telephony.registry | grep 'mServiceState' | tr ', ' '\\n' | grep getRilDataRadioTechnology | cut -d '(' -f 2 | cut -d ')' -f 1\""
        #voice_command = "\"dumpsys telephony.registry | grep 'mServiceState' | tr ', ' '\\n' | grep getRilVoiceRadioTechnology | cut -d '(' -f 2 | cut -d ')' -f 1\""
        output = self.execute_adb_shell(data_command, ue_id, "get_sebeke_kayit_info", verbose=0, blocking=blocking)
        return output

    # o.read(len(i.channel.in_buffer))  -> Bitmesini beklemeden bufferi oku
    # o.channel.exit_status_ready()     -> Bitiş kontrolü
    class ParamikoContainer:
        """device = None
        func = ""
        job_id = None
        stdin = None
        stdout = None
        stderr = None
        total_out = None"""

        def __init__(self, device, func, job_id, stdin, stdout, stderr):
            self.device = device
            self.func = func
            self.job_id = job_id
            self.stdin = stdin
            self.stdout = stdout
            self.stderr = stderr
            self.total_out = []

        def check_finish(self):
            return self.stdout.channel.exit_status_ready()

        def print(self, intro=True):
            if intro:
                print(f"{self.device} ({self.job_id}):  {self.func}")
            err = ADBShellViaSSH.fix_output(self.stderr.readlines())
            out = (self.stdout.read(len(self.stdout.channel.in_buffer)))
            out = ADBShellViaSSH.fix_output(out.decode("UTF-8").splitlines())
            for line in out:
                print(line)
                self.total_out.append(line)
            if err:
                for line in err:
                    print(line)
                    self.total_out.append(line)
                    raise Exception(err)
            return out

        def print_all(self):
            print(self.device, f"({self.job_id}): ", self.func)
            for line in self.total_out:
                print(line)
            self.print(False)
            return self.total_out

        def close(self):
            self.stdin.channel.close()
