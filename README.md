# Cloudflare DNS Updater
This image will automatically update your Cloudflare DNS records using their API and whatsmyip's API. It will first determine your IP and compare to Cloudflare then update if necessary. You will have to mount a volume to /ScriptData for the configuration file and log file.

Here is an example docker-compose

```
services:
  app:
      image: adambastin/cloudflare-ip-updater:latest
      volumes:
          -  /Path/To/Config:/ScriptData
```
After running for the first time, you will need to:

1. Edit the cloudflarescript.config file with your API key and zone ID.
2. Save your changes
3. Start the container again
