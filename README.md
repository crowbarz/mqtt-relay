# mqtt-relay

Monitor file changes and publish contents to MQTT whenever the file is updated. Provides the functionality of [watchdir](https://github.com/jpmens/mqtt-watchdir) but for just a single path.

## Installation

```bash
$ pip install mqtt_relay
```

## Usage
```
usage: mqtt-relay [-h] [-H HOST] [-P PORT] [--connect-timeout CONNECT_TIMEOUT]
                  [--max-reconnect-delay MAX_RECONNECT_DELAY] [-u USERNAME]
                  [-p PASSWORD] [--password-file PASSWORD_FILE] [-c CLIENT_ID] [-C] -t
                  TOPIC [--payload-file-missing PAYLOAD_FILE_MISSING] [-q {0,1,2}]
                  [-R] [--refresh-interval REFRESH_INTERVAL] [--keepalive KEEPALIVE]
                  [--tls] [--tls-insecure TLS_INSECURE] [--ca-certs CA_CERTS]
                  [--certfile CERTFILE] [--keyfile KEYFILE]
                  [--birth-topic BIRTH_TOPIC] [--birth-payload BIRTH_PAYLOAD]
                  [--birth-qos {0,1,2}] [--birth-retain] [--will-topic WILL_TOPIC]
                  [--will-payload WILL_PAYLOAD] [--will-qos {0,1,2}] [--will-retain]
                  [--inotify-trigger-delay INOTIFY_TRIGGER_DELAY]
                  [--inotify-restart-delay INOTIFY_RESTART_DELAY] [--daemon]
                  [--pidfile PIDFILE] [-d DEBUG] [--logfile LOGFILE] [-v]
                  path

positional arguments:
  path                  Path to file whose contents are relayed to MQTT

options:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  Hostname for the MQTT broker
  -P PORT, --port PORT  Port for the MQTT broker
  --connect-timeout CONNECT_TIMEOUT
                        Timeout for initial connection to MQTT broker
  --max-reconnect-delay MAX_RECONNECT_DELAY
                        Set maximum broker reconnect delay (in seconds)
  -u USERNAME, --username USERNAME
                        Username to authenticate with MQTT broker
  -p PASSWORD, --password PASSWORD
                        Password to authenticate with MQTT broker
  --password-file PASSWORD_FILE
                        Path to file to read password from
  -c CLIENT_ID, --client-id CLIENT_ID
                        Client ID to use when connecting to MQTT broker
  -C, --clean-session   Set MQTT retain flag for published message
  -t TOPIC, --topic TOPIC
                        MQTT topic for published message
  --payload-file-missing PAYLOAD_FILE_MISSING
                        MQTT payload to publish if file is not found
  -q {0,1,2}, --qos {0,1,2}
                        MQTT QoS for published message
  -R, --retain          Set MQTT retain flag for published message
  --refresh-interval REFRESH_INTERVAL
                        Set the interval for republishing with current content
  --keepalive KEEPALIVE
                        Set the keepalive interval for the MQTT client
  --tls                 Enable SSL/TLS support
  --tls-insecure TLS_INSECURE
                        Disable certificate verification. Not recommended
  --ca-certs CA_CERTS   Path to the Certificate Authority certificate files that are
                        to be treated as trusted
  --certfile CERTFILE   Path to the PEM encoded client certificate for authentication
                        with the broker
  --keyfile KEYFILE     Path to the private keys for authentication with the broker
  --birth-topic BIRTH_TOPIC
                        Set a birth topic to be sent to the broker
  --birth-payload BIRTH_PAYLOAD
                        Set a birth payload to be sent to the broker
  --birth-qos {0,1,2}   Set the QoS for the birth payload
  --birth-retain        Set retain flag for the birth payload
  --will-topic WILL_TOPIC
                        Set a will topic to be sent to the broker
  --will-payload WILL_PAYLOAD
                        Set a will payload to be sent to the broker
  --will-qos {0,1,2}    Set the QoS for the will payload
  --will-retain         Set retain flag for the will payload
  --inotify-trigger-delay INOTIFY_TRIGGER_DELAY
                        Time in seconds to wait after file update is detected before
                        publishing file
  --inotify-restart-delay INOTIFY_RESTART_DELAY
                        Time in seconds to wait before restarting inotify watcher
  --daemon              Run application as a daemon
  --pidfile PIDFILE     File to store PID when running as a daemon
  -d DEBUG, --debug DEBUG
                        Set application debug level
  --logfile LOGFILE     File to log messages to
  -v, --version         Show application version
```
