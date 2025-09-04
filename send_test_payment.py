#!/usr/bin/env python3
# send_test_payment.py <merchant_pub> <amount_xlm> <memo_text>
import sys, time, requests
from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset

if len(sys.argv) < 4:
    print("Usage: python send_test_payment.py <merchant_pub> <amount_xlm> <memo_text>")
    sys.exit(1)

merchant = sys.argv[1]
amount = sys.argv[2]
memo_text = sys.argv[3]

server = Server("https://horizon-testnet.stellar.org")

# 1) generate buyer keypair
kp = Keypair.random()
print("Buyer public:", kp.public_key)
print("Buyer secret:", kp.secret)

# 2) fund buyer via friendbot
print("Funding buyer via Friendbot...")
r = requests.get(f"https://friendbot.stellar.org/?addr={kp.public_key}")
if r.status_code != 200:
    print("Friendbot failed:", r.text)
    sys.exit(1)
print("Friendbot funded buyer.")

# small pause to allow horizon to index
time.sleep(2)

# 3) build transaction: send amount XLM to merchant with memo
acct = server.load_account(kp.public_key)
tx = (TransactionBuilder(source_account=acct, network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE, base_fee=100)
      .add_text_memo(memo_text)
      .append_payment_op(destination=merchant, amount=str(amount), asset=Asset.native())
      .set_timeout(30)
      .build())
tx.sign(kp)
resp = server.submit_transaction(tx)
print("Transaction submitted. Hash:", resp["hash"])
print("Full response:", resp)
