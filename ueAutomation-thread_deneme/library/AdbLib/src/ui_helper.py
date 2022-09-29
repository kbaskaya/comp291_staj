import time
import xml.dom
import xml.etree.ElementTree


def click_by(driver, waiter, by, target):
    waiter.until(lambda x: x.find_element(by=by, value=target))
    driver.find_element(by=by, value=target).click()


def dump_find_click(adb_ssh, device, attr, component):
    i = 0
    cat_xml = ""
    dump = ""
    while i < 30:
        i += 4
        time.sleep(1)
        try:
            dump = adb_ssh.execute_adb_shell("uiautomator dump --compressed", device=device, verbose=0)[device][0]
        except:
            dump = "Failed dumping UI."
            continue
        try:
            cat_xml = adb_ssh.execute_adb_shell("cat /sdcard/window_dump.xml", device=device, verbose=0)[device][0]
            if component not in cat_xml:
                raise Exception("Failed finding in UI: "+component)
            break
        except Exception as e:
            cat_xml = str(e)
            continue
    if i >= 30:
        raise Exception(dump + "\n" + cat_xml)
    x, y = calculate_bounds_from_xml_str(cat_xml, attr, component)
    adb_ssh.execute_adb_shell(f"input tap {x} {y}", device=device)


def calculate_bounds_from_xml_str(xml_str, attr, component):
    tr = xml.etree.ElementTree.fromstring(xml_str)
    for n in tr.findall('.//node'):
        if component in n.attrib[attr]:
        #if n.attrib[attr].startswith(component):
        #if n.attrib[attr] == component:
            bounds = n.attrib['bounds']
            i = 1
            j = bounds.find(",", i)
            x = int(bounds[i:j])
            i = bounds.find("]", j)
            y = int(bounds[j + 1:i])

            i = bounds.find("[", j) + 1
            j = bounds.find(",", i)
            x += int(bounds[i:j])
            i = bounds.find("]", j)
            y += int(bounds[j + 1:i])
            break
    return x/2, y/2


def data_from_result_page(xmls: list):
    myd = {'Server': ""}
    for xml_str in xmls:
        tr = xml.etree.ElementTree.fromstring(xml_str)
        for n in tr.findall('.//node'):
            if n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_download_container":
                for n2 in n.findall('.//'):
                    if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                        myd['Download Speed'] = n2.attrib['text']
            elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_upload_container":
                for n2 in n.findall('.//'):
                    if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                        myd['Upload Speed'] = n2.attrib['text']
            elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_idle_ping_container":
                for n2 in n.findall('.//'):
                    if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                        myd['Idle Ping'] = n2.attrib['text']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_jitter_value":
                        myd['Idle Jitter'] = n2.attrib['text']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_low_value":
                        myd['Idle Jitter Low'] = n2.attrib['text']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_high_value":
                        myd['Idle Jitter High'] = n2.attrib['text']
            elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_download_ping_container":
                for n2 in n.findall('.//'):
                    if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                        myd['Download Ping'] = n2.attrib['text']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_jitter_value":
                        myd['Download Jitter'] = n2.attrib['text']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_low_value":
                        myd['Download Jitter Low'] = n2.attrib['text']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_high_value":
                        myd['Download Jitter High'] = n2.attrib['text']
            elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_upload_ping_container":
                for n2 in n.findall('.//'):
                    if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                        myd['Upload Ping'] = n2.attrib['text']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_jitter_value":
                        myd['Upload Jitter'] = n2.attrib['text']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_low_value":
                        myd['Upload Jitter Low'] = n2.attrib['text']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_high_value":
                        myd['Upload Jitter High'] = n2.attrib['text']
            elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_packetloss_container":
                for n2 in n.findall('.//'):
                    if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                        myd['Packet Loss'] = n2.attrib['text']
            elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_network_container":
                for n2 in n.findall('.//'):
                    if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_label":
                        myd['Provider'] = n2.attrib['text']
            elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_sponsor_container":
                for n2 in n.findall('.//'):
                    if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_label":
                        myd['Server'] = n2.attrib['text'] + myd['Server']
                    elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_sublabel":
                        myd['Server'] = myd['Server'] + " -- " + n2.attrib['text']
            # test time
            elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/results_top_bar":
                for n2 in n.findall('.//'):
                    if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_result_top_bar_logo_text":
                        myd['Time'] = n2.attrib['text']
    return myd


def data_from_result_page_appium(xmls: list):
    myd = {'Server': ""}
    for xml_str in xmls:
        tr = xml.etree.ElementTree.fromstring(xml_str)
        for n in tr.findall('.//android.view.ViewGroup'):
            if 'resource-id' in n.attrib:
                if n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_download_container":
                    for n2 in n.findall('.//'):
                        if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                            myd['Download Speed'] = n2.attrib['text']
                elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_upload_container":
                    for n2 in n.findall('.//'):
                        if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                            myd['Upload Speed'] = n2.attrib['text']
                elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_idle_ping_container":
                    for n2 in n.findall('.//'):
                        if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                            myd['Idle Ping'] = n2.attrib['text']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_jitter_value":
                            myd['Idle Jitter'] = n2.attrib['text']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_low_value":
                            myd['Idle Jitter Low'] = n2.attrib['text']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_high_value":
                            myd['Idle Jitter High'] = n2.attrib['text']
                elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_download_ping_container":
                    for n2 in n.findall('.//'):
                        if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                            myd['Download Ping'] = n2.attrib['text']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_jitter_value":
                            myd['Download Jitter'] = n2.attrib['text']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_low_value":
                            myd['Download Jitter Low'] = n2.attrib['text']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_high_value":
                            myd['Download Jitter High'] = n2.attrib['text']
                elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_upload_ping_container":
                    for n2 in n.findall('.//'):
                        if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                            myd['Upload Ping'] = n2.attrib['text']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_jitter_value":
                            myd['Upload Jitter'] = n2.attrib['text']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_low_value":
                            myd['Upload Jitter Low'] = n2.attrib['text']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_high_value":
                            myd['Upload Jitter High'] = n2.attrib['text']
                elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_packetloss_container":
                    for n2 in n.findall('.//'):
                        if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_value":
                            myd['Packet Loss'] = n2.attrib['text']
                elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_network_container":
                    for n2 in n.findall('.//'):
                        if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_label":
                            myd['Provider'] = n2.attrib['text']
                elif n.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_detail_sponsor_container":
                    for n2 in n.findall('.//'):
                        if n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_label":
                            myd['Server'] = n2.attrib['text'] + myd['Server']
                        elif n2.attrib['resource-id'] == "org.zwanoo.android.speedtest:id/ookla_view_result_details_blob_sublabel":
                            myd['Server'] = myd['Server'] + " -- " + n2.attrib['text']
    return myd
    