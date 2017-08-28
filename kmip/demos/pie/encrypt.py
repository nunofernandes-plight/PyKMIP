# Copyright (c) 2017 The Johns Hopkins University/Applied Physics Laboratory
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import binascii
import logging
import sys

from kmip.core import enums
from kmip.demos import utils
from kmip.pie import client

# Real world example, assuming 'test' is a valid configuration:
#
# $ python kmip/demos/pie/encrypt.py -c test -m "My test message."
# INFO - Successfully created a new encryption key.
# INFO - Secret ID: 470
# INFO - Successfully activated the encryption key.
# INFO - Successfully encrypted the message.
# INFO - Cipher text: b'49cfacbb62659180c20dfbf9f7553488b3ea9ebeecd70ce2e5c4d4
# ece6def0d4'
# INFO - No autogenerated IV expected, since one was provided.
# INFO - Autogenerated IV: None
# $ python kmip/demos/pie/decrypt.py -c test -i 470 -m b'49cfacbb62659180c20df
# bf9f7553488b3ea9ebeecd70ce2e5c4d4ece6def0d4'
# INFO - Successfully decrypted the message.
# INFO - Plain text: 'My test message.'


if __name__ == '__main__':
    logger = utils.build_console_logger(logging.INFO)

    # Build and parse arguments
    parser = utils.build_cli_parser(enums.Operation.ENCRYPT)
    opts, args = parser.parse_args(sys.argv[1:])
    config = opts.config
    message = opts.message

    message = bytes(message, 'utf-8')

    # Build the client and connect to the server
    with client.ProxyKmipClient(config=config) as client:
        # Create an encryption key.
        try:
            key_id = client.create(
                enums.CryptographicAlgorithm.AES,
                128,
                cryptographic_usage_mask=[
                    enums.CryptographicUsageMask.ENCRYPT,
                    enums.CryptographicUsageMask.DECRYPT
                ]
            )
            logger.info("Successfully created a new encryption key.")
            logger.info("Secret ID: {0}".format(key_id))
        except Exception as e:
            logger.error(e)
            sys.exit(-1)

        # Activate the encryption key so that it can be used.
        try:
            client.activate(key_id)
            logger.info("Successfully activated the encryption key.")
        except Exception as e:
            logger.error(e)
            sys.exit(-1)

        # Encrypt some data with the encryption key.
        try:
            cipher_text, autogenerated_iv = client.encrypt(
                message,
                uid=key_id,
                cryptographic_parameters={
                    'cryptographic_algorithm':
                        enums.CryptographicAlgorithm.AES,
                    'block_cipher_mode': enums.BlockCipherMode.CBC,
                    'padding_method': enums.PaddingMethod.ANSI_X923
                },
                iv_counter_nonce=(
                    b'\x01\x7D\x45\xA0\x88\x08\x11\x11'
                    b'\xF0\x00\x12\xFF\x7A\x3A\x36\x90'
                )
            )
            logger.info("Successfully encrypted the message.")
            logger.info(
                "Cipher text: {0}".format(binascii.hexlify(cipher_text))
            )
            logger.info(
                "No autogenerated IV expected, since one was provided."
            )
            logger.info("Autogenerated IV: {0}".format(autogenerated_iv))
        except Exception as e:
            logger.error(e)