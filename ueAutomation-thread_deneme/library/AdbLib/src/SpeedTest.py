from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
import threading
import ADBShellViaSSH
from ui_helper import *
import datetime


def speedtest_appium(adb_ssh, device=""):
    """
    Run the "SpeedTest by Ookla" app through Appium and return results. Only works one device per call.
    :param adb_ssh: ADBShellViaSSH instance
    :param device: device id
    :return: SpeedTest results in a dictionary
    """
    if device == "":
        devices = adb_ssh.refresh_device_list()
        if len(devices) == 1:
            device = list(devices.keys())[0]
        else:
            raise Exception("Choose a device.")
    capabilities = dict(
        platformName='Android',
        automationName='uiautomator2',
        deviceName='ignore',
        appPackage='org.zwanoo.android.speedtest',
        appActivity='com.ookla.mobile4.screens.main.MainActivity',
        newCommandTimeout=360,
        udid=device
    )

    try:
        adb_ssh.execute_adb_shell("rm /sdcard/window_dump.xml", device=device, verbose=0)
    except Exception:
        pass
    try:
        a = webdriver.Remote('http://localhost:4723', capabilities)
        waiting = WebDriverWait(driver=a, timeout=120)
    except Exception as e:
        print("Failed at Appium initialization.")
        raise e
    try:
        click_by(a, waiting, AppiumBy.ID, 'com.android.permissioncontroller:id/permission_allow_button')
        click_by(a, waiting, AppiumBy.ID, 'org.zwanoo.android.speedtest:id/welcome_message_next_button')
        click_by(a, waiting, AppiumBy.ID, 'org.zwanoo.android.speedtest:id/permissions_continue_button')
        click_by(a, waiting, AppiumBy.ID, 'com.android.permissioncontroller:id/permission_allow_foreground_only_button')
        click_by(a, waiting, AppiumBy.ID, 'com.android.permissioncontroller:id/permission_deny_button')
        click_by(a, waiting, AppiumBy.ID, 'org.zwanoo.android.speedtest:id/enable_bg_sampling_do_not_allow_button')
        click_by(a, waiting, AppiumBy.ID, 'org.zwanoo.android.speedtest:id/gdpr_privacy_next_button')
        click_by(a, waiting, AppiumBy.ID, 'org.zwanoo.android.speedtest:id/go_button')
        click_by(a, waiting, AppiumBy.ID, 'org.zwanoo.android.speedtest:id/suite_completed_feedback_assembly_detailed_result')
        waiting.until(lambda x: x.find_element(by=AppiumBy.ID, value="org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value"))
        source1 = a.page_source  # Biraz uzun sürüyor, alternatif olarak teker teker find_element denenebilir
        # a.execute_script("mobile: scroll",{"direction": "down","strategy": "accessibility id","selector": "org.zwanoo.android.speedtest:id/ookla_view_result_detail_map_label"})
        adb_ssh.execute_adb_shell(f"input roll 0 100", device=device)
        waiting.until(lambda x: x.find_element(by=AppiumBy.ID, value="org.zwanoo.android.speedtest:id/ookla_view_result_detail_map_label"))
        # ta = TouchAction(a)
        source2 = a.page_source
    except Exception as e:
        print("Failed while running Appium.")
        raise e
    return data_from_result_page_appium([source1, source2])


def speedtest_shell(adb_ssh: ADBShellViaSSH.ADBShellViaSSH, device=""):
    """
    Run the SpeedTest by Ookla app through device shell and return results. Assumes the app was launched before and
    the permissions were granted. Which means function expects to see the "Go" button when the app launches. (Not
    permission request notifications.) Requires unlocked screen.
    :param adb_ssh: ADBShellViaSSH instance
    :param device: device id
    :return: SpeedTest results in a dictionary, or a bigger dictionary containing all the devices' results
    """
    return _speedtest_shell(adb_ssh, device, None)


