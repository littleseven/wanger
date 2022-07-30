import re


def yf_to_ft(yf_code: str) -> str:
    """
        Convert Yahoo Finance Stock Code to Futu Stock Code format
        E.g., 9988.HK -> HK.09988
    :param yf_code: Stock code used in Yahoo Finance (e.g., 9988.HK)
    """
    matches = re.match(r'^\d{4,6}.[A-Z]{2}$', yf_code)
    if matches is not None:
        part = yf_code.split('.')
        if part[1] == 'SS' and len(part[0]) == 6:
            part[1] = 'SH'
        if len(part[0]) == 4 and part[1] == 'HK':
            part[0] = '0' + part[0]
        code = part[1] + '.' + part[0]
    else:
        print('error code is ', yf_code)
    return code


def ft_to_yf(ft_code: str) -> str:
    """
        Convert Yahoo Finance Stock Code to Futu Stock Code format
        E.g., HK.09988->9988.HK
    :param ft_code: Stock code used in Yahoo Finance (e.g., 9988.HK)
    """
    matches = re.match(r'^[A-Z]{2}.\d{5,6}$', ft_code)
    if matches is not None:
        part = ft_code.split('.')
        if part[0] == 'SH' and len(part[1]) == 6:
            part[0] = 'SS'
        if len(part[1]) == 5 and part[0] == 'HK':
            part[1] = part[1][1:]
        code = part[1] + '.' + part[0]
    else:
        print('error code is ', ft_code)
    return code