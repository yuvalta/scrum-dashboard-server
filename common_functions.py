from datetime import datetime


def days_between_dates(start_date, end_date):
    """
    Calculate the number of days between two dates.
    2024-06-06T15:39:23.421+0300
    """
    start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f%z')
    end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%f%z')
    return abs((end_date - start_date).days)
