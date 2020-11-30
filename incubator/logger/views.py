from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from subprocess import call
import time
import datetime
import calendar

import logger as log
import models as mod

rht_i = 10
rht_len = 0
rhts = None

def main_page(request):
    print "main_page"
    
    return render(request, 'logger/main_page.html', {})

def active(request):
    global rht_len, rhts, rht_i
    
    time_now = time.time()
    batch = mod.incubation.objects.last()
    if batch.stop is False:
        inc_time = (batch.start_date.year, batch.start_date.month,
                batch.start_date.day, batch.start_date.hour,
                batch.start_date.minute, batch.start_date.second)
        time_inc = calendar.timegm(inc_time)
        
        t_delta = datetime.timedelta((time_now-time_inc)/(3600*24))
        
        if t_delta.days < 21:
            rhts = mod.RHT.objects.filter(incub=batch)
            csv = []
            for i, rht in enumerate(rhts):
                if i < 1000:
                    csv.append(rht)
                else:
                    break
            rht_i = 1000
            rht_len = len(rhts)

            rot = mod.Rotation.objects.last()
            
            rot_list = mod.Rotation.objects.filter(incub=batch)
            
            context = { 'g_data': csv, 'rot':rot, 'rot_list': rot_list, 'batch':batch }
            return render(request, "logger/index.html", context)
		
        else:
            batch.stop = True
            incubations = mod.incubation.objects.all()
            return render(request, "logger/start.html", {'incubation': mod.IncubationForm, 'incubations': incubations})
					
    else:       
        #inc = incubation()
        incubations = mod.incubation.objects.all()
        return render(request, "logger/start.html", {'incubation': mod.IncubationForm, 'incubations': incubations})

def start(request):
    if request.method == "POST":
        print "start POST request"
        inc = mod.incubation()
        f = mod.IncubationForm(request.POST, inc)
        f.save()
        return render(request, "logger/index.html", {})
        
def timer(request):
    global rhts, rht_i, rht_len
    
    if request.is_ajax():
        #print time.localtime()
        #print rht_i, rht_len
        temp_len = 1000
        if rht_i < rht_len:
            if rht_i + temp_len < rht_len:
                j = rht_i + temp_len
            else:
                temp_len = rht_len - rht_i
                j = rht_len
                
            temp_s = ""
            print 'j', j, 'rht_len', rht_len
            for i in range(rht_i, j):
                temp_s += str(rhts[i].date_log.strftime("%a %b %d %Y %H:%M:%S %Z")) + ","
                temp_s += str(rhts[i].ktherm_temp) + ","
                temp_s += str(rhts[i].rh) + ","
                temp_s += str(rhts[i].amb_temp) + ","
                temp_s += str(rhts[i].inc_temp) + ";"
            rht_i += temp_len
            data = {'data': temp_s, 'timer': 1}
        else:            
            data = log.logger_get()
            #print data
                        
        return render_to_response('logger/timer.html',  data)

def get_keys(request):
    value=''
    for key in request.GET.keys():
        if key!='_':
            value=key
            break
    return value
    
def capture_image(request):
    if request.is_ajax():
        print "capture_image"
        t = time.gmtime()
        start_image_name = "/logger/pictures/" + str(t.tm_year) + '_' + str(t.tm_mon) + '_' + str(t.tm_mday) + '_' + str(t.tm_hour) + '_' + str(t.tm_min) + '.jpg'
        call(['fswebcam', '-S', '20', '-r', '1280x720', "/home/pi/incubator/logger/static" + start_image_name])
        #call(['motion', '-n'])
        context = {'image': start_image_name}        
        return render_to_response('logger/timer.html', context)

def past_inc(request, incubation_id):
    print "past_inc"
    past = mod.incubation.objects.filter(pk=incubation_id)

    # For first or older incubations
    dhts = mod.DHT.objects.filter(incub=past)
    rot_list = mod.Rotation.objects.filter(incub=past)
    rot = rot_list.last()

    # For newer incubations
    rhts = mod.RHT.objects.filter(incub=past)

    context = {'g_data': dhts, 'rot':rot, 'rot_list': rot_list, 'batch':past , 'rht_data': rhts}
    return render(request, "logger/past.html", context)

def rh_step(request):
    if request.is_ajax():
        value = get_keys(request)
        print "rh_step", value

        log.cmd("modify_rh_limit", value)
        time.sleep(1)
        log.cmd("peak_rh_&_temp_limit")
        time.sleep(1)
        print log.SER.readlines()

        return render_to_response('logger/timer.html', {})

def on_off(request):
    if request.is_ajax():
        value = get_keys(request)
        print "rh_step", value

        log.cmd("enable_incubator", value)
        print log.SER.readlines()

        return render_to_response('logger/timer.html', {})
        
