#
# Copyright (c) 2018, Centrica Hive Ltd.
#
#     This file is part of chaim.
#
#     chaim is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     chaim is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with chaim.  If not, see <http://www.gnu.org/licenses/>.
#
"""AWS SNS client functions"""

import chalicelib.glue as glue
from chalicelib.botosession import BotoSession

log = glue.log


class SnsClient(BotoSession):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.newClient("sns")

    def publishToSns(self, topicarn, msg):
        self.client.publish(TopicArn=topicarn, Message=msg)
