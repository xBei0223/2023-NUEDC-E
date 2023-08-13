#from Maix import utils
#import machine
#import gc
#old = utils.gc_heap_size()
#print(old)
#new = 4096*1024
#utils.gc_heap_size(new)
#print(utils.gc_heap_size())
#print("Free Memory:", gc.mem_free())
#machine.reset()

import sensor, image,time,lcd,utime,math
import machine
from math import sqrt
from machine import UART
from fpioa_manager import fm
from board import board_info
import random

lcd.init()
#sensor.reset(dual_buff=True)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 3000)
sensor.set_auto_gain(0, gain_db = 17)
sensor.set_auto_whitebal(False)
sensor.set_auto_exposure(True)
sensor.set_hmirror(0)
sensor.skip_frames(30)
sensor.run(1)

red_threshold=(44, 77, -2, 54, -16, 33)
red_threshold2=(66, 88, 3, 55, 5, 56)
white_threshold=(75, 100, -20, 35, -24, 32)
point_threshold=(66, 100, -11, 43, -10, 44)
green_threshold=(55, 77, -50, -13, -26, 25)
gray_threshold=(180, 255)
min_area_red=4
clock = time.clock()

roi_QQVGA=(25,6,110,108)
roi_QVGA=(40,15,240,210)
rect_x1=[]#缓存矩形的四个坐标
rect_x2=[]
rect_x3=[]
rect_x4=[]
rect_y1=[]
rect_y2=[]
rect_y3=[]
rect_y4=[]

#fm.register(7,fm.fpioa.UART1_TX, force=True)#定义接口
#uart_A = UART(UART.UART1, 921600, 8, 0, 1, timeout=1000, read_buf_len=4096)

# 定义 STM32 发送类
class STM32_transmit():                              # 定义 STM32 发送类
    head1  = 0xAA                                    # uint8_t   帧头1
    head2  = 0xAA                                    # uint8_t   帧头2
    x=[0] * 4                                       # 矩形顶顶点x轴坐标
    y=[0] * 4                                     # 矩形顶点y轴坐标

# 实例化类
TSTM32 = STM32_transmit()                            # 实例化 STM32_transmit() 为 TSTM32

# 定义矩形坐标打包函数
def TSTM32_data():# 数据打包函数
    global TSTM32
    data=bytearray([TSTM32.head1,                    # 帧头1
                    TSTM32.head2,                    # 帧头2
                    0x00,                            # 有效数据长度 0x00 + data_len - 4
                    TSTM32.x[0],
                    TSTM32.y[0],
                    TSTM32.x[1],
                    TSTM32.y[1],
                    TSTM32.x[2],
                    TSTM32.y[2],
                    TSTM32.x[3],
                    TSTM32.y[3],
                    0x00])                           # 数据和校验位

    # 数据包的长度
    data_len = len(data)                             # 获得数据包总长度
    data[2]  = data_len - 4                          # 有效数据的长度 扣去 帧头1 帧头2 有效数据长度位 校验位

    # 校验和
    sum = 0                                          # 和置零
    for i in range(0,data_len-1):
        sum = sum + data[i]                          # 和累加
    data[data_len-1] = sum                           # 和赋值 给数组最后一位发送 只保存低8位 溢出部分无效

    # 返回打包好的数据
    return data

# 定义 STM32 发送类
class STM32_transmit2():                              # 定义 STM32 发送类
    head1  = 0xAB                                    # uint8_t   帧头1
    head2  = 0xAB                                   # uint8_t   帧头2
    x=0                                     # 红点x轴坐标
    y=0                                   # 红点y轴坐标

# 实例化类
point = STM32_transmit2()                            # 实例化 STM32_transmit() 为 TSTM32

#定义红点坐标打包函数
def TSTM32_data2():# 数据打包函数
    global point
    data=bytearray([point.head1,                    # 帧头1
                    point.head2,                    # 帧头2
                    0x00,                            # 有效数据长度 0x00 + data_len - 4
                    point.x,            # 保存目标坐标x 将整形数据拆分成两个8位,高八位和低八位
                    point.y,            # 保存目标坐标y 将整形数据拆分成两个8位
                    0x00])                           # 数据和校验位

    # 数据包的长度
    data_len = len(data)                             # 获得数据包总长度
    data[2]  = data_len - 4                          # 有效数据的长度 扣去 帧头1 帧头2 有效数据长度位 校验位

    # 校验和
    sum = 0                                          # 和置零
    for i in range(0,data_len-1):
        sum = sum + data[i]                          # 和累加
    data[data_len-1] = sum                           # 和赋值 给数组最后一位发送 只保存低8位 溢出部分无效

    # 返回打包好的数据
    return data


