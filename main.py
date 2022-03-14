# from urouter import uRouter
# app = uRouter()

# import upip
# upip.install('micropython-uRouter')

try:
    import usocket as socket
except:
    import socket

import json
import utime

from machine import Pin
from machine import Timer
import network
station = network.WLAN(network.AP_IF)
station.active(False)

import esp
esp.osdebug(None)

import gc
gc.collect()

from machine import I2C, Pin
from pcf8563t import PCF8563

#读取规则文件内容
def read_rule():
    f = open("rule.txt","r")
    i = int(f.read())
    f.close()
    return i

#写入规则到文件
def update_rule(i):
    f = open("rule.txt","w")
    f.write(i)
    f.close()

#返回发送的时间格式[年，月，日，时，分，秒，规则]
def tran_send_time():
    pd = pcf.datetime()#[2021, 10, 31, 0, 18, 47, 35, 0]
    return [pd[0],pd[1],pd[2],pd[4],pd[5],pd[6],read_rule()]

#html页面
def web_page():
    with open("index.html","r") as f:
        html = f.read()
    html = html.replace("[2021,08,25,12,24,56,6]",str(tran_send_time()))
    return html

#播报完成后快速滴滴两声
def didi():
    utime.sleep(1)
    for i in range(2):
        p3.on()
        utime.sleep(0.1)
        p3.off()
        utime.sleep(0.1)

#判断限行
def xianxing():
    cur_time = pcf.datetime() 
    i = read_rule()
    print(i,cur_time[2],cur_time[3])
    if i >= 5:
        #对于单双号限行,5单号限行，6双号限行
        if i%2 == cur_time[2]%2:
            p3.on()
            #按键清楚警报
            while 1:
                if p4.value() == 0:
                    p3.off()
                    #p4.off()
                    didi()
                    break
                led.value(not led.value())
                utime.sleep(0.1)
    else:
        #对于星期限行
        if i == cur_time[3]:
            p3.on()
            #按键清楚警报
            while 1:
                if p4.value() == 0:
                    p3.off()
                    #p4.off()
                    didi()
                    break
                led.value(not led.value())
                utime.sleep(0.1)
    return

#时钟故障回调函数
def err_time():
    p3.value(not p3.value())
    led.value(not led.value())

#开启wifi同步时慢闪led
def slow_flash():
    led.value(not led.value())

i2c = I2C(scl=Pin(12), sda=Pin(13), freq=100000)
pcf = PCF8563(i2c) #datetime()-->[年，月，日，周，时，分，秒，0]
led = Pin(2, Pin.OUT)
p3 = Pin(5,Pin.OUT) #蜂鸣器
p3.off()
p4 = Pin(0,mode=Pin.IN,pull=Pin.PULL_UP)    #按键

#诊断时间是否清零重置,改定时器
timer = Timer(-1)
if pcf.datetime()[0] < 2021:
    timer.init(mode=Timer.PERIODIC,period=500,callback=lambda t:err_time())
    while 1:
        if p4.value() == 0:
            timer.deinit()
            p3.off()
            didi()
            break
        utime.sleep(0.05)
else:
    #限行判断
    xianxing()

#点亮待机指示灯
led.off()

#长按5秒嘀嘀嘀三声后开启ap热点，进入手机配置页面
flag1 = True
while flag1:
    utime.sleep(0.1)
    if p4.value() == 0:
        flag2 = utime.ticks_ms()
        while 1:
            utime.sleep(0.1)
            if (utime.ticks_ms() - flag2)/1000 >= 5:
                for i in range(3):
                    p3.on()
                    utime.sleep(0.1)
                    p3.off()
                    utime.sleep(0.1)
                flag1 = False
                break
#让led慢速一闪一闪的
timer = Timer(-1)
timer.init(mode=Timer.PERIODIC,period=1000,callback=lambda t:slow_flash())

# ssid = 'TP-LINK_A33706'
# password = '70000000'
# station = network.WLAN(network.AP_IF)
station.active(True)
station.config(essid="限号提醒器", authmode=network.AUTH_WPA_WPA2_PSK, password="87654321")
station.ifconfig(('192.168.0.1', '255.255.255.0', '192.168.0.1', '192.168.0.1'))
# station.active(True)
# station.connect(ssid,password)
# while station.isconnected() == False:
#   pass

print('Connection successful')
print(station.ifconfig())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    print("等待客户端连接")
    conn, addr = s.accept()
    try:
        print('Got a connection from %s' % str(addr))
        request = conn.recv(2048)
        request = str(request)
        print('Content = %s' % request)
        http = request.find("GET / HTTP")
        if http != -1:
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(web_page())
            conn.close()
            continue
        http = request.find("POST /updaterulev0.1 HTTP")
        if http != -1:
            rm = request.find('now=')#接收到的是一个数字
            rl = request[rm+4]
            update_rule(rl)
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json; charset=utf-8\n')
            conn.send('Connection: close\n\n')
            conn.sendall(json.dumps({"data":tran_send_time()}))
            conn.close()
            continue
        http = request.find("POST /updatetimev0.1 HTTP")
        if http != -1:
            tm = request.find('now=')#接收到的时间格式字符串2021=10=08=18=33=48=01：年=月=日=时=分=秒=星期
            tll = request[tm+4:tm+26].split("=")
            tl = []
            for i in tll:
                tl.append(int(i))
            pcf.datetime([tl[0],tl[1],tl[2],tl[6],tl[3],tl[4],tl[5]])
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json; charset=utf-8\n')
            conn.send('Connection: close\n\n')
            conn.sendall(json.dumps({"data":tran_send_time()}))
            conn.close()
            continue

        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall("请求地址错误")
        conn.close()
    except:
        pass
timer.deinit()
