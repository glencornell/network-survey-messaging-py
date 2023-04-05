import argparse
import os
import sys

class Args:
    """The Args class contains the application context, including the parameters to connect woth the MQTT Broker and GPSD daemon."""
    def __init__(self):
        self.gpsd_host=os.getenv("GPSD_HOST") or 'localhost'
        self.gpsd_port=os.getenv("GPSD_PORT") or 2947
        self.gpsd_port=int(self.gpsd_port)
        self.mqtt_host=os.getenv("MQTT_HOST") or 'localhost'
        self.mqtt_port=os.getenv("MQTT_PORT") or 1883
        self.mqtt_port=int(self.mqtt_port)
        self.mqtt_user=os.getenv("MQTT_USER") or None
        self.mqtt_password=os.getenv("MQTT_PASSWORD") or None
        self.mqtt_tls=os.getenv("MQTT_TLS") or 0
        self.mqtt_tls=int(self.mqtt_tls)
        self.mqtt_use_ca_cert=os.getenv("MQTT_USE_CA_CERT") or 0
        self.mqtt_use_ca_cert=int(self.mqtt_use_ca_cert)
        self.mqtt_client_id = os.getenv('MQTT_CLIENT_ID') or os.getenv('DEVICE_NAME') + os.uname().nodename
        self.device_id=os.getenv("DEVICE_ID")
        self.device_name=os.getenv("DEVICE_NAME")
        self.device_model=os.getenv("DEVICE_MODEL")
        self.protocol_version='JATF-0.9.0' # This should require a code change
        self.survey_name=os.getenv("SURVEY_NAME")
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description=__doc__,
        )

    def parse_args(self):
        self.parser.add_argument(
            "--gpsd_host",
            help="The host running GPSD",
        )
        self.parser.add_argument(
            "--gpsd_port",
            type=int,
            help="GPSD port",
        )
        self.parser.add_argument(
            "--mqtt_host",
            help="Hostname or IP address of the network survey MQTT broker",
        )
        self.parser.add_argument(
            "--mqtt_port",
            type=int,
            help="Port number of the network survey MQTT broker",
        )
        self.parser.add_argument(
            "--mqtt_user",
            help="User name for the network survey MQTT broker",
        )
        self.parser.add_argument(
            "--mqtt_password",
            help="Password for the network survey MQTT broker",
        )
        self.parser.add_argument(
            "--mqtt_tls",
            type=int,
            help="Use TLS for the network survey MQTT broker",
        )
        self.parser.add_argument(
            "--mqtt_use_ca_cert",
            type=int,
            help="Use CA cert for the network survey MQTT broker",
        )
        self.parser.add_argument(
            "--mqtt_client_id",
            help="Client ID for network survey MQTT broker",
        )
        self.parser.add_argument(
            "--device_id",
            help="Unique, machine identifier",
        )
        self.parser.add_argument(
            "--device_name",
            help="Unique, human readable device name",
        )
        self.parser.add_argument(
            "--device_model",
            help="Human readable device make & model",
        )
        self.parser.add_argument(
            "--survey_name",
            help="The human readable name for the mission (aka survey, exercise or campaign)",
        )
        args = self.parser.parse_args()
        # now validate the arguments
        # mqtt user/pw/tls/cert isn't required
        if (self.gpsd_host is None or
                self.gpsd_port is None or
                self.mqtt_host is None or
                self.mqtt_port is None or
                self.device_id is None or
                self.device_name is None or
                self.device_model is None or
                self.protocol_version is None or
                self.survey_name is None):
            print("Error: empty parameters")
            self.parser.print_help(sys.stderr)
            sys.exit(1)
