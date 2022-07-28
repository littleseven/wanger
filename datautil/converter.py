import re


def yfinance_code_to_futu_code(yfinance_code: str) -> str:
    """
        Convert Yahoo Finance Stock Code to Futu Stock Code format
        E.g., 9988.HK -> HK.09988
    :param yfinance_code: Stock code used in Yahoo Finance (e.g., 9988.HK)
    """
    matches = re.match(r'^\d{4,6}.[A-Z]{2}$', yfinance_code)
    if matches is not None:
        part = yfinance_code.split('.')
        print('part is ', part[0], part[1])
        if part[1] == 'SS' and len(part[0]) == 6:
            part[1] = 'SH'
        if len(part[0]) == 4 and part[1] == 'HK':
            part[0] = '0' + part[0]
        code = part[1] + '.' + part[0]
    else:
        print('error code is ', yfinance_code)
    return code
