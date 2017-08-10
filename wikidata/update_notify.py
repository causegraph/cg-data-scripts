#!/usr/bin/python

import os
from gi.repository import Notify

Notify.init("CauseGraph")
Notify.Notification.new("CauseGraph", "New Wikidata dump processed!", os.path.abspath("cg_logo_white.png")).show()
