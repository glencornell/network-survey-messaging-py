#!/usr/bin/env python3
"""
Connect to a running gpsd instance and publish device_status_message to an MQTT broker.
"""
import gpsdthreaded
import sys
import time
import network_survey

def main_loop(gpsd, args):
    the_ds_record = network_survey.DeviceStatus(args)
    the_ds_record.connect()
    while True:
        gps = gpsd.get_current()
        # continue only if there's a gps fix
        if gps.mode >= 2:
            the_ds_record.update_gps(gps)
            the_ds_record.batteryLevelPercent = 75
            the_ds_record.publish()
        # to prevent excessive CPU utilization:
        time.sleep(1)

def main():
    args = network_survey.Args()
    args.parse_args()
    print(f"Attempting to connect to gpsd:://{args.gpsd_host}:{args.gpsd_port}/")
    try:
        gpsd = gpsdthreaded.ThreadedClient()
        gpsd.connect(host=args.gpsd_host, port=args.gpsd_port)
        main_loop(gpsd, args)
    except (ConnectionError, EnvironmentError) as e:
        print(e)
    except KeyboardInterrupt:
        gpsd.terminate()
        print()
        return 0

if __name__ == "__main__":
    sys.exit(main())