#def sending_data():
    #global uart_A,point
    #data = ustruct.pack("<BBBBb",      #B: 无符号字节（byte），占用1字节。表示范围为0到255。
                   #point.head1,#帧头1         #b: 有符号字节（byte），占用1字节。表示范围为-128到127
                   #point.head2,#帧头2
                   #point.x,
                   #point.y,
                   #0x00)
    #uart_A.write(data)

#def sending_rect():
    #global uart_A,TSTM32
    #data = ustruct.pack("<BBBBBBBBBBb",
                   #TSTM32.head1,#帧头1
                   #TSTM32.head2,#帧头2
                   #TSTM32.x[0],
                   #TSTM32.y[0],
                   #TSTM32.x[1],
                   #TSTM32.y[1],
                   #TSTM32.x[2],
                   #TSTM32.y[2],
                   #TSTM32.x[3],
                   #TSTM32.y[3],
                   #0x00)
    #uart_A.write(data)

#粗糙地去除差异较大的值
def remove_outliers(arr, threshold):
    # 计算数组的平均值
    if len(arr)==0:
        i = random.randint(1, 100)
        new_arr=[i]
        return new_arr
    avg = sum(arr) / len(arr)
    # 筛选与平均值相差较小的值
    new_arr = [x for x in arr if abs(x - avg) <= threshold]
    if len(new_arr)==0:#防止除以0
        i = random.randint(1, 100)
        new_arr=[i]
    return new_arr


#判断是否为矩形
def is_rectangle(x,y,tolerance):
    xc = sum(x)/ 4
    yc = sum(y)/ 4
    d1 = sqrt((x[0] - xc) ** 2 + (y[0] - yc) ** 2)
    d2 = sqrt((x[1] - xc) ** 2 + (y[1] - yc) ** 2)
    d3 = sqrt((x[2] - xc) ** 2 + (y[2] - yc) ** 2)
    d4 = sqrt((x[3] - xc) ** 2 + (y[3] - yc) ** 2)
    avg=sum([d1,d2,d3,d4])/4
    tolerance=tolerance
    #print(d1,d2,d3,d4,avg)
    if (abs(d1 - avg) <= tolerance and
        abs(d2 - avg) <= tolerance and
        abs(d3 - avg) <= tolerance and
        abs(d4 - avg) <= tolerance):
        return True
    else:
        return False


#判断矩形长宽比
def is_in_proportion(x,y,tolerance):
    target_ratio = math.sqrt(2)
    def dist(a, b , c, d):
        return ((a-c)**2 + (b-d)**2)**0.5
    por_1=dist(x[0], y[0],x[1],y[1])
    por_2=dist(x[1], y[1],x[2],y[2])
    por_3=dist(x[2], y[2],x[3],y[3])
    por_4=dist(x[3], y[3],x[0],y[0])
    th1=target_ratio-tolerance       #阈值下限
    th2=target_ratio+tolerance     #阈值上限
    th3=target_ratio/2-tolerance
    th4=target_ratio/2+tolerance
    if ((th1 <= por_1/por_2 <= th2 ) and
        (th1 <= por_3/por_4 <= th2)) or \
       ((th3 <= por_1/por_2 <= th4) and
        (th3 <= por_3/por_4 <= th4)):
        return True
    else:
        return False


t2=utime.time()
while(utime.time()-t2<=4):#拍摄四秒矩形
#while True:
    clock.tick()
    img = sensor.snapshot()
    rects=img.find_rects(threshold =11000,area_threshold=800,roi=roi_QQVGA)
    if rects:
        for r in rects:
            temp=(r.corners())
            corner_x = [x[0] for x in temp]
            corner_y = [x[1] for x in temp]
            if is_in_proportion(corner_x,corner_y,0.1):
                img.draw_rectangle(r.rect(), color = (0, 0, 255))
                print("ok")
                lcd.display(img)
                for idx, p in enumerate(r.corners()):
                    img.draw_circle(p[0], p[1], 5, color = (0, 255, 0))#从左下角逆时针返回顶点坐标
                    if idx==0:
                        rect_x1.append(p[0])
                        rect_y1.append(p[1])
                    elif idx==1:
                        rect_x4.append(p[0])
                        rect_y4.append(p[1])
                    elif idx==2:
                        rect_x3.append(p[0])
                        rect_y3.append(p[1])
                    elif idx==3:
                        rect_x2.append(p[0])
                        rect_y2.append(p[1])
    lcd.display(img)
    print(clock.fps())

