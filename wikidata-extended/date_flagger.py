#!/usr/bin/env python3
import json

def flag_monthday(datestr):
    """a date in this range is likely a month/day entered by a user, but stored as a month/year by Wikidata; check to make sure this isn't the case"""
    try:
        y,m,d = [int(x) for x in datestr.split('T')[0].rsplit('-', 2)]
        # is "year" in the range where it could actually be a day of the month?
        y_inrange = y in range(1,32)
        # is a month specified  and valid? (unspecified == 0)
        m_inrange = m in range(1,13)
        if y_inrange and m_inrange and d == 0:
            return True
        else:
            return False
    except:
        return False

dates_obj = json.load(open('date_claims.json'))

for k in dates_obj:
    for l in dates_obj[k]:
        claim_date = l[1]
        if flag_monthday(claim_date):
            print(k, l[1])
