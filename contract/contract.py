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

    @create
    def create(self, reg_begin: abi.Uint64, reg_end: abi.Uint64, vote_begin: abi.Uint64, vote_end: abi.Uint64):
        return Seq(
            self.reg_begin.set(reg_begin.get()),
            self.reg_end.set(reg_end.get()),
            self.vote_begin.set(vote_begin.get()),
            self.vote_end.set(vote_end.get()),
            self.initialize_application_state()
        )


if __name__ == "__main__":
    VotingApp().dump()
