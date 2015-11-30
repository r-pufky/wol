#!/usr/bin/python2.6 -u
# -*- coding: utf-8 -*-
#
# Copyright 2010, Robert M. Pufky
# Send Wake On LAN packets to given MAC addresses via Apache2 CGI.
#
"""Send Wake On LAN packets to given MAC addresses.

This is somewhat hard-coded to a Ubuntu installation, and assumes that the SUID
bit has been set on the etherwake binary.
"""
__author__ = 'Robert Pufky'
import cgi
import re
import subprocess

COMPUTERS = {
  'Media Center': 'FF:FF:FF:FF:FF:FF',
  'Mac Desktop': 'FF:FF:FF:FF:FF:FF',
  'Windows Desktop': ['FF:FF:FF:FF:FF:FF', 'FF:FF:FF:FF:FF:FF']}
ETHERWAKE = '/usr/sbin/etherwake'
print 'Content-Type: text/html'
print


class Error(Exception):
  """Base exception WakeOnLan CGI script."""


class BadEthernetAddress(Error):
  """A mal-formed ethernet address was specified."""


class WakeOnLanFail(Error):
  """An attempt to send the WOL magic packet failed."""


class MacAddress(object):
  """Contains MAC address and specific MAC address related functions.

  Accepts a MAC address in the format 00:00:00:00:00:00 or 00-00-00-00-00-00, or
  a list, verifies and stores the MAC address.

  Attributes:
    _MAC_REGEX: Regex object to match MAC addresses using : or -.
    _mac: List containing Strings reprsenting the MAC address.
  """
  _MAC_REGEX = re.compile('([a-fA-F0-9]{2}[:|\-]?){6}')

  def __init__(self, address):
    """Initialize MAC address with a given ethernet address.

    Args:
      address: String/List containing ethernet address.

    Raises:
      BadEthernetAddress: If ethernet address cannot be parsed.
    """
    if isinstance(address, list):
      mac_as_list = address
    elif self._MAC_REGEX.match(address):
      mac_as_list = re.findall('[a-fA-F0-9]{2}', address)
    else:
      raise BadEthernetAddress('%s is not a valid ethernet address!' % address)
    self._mac = [str(byte) for byte in mac_as_list]

  def MacAddress(self):
    """Returns a properly formatted MAC address String."""
    return ':'.join(self._mac)


class Computer(object):
  """Contains information related to computers for WOL purposes.
  
  Attributes:
    adaptors: List containing MacAddress objects.
  """

  def __init__(self, mac_addresses):
    """Initalize Computer class.

    Args:
      mac_addresses: String/List containing MAC addresses for this computer.
    """
    self.adaptors = []
    if not isinstance(mac_addresses, list):
      mac_addresses = [mac_addresses]
    for address in mac_addresses:
      self.adaptors.append(MacAddress(address))

  def Wake(self):
    """Issue a WOL request to all of the computers specified adaptors."""
    for adaptor in self.adaptors:
      subprocess.call('%s %s' % (ETHERWAKE, adaptor.MacAddress()), shell=True)


def RenderWakeUpPage():
  """Displays a page to select the computers to wake up."""
  print '<body><html>'
  for name in COMPUTERS.keys():
    print "<a href='./wake.py?name=%s'>%s</a></br>" % (name, name)
  print '</body></html>'


if __name__ == '__main__':
  form = cgi.FieldStorage()
  computer_name = cgi.escape(form.getfirst('name', ''))
  if not computer_name:
    RenderWakeUpPage()
  else:
    computer = Computer(COMPUTERS[computer_name])
    computer.Wake()
    print '<pre>WOL sent to %s</pre>' % computer_name

