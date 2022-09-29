# ueautomation
ue automation python library
- [ueautomation](https://github.com/galipo/ueAutomation/blob/main/README.md#ueautomation)
  - [AdbShellViaSSH.py](https://github.com/galipo/ueAutomation/blob/main/README.md#adbshellsshpy)
    - [ADBShellViaSSH](https://github.com/galipo/ueAutomation/blob/main/README.md#adbshellviassh)
    - [ParamikoContainer](https://github.com/galipo/ueAutomation/blob/main/README.md#paramikocontainer)
    - [Exceptionlar](https://github.com/galipo/ueAutomation/blob/main/README.md#komutlarda-al%C4%B1nan-hatalar%C4%B1n-kontrol%C3%BC)
  - [adb / idb Genel Bilgi](https://github.com/galipo/ueAutomation/blob/main/README.md#adb--idb-genel-bilgi)
    - [Android Debug Bridge (adb)](https://github.com/galipo/ueAutomation/blob/main/README.md#android-debug-bridge-adb)
      - [Kurulum](https://github.com/galipo/ueAutomation/blob/main/README.md#kurulum)
      - [Android Emulatörü](https://github.com/galipo/ueAutomation/blob/main/README.md#android-emulat%C3%B6r%C3%BC)
    - [iOS Development Bridge (idb)](https://github.com/galipo/ueAutomation/blob/main/README.md#ios-development-bridge-idb)
      - [Kurulum](https://github.com/galipo/ueAutomation/blob/main/README.md#kurulum-1)
  - [adb Kullanımı](https://github.com/galipo/ueAutomation/blob/main/README.md#adb-kullan%C4%B1m%C4%B1)
    - [Bazı Shell komutları](https://github.com/galipo/ueAutomation/blob/main/README.md#baz%C4%B1-shell-komutlar%C4%B1)
      - ["iperf" kurulumu ve kullanımı](https://github.com/galipo/ueAutomation/blob/main/README.md#cihaza-iperf-kurulumu-ve-kullan%C4%B1m%C4%B1)
  - [Python - adb](https://github.com/galipo/ueAutomation/blob/main/README.md#python---adb)
  - [Python üzerinden Android aygıtta uygulama çalıştırma](https://github.com/galipo/ueAutomation/blob/main/README.md#python-%C3%BCzerinden-android-ayg%C4%B1tta-uygulama-%C3%A7al%C4%B1%C5%9Ft%C4%B1rma)
- [Kısaltmalar](https://github.com/galipo/ueAutomation/blob/main/docs/KEYWORDS.md)
- [Örnekler](https://github.com/galipo/ueAutomation/blob/main/docs/ADB_SHELL_EXAMPLE.md)
  - [Cihazı restart etme](https://github.com/galipo/ueAutomation/blob/main/docs/ADB_SHELL_EXAMPLE.md#cihaz%C4%B1-restart-etme)
  - [Internet sitesi açma](https://github.com/galipo/ueAutomation/blob/main/docs/ADB_SHELL_EXAMPLE.md#internet-sitesi-a%C3%A7ma)
  - [Uçak modu açma/kapama](https://github.com/galipo/ueAutomation/blob/main/docs/ADB_SHELL_EXAMPLE.md#u%C3%A7ak-modu-a%C3%A7makapama)
  - [Sebeke kayıt bilgilerine erişim](https://github.com/galipo/ueAutomation/blob/main/docs/ADB_SHELL_EXAMPLE.md#%C5%9Febeke-kay%C4%B1t-bilgilerine-eri%C5%9Fim)

---
## AdbShellViaSSH.py
### ADBShellViaSSH
[Paramiko](https://www.paramiko.org/) librarysini kullanarak bir sunucuya SSH bağlantısı kurar. Bu bağlantı üzerinden karşıda ADB fonksiyonlarını çalıştırır. ADB executable'ın path'i açıkça yazılmazsa, ADB'nin PATH environment variable'ının içinde olduğu varsayılır.

Komutlar, "blocking=False" argumanıyla arka planda çalıştırılabilir. Arka plandaki komutlar "active_list" ve "finished_list"lerde bekletilir.
#### execute_adb()
Verilen ADB komutunu, verilen aygıtta çalıştırır. ADB çıktısı return edilir. Diğer fonksiyonların aksine, "device" parametresi "all" kabul ETMEZ.
#### execute_adb_shell()
Verilen shell komutunu, verilen aygıtta çalıştırır. Çıktı, dictionary olarak return edilir. Aygıt olarak "all" verilirse, bütün bağlı aygıtlarda komut çalıştırılır. Hepsinin çıktısı, dictionary'e eklenir.
#### airplane_mode_on/off()
Aygıtın uçak modunu açar/kapar. Aygıt Android 7 veya daha güncel bir versiyona sahipse, cihaza root access gerekir.
#### send_ping()
Aygıtta ping komutunu çalıştırır.
#### send_iperf()
Aygıtta iperf executable çalıştırır. Telefonlarda varsayılan olarak yüklü olmadığı için, ayrıca temin edilmelidir. Fonksiyon, varsayılan olarak iperf'i "data/local/tmp/" içerisinde arar.
#### refresh_device_list()
ADB'ye bağlı aygıt listesini yeniler.
#### get_finished_jobs() / get_active_jobs()
Arka planda çalışan ve biten komutların ParamikoContainer listelerini getirir.
#### refresh_active_jobs()
Arka plandaki komutların bitme durumunu kontrol eder.
### ParamikoContainer
Paralel komut çalıştırılmak istendiğinde, çalıştırılan komutun stdin, stdout, stderr bağlantıları, aygıt adı ve komut adı bu objectin içinde kayıtlanır.
#### check_finish()
SSH Channel'ın exit-status'üne bakıp, komutun bitip bitmediğine bakar.
#### print()
SSH Channel'ın stdout/err bufferini printler, boşaltır ve kaydeder.
#### print_all()
SSH Channel'ın stdout/err bufferini kaydeder ve kayıtlı bütün outputu printler.
### Komutlarda alınan hataların kontrolü:
- Bütün Shell komutlarında:
  - ADB'ye bağlı device sayısı 0 -> *exception*
- Blocking/seri çağırılan komutlarda:
  - Tek cihazda çağırılan komutlarda:
    - ADB veya aygıt shell bir hata yazarsa -> *exception*
    - SSH/Ping/İperf timeout yaşanırsa -> *exception*
    - Aygıt belirtilmez ve ADB'ye bağlı 1'den fazla device varsa -> *exception*
    - Aygıt offline ise -> *exception*
  - Bütün cihazlarda çağırılan komutlarda:
    - Üstte belirtilen 1. ve 2. durumlarda -> exception yakalanıp sadece print edilir, *program devam eder*
- Nonblocking/background çağırılan komutlarda:
  - Komut kaydından (ParamikoContainer) print alınana kadar hiçbir uyarı olmaz.
  - print()/print_all() alınan hata -> *exception*

**Yukaridaki durumlar istenirse source code'da raise Exception veya print(Exception) vs olarak değiştirilebilir**

---
## ADB / IDB Genel Bilgi
### Android Debug Bridge (ADB)
ADB, komut satırını kullanarak android çalıştıran aygıtları ve emulatörleri kontrol etmeye yarar. 

ADB client, önce ana makinada 5037 portunu dinleyen bir sunucu kurar.

ADB'ye girdiğiniz komutlar bu porta aktarılır. Bu sunucu ise gelen komutları android cihazlarına iletir. 

Sunucuya bağlanan cihazlar, ADB client üzerinden belli komutlar ile kontrol edilebilir.(program yükleme, silme, debuglama, shell komutları vs...)

*Ana Makina:* **[**(ADB client) <-> (ADB sunucu)**]** <-> *UE:* **[**(ADB daemon)**]**

Gerçek cihazların ADB'ye bağlanabilmesi için developer ayarlarından debugging veya wi-fi debugging ayarlarının açması gerekir. Sonrasında USB veya Wi-Fi üzerinden sunucu tarafından keşfedilir. Ana makinada çalışan emulatörler ise 5555-5585 portlarını kullanır. ADB sunucusu, bu portlar arasındaki tek olan portlara bağlanır ve komutları iletir.

İlgili kaynak: [Android ADB](https://developer.android.com/studio/command-line/adb)
#### Kurulum
Android Studio veya komut satırı üzerinden SDK Manager kullanılarak indirilebilir.

"platform-tool" paketinin içinde gelir.
> sdkmanager -install platform-tools
#### Android Emulatörü
Android emulatör, fiziksel bir aygıta gerek kalmadan Android API, sensörler veya uygulamaları denememize fırsat veren bir programdır.

Emulatörler, ADB ile çalışabilir. ADB’nin varsayılan ayarlarında, 5554-5586 portları arasında 16 tane emulatör ile çalışabilir. Emulatörler, varsayılan olarak zaten bu portları kullanacaktır. ADB ayarlarından $ADB_LOCAL_TRANSPORT_MAX_PORT’ın değeri, emulatör sayısını belirlemek için değiştirilebilir.

Emulatör, Android Studio ile birlike veya sdkmanager üzerinden tek başına indirilebilir. 
>sdkmanager -install emulator

Intel HAXM:
>sdkmanager -install extras;intel;Hardware_Accelerated_Execution_Manager

AMD Hypervisor Driver:
>sdkmanager -install xtras;google;Android_Emulator_Hypervisor_Driver

Her çalışan emulatorun bir tane Android Sanal Aygıt (Android Virtual Device - AVD) kurulumuna ihtiyacı vardır.

AVD; android versiyonu, taklit edilen cihazın fiziksel özellikleri ve sabit sürücüsü gibi bilgileri içerir. 

AVD oluşturmak için aygıt tanımı dosyası ve sistem imaj dosyası gerekir. (SDK Manager üzerinden) Bunlar temin edildikten sonra bir AVD oluşturulabilir. Bunu hem Android Studio üzerinden, hem de komut satırından "avdmanager" çalıştırılarak yapabiliriz. 
>avdmanager create avd -n ISIM -k SIS_IMAJ -d AYGIT
#### Android Cihazı ADB'ye Bağlama
Android çalıştıran bir cihazı, ADB’ye USB kablo veya Wi-Fi üzerinden bağlayabiliriz. Öncelikle cihaz üzerinden, geliştirici ayarlarında USB debuggingi açmalıyız. Ayrıca Wi-Fi debugging de istersek aynı yerden açabiliriz. Android 10 ve daha eski modeller için ise daha farklı bir yöntem izleniyor.(Detaylar: [ADB](https://developer.android.com/studio/command-line/adb))

Alternatif olarak rootlanmış aygıtlar, Google Play üzerinden WiFi debugging yada local ADB console benzeri uygulamalar indirebiliyor.
### iOS Development Bridge (idb)
İdb, iOS kullanan aygıtları ve simulatörleri otomatikleştirmek için kullanılır.

Ana makinaya kurulan idb client, cihazlardaki idb companion'a bağlantı kurup komutları gönderir. Companionlar da komutları aygıtta gerçekleştirip sonuçları cliente gönderir. Bu bağlantılar TCP yada UDS(unix domain socket) üzerinden yapılır.

*Ana Makina:* **[**(idb client)**]** <-> *UE:* **[**(idb companion)**]**

İlgili kaynak: [İDB](https://fbidb.io/docs/overview/)
#### Kurulum
idb client, pip üzerinden; idb companion ise homebrew üzerinden indirilebilir.
> pip3.6 install fb-idb
>
> brew tap facebook/fb
>
> brew install idb-companion
## ADB Kullanımı
Komut satırı üzerinden ADB ile ilgili detaylı bilgiye erişilebilir.
>ADB --help

ADB sunucusu açılıp kapanabilir.
>adb start-server

>adb kill-server

Bağlanılabilecek cihazlar listelenebilir.
>adb devices

Birden fazla cihaz varsa, komut yollanacak cihaz -s ile belirtilmelidir. Seri no, üstteki komut ile bulunabilir.
>adb -s *SERI_NO KOMUT*

Cihaza dosya atılabilir ve cihazdan dosya çekilebilir.
>adb push *LOCAL_DIR UE_DIR*

>adb pull *UE_DIR LOCAL_DIR*

Cihaz üzerinde herhangi bir shell komutu çalıştırılabilir.
>adb shell *SHELL_KOMUT*

Ayrıca .apk kurulabilir ve silinebilir; socket forward ve reverse edilebilir; cihaz debug edilebilir vs...
### Bazı shell komutları
Öncelikle, ADB üzerinden 2 şekilde shell komutları gönderilebilir. Birincisi, her komutu ADB üzerinden yollamak:
>adb shell *SHELL_KOMUT_1*
>
>adb shell *SHELL_KOMUT_2*

İkincisi, önce shelle bir kere bağlanmak ve sonrasında shell içerisinden komut girmek:
>adb shell
>
>*SHELL_KOMUT_1*
>
>*SHELL_KOMUT_2*

Shell üzerinden activity manager(am), package manager(pm), device manager(dm) çağırılabilir; ekran görüntüsü alınabilir, test cihazları resetlenebilir vs...

Activity manager, cihazda çeşitli eylemleri tetiklemeye, program açmaya, tuş girdisi vermeye yarar. Package mananger, yeni packagelar yüklemeye ve yüklü packageları düzenlemeye yarar. Device manager, cihazın yönetim ayarlarına erişim sağlar.

Örnek olarak Google Chrome üzerinden "www.google.com" açabiliriz:
>ADB shell am start -a android.intent.action.VIEW -d http://www.google.com
#### Cihaza "iperf" kurulumu ve kullanımı:
Iperf, Android cihazlarda varsayılan olarak kurulu gelmez. Bunun için PlayStore'dan bir uygulama indirilmeli, veya shell'de çalıştırmak için "iperf" binaryleri bulunup telefona atılmalıdır. Github'da bulup denediğim hazır bir iperf binarysini başarılı bir şekilde çalıştırabildim. Binary dosyasını "/data/local/tmp/" içine atıp çalıştırdım.
## Python - ADB
ADB’nin Python portu veya Python wrapperları internette mevcuttur. Bunları kullanarak veya benzerleri yazılarak kolayca Python’dan ADB komutları çağırılabilir. 

"[PythonADB](https://github.com/ClaudiuGeorgiu/PythonADB)"(wrapper), Python subprocess çağırarak, zaten yüklü olan adb programını çalıştırır. Bunu ADB_PATH ortam değişkenini kullanarak yapar. Yüklü olan bir ADB kullanıldığı için, Android’in yayınladığı ADB güncellemelerini takip etmesi daha kolaydır. Başka wrapperlar da kullanılabilir.

>from adb.adb import *
>
>a=ADB()
>
>a.get_available_devices()
>
>a.execute(LIST_İÇİNDE_ADB_KOMUTU)
>
>a.shell(LIST_ICINDE_SHELL_KOMUTU)

"PurePytonADB"/"adbutils"(port), ADB client’inin sıfırdan Pythonda yazılmış halleridir. ADB server ve daemonu içinde barındırmaz. Orijinal ADB clientindeki bazı sorunlar burada çözülmüştür. Buna rağmen, bu projelerin devamlı güncel tutulması gerektiği için, wrapper kullanmak daha mantıklı olabilir.
## Python üzerinden Android aygıtta uygulama çalıştırma
Pyton kullanarak, Android çalıştıran bir aygıtta uygulama açıp kontrol etmek için birkaç alternatif vardır. Bunlar Appium kullanmak, shell üzerinden input girmek ve UiAutomator/Espresso kullanarak JUnitTest yazmak olarak sıralanabilir.
### Appium
Appium, Selenium üzerine kurulan bir mobil uygulama otomasyon framework'üdür. Appium kullanabilmek için, öncelikle bir Appium server kurulmalıdır. Appium server, ADB server ile aynı işleve sahiptir; gelen komutları aygıtlara iletir. Appium, ADB'den farklı olarak komut satırından komut almaz. Onun yerine desteklenen bir programlama dilinde Appium Client kullanılarak komutlar yazılmalıdır. Son olarak bu yazılan komut dosyası; Appium server ve Espresso/UiAutomator2 driver üzerinden aygıtta çalıştırılır.
### Shell
Shell üzerinden uygulamalar kullanılabilir. Shell "input" komutu, cihaza herhangi bir input vermek için kullanılabilir. Eğer uygulamada nereye basılması gerektiği biliniyorsa, direk kordinatları vererek sırayla gerekli yerlere basılabilir. Eğer basılması gereken yerler bilinmiyorsa ya da daha fazla kontrol gerekiyorsa, shell "uiautomator" komutu kullanılabilir.
>uiautomator dump *--compressed(opsiyonel)*

Bu komut; o an ekrandaki herşeyi, hiyerarşik bir XML olarak /sdcard/window_dump.xml(değiştirilebilir) dosyasına kaydeder. Bu çıktı kullanılarak ekranda aranan buton, yazı vs kontrol edilebilir, bulunabilir ve kordinatları alınabilir.
### UiAutomator (JUnit)
UiAutomator; uygulamanın kaynak kodundan bağımsız olarak, ekranı kullanarak uygulamaları test etmeye yarar. JUnit benzeri testler yazılarak bir uygulama kontrol edilebilir. UiAutomator API üzerinden ekrandaki elementler okunabilir ve butonlara basılabilir. Oluşturulan test, aygıta yüklendikten sonra shell üzerinden çalıştırılabilir.
>adb shell am instrument -w <test_package_name>/<runner_class>

Arka planda çalışan uygulamaları da yönetebiliyor olabilir:
>The UI Automator APIs let you interact with visible elements on a device, ***regardless of which Activity is in focus***, so it allows you to perform operations such as opening the Settings menu or the app launcher in a test device.
