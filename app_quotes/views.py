from django.shortcuts import render
from tmqrwebui.models import SiteConfiguration
import pickle
import pandas as pd
from collections import OrderedDict
from exobuilder.data.assetindex_mongo import AssetIndexMongo
from exobuilder.data.exostorage import EXOStorage
from exobuilder.data.datasource_hybrid import DataSourceHybrid
from webui.site_settings import *
from datetime import datetime
from exobuilder.algorithms.rollover_helper import RolloverHelper
from pymongo import MongoClient


#
#  Helper functions
#


def get_instrument_recent_quotes(instruments_list, date_now):
    # Get information about decision and execution time
    assetindex = AssetIndexMongo(MONGO_CONNSTR, MONGO_EXO_DB)
    exostorage = EXOStorage(MONGO_CONNSTR, MONGO_EXO_DB)

    #
    # Test DB temporary credentials
    #
    tmp_mongo_connstr = 'mongodb://tml:tml@10.0.1.2/tmldb_test?authMechanism=SCRAM-SHA-1'
    tmp_mongo_db = 'tmldb_test'
    datasource = DataSourceHybrid(SQL_HOST, SQL_USER, SQL_PASS, assetindex, tmp_mongo_connstr, tmp_mongo_db,
                                  3, 10, exostorage)

    result = []

    for instrument in instruments_list:
        asset_info = assetindex.get_instrument_info(instrument)
        exec_time, decision_time = AssetIndexMongo.get_exec_time(date_now, asset_info)

        if date_now < exec_time:
            exec_time = date_now

        if date_now < decision_time:
            decision_time = date_now

        exec_time_instr = datasource.get(instrument, exec_time)
        rh = RolloverHelper(exec_time_instr)
        exec_time_fut, opt_chain = rh.get_active_chains()

        decision_time_instr = datasource.get(instrument, decision_time)
        rh = RolloverHelper(decision_time_instr)
        decision_time_fut, opt_chain = rh.get_active_chains()

        months_series = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        quotes_context = {
            'instrument': instrument,
            'date_now': date_now,
            'fut_contract': exec_time_fut.name,
            'opt_series': '{0} {1}'.format(months_series[opt_chain[0].c.month_int-1], opt_chain.expiration.year),
            #
            'exec_time': exec_time,
            'exec_price_fut': exec_time_fut,
            'exec_time_quote_date': exec_time_fut.price_quote_date, # The time when the real quote occurred

            'decision_time': decision_time,
            'decision_time_fut': decision_time_fut,
            'decision_time_quote_date': decision_time_fut.price_quote_date, # The time when the real quote occurred
        }

        result.append(quotes_context)

    return result


def get_exo_list_info():
    storage = EXOStorage(MONGO_CONNSTR, MONGO_EXO_DB)

    exo_data = storage.exo_list(exo_filter='*', return_names=False)

    result = OrderedDict()

    for d in exo_data:
        exo_name = d['name']
        asset_name = 'N/A'
        toks = exo_name.split('_')
        if len(toks) > 0:
            asset_name = toks[0]

        exo_dict = result.setdefault(asset_name, OrderedDict())

        series_df = pickle.loads(d['series'])
        series_df.index = pd.to_datetime(series_df.index)

        exo_dict[exo_name] = {
            'exo_name': exo_name,
            'calc_date': datetime(1900, 1, 1) if 'calc_date' not in d else d['calc_date'],
            'exo_last_quote': series_df['exo'].iloc[-1],
            'exo_last_date': series_df.index[-1],
            'last_rollover_date': d['transactions'][-1]['date'],
        }
    return result


def get_actual_alphas():
    client = MongoClient(MONGO_CONNSTR)
    db = client[MONGO_EXO_DB]

    #
    # Get all campaigns for active accounts
    #
    active_campaigns = db['accounts'].aggregate(
        [
            {
                '$group': {
                    '_id': None,
                    'campaign_name': {'$addToSet': '$campaign_name'},
                }
            }
        ])

    campaign_list = []
    for cmp_rec in active_campaigns:
        campaign_list += cmp_rec['campaign_name']

    #
    # Get alpha list for each campaign
    #
    result = OrderedDict()

    # Keep only unique campaign_names
    for cmp_name in list(set(campaign_list)):
        campaign = db['campaigns'].find({'name': cmp_name}).next()

        alpha_names_list = list(campaign['alphas'].keys())
        alphas_dict = result.setdefault(cmp_name, OrderedDict())

        for alpha_data in db['swarms'].find({'swarm_name': {'$in': alpha_names_list}}):

            swarm_name = alpha_data['swarm_name']

            alphas_dict[swarm_name] = {
                'swarm_name': swarm_name,
                'last_date':  alpha_data['last_date'],
                'last_rebalance_date': alpha_data['last_rebalance_date'],
                'last_exposure': alpha_data['last_exposure'],
                'last_prev_exposure': alpha_data['last_prev_exposure'],
                'calc_date': datetime(1900, 1, 1) if 'calc_date' not in alpha_data else alpha_data['calc_date'],
            }

        # Check if some alphas were not found in the DB
        for missed_alpha in alpha_names_list:
            if missed_alpha not in alphas_dict:
                alphas_dict[missed_alpha] = False

    return result


#
#
# Views
#
#

# Create your views here.
def view_quotes_monitor(request):
    config = SiteConfiguration.objects.get()

    context = {
        'instruments': config.insruments_list,
        'page_name': 'Contracts quotes monitoring',
        'site_name': config.site_name,
        'quotes_info': get_instrument_recent_quotes(config.insruments_list, datetime.now())
    }
    return render(request, 'quotes_monitor.html', context=context)


def view_quotes_exo(request):
    config = SiteConfiguration.objects.get()

    context = {
        'page_name': 'EXO quotes monitoring',
        'site_name': config.site_name,
        'exo_info': get_exo_list_info()
    }
    return render(request, 'quotes_exo.html', context=context)


def view_actual_alphas(request):
    config = SiteConfiguration.objects.get()

    context = {
        'page_name': 'Actual alphas monitoring',
        'site_name': config.site_name,
        'alphas_info': get_actual_alphas()
    }
    return render(request, 'quotes_alphas.html', context=context)