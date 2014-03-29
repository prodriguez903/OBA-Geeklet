from __future__ import print_function
from functions import call, decode_json, build_dict_of_buses, print_departures_for_bus, notify, list_buses_at_stop
import simplejson as json




def main():
  primary_raw = call("arrivals-and-departures-for-stop", "1_1920", "minutesBefore=5&minutesAfter=60").text
  secondary_raw = call("arrivals-and-departures-for-stop", "1_1084", "minutesBefore=5&minutesAfter=60").text
  primary_stop = decode_json(primary_raw)
  secondary_stop = decode_json(secondary_raw)
  primary = build_dict_of_buses(primary_stop)
  secondary = build_dict_of_buses(secondary_stop)
  print_departures_for_bus(primary['1_202'], primary_stop)
  print_departures_for_bus(primary['40_554'], primary_stop)
  print_departures_for_bus(secondary['40_550'], secondary_stop)

#print("~~~~~~")

main()
#stops_for_202_raw = call("stops-for-route","40_550","version=2&includePolylines=false").text
#stops_json = decode_json(stops_for_202_raw)

#for i in stops_json['data']['references']['stops']:
#  print(json.dumps(i, sort_keys=True, indent=4 * ' '))
#print(type(list_buses_at_stop(busdict,primary_stop)))
#list_buses = list()
#list_buses = list_buses_at_stop(busdict,primary_stop)
#for index in range(len(list_buses)):
#  print(index + 1, list_buses[index])
#choice = raw_input("Pick a bus: ")
#choice = int(choice) - 1
#print("Your choice was: " + str(list_buses[choice]))
