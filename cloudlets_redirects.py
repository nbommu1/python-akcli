#! /bin/env python
#
# distributed from ansible
#
# this module being imported in akapi

import json, os
import difflib
import csv
import urlparse as parse

def get_current_version(cloudlets_live_file, httpCaller, apisession, akconfig):

  version_path = "/cloudlets/api/v2/policies/%s/versions" % policy
  version_result = httpCaller.getResult(version_path)
  version = version_result[0]["version"]
  headers = {'Content-Type': 'application/octet-stream'}
  path = "/cloudlets/api/v2/policies/{}/versions/{}/download".format(policy, version)
  baseurl = 'https://{}/'.format(akconfig.get('default','host'))
  products_result = apisession.get(parse.urljoin(baseurl,path),headers=headers)
  current_version = '{}-{}.csv'.format(cloudlets_live_file, version)
  with open(current_version, 'w') as f:
    writer = csv.writer(f)
    reader = csv.reader(products_result.text.splitlines())
    for row in reader:
      writer.writerow(row)
  return current_version

def cloudlets_activate(policy, version, activate, httpCaller):
  # now we know which version and we've set the policy
  activation_path = "/cloudlets/api/v2/policies/%s/versions/%s/activations" % (policy, version)
  print "activating cloudlets version {} in {}".format(version, activate)
  activation_obj = {
                    "network": activate
                    }
  activation_result = httpCaller.postResult(activation_path, json.dumps(activation_obj))


def create_cloudlets_version(ticket, partner, httpCaller):
  print"creating cloudlets version {} {}".format(ticket, partner)
  new_version_info = {
                      "description":"{} Adding a new partner {} match rules".format(ticket, partner),
                       "matchRuleFormat":"1.0",
                       "matchRules": []
                      }
  create_path = "/cloudlets/api/v2/policies/%s/versions" % policy
  create_result = httpCaller.postResult(create_path, json.dumps(new_version_info))

def cloudlets_edge_redirector(args, httpCaller, apisession, akconfig):

  ticket = args.ticket
  partner = args.partner
  activate = args.activate

  # get the current version and save it in tmp for processing later
  old_version = get_current_version(cloudlets_live_file, httpCaller, apisession, akconfig)

  if cloudlets_version == "create" and activate != "production":
     create_cloudlets_version(ticket, partner, httpCaller)

  # get the new verson to upload rules.
  version_path = "/cloudlets/api/v2/policies/%s/versions" % policy
  version_result = httpCaller.getResult(version_path)
  # print json.dumps(version_result)
  version = version_result[0]["version"]
  # print version

  # now we know which version and we've set the policy


  # Open the JSON filename with mappings and activate in staging,
  # print the diff at the end

  if activate == "staging":
    with open(filename) as data_file:
      data = json.load(data_file)
    for rule in data:
      rule_path = "/cloudlets/api/v2/policies/%s/versions/%s/rules" % (policy, version)
      rule_result = httpCaller.postResult(rule_path, json.dumps(rule))
      # print rule_result
      print "uploading rules......"

    # get the new version to compare before activating in staging

    new_version =  get_current_version(cloudlets_live_file, httpCaller, apisession, akconfig)
    with open(old_version, 'rb') as f1:
      file_one = f1.readlines()
    with open(new_version, 'rb') as f2:
      file_two = f2.readlines()
    print os.linesep.join(difflib.unified_diff(file_one, file_two))

    # clean up files after the diff
    for f in [ old_version, new_version ]:
      if os.path.exists(f):
        os.remove(f)

    # activate the new version in stage
    cloudlets_activate(policy, version, activate, httpCaller)
  else:
    # assuming we have version activated in staging
    # go ahead and activate in prod
    cloudlets_activate(policy, version, activate, httpCaller)


cloudlets_version = "create"
cloudlets_live_file = "/tmp/cloudlets_live"
# set up policy and redirect file
policy = "12345"
filename = "/etc/akamai/redirects.json"
