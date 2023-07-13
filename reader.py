import os
import numpy as np
import pandas as pd
from pyreadstat import read_dta

import warnings


def pjoin(b, p):
    return os.path.join(b, p)


def get_hhid(b, fsu='FSU',
             hamlet_sub_block='Hamlet_Sub_block',
             second_stage_stratum='Second_stage_stratum',
             sample_hh_number='Sample_hhld'):
    # concat all the strings!
    return (b[fsu] + b[hamlet_sub_block] + b[second_stage_stratum]
            + b[sample_hh_number]).rename('HHID')


def read_nss68_consumer_expen(base):
    nss68ce_b12_data, nss68ce_b12_meta = read_dta(pjoin(base, 'Block 1 and 2.dta'))
    nss68ce_b32_data, nss68ce_b32_meta = read_dta(pjoin(base, 'Block 3 - Level2 - type2 - 68.dta'))
    nss68ce_b33_data, nss68ce_b33_meta = read_dta(pjoin(base, 'Block 3 -  level3 - type2 - 68.dta'))

    b12_cols = [
        'Sector', 'Sub_Sample', 'State_code', 'District', 'Stratum',
        'Sub_Stratum_No', 'Response_Code', 'Combined_Multiplier',
        'Subsample_multiplier'
    ]
    b12 = nss68ce_b12_data.set_index('HHID')[b12_cols]
    b32 = nss68ce_b32_data.set_index('HHID')[['hh_size']]
    b33 = nss68ce_b33_data.set_index('HHID')[['MPCE']] / 100
    data = b12.join(b32).join(b33)
    data.columns = [
        'sector', 'subsample', 'state', 'district', 'stratum', 'substratum',
        'response_code', 'combined_weight', 'subsample_weight',
        'hhsize', 'monthly_percap_expen'
    ]
    data['hhsize'] = data['hhsize'].astype(int)
    return data


def read_nss68_employ_unemp(base):
    nss68eu_b12_data, nss68eu_b12_meta = read_dta(pjoin(base, 'Block_1_2.dta'))
    nss68eu_b3_data, nss68eu_b3_meta = read_dta(pjoin(base, 'Block_3.dta'))

    b12_cols = [
        'Sector', 'Sub_Sample', 'State', 'District_Code', 'Stratum',
        'Sub_Stratum_No', 'Response_Code', 'Multiplier_comb', 'MLT'
    ]
    b12 = nss68eu_b12_data.set_index('HHID')[b12_cols]
    b12['MLT'] = b12['MLT'] / 100
    data = b12.assign(hhsize=nss68eu_b3_data['HH_Size'].to_numpy())
    data.columns = [
        'sector', 'subsample', 'state', 'district', 'stratum', 'substratum',
        'response_code', 'combined_weight', 'subsample_weight', 'hhsize'
    ]
    data['hhsize'] = data['hhsize'].astype(int)
    return data


def read_nss72_household_expen(base):
    nss72he_b12_data, nss72he_b12_meta = read_dta(pjoin(base, 'Block 1 &  2.dta'))
    nss72he_b3_data, nss72he_b3_meta = read_dta(pjoin(base, 'Block 3.dta'))

    b12_cols = [
        'Sector', 'SubSample', 'State', 'State_District', 'Stratum',
        'SubStratumNo', 'Resp_Code', 'Weight_SC', 'Weight_SS'
    ]
    b12 = nss72he_b12_data.set_index('HHID')[b12_cols]

    # code assumes districts indexed within the state
    b12['State_District'] = b12['State_District'].str[2:]

    # household size and monthly household expenditure
    b3 = nss72he_b3_data.set_index('HHID')[['b3q1', 'b3q9']].astype(float)

    # since we are comparing monthly per capita expenditures
    b3['b3q9'] = b3['b3q9'] / b3['b3q1']

    data = b12.join(b3)
    data.columns = [
        'sector', 'subsample', 'state', 'district', 'stratum', 'substratum',
        'response_code', 'combined_weight', 'subsample_weight',
        'hhsize', 'monthly_percap_expen'
    ]
    return data


def read_nss72_domestic_tour(base):
    nss72dt_b12_data, nss72dt_b12_meta = read_dta(pjoin(base, 'Block 1 & Block 2.dta'))
    nss72dt_b3_data, nss72dt_b3_meta = read_dta(pjoin(base, 'Block 3.dta'))

    b12_cols = [
        'Sector', 'SubSample', 'State', 'State_District', 'Stratum',
        'SubStratumNo', 'Resp_Code', 'Weight_SC', 'Weight_SS'
    ]
    b12 = nss72dt_b12_data.set_index('HHID')[b12_cols]

    # code assumes districts indexed within the state
    b12['State_District'] = b12['State_District'].str[2:]

    # household size and monthly household expenditure
    b3 = nss72dt_b3_data.set_index('HHID')[['b3q1', 'b3q7']]

    # since we are comparing monthly per capita expenditures
    b3['b3q7'] = b3['b3q7'] / b3['b3q1']

    data = b12.join(b3)
    data.columns = [
        'sector', 'subsample', 'state', 'district', 'stratum', 'substratum',
        'response_code', 'combined_weight', 'subsample_weight',
        'hhsize', 'monthly_percap_expen'
    ]
    return data


