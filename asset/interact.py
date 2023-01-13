from asset import Asset
from beaker import sandbox
from beaker.client import ApplicationClient
from beaker import consts
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algosdk.future.transaction import PaymentTxn


client = sandbox.get_algod_client()
creator_account = sandbox.get_accounts().pop()
acct1 = sandbox.get_accounts().pop()
acct2 = sandbox.get_accounts().pop()

app = Asset()

app_client = ApplicationClient(client=client, app=app, signer=creator_account.signer)


def test_app():
    sp = client.suggested_params()

    app_id, app_addr, txid = app_client.create()
    print(
        f"App created with app id: {app_id} and app addr: {app_addr} and signed with: {txid}"
    )

    app_client.fund(consts.algo * 100)

    app_client.call(app.create_asset, token_name="ENB", total_supply=1_000_000)

    token_id = app_client.call(app.get_token_id).return_value

    print(f"App addr: {app_addr}")

    print(f"Asset ID: {token_id}")

    print(
        f"Asset Balance: {app_client.call(app.read_asset_bal, asset_id=token_id).return_value}"
    )


test_app()
