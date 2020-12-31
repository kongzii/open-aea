# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Abstract module wrapping the public and private key cryptography and ledger api."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, BinaryIO, Dict, Generic, Optional, Tuple, TypeVar

from aea.common import Address, JSONLike


EntityClass = TypeVar("EntityClass")


class Crypto(Generic[EntityClass], ABC):
    """Base class for a crypto object."""

    identifier = "base"

    def __init__(
        self, private_key_path: Optional[str] = None, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Initialize the crypto object.

        The actual behaivour of this constructor is determined by the abstract
        methods 'generate_private_key()' and 'load_private_key_from_path().
        Either way, the entity object will be accessible as a property.

        :param private_key_path: the path to the private key.
                If None, the key will be generated by 'generate_private_key()'.
                If not None, the path will be processed by 'load_private_key_from_path()'.
        :param kwargs: keyword arguments.
        """
        self._entity = (
            self.generate_private_key()
            if private_key_path is None
            else self.load_private_key_from_path(private_key_path)
        )

    @classmethod
    @abstractmethod
    def generate_private_key(cls) -> EntityClass:
        """
        Generate a private key.

        :return: the entity object. Implementation dependent.
        """

    @classmethod
    @abstractmethod
    def load_private_key_from_path(cls, file_name: str) -> EntityClass:
        """
        Load a private key in hex format from a file.

        :param file_name: the path to the hex file.
        :return: the entity object.
        """

    @property
    def entity(self) -> EntityClass:
        """
        Return an entity object.

        :return: an entity object
        """
        return self._entity

    @property
    @abstractmethod
    def private_key(self) -> str:
        """
        Return a private key.

        :return: a private key string
        """

    @property
    @abstractmethod
    def public_key(self) -> str:
        """
        Return a public key.

        :return: a public key string
        """

    @property
    @abstractmethod
    def address(self) -> str:
        """
        Return the address.

        :return: an address string
        """

    @abstractmethod
    def sign_message(self, message: bytes, is_deprecated_mode: bool = False) -> str:
        """
        Sign a message in bytes string form.

        :param message: the message to be signed
        :param is_deprecated_mode: if the deprecated signing is used
        :return: signature of the message in string form
        """

    @abstractmethod
    def sign_transaction(self, transaction: JSONLike) -> JSONLike:
        """
        Sign a transaction in dict form.

        :param transaction: the transaction to be signed
        :return: signed transaction
        """

    @abstractmethod
    def dump(self, fp: BinaryIO) -> None:
        """
        Serialize crypto object as binary stream to `fp` (a `.write()`-supporting file-like object).

        :param fp: the output file pointer. Must be set in binary mode (mode='wb')
        :return: None
        """


class Helper(ABC):
    """Interface for helper class usable as Mixin for LedgerApi or as standalone class."""

    @staticmethod
    @abstractmethod
    def is_transaction_settled(tx_receipt: JSONLike) -> bool:
        """
        Check whether a transaction is settled or not.

        :param tx_digest: the digest associated to the transaction.
        :return: True if the transaction has been settled, False o/w.
        """

    @staticmethod
    @abstractmethod
    def is_transaction_valid(
        tx: JSONLike, seller: Address, client: Address, tx_nonce: str, amount: int,
    ) -> bool:
        """
        Check whether a transaction is valid or not.

        :param tx: the transaction.
        :param seller: the address of the seller.
        :param client: the address of the client.
        :param tx_nonce: the transaction nonce.
        :param amount: the amount we expect to get from the transaction.
        :return: True if the random_message is equals to tx['input']
        """

    @staticmethod
    @abstractmethod
    def generate_tx_nonce(seller: Address, client: Address) -> str:
        """
        Generate a unique hash to distinguish txs with the same terms.

        :param seller: the address of the seller.
        :param client: the address of the client.
        :return: return the hash in hex.
        """

    @classmethod
    @abstractmethod
    def get_address_from_public_key(cls, public_key: str) -> str:
        """
        Get the address from the public key.

        :param public_key: the public key
        :return: str
        """

    @classmethod
    @abstractmethod
    def recover_message(
        cls, message: bytes, signature: str, is_deprecated_mode: bool = False
    ) -> Tuple[Address, ...]:
        """
        Recover the addresses from the hash.

        :param message: the message we expect
        :param signature: the transaction signature
        :param is_deprecated_mode: if the deprecated signing was used
        :return: the recovered addresses
        """

    @classmethod
    @abstractmethod
    def recover_verifying_keys_from_message(
        cls, message: bytes, signature: str, is_deprecated_mode: bool = False
    ) -> Tuple[str, ...]:
        """
        Get the public key used to produce the `signature` of the `message`

        :param message: raw bytes used to produce signature
        :param signature: signature of the message
        :param is_deprecated_mode: if the deprecated signing was used
        :return: the recovered public keys
        """

    @staticmethod
    @abstractmethod
    def get_hash(message: bytes) -> str:
        """
        Get the hash of a message.

        :param message: the message to be hashed.
        :return: the hash of the message.
        """

    @classmethod
    @abstractmethod
    def is_valid_address(cls, address: Address) -> bool:
        """
        Check if the address is valid.

        :param address: the address to validate
        """

    @classmethod
    @abstractmethod
    def load_contract_interface(cls, file_path: Path) -> Dict[str, str]:
        """
        Load contract interface.

        :param file_path: the file path to the interface
        :return: the interface
        """


class LedgerApi(Helper, ABC):
    """Interface for ledger APIs."""

    identifier = "base"  # type: str

    @property
    @abstractmethod
    def api(self) -> Any:
        """
        Get the underlying API object.

        This can be used for low-level operations with the concrete ledger APIs.
        If there is no such object, return None.
        """

    @abstractmethod
    def get_balance(self, address: Address) -> Optional[int]:
        """
        Get the balance of a given account.

        This usually takes the form of a web request to be waited synchronously.

        :param address: the address.
        :return: the balance.
        """

    @abstractmethod
    def get_state(self, callable_name: str, *args, **kwargs) -> Optional[JSONLike]:
        """
        Call a specified function on the underlying ledger API.

        This usually takes the form of a web request to be waited synchronously.

        :param callable_name: the name of the API function to be called.
        :param args: the positional arguments for the API function.
        :param kwargs: the keyword arguments for the API function.
        :return: the ledger API response.
        """

    @abstractmethod
    def get_transfer_transaction(
        self,
        sender_address: Address,
        destination_address: Address,
        amount: int,
        tx_fee: int,
        tx_nonce: str,
        **kwargs,
    ) -> Optional[JSONLike]:
        """
        Submit a transfer transaction to the ledger.

        :param sender_address: the sender address of the payer.
        :param destination_address: the destination address of the payee.
        :param amount: the amount of wealth to be transferred.
        :param tx_fee: the transaction fee.
        :param tx_nonce: verifies the authenticity of the tx
        :return: the transfer transaction
        """

    @abstractmethod
    def send_signed_transaction(self, tx_signed: JSONLike) -> Optional[str]:
        """
        Send a signed transaction and wait for confirmation.

        Use keyword arguments for the specifying the signed transaction payload.

        :param tx_signed: the signed transaction
        """

    @abstractmethod
    def get_transaction_receipt(self, tx_digest: str) -> Optional[JSONLike]:
        """
        Get the transaction receipt for a transaction digest.

        :param tx_digest: the digest associated to the transaction.
        :return: the tx receipt, if present
        """

    @abstractmethod
    def get_transaction(self, tx_digest: str) -> Optional[JSONLike]:
        """
        Get the transaction for a transaction digest.

        :param tx_digest: the digest associated to the transaction.
        :return: the tx, if present
        """

    @abstractmethod
    def get_contract_instance(
        self, contract_interface: Dict[str, str], contract_address: Optional[str] = None
    ) -> Any:
        """
        Get the instance of a contract.

        :param contract_interface: the contract interface.
        :param contract_address: the contract address.
        :return: the contract instance
        """

    @abstractmethod
    def get_deploy_transaction(
        self, contract_interface: Dict[str, str], deployer_address: Address, **kwargs,
    ) -> Optional[JSONLike]:
        """
        Get the transaction to deploy the smart contract.

        :param contract_interface: the contract interface.
        :param deployer_address: The address that will deploy the contract.
        :returns tx: the transaction dictionary.
        """

    @abstractmethod
    def update_with_gas_estimate(self, transaction: JSONLike) -> JSONLike:
        """
        Attempts to update the transaction with a gas estimate

        :param transaction: the transaction
        :return: the updated transaction
        """


class FaucetApi(ABC):
    """Interface for testnet faucet APIs."""

    identifier = "base"  # type: str
    network_name = "testnet"  # type: str

    @abstractmethod
    def get_wealth(self, address: Address, url: Optional[str] = None) -> None:
        """
        Get wealth from the faucet for the provided address.

        :param address: the address.
        :param url: the url
        :return: None
        """
