import unittest
import tempfile
import subprocess
from pathlib import Path

from ssh_keygen import SSHKeygen


class TestSshKeyGen(unittest.TestCase):
    COMMENT = 'testing ssh key generation'
    PASSPHRASE = ''
    INDENTITY = 'TESTING'
    DOMAIN = 'testing.com.au'
    VALIDITY = '-1:+1d' 
    PRINCIPALS = 'testing_user' 
    SSH_NAME = 'python_key'

    def test_gen_key(self):
        """ Test ssh-key generation
        """

        ssh = SSHKeygen(self.COMMENT)
        private_key, public_key, cert_key = ssh.gen_key(
            self.PASSPHRASE,
            self.INDENTITY,
            self.DOMAIN,
            self.VALIDITY,
            self.PRINCIPALS
        )

        self.assertIsInstance(private_key, bytes)
        self.assertIsInstance(public_key, bytes)
        self.assertIsInstance(cert_key, bytes)

    def test_sing_key(self):
        """ Signing certificate """
        ssh = SSHKeygen(self.COMMENT)
        # Create temporary dicrectory and storage the keys there
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Check if Directory was create 
            self.assertTrue(Path(tmp_dir).exists())

            keys_path = f'{tmp_dir}/{self.SSH_NAME}'
            # Genarate private and public key
            subprocess.run(f'ssh-keygen -t rsa -C "{self.COMMENT}" -N "{self.PASSPHRASE}" -f {keys_path}', shell=True, capture_output=True)
            # Sign key
            ssh.sign_key(keys_path, f'{keys_path}.pub', self.INDENTITY, self.DOMAIN, self.VALIDITY, self.PRINCIPALS)
            # Read files into binary variables
            private_key, public_key, cert_key = ssh.load_keys(keys_path)
            # Delete tmp directory
        
        self.assertIsInstance(cert_key, bytes)

    def test_load_keys(self):
        """ Load ssh_keys from a file """
        ssh = SSHKeygen(self.COMMENT)
        dir = ''
        # Create temporary dicrectory and storage the keys there
        with tempfile.TemporaryDirectory() as tmp_dir:
            keys_path = f'{tmp_dir}/{self.SSH_NAME}'
            # Genarate private and public key
            subprocess.run(f'ssh-keygen -t rsa -C "{self.COMMENT}" -N "{self.PASSPHRASE}" -f {keys_path}', shell=True, capture_output=True)
            # Sign key
            ssh.sign_key(keys_path, f'{keys_path}.pub', self.INDENTITY, self.DOMAIN, self.VALIDITY, self.PRINCIPALS)
            # Read files into binary variables
            loaded_keys = ssh.load_keys(keys_path)
            # Delete tmp directory
            dir = keys_path

        # Check if Directory was removed 
        self.assertFalse(Path(dir).exists())
        # Check if keys where loaded
        private_key, public_key, cert_key = loaded_keys
        self.assertIsInstance(private_key, bytes)
        self.assertIsInstance(public_key, bytes)
        self.assertIsInstance(cert_key, bytes)

    def test_verify_signature(self):
        """ Veify the signature of the cert with the public key """
        ssh = SSHKeygen(self.COMMENT)
        # Create temporary dicrectory and storage the keys there
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Check if Directory was create 
            self.assertTrue(Path(tmp_dir).exists())

            keys_path = f'{tmp_dir}/{self.SSH_NAME}'
            # Genarate private and public key
            subprocess.run(f'ssh-keygen -t rsa -C "{self.COMMENT}" -N "{self.PASSPHRASE}" -f {keys_path}', shell=True, capture_output=True)
            # Sign key
            ssh.sign_key(keys_path, f'{keys_path}.pub', self.INDENTITY, self.DOMAIN, self.VALIDITY, self.PRINCIPALS)
            # Read files into binary variables
            private_key, public_key, cert_key = ssh.load_keys(keys_path)
            # Delete tmp directory

        is_signed = ssh.verify_signature(public_key, cert_key)
        self.assertTrue(is_signed)

    def test_get_certificate_data(self):
        """ Check if is possible to get the data from the certificate """
        ssh = SSHKeygen(self.COMMENT)
        cert_output = ''
        # Create temporary dicrectory and storage the keys there
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Check if Directory was create 
            self.assertTrue(Path(tmp_dir).exists())

            keys_path = f'{tmp_dir}/{self.SSH_NAME}'
            # Genarate private and public key
            subprocess.run(f'ssh-keygen -t rsa -C "{self.COMMENT}" -N "{self.PASSPHRASE}" -f {keys_path}', shell=True, capture_output=True)
            # Sign key
            ssh.sign_key(keys_path, f'{keys_path}.pub', self.INDENTITY, self.DOMAIN, self.VALIDITY, self.PRINCIPALS)
            cert_output = subprocess.run(f'ssh-keygen -L -f {keys_path}-cert.pub', shell=True, capture_output=True)
            # Delete tmp directory

        cert = ssh.get_certificate_data(cert_output.stdout.decode())
        self.assertIsInstance(cert, dict)
