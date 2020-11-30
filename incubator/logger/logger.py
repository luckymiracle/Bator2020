import time
import smtplib
from threading import Timer
import datetime
import calendar
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.mime.image import MIMEImage
from subprocess import call
import serial
import re
import models as mod

dht_interval = 60 # 120  # 2 minutes interval
batch = None
time_inc = humidity_counter = temp_counter = 0
clockwise = False

servo_on = False
dht_on = False
nan_cnt = 0
vent_angle = 90
new_rotation = False
t_delta = None
last_time = None
SER = None
ktherm_temp = None
amb_temp = None
rh = None
inc_temp = None
rh_alert_sent = False
temp_alert_sent = False
rotation_stop_day = 18
camera_motion_on = False


def cmd(cmd, limit="\r"):
    global SER

    cmds = {"enable_cold_fan": "01", "disable_cold_fan": "00",
            "enable_hot_fan": "11", "disable_hot_fan": "10",
            "enable_peltier": "21", "disable_peltier": "20",
            "enable_debug": "31", "disable_debug": "30",
            "modify_temp_limit": "32 ", "modify_rh_limit": "33 ",
            "peak_rh_&_temp_limit": "34", "enable_incubator": "41",
            "disable_incubator": "40", "detach_rotation_servo": "50",
            "attach_rotation_servo": "51", "rotate_3": "52",
            "rotate_180": "53", "rotate_x": "54 ", "disable_rotation": "55",
            "enable_rotation": "56", "get_data": "6 "}

    if cmd in cmds:
        suffix = "\r"
        if cmd == "modify_temp_limit" or cmd == "modify_rh_limit" or \
           cmd == "rotate_x":
            suffix = " " + str(limit) + "\r"
            print cmds[cmd] + suffix
            
        SER.write(cmds[cmd] + suffix)
    else:
        print "wrong command:", cmd, limit


def logger_init():
    global SER, relay, rotation_stop_day, batch, time_inc, last_time

    print "logger_init"
    time_now = time.time()
    last_time = time_now
    print 'Opening the serial connection to Arduino.'
    SER = serial.Serial('/dev/ttyS0', 115200, timeout=0.1)
    batch = mod.incubation.objects.last()
    print batch
    if batch.stop is False:
        rotation_stop_day = batch.lockdown
        inc_time = (batch.start_date.year, batch.start_date.month,
                    batch.start_date.day, batch.start_date.hour,
                    batch.start_date.minute, batch.start_date.second)
        time_inc = calendar.timegm(inc_time)

        t_delta = datetime.timedelta((time_now-time_inc)/(3600*24))

        if t_delta.days < 22:
            cmd("disable_debug")
            time.sleep(1)
            data = SER.readline()

            cmd("get_data")
            time.sleep(1)
            data = SER.readline()
            print data
            split = re.split(' ', data)
            if len(split) >= 5:
                if int(split[4]) == 0:
                    cmd("enable_incubator")
                    time.sleep(0.5)
                    print SER.readlines()
            else:
                #  Let's reset the microcontroller before anything
                call(['avrdude', '-c', 'gpio', '-p', 'm328p'])
                time.sleep(0.5)
                cmd("enable_incubator")
                time.sleep(0.5)
                print SER.readlines()

            rht_timer = Timer(5, dht_store)
            rht_timer.start()

            if len(mod.RHT.objects.all()) > 0:
                last_dht = mod.RHT.objects.last()
                dht_time = (last_dht.date_log.year, last_dht.date_log.month,
                            last_dht.date_log.day, last_dht.date_log.hour,
                            last_dht.date_log.minute, last_dht.date_log.second)
                print "last_rht.date_log", last_dht.date_log
                time_dht = calendar.timegm(dht_time)
                lapse_time = abs(time_now-time_dht)
                logger_msg("A restart has taken place. Lapse time was " +
                           str(lapse_time) + " seconds.")
            # break

    else:
        cmd("disable_incubator")
        print SER.readlines()
        batch = None
        print "There are no active incubations!"
        return


