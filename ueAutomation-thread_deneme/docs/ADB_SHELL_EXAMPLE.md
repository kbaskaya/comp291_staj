# adb shell Örnekleri

## Cihazı restart etme
Komut
>adb shell reboot

Ya da
>adb reboot

Çıktı
>*--boş--*
## Internet sitesi açma
Komut
>adb shell am start -a android.intent.action.VIEW -d http://www.google.com

Çıktı
>Starting: Intent { act=android.intent.action.VIEW dat=http://www.google.com/... }
## Uçak modu açma/kapama
Bu komutu çalıştırabilmek için root erişime ihtiyaç vardır. (Uçak modu - 1, Normal mod - 0)

Komut
>adb shell "su 0 settings put global airplane_mode_on *[1 / 0]* && su 0 am broadcast -a android.intent.action.AIRPLANE_MODE"

Çıktı
>Broadcasting: Intent { act=android.intent.action.AIRPLANE_MODE flg=0x400000 }
>
>Broadcast completed: result=0
## Şebeke kayıt bilgilerine erişim
"dumpsys" aracı, UE ile ilgili bir çok bilgiye erişmemizi sağlar. UE’nin o anki şebeke bilgilerine erişmek için "telephony.registry" bilgilerine erişebiliriz. "mServiceState" diye başlayan satırda "getRilVoiceRadioTechnology=" kısmı bize EDGE(2G), HSPA(3G), LTE(4G) veya NR-SA(5G) bilgisini verir. Ayrıca bu komutun "grep"siz halinin altında, cihazın en son geçirdiği şebeke değişimlerinin (mesela 3G'den 4G'ye geçiş) logu bulunur.

Komut
>adb shell "dumpsys telephony.registry | grep 'mServiceState'"

Çıktı
>    mServiceState={mVoiceRegState=0(IN_SERVICE), mDataRegState=0(IN_SERVICE), mChannelNumber=-1, duplexMode()=0, mCellBandwidths=[], mOperatorAlphaLong=T-Mobile, mOperatorAlphaShort=TMOBILE, isManualNetworkSelection=false(automatic), **getRilVoiceRadioTechnology=20(NR_SA)**, **getRilDataRadioTechnology=20(NR_SA)**, mCssIndicator=unsupported, mNetworkId=-1, mSystemId=-1, mCdmaRoamingIndicator=-1, mCdmaDefaultRoamingIndicator=-1, mIsEmergencyOnly=false, isUsingCarrierAggregation=false, mArfcnRsrpBoost=0, mNetworkRegistrationInfos=[NetworkRegistrationInfo{ domain=PS transportType=WLAN registrationState=UNKNOWN roamingType=NOT_ROAMING accessNetworkTechnology=UNKNOWN rejectCause=0 emergencyEnabled=false availableServices=[] cellIdentity=null voiceSpecificInfo=null dataSpecificInfo=null nrState=NONE rRplmn= isUsingCarrierAggregation=false}, NetworkRegistrationInfo{ domain=CS transportType=WWAN registrationState=HOME roamingType=NOT_ROAMING accessNetworkTechnology=NR rejectCause=0 emergencyEnabled=false availableServices=[VOICE,SMS,VIDEO] cellIdentity=null voiceSpecificInfo=VoiceSpecificRegistrationInfo { mCssSupported=false mRoamingIndicator=0 mSystemIsInPrl=0 mDefaultRoamingIndicator=0} dataSpecificInfo=null nrState=NONE rRplmn=310260 isUsingCarrierAggregation=false}, NetworkRegistrationInfo{ domain=PS transportType=WWAN registrationState=HOME roamingType=NOT_ROAMING accessNetworkTechnology=NR rejectCause=-1 emergencyEnabled=false availableServices=[DATA] cellIdentity=null voiceSpecificInfo=null dataSpecificInfo=android.telephony.DataSpecificRegistrationInfo :{ maxDataCalls = 16 isDcNrRestricted = false isNrAvailable = false isEnDcAvailable = false NrVopsSupportInfo :  mVopsSupport = 0 mEmcSupport = 0 mEmfSupport = 0 } nrState=NONE rRplmn=310260 isUsingCarrierAggregation=false}], mNrFrequencyRange=0, mOperatorAlphaLongRaw=T-Mobile, mOperatorAlphaShortRaw=TMOBILE, mIsDataRoamingFromRegistration=false, mIsIwlanPreferred=false}
