# Restrictions-to-remind_V2

这是改进版的车载限号提醒器，使用ESP8266（WeMos D1 mini）、PCF8563T、蜂鸣器、按钮等模块和元器件。
上一个版本的由于DS1302走时误差太大，经过价格和准度的考量，这个版本用性价比高的PCF8563T模块代替。
这个版本修改设备时间和限行规则改为使用手机WiFi设置。

使用方法：
限号器接入车载USB接口，每次启动车辆会自动判断当天是否，如果限号，设备会长鸣，不限号没反应。
长鸣后如要继续开车，请按下按键关闭噪音，无需拔下限号器。
时间同步和限号规则修改：
限号器通电后，长按按键5秒钟，听到嘀嘀嘀三声后松开按键，打开手机连接WIFI，名称“限号提醒器”密码“87654321”
打开手机浏览器输入网址192.168.0.1即可进入设置页面。

如遇到每隔1秒钟“滴”一次，表示设备时间错误，请修改时间，

引用资料：
https://www.wemos.cc/en/latest/d1/d1_mini.html

http://www.1zlab.com/wiki/micropython-esp32/timer/

https://randomnerdtutorials.com/esp32-esp8266-micropython-web-server/

https://blog.csdn.net/ruoyusixian/article/details/102654355

https://www.cnblogs.com/cuianbing/p/14378964.html

https://blog.csdn.net/m0_45040529/article/details/109890884

https://rabbithole.wwwdotorg.org/2017/03/28/esp8266-gpio.html

