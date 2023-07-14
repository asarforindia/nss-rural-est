import argparse
import os
import pickle
from tqdm.auto import tqdm
import numpy as np
import pandas as pd

from reader import (read_nss68_consumer_expen, read_nss68_employ_unemp,
                    read_nss72_household_expen, read_nss72_domestic_tour,
                    read_nss75_education_cons, read_nss75_health_cons,
                    read_nss76_disability, read_nss76_sanitation,
                    )
import calc

readers = {'NSS-68-CE': read_nss68_consumer_expen,
           'NSS-68-EU': read_nss68_employ_unemp,
           'NSS-72-DT': read_nss72_domestic_tour,
           'NSS-72-HE': read_nss72_household_expen,
           'NSS-75-SCE': read_nss75_education_cons,
           'NSS-75-SCH': read_nss75_health_cons,
           'NSS-76-DW': read_nss76_sanitation,
           'NSS-76-PD': read_nss76_disability,
           }


def prepare_datasets(inp, cache):
    for name, reader in tqdm(readers.items(), total=len(readers)):
        cache_path = os.path.join(cache, f'{name}.csv')
        if os.path.exists(cache_path):
            continue
        survey_base = os.path.join(inp, name, 'Microdata')
        survey_data = reader(survey_base)
        survey_data.to_csv(cache_path)


def run_estimates(cache, which=None):
    estimates = {}
    surveys = sorted(readers.keys())
    for survey in tqdm(surveys):
        if which is not None and survey not in which:
            continue
        cache_path = os.path.join(cache, f'{survey}.csv')
        data = pd.read_csv(cache_path, dtype={
            'HHID': str, 'sector': str, 'subsample': str,
            'state': str, 'district': str, 'stratum': str,
            'substratum': str, 'response_code': str,
            'combined_weight': float, 'subsample_weight': float,
            'hhsize': int, 'monthly_percap_expen': float
        })
        estimates[survey] = calc.estimate(data)
    return estimates


def save_output(estimates, outp):
    rural_items = {}
    response_items = {}
    for survey, (rural, response) in estimates.items():
        skip_errors = '76' in survey
        rural_est, rural_var = rural
        rural_items[survey] = (
            rural_est, np.sqrt(rural_var) if not skip_errors else None
        )
        if response is not None:
            response_est, response_var = response
            response_items[survey] = pd.DataFrame({
                'ratio': response_est,
                'err': np.sqrt(response_var) if not skip_errors else None
            })
    rural_ratios = pd.DataFrame(rural_items, index=['ratio', 'err']).T
    response_ratios = (pd.concat(response_items, names=['survey'])
                       .reset_index())
    rural_ratios.to_csv(os.path.join(outp, 'rural-ratios.csv'))
    response_ratios.to_csv(os.path.join(outp, 'response-ratios.csv'))
    return rural_ratios, response_items


def main(inp, cache, outp, which=None):
    if which is not None:
        which = which.split(',')

    prepare_datasets(inp, cache)
    estimates_path = os.path.join(cache, 'estimates.pkl')

    if os.path.exists(estimates_path):
        with open(estimates_path, 'rb') as pkl:
            estimates = pickle.load(pkl)
    else:
        estimates = {}

    new_estimates = run_estimates(cache, which=which)
    estimates.update(new_estimates)
    with open(estimates_path, 'wb') as pkl:
        pickle.dump(estimates, pkl)
    save_output(estimates, outp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('inp')
    parser.add_argument('cache')
    parser.add_argument('outp')
    parser.add_argument('--which')
    args = parser.parse_args()
    main(args.inp, args.cache, args.outp, args.which)
