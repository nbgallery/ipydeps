# vim: expandtab tabstop=4 shiftwidth=4

from datetime import datetime

if __name__ == "__main__":
    now = datetime.utcnow()
    julian_int = int(now.strftime('%j'))
    minute_of_day = now.hour * 60 + now.minute
    print('{}.{}.{}'.format(now.year, julian_int, minute_of_day))
