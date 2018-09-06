#!/bin/env python
#
# distributed from ansible
#
#
# Talk to the Akamai API.
# this module being imported in akapi

### Imports

import email
import json
import smtplib
import sys
import time

## do_purge
#
# Do a purge.

def do_purge(args, httpCaller):

  # Assemble the data to post.

  data = { "type": args.type,
           "objects": args.objects }

  if args.type == 'cpcode':
    data['action'] = "remove"

  # If we're going to notify anyone, prepare to stash notification text.

  if args.notify:
    notification_text="Here are the results of purging {} {}:\n\n".format(args.type, args.objects)

  # Submit the purge request, stash the result for later notification if
  # we're notifying anyone, and print the result right now too unless quiet
  # is on.

  result = httpCaller.postResult('/ccu/v2/queues/default', json.dumps(data))

  result_text = "Purge request sent. Result:\n\n"
  result_text += json.dumps(result, sys.stdout, sort_keys=True, indent=1)

  if args.notify:
    notification_text = notification_text + result_text + "\n"

  if not args.quiet:
    print result_text

  # Wait a bit before we start checking status.

  waiting_text = "\nWaiting {0} seconds before starting to ping for status...\n".format(result['pingAfterSeconds'])

  if args.notify:
    notification_text = notification_text + waiting_text + "\n"

  if not args.quiet:
    print waiting_text

  time.sleep(result['pingAfterSeconds'])

  # Stash the original result, and clear the result variable for reuse.

  purge_result = result
  progress_uri = result['progressUri']

  result = {}
  result['purgeStatus'] = ""

  # Check on the progress, until it finishes. Each time, stash the result
  # for later notification if we're notifying anyone, and print the result
  # right now too unless quiet is on.

  while result['purgeStatus'] != "Done":

    result = httpCaller.getResult(progress_uri)

    result_text = "Status request sent. Result:\n\n"
    result_text += json.dumps(result, sys.stdout, sort_keys=True, indent=1)

    if args.notify:
      notification_text = notification_text + result_text + "\n"

    if not args.quiet:
      print result_text

    if 'pingAfterSeconds' in result:

      waiting_text = "\nWaiting {0} seconds before pinging for status again...\n".format(result['pingAfterSeconds'])

      if args.notify:
        notification_text = notification_text + waiting_text + "\n"

      if not args.quiet:
        print waiting_text

      time.sleep(result['pingAfterSeconds'])

  # If we get this far, we're done! Say so, and send a notification if we're
  # notifying anyone.

  if not args.quiet:
    print "\nDone!\n"

  if args.notify:

    notification_text = notification_text + "\nDone!\n\n"

    msg = email.MIMEText.MIMEText(notification_text)

    msg.add_header('From', 'Akamai Cache Purge Script <niranjan.bommu@gmail.com>')
    msg.add_header('To', args.notify)
    msg.add_header('Subject', "Akamai cache purge notification")

    smtpconnection = smtplib.SMTP("localhost")
    smtpconnection.ehlo()
    smtpconnection.sendmail("niranjan.bommu@gmail.com", args.notify, msg.as_string())
    smtpconnection.quit()

  if not args.quiet:
    if args.notify:
      print "(sent notification to {0})\n".format(args.notify)
    else:
      print "(no e-mail notification sent)\n"