def _speedtest_shell(adb_ssh: ADBShellViaSSH.ADBShellViaSSH, device="", dic=None):
    """
    Run the SpeedTest by Ookla app through device shell and return results. Assumes the app was launched before and
    the permissions were granted. Which means function expects to see the "Go" button when the app launches. (Not
    permission request notifications.) Requires unlocked screen.
    :param adb_ssh: ADBShellViaSSH instance
    :param device: device id
    :param dic: Used internally for thread results, DO NOT USE
    :return: SpeedTest results in a dictionary, or a bigger dictionary containing all the devices' results
    """
    devices = adb_ssh.refresh_device_list()
    if device == "":
        if len(devices) == 1:
            device = list(devices.keys())[0]
        else:
            raise Exception("Specify a device")
    if device.casefold() == "all":
        jobs = []
        returns = {}
        for d in devices:
            j = threading.Thread(target=_speedtest_shell, args=(adb_ssh, d, returns,))
            jobs.append(j)
            returns[d] = ""
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        return returns
    adb_ssh.execute_adb_shell("am force-stop org.zwanoo.android.speedtest", device=device)
    adb_ssh.execute_adb_shell("am start org.zwanoo.android.speedtest/com.ookla.mobile4.screens.main.MainActivity",
                              device=device)
    try:
        adb_ssh.execute_adb_shell("rm /sdcard/window_dump.xml", device=device)
    except Exception:
        pass
    dump_find_click(adb_ssh, device, 'resource-id', "org.zwanoo.android.speedtest:id/go_button")
    time.sleep(75)  # TODO Testin bittiğini kontrol edemiyoruz
    adb_ssh.execute_adb_shell("am force-stop org.zwanoo.android.speedtest", device=device)
    adb_ssh.execute_adb_shell("am start org.zwanoo.android.speedtest/com.ookla.mobile4.screens.main.MainActivity",
                              device=device)
    # UiAutomator, test sonrası ekranı okuyamadığı için uygulamayı restart ediyoruz.
    dump_find_click(adb_ssh, device, 'resource-id', "org.zwanoo.android.speedtest:id/side_menu_hamburger_button")
    dump_find_click(adb_ssh, device, 'resource-id', "org.zwanoo.android.speedtest:id/side_menu_results")
    dump_find_click(adb_ssh, device, 'resource-id', "org.zwanoo.android.speedtest:id/table_cell_download")
    time.sleep(1)
    adb_ssh.execute_adb_shell("uiautomator dump", device=device, verbose=0)
    xml_str1 = adb_ssh.execute_adb_shell("cat /sdcard/window_dump.xml", device=device, verbose=0)[device][0]
    adb_ssh.execute_adb_shell(f"input roll 0 100", device=device)
    time.sleep(1)
    adb_ssh.execute_adb_shell("uiautomator dump", device=device, verbose=0)
    xml_str2 = adb_ssh.execute_adb_shell("cat /sdcard/window_dump.xml", device=device, verbose=0)[device][0]
    r = data_from_result_page([xml_str1, xml_str2])
    adb_ssh.execute_adb_shell("am force-stop org.zwanoo.android.speedtest", device=device)
    try:
        cur_date = adb_ssh.execute_adb_shell("date +'%D %I%:%M %p'", device=device)[device][0]
    except Exception:
        raise Exception("Could not get device current date.")
    cur_date = datetime.datetime.strptime(cur_date, "%m/%d/%y %I:%M %p")
    test_date = datetime.datetime.strptime(r['Time'].replace(',', ''), "%m/%d/%y %I:%M %p")
    # bu doğruysa, güncel bir test yok demek -> return -1
    if (cur_date - test_date).total_seconds() / 60 > 4:
        r = "Unexpected error occurred."
    # Bu kısım sadece devices "all" olunca, threadlerin outputlarını kaydetmek için kullanılıyor.
    if dic is not None:
        dic[device] = r
    return {device: r}
