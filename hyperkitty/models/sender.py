# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 by the Free Software Foundation, Inc.
#
# This file is part of HyperKitty.
#
# HyperKitty is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# HyperKitty is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# HyperKitty.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Aurelien Bompard <abompard@fedoraproject.org>
#

# pylint: disable=no-init,unnecessary-lambda,unused-argument

from __future__ import absolute_import, unicode_literals, print_function


from urllib2 import HTTPError

from django.db import models
from mailmanclient import MailmanConnectionError

from hyperkitty.lib.mailman import get_mailman_client

import logging
logger = logging.getLogger(__name__)


class Sender(models.Model):
    address = models.EmailField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    mailman_id = models.CharField(max_length=255, null=True, db_index=True)

    class Meta:
        app_label = 'hyperkitty' # For Django < 1.7

    def set_mailman_id(self):
        try:
            client = get_mailman_client()
            mm_user = client.get_user(self.address)
        except HTTPError as e:
            if e.code == 404:
                return # User not found in Mailman
            raise MailmanConnectionError(e) # normalize all possible error types
        except ValueError as e:
            # This smells like a badly formatted email address (saw it in the wild)
            logger.warning(
                "Invalid response when getting user %s from Mailman",
                self.address)
            return # Ignore it
        self.mailman_id = mm_user.user_id
        self.save()
        ## Go further and associate the user's other addresses?
        #Sender.objects.filter(address__in=mm_user.addresses
        #    ).update(mailman_id=mm_user.user_id)
