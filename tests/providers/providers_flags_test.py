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
"""Tests that provider flags are registered when PKB starts."""

import subprocess
import sys
import unittest


class ProviderFlagsTest(unittest.TestCase):

  def testKubernetesFlagsRegisteredOnImport(self):
    # Run in a fresh interpreter: other test modules import the Kubernetes VM
    # module, which would register these flags and hide a regression.
    code = (
        'from absl import flags\n'
        'from perfkitbenchmarker import providers\n'
        'for name in ("kubernetes_anti_affinity", "k8s_env_from_secret"):\n'
        '  assert name in flags.FLAGS, name\n'
    )
    subprocess.run([sys.executable, '-c', code], check=True)


if __name__ == '__main__':
  unittest.main()
