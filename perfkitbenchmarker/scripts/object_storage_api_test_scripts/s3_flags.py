# Copyright 2016 PerfKitBenchmarker Authors. All rights reserved.
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

"""Flags for the S3 provider interface."""

from absl import flags

flags.DEFINE_string('region', None, 'The S3 region to use.')
flags.DEFINE_string(
    'endpoint_url',
    None,
    'Endpoint URL of an S3-compatible service (e.g. Aliyun OSS, Cloudflare '
    'R2). If unset, AWS S3 is used.',
)
flags.DEFINE_enum(
    'addressing_style',
    None,
    ['auto', 'virtual', 'path'],
    'S3 bucket addressing style. Only used with --endpoint_url.',
)
