# Copyright 2026 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the S3 client used by the object storage API test script."""

import sys
import unittest

from absl import flags
from absl.testing import flagsaver
import mock
from perfkitbenchmarker.scripts.object_storage_api_test_scripts import object_storage_interface
from perfkitbenchmarker.scripts.object_storage_api_test_scripts import s3_flags  # pylint: disable=unused-import

# On the VM, s3.py imports its siblings from a package named "providers".
sys.modules.setdefault(
    'providers', mock.Mock(object_storage_interface=object_storage_interface)
)
from perfkitbenchmarker.scripts.object_storage_api_test_scripts import s3  # pylint: disable=g-import-not-at-top

FLAGS = flags.FLAGS
FLAGS.mark_as_parsed()


class S3ServiceTest(unittest.TestCase):

  @flagsaver.flagsaver(region='us-east-1')
  def testAwsClient(self):
    with mock.patch.object(s3.boto3, 'client') as client:
      s3.S3Service()
    client.assert_called_once_with('s3', region_name='us-east-1')

  @flagsaver.flagsaver(
      region='auto',
      endpoint_url='https://example.r2.cloudflarestorage.com',
      addressing_style='virtual',
  )
  def testCompatibleEndpointClient(self):
    with mock.patch.object(s3.boto3, 'client') as client:
      s3.S3Service()
    _, kwargs = client.call_args
    self.assertEqual(kwargs['region_name'], 'auto')
    self.assertEqual(
        kwargs['endpoint_url'], 'https://example.r2.cloudflarestorage.com'
    )
    config = kwargs['config']
    self.assertEqual(config.s3, {'addressing_style': 'virtual'})
    self.assertEqual(config.request_checksum_calculation, 'when_required')
    self.assertEqual(config.response_checksum_validation, 'when_required')


if __name__ == '__main__':
  unittest.main()
