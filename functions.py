from __future__ import print_function
__author__ = 'prodriguez'
import requests
import simplejson as json
from urllib import urlencode
from sys import exit, stderr
import time
from collections import defaultdict
import objc


#http://api.pugetsound.onebusaway.org/api/where/stops-for-route/1_202.json?key=TEST&version=2&includePolylines=false


def build_url(api_call, option1 = "", option2 = None, use_beta_api=False):
  """ This function builds the URL required to make the call to OBA  """
  beta_api_url = 'http://soak-api.pugetsound.onebusaway.org/'
  api_url = 'http://api.pugetsound.onebusaway.org/'
  api_key = 'TEST'
  if type(option2) is str and len(option2) > 0:
    xtra_parameters = "&" + option2
  elif type(option2) is dict:
    xtra_parameters = urlencode(option2)
  else:
    xtra_parameters = ""
  if len(option1) > 0:
    api_call = api_call + "/" + option1
  else:
    pass
  if use_beta_api:
    url = beta_api_url
  else:
    url = api_url
  request_url = url + 'api/where/' + api_call + '.json?key=' + api_key + xtra_parameters
  return request_url

def call(method,option1,option2):
  url = build_url(method,option1,option2)
  try:
    request = requests.get(url)
  except requests.exceptions.ConnectionError:
    print("Connection Error, Try again later.", file=stderr)
    exit(1)
  try:
    request.raise_for_status()
  except (requests.exceptions.HTTPError, requests.exceptions.Timeout, requests.exceptions.ConnectionError):
    error = str("Server returned unexpected results. {!r} {!r}").format(request.status_code, url)
    print(error, file=stderr)
    exit(1)
  return request

def decode_json(json_encoded):
  def _decode_list(data):
    rv = []
    for item in data:
      if isinstance(item, unicode):
        item = item.encode('utf-8')
      elif isinstance(item, list):
        item = _decode_list(item)
      elif isinstance(item, dict):
        item = _decode_dict(item)
      rv.append(item)
    return rv
  def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
      if isinstance(key, unicode):
        key = key.encode('utf-8')
      if isinstance(value, unicode):
        value = value.encode('utf-8')
      elif isinstance(value, list):
        value = _decode_list(value)
      elif isinstance(value, dict):
        value = _decode_dict(value)
      rv[key] = value
    return rv
  # Build Dictionary tree from JSON received from OBA.
  try:
    """ Found the functions on the internet that converts unicode strings back ASCII strings since Python seems
  to shit on itself when it encounters unicode """
    decoded_data = json.loads(json_encoded, use_decimal = True, object_hook = _decode_dict)
  except TypeError:
  # Using print() from futures collection since its the best way to print to stderr.
    print("Got bad JSON from provider. Aborting..", file = stderr)
    print(json_encoded)
    exit(1)
  return decoded_data

def get_time(epoch_ms):
  time_epoch = epoch_ms / 1000
  time_human = time.strftime("%a, %d %b %Y %r", time.localtime(time_epoch))
  return time_human

def build_dict_of_buses(decoded_json):
  # Get total number of rows returned
  num_items = len(decoded_json['data']['arrivalsAndDepartures'])
  #print(len(decoded_data['data']['arrivalsAndDepartures']))
  """ Initializing data sets here. I will be putting busses into a list of buses and then recording the index for each time
  that bus appears in the array. """
  buses = set()
  #busdict = dict()
  # http://stackoverflow.com/questions/22421298/what-is-the-best-way-to-append-lists-inside-a-dict
  busdict = defaultdict(list)
  for i in range(num_items):
  # decoded_data['data']['arrivalsAndDepartures']
  #if decoded_data['data']['arrivalsAndDepartures'][i]['routeId'] == '40_554':
    bus = decoded_json['data']['arrivalsAndDepartures'][i]['routeId']
    buses.add(bus)
    busdict.setdefault(bus,[]).append(i)
  return busdict

def return_friendly_businfo(dict_of_buses,decoded_json):
  for index in dict_of_buses:
    bus_info = str(decoded_json['data']['arrivalsAndDepartures'][index]['routeShortName'] + ' ' + \
               decoded_json['data']['arrivalsAndDepartures'][index]['tripHeadsign']).format()
    return bus_info

def print_departures_for_bus(dict_of_buses,decoded_json):
  for index in dict_of_buses:
    bus_info = return_friendly_businfo(dict_of_buses,decoded_json)
    predicted_departure_time = decoded_json['data']['arrivalsAndDepartures'][index]['predictedDepartureTime']
    predicted_arrival_time = decoded_json['data']['arrivalsAndDepartures'][index]['predictedArrivalTime']
    scheduled_arrival_time = decoded_json['data']['arrivalsAndDepartures'][index]['scheduledArrivalTime']
    scheduled_departure_time = decoded_json['data']['arrivalsAndDepartures'][index]['scheduledDepartureTime']
    scheduled_arrival_time_human = get_time(scheduled_arrival_time)
    scheduled_departure_time_human = get_time(scheduled_departure_time)
    if predicted_arrival_time > 0:
      predicted_arrival_time_human = get_time(predicted_arrival_time)
      predicted_departure_time_human = get_time(predicted_departure_time)
      output = str("Bus: {!s}\nScheduled Arrival: {!s}\nPredicted Arrival: {!s}\nScheduled Departure: {!s}\n" + \
          "Predicted Departure: {!s}\n").format(bus_info, scheduled_arrival_time_human, predicted_arrival_time_human, \
                                          scheduled_departure_time_human, predicted_departure_time_human)
    else:
      #output = str("Bus: {!s}\nScheduled Arrival: {!s}\nScheduled Departure: {!s}\n").format(bus_info, scheduled_arrival_time_human,
      #                                    scheduled_departure_time_human,)
      #output = str("Bus: {!s}\nScheduled Departure: {!s}\n").format(bus_info, scheduled_departure_time_human)
      output =str()
      pass
    print(output)
    #print(json.dumps(decoded_data['data']['arrivalsAndDepartures'][index],sort_keys=True, indent=4 * ' '))
  #for item in decoded_data['data']['arrivalsAndDepartures']:
  #print(json.dumps(item, sort_keys=True, indent=4 * ' '))
  # print(decoded_data['data']['entry'])
  # print(repr(item) + repr(type(item)))

def list_buses_at_stop(dict_of_buses,decoded_json):
  keys = dict_of_buses.iterkeys()
  final = list()
  final = defaultdict(list)
  for i in keys:
    bus_info = return_friendly_businfo(dict_of_buses[i],decoded_json)
    final.append(bus_info)
    #final.setdefault(i,bus_info)
  return final

def notify(title, subtitle, info_text, delay=0, sound=False, userInfo={}):
  NSUserNotification = objc.lookUpClass('NSUserNotification')
  NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')
  notification = NSUserNotification.alloc().init()
  notification.setTitle_(title)
  notification.setSubtitle_(subtitle)
  notification.setInformativeText_(info_text)
  notification.setUserInfo_(userInfo)
  if sound:
     notification.setSoundName_("NSUserNotificationDefaultSoundName")
  notification.setDeliveryDate_(Foundation.NSDate.dateWithTimeInterval_sinceDate_(delay, Foundation.NSDate.date()))
  NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)
