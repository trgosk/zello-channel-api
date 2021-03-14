# Zello-rtl-streamer
Streams audio in Ogg format to Zello API encoded with the [Opus codec](https://tools.ietf.org/html/rfc7845)

# Using with RTLSDR-Airband
This app can be used to stream audio from RTLSDR-Airband

### 1. General Theory of Operation

* Using my fork of [RTLSDR-Airband](https://github.com/trgosk/RTLSDR-Airband) Pulseaudio output as source of audio 
* Using [opusenc](https://opus-codec.org/docs/opus-tools/opusenc.html) utility from opus-tools to encode audio from Pulseaudio output into Ogg format
* Using this repo to stream opusenc output to Zello API

### 2. Voice activated transmission
In my fork of [RTLSDR-Airband](https://github.com/trgosk/RTLSDR-Airband) has an extra feature compared to original [szpajder/RTLSDR-Airband](https://github.com/szpajder/RTLSDR-Airband)
* Extra thread that is watching the squelch level in SCAN mode and a ZeroMQ publisher, so ZeroMQ sends a message about start and end of a transmission to listening subscribers

# Setup & Configuration

## Pulseaudio
### Install pulseaudio-utils
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install pulseaudio pulseaudio-utils libpulse-dev
```
### Create a virtual sink
```
pactl load-module module-null-sink format=float32le rate=16000 channels=1 sink_name=Virtual1
```

## Install and configure RTLSDR-Airband
Get the code
```
sudo apt-get install git libzmq3-dev
cd
git clone https://github.com/trgosk/RTLSDR-Airband.git
cd RTLSDR-Airband
```

Follow instructions on [szpajder/RTLSDR-Airband/wiki](https://github.com/szpajder/RTLSDR-Airband/wiki)

Extra steps:
Compile with `PULSE=1 VOXZMQ=1` options  
In rtl_airband.conf add at top level 
* add `vox_zmq_enabled = true;`
* optional add `vox_zmq_host = "tcp://*:5556"`

Configuation hints:
* use `mode = "scan"`
* define PulseAudio output `type = "pulse"`
   * define `sink = Virtual1`

## Install Opus encoder

```
sudo apt-get install opus-tools
```
sudo apt-get install libogg-dev libssl-dev libflac-dev
https://opus-codec.org/downloads/
libopusenc
opusfile
opus-tools
./configure
make
sudo make install
sudo ldconfig
<br/>

## Install and configure Zello-rtl-streamer
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3
```
sudo apt-get install build-essential python3 python3-dev python3-numpy
sudo apt-get python3-pip 
sudo pip3 install aiohttp 
sudo pip3 install configparser 
sudo pip3 install asyncio 
sudo pip3 install uvloop 
sudo pip3 install bitstream 
sudo pip3 install zmq
sudo pip3 install PyJWT
cd
git clone https://github.com/trgosk/zello-rtl-streamer.git
cd zello-rtl-streamer
```

# Prepare configuration file


## Edit the configuration file [stream.conf](./stream.conf).


### Configure the appropriate Zello account's `username` and `password`.

This account is used by the application to send the audio message.

### Set the `channel` name to send the message to.

Make sure the configured account is allowed to send the audio message to this channel.

### Get your private key and issuer value from [developers.zello.com/keys](https://developers.zello.com/keys)

Set `issuer` field  
Set `privatekeyfile` to filename with the private key 
<br/><br/>
# Test your setup
This will stream the `sample.opus` file
```
python3 main.py -t
```

## Operation as a systemd Service
Configure user service
```
sudo cp zello-rtl-streamer.service /etc/systemd/user/
sudo nano /etc/systemd/user/zello-rtl-streamer.service
systemctl --user enable zello-rtl-streamer.service
systemctl --user start zello-rtl-streamer.service
```
When expecting this problems while starting RTLSDR-Airband  
`pulse: <default_server>: connection failed: Connection refused`  
`pulse: <default_server>: failed to connect: Invalid argument`  
start RTLSDR-Airband also as user service
