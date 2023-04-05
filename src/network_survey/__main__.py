import sys
import gpsdthreaded
import time
from .args import Args
from .network_survey import GnssRecord

def main_loop(gpsd, args):
    while True:
        gps = gpsd.get_current()
        # continue only if there's a gps fix
        if gps.mode >= 2:
            GnssRecord(args, gps).publish()
        # to prevent excessive CPU utilization:
        time.sleep(1)

def main():
    args = Args()
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
