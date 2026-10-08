"""Tests for the AWS S3 service."""

import unittest
from absl.testing import flagsaver
import mock
from perfkitbenchmarker import linux_packages
from perfkitbenchmarker import vm_util
from perfkitbenchmarker.providers.aws import s3
from tests import pkb_common_test_case


class S3Test(pkb_common_test_case.PkbCommonTestCase):

  def setUp(self):
    super().setUp()
    flag_values = {'timeout_minutes': 0, 'persistent_timeout_minutes': 0}
    p = mock.patch.object(s3, 'FLAGS')
    flags_mock = p.start()
    flags_mock.configure_mock(**flag_values)
    self.mock_command = mock.patch.object(vm_util, 'IssueCommand').start()
    self.mock_retryable_command = mock.patch.object(
        vm_util, 'IssueRetryableCommand'
    ).start()
    self.s3_service = s3.S3Service()
    self.s3_service.PrepareService(None)  # will use s3.DEFAULT_AWS_REGION

  def tearDown(self):
    super().tearDown()
    mock.patch.stopall()

  def test_make_bucket(self):
    self.mock_command.return_value = (None, None, None)
    self.s3_service.MakeBucket(bucket_name='test_bucket')
    self.mock_command.assert_called_once_with(
        [
            'aws',
            's3api',
            'create-bucket',
            '--bucket=test_bucket',
            '--region={}'.format(s3.DEFAULT_AWS_REGION),
        ],
        raise_on_failure=False,
    )
    self.mock_retryable_command.assert_called_once_with([
        'aws',
        's3api',
        'put-bucket-tagging',
        '--bucket',
        'test_bucket',
        '--tagging',
        'TagSet=[]',
        '--region={}'.format(s3.DEFAULT_AWS_REGION),
    ])

  def test_prepare_vm_requires_instance_profile_without_endpoint(self):
    vm = mock.Mock(instance_profile=None)
    with self.assertRaises(ValueError):
      self.s3_service.PrepareVM(vm)

  def test_api_script_args_without_endpoint(self):
    self.assertEqual(
        self.s3_service.APIScriptArgs(),
        ['--region={}'.format(s3.DEFAULT_AWS_REGION)],
    )


_ENDPOINT = 'https://oss-us-west-1-internal.aliyuncs.com'


class S3CompatibleEndpointTest(pkb_common_test_case.PkbCommonTestCase):

  def setUp(self):
    super().setUp()
    self.enter_context(
        flagsaver.flagsaver(
            s3_endpoint_url=_ENDPOINT, s3_addressing_style='virtual'
        )
    )
    self.mock_command = self.enter_context(
        mock.patch.object(vm_util, 'IssueCommand')
    )
    self.mock_retryable_command = self.enter_context(
        mock.patch.object(vm_util, 'IssueRetryableCommand')
    )
    self.s3_service = s3.S3Service()

  def test_prepare_service_accepts_non_aws_region(self):
    self.s3_service.PrepareService('auto')
    self.assertEqual(self.s3_service.region, 'auto')
    self.assertIsNone(self.s3_service.zone)

  def test_prepare_service_defaults_region(self):
    self.s3_service.PrepareService(None)
    self.assertEqual(self.s3_service.region, s3.DEFAULT_AWS_REGION)

  def test_bucket_lifecycle_issues_no_commands(self):
    self.s3_service.PrepareService('us-west-1')
    self.s3_service.MakeBucket('existing-bucket')
    self.s3_service.EmptyBucket('existing-bucket')
    self.s3_service.DeleteBucket('existing-bucket')
    self.mock_command.assert_not_called()
    self.mock_retryable_command.assert_not_called()

  def test_prepare_vm_without_instance_profile(self):
    vm = mock.Mock(spec=['Install'])
    self.s3_service.PrepareVM(vm)
    vm.Install.assert_has_calls([mock.call('awscli'), mock.call('boto3')])

  def test_api_script_args(self):
    self.s3_service.PrepareService('us-west-1')
    self.assertEqual(
        self.s3_service.APIScriptArgs(),
        [
            '--region=us-west-1',
            '--endpoint_url=' + _ENDPOINT,
            '--addressing_style=virtual',
        ],
    )

  def test_metadata_records_endpoint(self):
    self.enter_context(
        mock.patch.object(
            linux_packages, 'GetPipPackageVersion', return_value='1.40.0'
        )
    )
    metadata = self.s3_service.Metadata(mock.Mock())
    self.assertEqual(metadata['s3_endpoint_url'], _ENDPOINT)


if __name__ == '__main__':
  unittest.main()
