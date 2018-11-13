from decimal import Decimal


def validate_slip(slip, account, post):
    if Decimal(post['betlsip-total-risk']) > account.balance:
        return False, "Insufficient Funds"
    if not slip.check_odd_times():
        return False, "One Game Has already Started"
    for bet in slip.odds.all():
        total = Decimal(post['risk-{}'.format(bet.pk)])
        if total > account.limit:
            return False, "Bet total is greater than Account Limit"
    return True, "Valid Slip"
