# nixflickr
NixPlay / Flickr album sync

Requires Python3.6+

# Installation

`service/install.sh`

Nixplay credentials must be configured for the systemd service (see below)

# Credentials

Set NixPlay credentials as environment variables, or specify --username and --password at the commandline
* NIXPLAY_USERNAME=username
* NIXPLAY_PASSWORD=password

Set NixPlay credentials for systemd service

`systemctl edit nixflix.service`

Enter the following for override.conf
```
[Service]
Environment="NIXPLAY_USERNAME=<username here>"
Environment="NIXPLAY_PASSWORD=<password here>"
```


# Usage

`python nixflix.py --playlist <NixPlay playlist name> --album <Flickr Album Name>`
