#!/usr/bin/env python3

'''Sets the DNS name for this AWS ec2 host on boot.

Designed to be run on ec2 startup, will update a route53 record set
(given by target_record variable) with a CNAME record pointing at the
current public domain name of this ec2 instance, as determined through
instance metadata.


    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import datetime
import json
import logging
import sys
import urllib.request

import boto3

target_record = 'andy.aws.example.com'  # pylint: disable=invalid-name

#logging.basicConfig(level=logging.DEBUG)

def get_public_domain():
    '''Returns the public domain name of this EC2 instance from metadata.'''

    url_pubdmn = 'http://169.254.169.254/latest/meta-data/public-hostname'
    return urllib.request.urlopen(url_pubdmn).read().decode()

def get_hosted_zone():
    '''Returns the arn for the hosted zone for domain of target_record.'''

    domain = '.'.join(target_record.split('.')[1:])

    client = boto3.client('route53')
    result = client.list_hosted_zones_by_name(DNSName=domain)
    if len(result['HostedZones']) > 1:
        logging.warning(json.dumps(result))
        sys.exit("I am not currently prepared to have more than one zone returned.")
    return result['HostedZones'][0]['Id']

def update_r53():
    '''Update the Route53 Resource Record Set for target_record.  Returns the
    result from the AWS Route53 ChangeResourceRecordSets call.'''

    client = boto3.client('route53')
    target = get_public_domain()
    hosted_zone = get_hosted_zone()

    changes = {
        'Action':  'UPSERT',
        'ResourceRecordSet': {
            'Name': target_record,
            'Type': 'CNAME',
            'TTL': 300,
            'ResourceRecords': [
                {'Value': target}
            ],
        }
    }

    xargs = {
        'HostedZoneId': hosted_zone,
        'ChangeBatch': {
            'Changes': [changes]
        }
    }

    return client.change_resource_record_sets(**xargs)

def json_serial(obj):
    '''JSON serializer for objects not serializable by default json code'''

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


if __name__ == '__main__':
    logging.info(json.dumps(update_r53(), default=json_serial))
