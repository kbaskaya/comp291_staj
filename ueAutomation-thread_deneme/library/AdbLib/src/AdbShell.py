import adb


class UeAutomation:
    adb_inst = None

    def __init__(self):
        self.adb_inst = adb.ADB()
        self.adb_inst.connect()

    def ue_list(self, detailed: bool = False, verbose: bool = True) -> dict:
        UEList = {}
        if detailed:
            pure_device_list = self.adb_inst.execute(["devices", "-l"]).splitlines()
            if len(pure_device_list) == 1:
                return UEList
            del (pure_device_list[0])
            for ue_str in pure_device_list:
                line = ue_str.split()  # l = ["emu1","device","detail","detail"]
                val = ""
                for s in line[1:]:
                    val += s
                    val += "; "
                UEList[line[0]] = val
        else:
            pure_device_list = self.adb_inst.execute(["devices"]).splitlines()
            if len(pure_device_list) == 1:
                return UEList
            del (pure_device_list[0])
            for ue_str in pure_device_list:
                line = ue_str.split("\t")
                UEList[line[0]] = line[1]
        if verbose:
            # print(UEList)
            a = 1
        return UEList

    def airplane_mode_on(self, connection, ue_id):
        """ Assumes device is rooted, or has Android 7 or below """
        output = self.__call_shell(connection, ue_id, "airplane_mode_on",
                                   [f"su 0 settings put global airplane_mode_on 1 && su 0 am broadcast -a "
                                    "android.intent.action.AIRPLANE_MODE"])
        if "result=0" not in output:
            # raise Exception("Error while turning on airplane mode.")
            print("Error while turning on airplane mode.")

    def airplane_mode_off(self, connection, ue_id):
        """ Assumes device is rooted, or has Android 7 or below """
        output = self.__call_shell(connection, ue_id, "airplane_mode_on",
                                   [f"su 0 settings put global airplane_mode_on 0 && su 0 am broadcast -a "
                                    "android.intent.action.AIRPLANE_MODE"])
        if "result=0" not in output:
            # raise Exception("Error while turning off airplane mode.")
            print(f"Error while turning off airplane mode.")

    def send_iperf(self, connection, ue_id, ip, buffer_bytes_length, bandwidth, periodic_bandwidth=1, timeout=10):
        """ Assumes iperf executable is at "/data/local/tmp/iperf" """
        self.__call_shell(connection, ue_id, "send_iperf", [
            f"./data/local/tmp/iperf -c {ip} -l {buffer_bytes_length} -b {bandwidth} -i {periodic_bandwidth}"],
                          timeout=timeout)

    def send_ping(self, connection, ue_id, ip, timeout=10):
        self.__call_shell(connection, ue_id, "send_ping()", [f"ping -W {timeout} {ip}"], timeout=timeout)

    def __call_shell(self, connection, ue_id, func_id, shell_list: list, timeout=None):
        devices = self.ue_list(verbose=False)
        output = None
        if ue_id.casefold() == "all":  # all devices
            for device_id in devices:
                # execute shellcode in series
                self.adb_inst.target_device = device_id
                try:
                    output = self.adb_inst.shell(shell_list, timeout=timeout)
                    print(output)
                except Exception as e:
                    print(f"Failed {func_id} for device: {device_id}")
                    print(e)

        else:  # 1 device
            if (ue_id in devices) and (devices[ue_id] == "device"):
                self.adb_inst.target_device = ue_id
                try:
                    output = self.adb_inst.shell(shell_list, timeout=timeout)
                    print(output)
                except Exception as e:
                    print(f"Failed {func_id} for device: {ue_id}")
                    print(e)
            else:
                print("Device does not exist or not powered on yet.")
        return output
