# Network Survey Messaging Python Library

This is a simple python library that is used by clients of the
[network-survey-messaging MQTT
protocol](https://messaging.networksurvey.app/) to simplify message
construction and JSON serialization.  This library also connects to
the GPSD server and grabs PVT, ATT and SKY reports from the GPS/INS
device.

This library depends upon [gpsdthreaded](https://github.com/glencornell/gpsd-threaded).
