from decimal import Decimal
from django.utils import timezone


def validate_slip(slip, account, post):
    if not slip.odds.all():
        return False, "No Bet in Slip"
    if Decimal(post['betlsip-total-risk']) > account.balance:
        return False, "Insufficient Funds"
    start = slip.get_earliest_start_time()
    if start < timezone.now():
        return False, "One Game Has already Started"
    for bet in slip.odds.all():
        total = Decimal(post['risk-{}'.format(bet.pk)])
        if total > account.limit:
            return False, "Bet total is greater than Account Limit"
    return True, "Valid Slip"