#print(len(rect_x1))
threshold = 3
filtered_rect_x1 = remove_outliers(rect_x1, threshold)
#print(filtered_rect_x1)
filtered_rect_y1 = remove_outliers(rect_y1, threshold)
filtered_rect_x2 = remove_outliers(rect_x2, threshold)
filtered_rect_y2 = remove_outliers(rect_y2, threshold)
filtered_rect_x3 = remove_outliers(rect_x3, threshold)
filtered_rect_y3 = remove_outliers(rect_y3, threshold)
filtered_rect_x4 = remove_outliers(rect_x4, threshold)
filtered_rect_y4 = remove_outliers(rect_y4, threshold)
avg_x1 = round(sum(filtered_rect_x1) / len(filtered_rect_x1))
avg_y1 = round(sum(filtered_rect_y1) / len(filtered_rect_y1))
avg_x2 = round(sum(filtered_rect_x2) / len(filtered_rect_x2))
avg_y2 = round(sum(filtered_rect_y2) / len(filtered_rect_y2))
avg_x3 = round(sum(filtered_rect_x3) / len(filtered_rect_x3))
avg_y3 = round(sum(filtered_rect_y3) / len(filtered_rect_y3))
avg_x4 = round(sum(filtered_rect_x4) / len(filtered_rect_x4))
avg_y4 = round(sum(filtered_rect_y4) / len(filtered_rect_y4))
TSTM32.x[0]=avg_x1
TSTM32.y[0]=avg_y1
TSTM32.x[1]=avg_x2
TSTM32.y[1]=avg_y2
TSTM32.x[2]=avg_x3
TSTM32.y[2]=avg_y3
TSTM32.x[3]=avg_x4
TSTM32.y[3]=avg_y4
#print(TSTM32.x,TSTM32.y)
if is_rectangle(TSTM32.x,TSTM32.y,3):
    #for i in range(20):
        #sending_rect()
    #LED_B.value(0)
    print("is rect")
else:
    machine.reset()

#摄像头好
while True:
    clock.tick()
    img = sensor.snapshot()
    gray_img=img.to_grayscale()
    binary_img = img.binary([(220,255)])
    binary_img = binary_img.dilate(3)
    blobs = img.find_blobs([(210,255)], merge=True)
    if blobs:
        #print("ok1")
        b = max(blobs, key=lambda b: b.pixels())
        img.draw_rectangle((b[0], b[1], b[2], b[3]), color=(0, 0, 255))#蓝
        center_x = b.cx()
        center_y = b.cy()
        img.draw_cross(center_x,center_y, thickness=2)
        point.y=center_y
        point.x=center_x
        #print(center_x,center_y)
        #sending_data()

    print(clock.fps())
    lcd.display(img)

#uart_A.deinit()
#del uart_A

#摄像头差
#先找红色块（为了区分红绿），确定红色块的区域
#然后灰度化，二值化，膨胀（使得打在黑胶带上的小的点放大），再找矩形
#while True:
    #clock.tick()
    #img = sensor.snapshot()
    #blobs = img.find_blobs([point_threshold], merge=True)

    #if blobs:
        #print("ok1")

        #b = max(blobs, key=lambda b: b.pixels())

        #img.draw_rectangle((b[0], b[1], b[2], b[3]), color=(0, 0, 255))#蓝
        #x, y, w, h = b[0:4]
        #roi_2=(x-10,y-10,w+24,h+24)
        #gray_img=img.to_grayscale()#灰度
        #binary_img = img.binary([(210,255)])#二值化
        #binary_img = binary_img.dilate(4)#膨胀
        #sub_blobs = binary_img.find_rects(threshold=11000,roi=roi_2, merge=True,pixel_threshold=8)

        #if sub_blobs:
            ##print("ok")
            #sb = max(sub_blobs, key=lambda sb: sb.w()*sb.h())
            ##img.draw_rectangle((sb.x(), sb.y(), sb.w(), sb.h()), color=(255, 0, 0))  # Draw a green rectangle
            #center_x = int(sb.x()+sb.w()/2)
            #center_y = int(sb.y()+sb.h()/2)
            ##img.draw_cross(center_x,center_y, thickness=2)
            #point.y=center_y
            #point.x=center_x
            ##print(center_x,center_y)
            ##uart_A.write(TSTM32_data2())

    #print(clock.fps())
    #lcd.display(img)

