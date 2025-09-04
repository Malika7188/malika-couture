from stellar_sdk import Server
from django.conf import settings
from decimal import Decimal

def find_payment_for_memo(merchant_pubkey: str, memo: str, max_tx=200):
    """
    Search recent transactions for merchant account and match memo.
    Returns (tx_hash, amount_decimal, asset_string) or (None, None, None).
    Note: this checks recent `max_tx` transactions (default 200).
    """
    server = Server(horizon_url=settings.STELLAR_HORIZON_URL)
    try:
        resp = server.transactions().for_account(merchant_pubkey).order(desc=True).limit(max_tx).call()
    except Exception:
        return None, None, None

    records = resp.get("_embedded", {}).get("records", [])
    for tx in records:
        # memo checking
        if tx.get("memo") != memo:
            continue
        if tx.get("successful") is not True:
            continue
        tx_hash = tx.get("hash")
        # get operations for this transaction to find payment ops
        try:
            ops = server.operations().for_transaction(tx_hash).call()
        except Exception:
            continue
        ops_records = ops.get("_embedded", {}).get("records", [])
        for op in ops_records:
            # We only accept payment operations that target the merchant
            if op.get("type") not in ("payment", "path_payment_strict_receive", "path_payment_strict_send"):
                continue
            if op.get("to") != merchant_pubkey:
                continue
            # determine asset and amount
            asset_type = op.get("asset_type")
            amount = Decimal(op.get("amount"))
            if asset_type == "native":
                return tx_hash, amount, "XLM"
            else:
                asset = f"{op.get('asset_code')}:{op.get('asset_issuer')}"
                return tx_hash, amount, asset
    return None, None, None