def read_nss75_education_cons(base):
    nss75sce_b1_data, nss75sce_b1_meta = read_dta(pjoin(base, 'Blocks 1, 2 and 11.dta'))
    nss75sce_b3_data, nss75sce_b3_meta = read_dta(pjoin(base, 'Block 3.dta'))

    cols = pd.Index([
        'Sector', 'Sub_sample', 'NSS_Region', 'District', 'Stratum',
        'Sub_stratum', 'Response_Code', 'MULT_Combined', 'MULT_SubSample'
    ])
    b12 = nss75sce_b1_data.set_index('HHID')[cols]

    # household size and monthly household expenditure
    b3_cols = ['Household_size', 'HH_Con_exp_rs']
    b3 = nss75sce_b3_data.set_index('HHID')[b3_cols].astype(int)

    # since we are comparing monthly per capita expenditures
    b3[b3_cols[1]] = b3[b3_cols[1]] / b3[b3_cols[0]]
    data = b12.join(b3)

    data.columns = [
        'sector', 'subsample', 'state', 'district', 'stratum', 'substratum',
        'response_code', 'combined_weight', 'subsample_weight',
        'hhsize', 'monthly_percap_expen'
    ]
    return data


def read_nss75_health_cons(base):
    nss75sch_b12_data, nss75sch_b12_meta = read_dta(pjoin(base, 'Block 0 and Block 1.dta'))
    nss75sch_b3_data, nss75sch_b3_meta = read_dta(pjoin(base, 'Block 3 Level 2.dta'))

    b12_cols = pd.Index([
        'Sector', 'Sub_sample', 'NSS_Region', 'District', 'Stratum',
        'Sub_stratum', 'Response_Code', 'Mult_Combined', 'MULT_Sub_Sample'
    ])

    b12 = nss75sch_b12_data.set_index(get_hhid(nss75sch_b12_data))[b12_cols]

    # household size and monthly household expenditure
    b3_cols = ['Household_size', 'Household_usual_consumer_expendi']
    b3 = nss75sch_b3_data.set_index(get_hhid(nss75sch_b3_data))[b3_cols].astype(int)

    # since we are comparing monthly per capita expenditures
    b3[b3_cols[1]] = b3[b3_cols[1]] / b3[b3_cols[0]]
    data = b12.join(b3)

    data.columns = [
        'sector', 'subsample', 'state', 'district', 'stratum', 'substratum',
        'response_code', 'combined_weight', 'subsample_weight',
        'hhsize', 'monthly_percap_expen'
    ]
    return data


def read_nss76_disability(base):
    nss76pd_l1_data, nss76pd_l1_meta = read_dta(pjoin(base, 'Block 1 Level 1.dta'))
    nss76pd_l3_data, nss76pd_l3_meta = read_dta(pjoin(base, 'Block 4 Level 3.dta'))

    b12_cols = pd.Index([
        'Sector', 'NSS_Region', 'District', 'Stratum',
        'Sub_stratum', 'Response_Code', 'MULT'
    ])
    b12 = nss76pd_l1_data.set_index('HHID')[b12_cols]

    # making up the subsample division for consistency.
    # standard errors will be incorrect - we will fix in the next version
    warnings.warn('nss75_disability: unreliable error estimates')
    b12['Sub_Sample'] = np.random.choice(['1', '2'], size=b12.shape[0])
    b12['Multiplier_SS'] = b12['MULT'] * 2
    b12 = b12[['Sector', 'Sub_Sample', 'NSS_Region', 'District', 'Stratum',
               'Sub_stratum', 'Response_Code', 'MULT', 'Multiplier_SS'
               ]]

    b3_cols = ['Household_size', 'Usual_monthly_consumer_expenditu']
    b3 = nss76pd_l3_data.set_index('HHID')[b3_cols].astype(int)
    b3[b3_cols[1]] = b3[b3_cols[1]] / b3[b3_cols[0]]
    data = b12.join(b3)

    data.columns = [
        'sector', 'subsample', 'state', 'district', 'stratum', 'substratum',
        'response_code', 'combined_weight', 'subsample_weight',
        'hhsize', 'monthly_percap_expen'
    ]
    return data


def read_nss76_sanitation(base):
    nss76dw_l1_data, nss76dw_l1_meta = read_dta(pjoin(base, 'R76120L01.dta'))
    nss76dw_l3_data, nss76dw_l3_meta = read_dta(pjoin(base, 'R76120L03.dta'))

    b12_cols = pd.Index([
        'Sector', 'NSS_Region', 'District', 'Stratum',
        'Sub_stratum', 'Response_Code', 'Multiplier'
    ])
    b12 = nss76dw_l1_data.set_index('HHID')[b12_cols]

    # making up the subsample division for consistency.
    # standard errors will be incorrect - we will fix in the next version
    warnings.warn('nss75_disability: unreliable error estimates')
    b12['Sub_Sample'] = np.random.choice(['1', '2'], size=b12.shape[0])
    b12['Multiplier_SS'] = b12['Multiplier'] * 2
    b12 = b12[['Sector', 'Sub_Sample', 'NSS_Region', 'District', 'Stratum',
               'Sub_stratum', 'Response_Code', 'Multiplier', 'Multiplier_SS'
               ]]

    b3_cols = ['HH_size', 'Total_Monthly_expenditure']
    b3 = nss76dw_l3_data.set_index('HHID')[b3_cols].astype(int)
    b3[b3_cols[1]] = b3[b3_cols[1]] / b3[b3_cols[0]]
    data = b12.join(b3)

    data.columns = [
        'sector', 'subsample', 'state', 'district', 'stratum', 'substratum',
        'response_code', 'combined_weight', 'subsample_weight',
        'hhsize', 'monthly_percap_expen'
    ]
    return data