def dht_store():
    global SER, batch, ktherm_temp, amb_temp, rh, inc_temp, t_delta
    global camera_motion_on, rh_alert_sent, temp_alert_sent

    cmd("get_data")
    time.sleep(1)
    data = SER.readline()
    split = re.split(' ', data)
    # print split
    if len(split) >= 4:
        ktherm_temp = float(split[2])
        amb_temp = float(split[3])
        rh = float(split[1])
        inc_temp = float(split[0])
        rht = mod.RHT(incub=batch, ktherm_temp=ktherm_temp, amb_temp=amb_temp,
                      rh=rh, inc_temp=inc_temp)
        rht.save()
        # print("htu_temp htu_rh ktype amb")
        # print(split[0], split[1], split[2], split[3], split[4])
        if rh <= 39 and rh_alert_sent is False:
            logger_msg("RH low alert: " + str(rh))
            rh_alert_sent = True
        elif rh >= 40 and rh_alert_sent is True:
            rh_alert_sent = False

        if ktherm_temp <= 35 and inc_temp <= 35 and temp_alert_sent is False:
            logger_msg("Temperature has dropped to " + str(ktherm_temp) + ".")
            temp_alert_sent = True
        elif ktherm_temp >= 36.5 and temp_alert_sent is True:
            temp_alert_sent = False
            
    else:
        print 'data:', data
        logger_msg("Invalid data received:" + data)

    t_delta = datetime.timedelta((time.time()-time_inc)/(3600*24))

    if t_delta.days >= batch.lockdown and camera_motion_on is False:
        camera_motion_on = True
        cmd("disable_rotation")        
        logger_msg("Rotations have stopped.")
        # Turn on the camera and motion
        cmd("modify_rh_limit", batch.RH)

    if t_delta.days < 22:
        timer = Timer(dht_interval, dht_store)
        timer.start()


def logger_get():
    global t_delta, ktherm_temp, amb_temp, rh, inc_temp, batch, last_time
    
    if batch.stop is False:
        cmd("get_data")
        time.sleep(1)
        data = SER.readline()
        split = re.split(' ', data)
        # print split
        if len(split) >= 4:
            ktherm_temp = float(split[2])
            amb_temp = float(split[3])
            rh = float(split[1])
            inc_temp = float(split[0])
             
        t_delta = datetime.timedelta((time.time()-last_time )/(3600*24))
        # dht_interval = 5       

    data = {'data': "time," + str(ktherm_temp) + "," + str(rh) + "," +
            str(amb_temp) + "," + str(inc_temp), 'delta': t_delta,
            'timer': dht_interval*1000}

    return data


def logger_msg(body_msg, image=None, image2=None):
    print "logger_msg", body_msg

    for email in mod.Email.objects.all():
        msg_from = email.from_email
        msg_to = [email.to_email]
        for to in mod.Recipients.objects.all():
            if to.add is True:
                msg_to.append(to.address)

        msg = MIMEMultipart()
        msg['From'] = msg_from
        msg['To'] = ", ".join(msg_to)
        msg['Subject'] = "Incubator message"
        body = body_msg
        msg.attach(MIMEText(body, 'plain'))
        if image is not None:
            fp = open(image, 'rb')
            img = MIMEImage(fp.read())
            fp.close()
            msg.attach(img)
        if image2 is not None:
            fp = open(image2, 'rb')
            img = MIMEImage(fp.read())
            fp.close()
            msg.attach(img)

        try:
            hotmail = smtplib.SMTP('smtp.live.com', 587)
            hotmail.starttls()
            hotmail.login(msg_from, email.from_password)
            text = msg.as_string()
            hotmail.sendmail(msg_from, msg_to, text)
            hotmail.quit()
        except (RuntimeError, TypeError, NameError, ValueError):
            print "Email not sent. Error"
        except:
            print "Email message failure"


timer = Timer(1, logger_init)
timer.start()
