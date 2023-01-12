import json
from typing import Final
from pyteal import *
from beaker import (
    Application,
    AccountStateValue,
    ApplicationStateValue,
    Authorize,
    external,
    internal,
    create,
    opt_in
)


class Asset(Application):
    token_id: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64, descr="Token ID"
    )

    MIN_BAL = Int(100_000)

    @external(authorize=Authorize.only(Global.creator_address()))
    def create_asset(self, token_name: abi.String, total_supply: abi.Uint64):
        return Seq(
            InnerTxnBuilder.Execute({
                    TxnField.type_enum: TxnType.AssetConfig,
                    TxnField.config_asset_name: token_name.get(),
                    TxnField.config_asset_total: total_supply.get(),
                    TxnField.config_asset_manager: self.address,
                    TxnField.fee: self.MIN_BAL
                    }
            ),
            self.token_id.set(InnerTxn.created_asset_id()),
        )

    @external
    def transfer_asset(self, amount: abi.Uint64, receiver: abi.Address):
        return Seq(
            InnerTxnBuilder.Execute({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_receiver: receiver.get(),
                TxnField.xfer_asset: self.token_id,
                TxnField.amount: amount.get()
            })
        )

    @external(authorize=Authorize.only(Global.creator_address()))
    def send_to_creator(self):
        return Seq(
            (bal := AssetHolding.balance(
                account=self.address,
                asset=self.token_id),
            ),
            self.transfer_asset(amount=bal.value(), receiver=Global.Txn.sender())
        )

    @external(read_only=True)
    def read_token_id(self, *, output: abi.Uint64):
        return output.set(self.token_id)

    @external
    def read_asset_bal(
        self,
        asset_id: abi.Asset = token_id,  # type: ignore[assignment]
        *,
        output: abi.Uint64,
    ):
        return Seq(
            (
                bal := AssetHolding.balance(
                    account=self.address, asset=asset_id.asset_id()
                )
            ),
            output.set(bal.value()),
        )


if __name__ == "__main__":
    vote_app = Asset()

    with open("approval.teal", "w") as teal:
        teal.write(vote_app.approval_program)

    with open("clear.teal", "w") as teal:
        teal.write(vote_app.clear_program)

    with open("contract.json", "w") as f:
        f.write(json.dumps(vote_app.application_spec(), indent=4))
