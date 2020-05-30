#!/usr/bin/env python3

import os
import gi

gi.require_version('Notify', '0.7')
from gi.repository import Notify


Notify.init("CauseGraph")
Notify.Notification.new("CauseGraph", "New Wikidata dump processed!", os.path.abspath("cg_logo_white.png")).show()
