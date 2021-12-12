import os
import urllib.request
import json
import time
import re

def get_metrics(manager):
    if not manager or manager==None:
        manager = "127.0.0.1"
    url = urllib.request.urlopen('http://%s/rest/items?fields=name,state,type' % (manager))
    content_bytes = url.read()
    content = content_bytes.decode('utf-8')
    url.close()

    obj = json.loads(content)

    numbers = [ item for item in obj if item['type'].lower().startswith('number') ]
    switches = [ item for item in obj if item['type'].lower().startswith('switch') ]
    contacts = [ item for item in obj if item['type'].lower().startswith('contact') ]
    strings = [ item for item in obj if item['type'].lower().startswith('string') ]

    res = ''
    res = res + print_metrics(numbers, 'number')
    res = res + print_metrics(switches, 'switch')
    res = res + print_metrics(contacts, 'contact')
    res = res + print_metrics(strings, 'string')

    return res

def print_metrics(metrics, type):
    res = ""
    for metric in metrics:
        strings = metric['name'].split('_')
        if metric['name'].startswith("solarwattBattery"):
            metric_name = strings[1]+'_'+strings[4]
        if metric['name'].startswith("modbus"):
            metric_name = strings[1]+'_'+strings[2]+'_'+strings[5]
        if metric_name.startswith("batteryflex"):
            metric_name = metric_name[:-12]
        if metric_name.startswith("sunspec"):
            if metric_name.endswith("kiwios"):
                metric_name = metric_name[:7]
        if metric_name.startswith("batteryflex"):
            uid = strings[2]+'_'+strings[3]
        if metric_name.startswith("sunspec"):
            uid = strings[3]+'_'+strings[4]
        name = strings[5]
        if metric_name.startswith("sunspec"):
            name = name + "_" + strings[6]
            if len(strings) > 7:
                name = name + "_" + strings[7]
        value = metric['state']
        vlabel = ""

        if value is None or value == 'NULL':
            continue
        if metric['type'].lower() == 'switch':
            value = 1 if value == 'ON' else 0
        elif metric['type'].lower() == 'contact':
            value = 1 if value == 'OPEN' else 0
        elif metric['type'].lower() == 'string':
            vlabel = ',value="'+value+'"'
            value = 1

        if isinstance(value,str):
          value = re.sub(r'[a-z°ω]','',value.lower()).strip()
          if value == "":
            value = "0"

        res = res + metric_name + '{uid="' + uid + '",name="' + name + '"'+vlabel+'} ' + '{}\n'.format(value)

    return res

def app(environ, start_response):
    try:
        metrics = get_metrics(os.getenv('MANAGER'))
    except urllib.error.HTTPError as e:
        start_response(str(e.code)+" "+e.msg,[('Content-Type', 'text/plain')])
        return iter([])

    data = metrics.encode('utf-8')

    start_response('200 OK', [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(data)))
        ])

    return iter([data])

