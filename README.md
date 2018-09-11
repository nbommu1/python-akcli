# akcli
An Akamai command line client written in Python. So far e DNS config API, cloudlets edge redirects and CCU purge are supported.

# What can it do?

Currently, the following items are supported.
  - ccu
  - redirect
  - dns
    - add_record
    - fetch_record
    - fetch_zone
    - list_records
    - remove_record

The --json flag will format output as JSON to be consumed by other tools such as [jq](https://stedolan.github.io/jq/).

# Installation


## Manually

```bash
git clone https://github.com/nbommu1/python-akcli.git
```

# Configuration

By default, akcli looks for a config file at ~/.akamai.cfg. The file should look something like this.

```ini
[auth]
baseurl = https://abcd-yaddayadda.luna.akamaiapis.net/
client_token = abcd-yaddayadda
client_secret = randomstuffhere
access_token = abcd-randomstuffhere
```
since we existing api client can't do CCU purge, we have to setup separate credentails for CCU( I did that /etc/akamai-edgerc)
# Usage

```bash
usage: akcli [-h] [--configfile CONFIGFILE] [--verbose VERBOSE]
             [--debug DEBUG] [--json JSON]
             {ccu,redirect,dns} ...

Talk to an Akamai API.

optional arguments:
  -h, --help            show this help message and exit
  --configfile CONFIGFILE
                        Path to config file (default: ~/.akamai.cfg)
  --verbose VERBOSE, -v VERBOSE
                        Enables verbose mode.
  --debug DEBUG         Enables debug mode.
  --json JSON           Output as JSON only for DNS.

Subcommands:
  {ccu,redirect,dns}    more help: akapi <subcommand> --help
    ccu                 purge the cache
    redirect            cloudlets edge redirector
    dns                 akamai fastDNS

```
