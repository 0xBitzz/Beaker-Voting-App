from pyteal import *
from typing import Final
from beaker import (
    Application,
    AccountStateValue,
    ApplicationStateValue,
    Authorize,
    create,
    opt_in,
    bare_external,
    external,
    internal
)


class VotingApp(Application):
    vote_amount: Final[AccountStateValue] = AccountStateValue(
        stack_type=TealType.uint64,
        default=Int(0),
        descr="Amount an account holds at voting time"
    )
    vote_choice: Final[AccountStateValue] = AccountStateValue(
        stack_type=TealType.bytes,
        default=Bytes(""),
        descr="Choice made by this account, can be either of yes, no, abstain"
    )

    vote_count: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default=Int(0),
        descr="The accumulated number of votes"
    )
    reg_begin: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        descr="Registration window begin time"
    )
    reg_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        descr="Registration window end time"
    )
    vote_begin: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        descr="Voting window start time"
    )
    vote_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        descr="Voting window end time"
    )

    AID = Int(5)
    MIN_VOTE_AMOUNT = Int(1_000)

    @create
    def create(self, reg_begin: abi.Uint64, reg_end: abi.Uint64, vote_begin: abi.Uint64, vote_end: abi.Uint64):
        return Seq(
            self.reg_begin.set(reg_begin.get()),
            self.reg_end.set(reg_end.get()),
            self.vote_begin.set(vote_begin.get()),
            self.vote_end.set(vote_end.get()),
            self.initialize_application_state()
        )

    @opt_in
    def register(self):
        return Seq(
            Assert(
                And(
                    Global.round() >= self.reg_begin,
                    Global.round() <= self.reg_end
                )
            ),
            self.initialize_account_state()
        )

    @external(authorize=Authorize.opted_in(Global.current_application_id()))
    def cast_vote(self, vote_choice: abi.String):
        return Seq(
            (bal := AssetHolding.balance(account=Txn.sender(), asset=self.AID)),
            Assert(
                Global.round() >= self.vote_begin,
                Global.round() <= self.vote_end,
                comment="Ensure that voting can only take place within voting window"
            ),
            Assert(
                bal.hasValue(),
                comment="Ensure account has opted into the ENB"
            ),
            Assert(
                bal.value() >= self.MIN_VOTE_AMOUNT
            ),
            Assert(
                Or(
                    vote_choice.get() == Bytes("abstain"),
                    vote_choice.get() == Bytes("no"),
                    vote_choice.get() == Bytes("yes")
                )
            ),
            self.vote_choice.set(vote_choice.get()),
            If (vote_choice.get() == Bytes("yes"), self.upvote())
        )

    @internal
    def upvote(self):
        return Seq(

        )

    @internal
    def downvote(self):
        return Seq(

        )


if __name__ == "__main__":
    VotingApp().dump()
