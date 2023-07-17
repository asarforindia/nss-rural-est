import numpy as np
import pandas as pd


def get_income_bins(data):
    weight_col = 'combined_weight' if 'combined_weight' in data.columns else 'weight'
    data = data.dropna(subset=['monthly_percap_expen'])
    sorted_ = (data[['monthly_percap_expen', weight_col, 'hhsize']]
               .sort_values('monthly_percap_expen')
               .pipe(lambda df: df.assign(cs=(df[weight_col] * df['hhsize']).cumsum())))

    min_, max_ = sorted_['cs'].min(), sorted_['cs'].max()
    qs = min_ + np.array([0, 0.25, 0.5, 0.75, 1.0]) * (max_ - min_)
    indices = np.searchsorted(sorted_['cs'], qs)
    income_bins = sorted_.iloc[indices]['monthly_percap_expen'].to_numpy()
    return income_bins


def get_quartiles(data):
    bins = get_income_bins(data)
    quartiles = pd.cut(data['monthly_percap_expen'], bins)
    quartiles = quartiles.cat.rename_categories(['q1', 'q2', 'q3', 'q4'])
    return quartiles


def get_population(data):
    return (data['weight'] * data['hhsize']).sum()


def get_rural_population(data):
    data = data[data['sector'] == '1']
    return get_population(data)


def get_rural_population_ratio_with_subsamples(data):
    pops = (data.rename({'combined_weight': 'weight'}, axis=1)
            .groupby('sector').apply(get_population))
    ratio = pops['1'] / pops.sum()
    variance = 0
    for _, g in data.groupby(['state', 'district']):
        if g['subsample'].unique().shape[0] == 1:
            continue

        gb = (g.rename({'subsample_weight': 'weight'}, axis=1)
              .groupby('subsample'))
        ss_total = gb.apply(get_population)
        ss_rural = gb.apply(get_rural_population)
        variance += (
                            (ss_rural.loc['1'] - ss_rural.loc['2'])
                            - ratio * (ss_total.loc['1'] - ss_total.loc['2'])
                    ) ** 2
    variance = variance / 4 / pops.sum() ** 2
    return ratio, variance


def get_rural_population_ratio_without_subsamples(data):
    pops = data.groupby('sector').apply(get_population)
    r = pops['1'] / pops.sum()
    district_pops = (data
                     .groupby(['state', 'district', 'sector'])
                     .apply(get_population)
                     .reset_index()
                     .pivot(['state', 'district'], 'sector')
                     .droplevel(0, axis=1)
                     .fillna(0)
                     .pipe(lambda df: df.assign(total=df.sum(axis=1)))
                     )
    mean = district_pops.mean()
    mn, md = mean.loc['1'], mean.loc['total']
    dn, dd = district_pops['1'], district_pops['total']
    n = district_pops.shape[0]
    var = (((dn - mn) - r * (dd - md)) ** 2).sum() / (n - 1) / dd.sum() ** 2
    return r, var


def get_rural_population_ratio(data):
    if 'subsample' in data.columns:
        return get_rural_population_ratio_with_subsamples(data)
    else:
        return get_rural_population_ratio_without_subsamples(data)


def get_quartile_response_population(data, reindex_like):
    return (data.groupby(['quartiles', 'response_code'])
            .apply(lambda g: g['weight'].sum())
            .reindex_like(reindex_like)
            .fillna(0)
            )


def quartile_response_rate_standard_error(data, rr, rw):
    # since we are not using standard errors for new surveys, ignoring this
    if 'subsample' not in data:
        return None

    variance = 0
    for _, g in data.groupby(['state', 'district', 'stratum', 'substratum']):
        if g['subsample'].unique().shape[0] == 1:
            continue

        gb = g.rename({'subsample_weight': 'weight'}, axis=1).groupby('subsample')
        ss1n = gb.get_group('1').pipe(get_quartile_response_population, rr)
        ss1d = ss1n.groupby(level='quartiles').sum()
        ss2n = gb.get_group('2').pipe(get_quartile_response_population, rr)
        ss2d = ss2n.groupby(level='quartiles').sum()
        variance += ((ss1n - ss2n) - rr * (ss1d - ss2d)) ** 2

    variance = variance / 4 / rw.groupby(level='quartiles').sum() ** 2
    return variance


def get_quartile_response_rates(data):
    weight_col = 'combined_weight' if 'combined_weight' in data.columns else 'weight'
    rw = (data.rename({weight_col: 'weight'}, axis=1)
          .groupby(['quartiles', 'response_code'])
          .apply(lambda grp: grp['weight'].sum()))

    rr = rw / rw.groupby(level='quartiles').sum()
    variance = quartile_response_rate_standard_error(data, rr, rw)
    return rr, variance


def estimate(data):
    rural_pop = get_rural_population_ratio(data)
    if 'monthly_percap_expen' in data.columns:
        data = data.assign(quartiles=get_quartiles(data))
        qrr = get_quartile_response_rates(data)
    else:
        qrr = None
    return rural_pop, qrr
