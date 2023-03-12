# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2023 sbot50
# Disclaimer: Heavily inspired by the therminal watch face of Infinitime
import wasp, ble, fonts.firacode as f
M,D='JanFebMarAprMayJunJulAugSepOctNovDec','MonTueWedThuFriSatSun'
class ThermClockApp():
    NAME='Therm'
    s=d=w=b=n=c=st=bl=-1
    wasp.system.notify(wasp.watch.rtc.get_uptime_ms(),
    {
        "src":"Hangouts",
        "title":"A Name",
        "body":"message contents1"
    })
    wasp.system.notify(wasp.watch.rtc.get_uptime_ms()+1,
    {
        "src":"Hangouts",
        "title":"A Name",
        "body":"message contents2"
    })
    wasp.system.notify(wasp.watch.rtc.get_uptime_ms()+2,
    {
        "src":"Hangouts",
        "title":"A Name",
        "body":"message contents3"
    })
    wasp.system.notify(wasp.watch.rtc.get_uptime_ms()+3,
    {
        "src":"Hangouts",
        "title":"A Name",
        "body":"message contents4"
    })
    wasp.system.notify(wasp.watch.rtc.get_uptime_ms()+4,
    {
        "src":"Hangouts",
        "title":"A Name",
        "body":"message contents5"
    })
    def foreground(self):wasp.system.bar.clock=False;self._d(1);wasp.system.request_tick(500)
    def sleep(self):return True
    def wake(self):self._d()
    def tick(self, ticks):self._d()
    def preview(self):wasp.system.bar.clock = False;self._d(1)
    def _d(self,r=0):
        d = wasp.watch.drawable;d.set_font(f);t=wasp.watch.rtc.get_localtime()
        if r:
            d.fill();d.set_color(0x8EE6);d.string("user@watch",0,0);d.string("user@watch",0,160)
            d.set_color(0xFFFF);d.string(": $ info",110,0);d.string(": $",110,160)
            d.set_color(0x74F9);d.string("~",120,0);d.string("~",120,160)
            d.set_color(0xFFFF)
            for i,s in enumerate(["[TIME]","[DATE]","[WDAY]","[BATT]","[STEP]","[BLE ]","[NOTI]"]):
                d.string(s, 0 ,20+20*i)
        if t[5]!=self.s or r:
            h,m,s=str(t[3]),str(t[4]),str(t[5])
            h,m,s=(h if len(h)>1 else "0"+h),(m if len(m)>1 else "0"+m),(s if len(s)>1 else "0"+s)
            d.string("{}:{}:{} ".format(h,m,s),70,20);self.s=t[5]
        if t[2]!=self.d or r:
            d.string("{} {} {} ".format(str(t[2]),M[(t[1]-1)*3:t[1]*3],str(t[0])),70,40);self.d=t[2]
        if t[6]!=self.w or r:d.string(D[t[6]*3:(t[6]+1)*3],70,60);self.w=t[6]
        if round(wasp.watch.battery.level()/20)!=self.b or wasp.watch.battery.charging()!=self.c or r:
            d.string("[     }",70,80);c=round(wasp.watch.battery.level()/20)
            if c==6:c=5
            if c<1:c=1
            d.set_color(0x2E0F)
            if wasp.watch.battery.level()<66:d.set_color(0xE300)
            if wasp.watch.battery.level()<33:d.set_color(0xC0E5)
            if wasp.watch.battery.charging():d.set_color(0x1B9B)
            d.string(c*"#",80,80);self.b=round(wasp.watch.battery.level()/20);self.c=wasp.watch.battery.charging();d.set_color(0xFFFF)        
        if wasp.watch.accel.steps!=self.st or r:
            d.fill(x=80,y=100,w=160,h=20);d.string(str(wasp.watch.accel.steps),70,100);self.st=wasp.watch.accel.steps
        if wasp.watch.connected()!=self.bl or (not ble.enabled() and ble.enabled()!=self.bl) or r:
            s="Connected   ";d.set_color(0x250D)
            if not wasp.watch.connected():s="Disconnected";d.set_color(0xA0E5)
            if not ble.enabled():s="Disabled    ";d.set_color(0x9CD2)
            d.string(s,70,120);self.bl=wasp.watch.connected() if ble.enabled() else ble.enabled();d.set_color(0xFFFF)
        if len(wasp.system.notifications)!=self.n or r:d.string(str(len(wasp.system.notifications)),70,140);self.n=len(wasp.system.notifications)