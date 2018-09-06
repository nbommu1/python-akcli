#!/bin/env python
#
# distributed from ansible
#

import sys
import json
import logging
import requests
from akamai.edgegrid import EdgeGridAuth,EdgeRc

### dns.py
# This is dns.py, from https://github.com/iamseth/akcli
# as of 2016-04-06, d7fb3d5f67bba093ad453efc4d19564f74f6d1b0, modified according
# our requirements 


# Python edgegrid module
""" Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.

 You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

# begin dns.py

if sys.version_info.major < 3:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

log = logging.getLogger(__name__)

class AkamaiDNSError(Exception):
    pass


class AkamaiDNS(object):
    def __init__(self, baseurl, configfile):
        self.baseurl = baseurl
        self.session = requests.Session()
        self.session.auth = EdgeGridAuth.from_edgerc(configfile)

    def _update_zone(self, zone):
        '''Update a given Zone. This method will handle incrementing the SOA serial number.

        :param zone: The zone to update.
        :return: True if successful otherwise False.
        '''

        # Increment the serial.
        zone['zone']['soa']['serial'] += 1
        name = zone['zone']['name']
        url = urljoin(self.baseurl, '/config-dns/v1/zones/{0}'.format(name))
        headers = {'content-type': 'application/json'}
        result = self.session.post(url, data=json.dumps(zone), headers=headers)

        if result.status_code != 204:
            log.error('Something went very wrong with updating the zone "{0}": {1}'.format(name, result.text))
            return False
        return True

    def fetch_zone(self, zone_name):
        '''Fetch a dictionary representation of a zone file.

        :param zone_name: This is the name of the zone e.g. citruslane.com.
        :return: A dict containing a zone.
        '''
        url = urljoin(self.baseurl, '/config-dns/v1/zones/{0}'.format(zone_name))
        result = self.session.get(url)
        if result.status_code == 404:
            log.error('Zone "{0}" not found.', zone_name)
            return None
        return result.json()

    def list_records(self, zone_name, record_type=None):
        '''List all records for a particular zone.

        :param zone_name: This is the name of the zone e.g. citruslane.com.
        :param record_type: (Optional) The type of records to limit the list to.
        :return: A list containing all records for the zone.
        '''

        zone = self.fetch_zone(zone_name)['zone']
        records = []
        for key, val in zone.items():
            if not isinstance(val, list): continue
            for record in val:
                record['type'] = key.upper()
                records.append(record)

        # Add a filter by record type if provided
        if record_type:
            return [r for r in records if r['type'] == record_type.upper()]
        return records

    def add_record(self, zone_name, record_type, name, target, ttl=600):
        '''Add a new DNS record to a zone.

        If the record exists, this will still return successfully so it is safe to re-run.

        :param zone_name: Name of the zone to add a record to.
        :param record_type: Type of record (a, cname etc).
        :param name: This is the "from" section. That is for test.citruslane.com, this would be test.
        :param target: This is the "to" section e.g. "10.0.0.1".
        :param ttl: The DNS record time to live value. Defaults to 600.
        :return: Returns True if successful, otherwise False.
        '''
        record_type = record_type.lower()
        zone = self.fetch_zone(zone_name)
        if not zone:
            raise AkamaiDNSError('Zone {0} not found.'.format(zone_name))

        zone['zone'][record_type].append({'name': name, 'target': target, 'ttl': ttl, 'active': True})
        return self._update_zone(zone)

    def fetch_records(self, zone_name, record_type, name):
        ''' Fetch list of records matching a particular type and name.

        :param zone_name: Name of the zone to remove a record from.
        :param record_type: Type of record (a, cname, ptr, etc).
        :param name: This is the "from" section. That is for test.citruslane.com, this would be test.

        :return: Returns a potentially empty list of records.
        '''

        records = self.list_records(zone_name, record_type)
        return [r for r in records if r['name'] == name.lower()]

    def remove_record(self, zone_name, record_type, name, target):
        '''Remove a DNS record from a given zone.

        :param zone_name: Name of the zone to remove a record from.
        :param name: This is the "from" section. That is for test.example.com, this would be test.
        :param target: This is the "to" section e.g. "10.0.0.1".

        :return: Returns True if successful, otherwise False.
        '''
        record_type = record_type.lower()
        zone = self.fetch_zone(zone_name)
        if not zone:
            raise AkamaiDNSError('Zone {0} not found.'.format(zone_name))

        for record in self.list_records(zone_name, record_type):
            if (record['name'].lower() == name.lower()) and (record['target'] == target):
                record.pop('type', None)
                zone['zone'].get(record_type).remove(record)
                return self._update_zone(zone)
        return True

# end dns.py
