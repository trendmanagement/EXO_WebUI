from django.shortcuts import render
from webui.site_settings import *
from tmqr_backend.models import SiteConfiguration
from django.shortcuts import render
from tmqr_backend.models import SiteConfiguration
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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from backtester.reports.campaign_report import CampaignReport
import traceback
from exobuilder.data.datasource_mongo import DataSourceMongo
from backtester.reports.payoffs import PayoffAnalyzer


EVENTS_STATUS = 'events_status'
EVENTS_LOG = 'events_log'

import pymongo

# Create your views here.
def view_mainpage(request):
    config = SiteConfiguration.get_solo()

    context = {
        'site_name': config.site_name,
        'page_name': 'Dashboard',
    }
    return render(request, 'base.html', context=context)





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
    datasource = DataSourceHybrid(MONGO_CONNSTR, MONGO_EXO_DB, assetindex, tmp_mongo_connstr, tmp_mongo_db,
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
            'exec_price_fut_price': exec_time_fut.price,
            'exec_time_quote_date': exec_time_fut.price_quote_date, # The time when the real quote occurred

            'decision_time': decision_time,
            'decision_time_fut_price': decision_time_fut.price,
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



def get_gmi_fees(start_date, end_date):
    tmp_mongo_connstr = 'mongodb://tmqr:tmqr@10.0.1.2/client-gmi?authMechanism=SCRAM-SHA-1'
    tmp_mongo_db = 'client-gmi'

    mongoClient = MongoClient(tmp_mongo_connstr)
    db = mongoClient[tmp_mongo_db]
    collection = db.accountdatacollection

    #cursor = collection.find({'Batchid': {'$gte': start_date, '$lte': end_date}})

    accountdata_list_out = [];
    account_summary = {};
    office_summary = {};

    for accountdata in collection.find({'Batchid': {'$gte': start_date, '$lte': end_date}}).sort([
        ('FCM', pymongo.ASCENDING),('Office', pymongo.ASCENDING),('Account', pymongo.ASCENDING)]):

        acct_key = (accountdata['FCM'], accountdata['Office'], accountdata['Account']);

        if acct_key in account_summary:
            account_summary[acct_key]['TradedQuantityBuy'] += accountdata['TradedQuantityBuy'];
            account_summary[acct_key]['TradedQuantitySell'] += accountdata['TradedQuantitySell'];
            account_summary[acct_key]['Commission'] += accountdata['Commission'];
            account_summary[acct_key]['ClearingFees'] += accountdata['ClearingFees'];
            account_summary[acct_key]['ExchangeFees'] += accountdata['ExchangeFees'];
            account_summary[acct_key]['TransactionFees'] += accountdata['TransactionFees'];
            account_summary[acct_key]['NFAFees'] += accountdata['NFAFees'];
            account_summary[acct_key]['BrokerageFees'] += accountdata['BrokerageFees'];
            account_summary[acct_key]['TradeProcessingFees'] += accountdata['TradeProcessingFees'];
            account_summary[acct_key]['CBOT_Globex_Fee'] += accountdata['CBOT_Globex_Fee'];
            account_summary[acct_key]['CME_Globex_Fee'] += accountdata['CME_Globex_Fee'];
            account_summary[acct_key]['Give_In_Fee'] += accountdata['Give_In_Fee'];
            account_summary[acct_key]['TotalFees'] += accountdata['TotalFees'];
            account_summary[acct_key]['SumOfFeesAndCommission'] += accountdata['Commission'] + accountdata['TotalFees'];

        else:
            newAccountData = {
                'FCM':accountdata['FCM'],
                'Office': accountdata['Office'],
                'Account': accountdata['Account'],
                'TradedQuantityBuy': accountdata['TradedQuantityBuy'],
                'TradedQuantitySell': accountdata['TradedQuantitySell'],
                'Commission': accountdata['Commission'],
                'ClearingFees': accountdata['ClearingFees'],
                'ExchangeFees': accountdata['ExchangeFees'],
                'TransactionFees': accountdata['TransactionFees'],
                'NFAFees': accountdata['NFAFees'],
                'BrokerageFees': accountdata['BrokerageFees'],
                'TradeProcessingFees': accountdata['TradeProcessingFees'],
                'CBOT_Globex_Fee': accountdata['CBOT_Globex_Fee'],
                'CME_Globex_Fee': accountdata['CME_Globex_Fee'],
                'Give_In_Fee': accountdata['Give_In_Fee'],
                'TotalFees': accountdata['TotalFees'],
                'SumOfFeesAndCommission': accountdata['Commission'] + accountdata['TotalFees'],
            }

            account_summary[acct_key] = newAccountData;

    #for accountdata in collection.find({'Batchid': {'$gte': start_date, '$lte': end_date}}):

        office_key = (accountdata['FCM'], accountdata['Office']);

        if office_key in office_summary:
            office_summary[office_key]['TradedQuantityBuy'] += accountdata['TradedQuantityBuy'];
            office_summary[office_key]['TradedQuantitySell'] += accountdata['TradedQuantitySell'];
            office_summary[office_key]['Commission'] += accountdata['Commission'];
            office_summary[office_key]['ClearingFees'] += accountdata['ClearingFees'];
            office_summary[office_key]['ExchangeFees'] += accountdata['ExchangeFees'];
            office_summary[office_key]['TransactionFees'] += accountdata['TransactionFees'];
            office_summary[office_key]['NFAFees'] += accountdata['NFAFees'];
            office_summary[office_key]['BrokerageFees'] += accountdata['BrokerageFees'];
            office_summary[office_key]['TradeProcessingFees'] += accountdata['TradeProcessingFees'];
            office_summary[office_key]['CBOT_Globex_Fee'] += accountdata['CBOT_Globex_Fee'];
            office_summary[office_key]['CME_Globex_Fee'] += accountdata['CME_Globex_Fee'];
            office_summary[office_key]['Give_In_Fee'] += accountdata['Give_In_Fee'];
            office_summary[office_key]['TotalFees'] += accountdata['TotalFees'];
            office_summary[office_key]['SumOfFeesAndCommission'] += accountdata['Commission'] + accountdata['TotalFees'];

        else:
            #office_summary[office_key] = accountdata;
            #office_summary[office_key]['Office'] = "Summary " + choose_fcm_name(accountdata['FCM']) + " " + accountdata['Office']
            #office_summary[office_key]['Account'] = "";
            #office_summary[office_key]['SumOfFeesAndCommission'] = accountdata['Commission'] + accountdata['TotalFees'];

            newAccountData = {
                'FCM': accountdata['FCM'],
                'Office':  "Summary " + choose_fcm_name(accountdata['FCM']) + " " + accountdata['Office'],
                'Account': "",
                'TradedQuantityBuy': accountdata['TradedQuantityBuy'],
                'TradedQuantitySell': accountdata['TradedQuantitySell'],
                'Commission': accountdata['Commission'],
                'ClearingFees': accountdata['ClearingFees'],
                'ExchangeFees': accountdata['ExchangeFees'],
                'TransactionFees': accountdata['TransactionFees'],
                'NFAFees': accountdata['NFAFees'],
                'BrokerageFees': accountdata['BrokerageFees'],
                'TradeProcessingFees': accountdata['TradeProcessingFees'],
                'CBOT_Globex_Fee': accountdata['CBOT_Globex_Fee'],
                'CME_Globex_Fee': accountdata['CME_Globex_Fee'],
                'Give_In_Fee': accountdata['Give_In_Fee'],
                'TotalFees': accountdata['TotalFees'],
                'SumOfFeesAndCommission': accountdata['Commission'] + accountdata['TotalFees'],
            }

            office_summary[office_key] = newAccountData;

    #for key in sorted(account_summary):
    #    print "%s: %s" % (key, account_summary[key])

    #for key in account_summary.items():
    for key in sorted(account_summary):

        value = account_summary[key]

        quotes_context = {
            'FCM': choose_fcm_name(value['FCM']),
            'Office': value['Office'],
            'Account': value['Account'],
            'TradedQuantityBuy': value['TradedQuantityBuy'],
            'TradedQuantitySell': value['TradedQuantitySell'],
            'Commission': round(value['Commission'],2),
            'ClearingFees': round(value['ClearingFees'],2),
            'ExchangeFees': round(value['ExchangeFees'],2),
            'TransactionFees': round(value['TransactionFees'],2),
            'NFAFees': round(value['NFAFees'],2),
            'BrokerageFees': round(value['BrokerageFees'],2),
            'TradeProcessingFees': round(value['TradeProcessingFees'],2),
            'CBOT_Globex_Fee': round(value['CBOT_Globex_Fee'],2),
            'CME_Globex_Fee': round(value['CME_Globex_Fee'],2),
            'Give_In_Fee': round(value['Give_In_Fee'],2),
            'TotalFees': round(value['TotalFees'],2),
            'SumOfFeesAndCommission': round(value['SumOfFeesAndCommission'],2),
        }

        #print(quotes_context);

        accountdata_list_out.append(quotes_context);

    #for key, value in office_summary.items():
    for key in sorted(office_summary):

        value = office_summary[key]

        quotes_context = {
            'FCM': choose_fcm_name(value['FCM']),
            'Office': value['Office'],
            'Account': value['Account'],
            'TradedQuantityBuy': value['TradedQuantityBuy'],
            'TradedQuantitySell': value['TradedQuantitySell'],
            'Commission': round(value['Commission'], 2),
            'ClearingFees': round(value['ClearingFees'], 2),
            'ExchangeFees': round(value['ExchangeFees'], 2),
            'TransactionFees': round(value['TransactionFees'], 2),
            'NFAFees': round(value['NFAFees'], 2),
            'BrokerageFees': round(value['BrokerageFees'], 2),
            'TradeProcessingFees': round(value['TradeProcessingFees'], 2),
            'CBOT_Globex_Fee': round(value['CBOT_Globex_Fee'], 2),
            'CME_Globex_Fee': round(value['CME_Globex_Fee'], 2),
            'Give_In_Fee': round(value['Give_In_Fee'], 2),
            'TotalFees': round(value['TotalFees'], 2),
            'SumOfFeesAndCommission': round(value['SumOfFeesAndCommission'], 2),
        }

        #print(quotes_context);

        accountdata_list_out.append(quotes_context)

    return accountdata_list_out


def return_error(message, **kwargs):
    context={
        'status': 'error',
        'message': message,
    }
    context.update(kwargs)
    print(context)
    return Response(context)

def choose_fcm_name(fcm_code):
    fcm_name_list = {'1':'ADM',
                  '2': 'RCG',
                  '4': 'WEDBUSH',};

    if fcm_code in fcm_name_list:
        return fcm_name_list[fcm_code];
    else:
        return fcm_code;

def get_account_performance(start_date, end_date):
    tmp_mongo_connstr = 'mongodb://tmqr:tmqr@10.0.1.2/client-gmi?authMechanism=SCRAM-SHA-1'
    tmp_mongo_db = 'client-gmi'

    mongoClient = MongoClient(tmp_mongo_connstr)
    db = mongoClient[tmp_mongo_db]
    collection = db.accountsummarycollection

    accountdata_list_out = [];

    for accountdata in collection.find({'Batchid': {'$gte': start_date, '$lte': end_date}}).sort([
        ('FCM', pymongo.ASCENDING),('Office', pymongo.ASCENDING),('Account', pymongo.ASCENDING)]):

        if(accountdata['SummaryDetailFlag'] == 'D'
           or (accountdata['SummaryDetailFlag'] == 'S' and accountdata['AccountType'] == '9Z') ):

            quotes_context = {
                'FCM': choose_fcm_name(accountdata['FCM']),
                'SummaryDetailFlag': accountdata['SummaryDetailFlag'],
                'Ccy': accountdata['Ccy'],
                'Firm': accountdata['Firm'],
                'Office': accountdata['Office'],
                'Account': accountdata['Account'],
                'Batchid': accountdata['Batchid'],
                'AccountType': accountdata['AccountType'],
                'Commission': round(accountdata['Commission'], 2),
                'TotalFees': round(accountdata['TotalFees'], 2),
                'TransactionsCommissionsFees': round(accountdata['TransactionsCommissionsFees'], 2),
                'TradedQuantityBuy': round(accountdata['TradedQuantityBuy'], 2),
                'TradedQuantitySell': round(accountdata['TradedQuantitySell'], 2),
                'CurrentPosition': round(accountdata['CurrentPosition'], 2),
                'TotalEquity': round(accountdata['TotalEquity'], 2),
                'CurrentOTE': round(accountdata['CurrentOTE'], 2),
                'CurrentOV': round(accountdata['CurrentOV'], 2),
                'ChangeInAV_At_MD_Converted': round(accountdata['ChangeInAV_At_MD_Converted'], 2),
                'ConvertedAccountValueAtMarket': round(accountdata['ConvertedAccountValueAtMarket'], 2),
                'ConvertedPriorAccountValueAtMarket': round(accountdata['ConvertedPriorAccountValueAtMarket'], 2),
                'ConvertedChangeInAccountValueAtMarket': round(accountdata['ConvertedChangeInAccountValueAtMarket'], 2),
                'InitialMarginRequirement': round(accountdata['InitialMarginRequirement'], 2),
                'MaintenanceMarginRequirement': round(accountdata['MaintenanceMarginRequirement'], 2),
                'MarginExcess': round(accountdata['MarginExcess'], 2),
                'SecurityMasterID': accountdata['SecurityMasterID'],
                'SectorId': accountdata['SectorId'],
                'Sector': accountdata['Sector'],
                'SecurityMasterDesc': accountdata['SecurityMasterDesc'],
            }

            accountdata_list_out.append(quotes_context);

    return accountdata_list_out


def get_events_log(query_dict):
    try:
        page = max(1, int(query_dict.get('page', 1)))
    except:
        page = 1

    client = MongoClient(MONGO_CONNSTR)
    db = client[MONGO_EXO_DB]

    records_per_page = 20

    result_events = []

    for status_rec in db[EVENTS_LOG].find({}).sort([("date", -1)]).skip((page-1)*records_per_page).limit(records_per_page):
        status_rec['_id'] = str(status_rec['_id'])
        result_events.append(status_rec)

    return result_events

def get_events_status():
    client = MongoClient(MONGO_CONNSTR)
    db = client[MONGO_EXO_DB]
    result_events = []

    for status_rec in db[EVENTS_STATUS].find({}).sort([("appclass", 1), ("appname", 1)]):
        status_rec['_id'] = str(status_rec['_id'])
        result_events.append(status_rec)

    return result_events
#
#
# Views
#
#


# Create your views here.
@api_view(['GET'])
def view_quotes_monitor(request):
    config = SiteConfiguration.objects.get()

    context = {
        'instruments': config.insruments_list,
        'page_name': 'Contracts quotes monitoring',
        'site_name': config.site_name,
        'quotes_info': get_instrument_recent_quotes(config.insruments_list, datetime.now())
    }
    return Response(context)


@api_view(['GET'])
def view_quotes_exo(request):
    config = SiteConfiguration.objects.get()

    context = {
        'page_name': 'EXO quotes monitoring',
        'site_name': config.site_name,
        'exo_info': get_exo_list_info()
    }
    return Response(context)


@api_view(['GET'])
def view_actual_alphas(request):
    config = SiteConfiguration.objects.get()

    context = {
        'page_name': 'Actual alphas monitoring',
        'site_name': config.site_name,
        'alphas_info': get_actual_alphas()
    }
    return Response(context)


@api_view(['GET'])
def view_fcm_fees(request, start_date, end_date):

    context = {
        'page_name': 'GMI Fees',
        'fee_info': get_gmi_fees(start_date, end_date)
    }
    return Response(context)


@api_view(['GET'])
def view_account_performance(request, start_date, end_date):

    context = {
        'page_name': 'Account Performance',
        'account_info': get_account_performance(start_date, end_date)
    }
    return Response(context)


@api_view(['GET'])
def view_events_log(request):
    config = SiteConfiguration.objects.get()

    context = {
        'page_name': 'Event log',
        'site_name': config.site_name,
        'events_info': get_events_log(request.GET)
    }
    return Response(context)

@api_view(['GET'])
def view_events_status(request):
    config = SiteConfiguration.objects.get()

    context = {
        'page_name': 'Event log',
        'site_name': config.site_name,
        'events_info': get_events_status()
    }
    return Response(context)

@api_view(['GET'])
def view_campaigns_list(request):
    def get_campaign_instrument(alphas):
        instr = set()
        for k, v in alphas.items():
            instr.add(k.split("_")[0])

        if len(instr) > 1:
            return 'MultiProduct'
        elif len(instr) == 0:
            return ''
        else:
            return instr.pop()

    campaigns = []
    storage = EXOStorage(MONGO_CONNSTR, MONGO_EXO_DB)

    for cmp in storage.campaign_load(None):
        cmp_name = cmp['name']
        cmp_desc = cmp['description']
        campaigns.append({
            'name': cmp_name,
            'description': cmp_desc,
            'instrument': get_campaign_instrument(cmp['alphas'])
        })
    context = {'status': 'OK', 'campaigns': campaigns}

    return Response(context)


@api_view(['GET'])
def view_campaigns_series(request):
    try:
        campaign = request.GET.get('campaign', '')
        performance_fee_percentage = request.GET.get('performance_fee_percentage', 0.0)
        commission_dollars = request.GET.get('commission_dollars', 0.0)
        starting_date = datetime.strptime(request.GET.get('starting_date', '1900-01-01'), "%Y-%m-%d")
        end_date = datetime.strptime(request.GET.get('end_date', '2100-01-01'), "%Y-%m-%d")

        storage = EXOStorage(MONGO_CONNSTR, MONGO_EXO_DB)
        rpt = CampaignReport(campaign, exo_storage=storage, raise_exceptions=True)

        if starting_date > end_date:
            return return_error("Starting date greater than end date.")

        df = rpt.campaign_stats.ix[starting_date:end_date]
        if len(df) < 2:
            return return_error("Empty campaign series for required period.")

        context = {
            'campaign': campaign,
            'starting_date': df.index[0],
            'end_date': df.index[-1],
            'starting_value': df['Equity'][0],
            'end_value': df['Equity'][-1],
            'total_number_of_trades': df[df['Costs'] != 0]['Costs'].count(),
            'total_cost': df['Costs'].sum(),
            'max_drawdown': (df['Equity'] - df['Equity'].expanding().max()).min(),
            'max_delta': df['Delta'].max(),
            'average_delta': df['Delta'].mean()
        }

        cmp_series = []

        for i in range(len(df)):
            r = df.iloc[i]
            cmp_series.append({
                'date': r.name,
                'change': r['Change'],
                'costs': r['Costs'],
                'trade_count': 0,
                'delta': r['Delta'],
                'equity': r['Equity']
            })
        context['series'] = cmp_series
        context['status'] = 'OK'
        return Response(context)
    except Exception as exc:
        return return_error(str(exc), traceback=traceback.format_exc())


@api_view(['GET'])
def view_campaigns_payoff(request):
    try:
        strikes_on_graph = request.GET.get('nstrikes', 30)
        analysis_date = request.GET.get('date', None)
        if analysis_date is not None:
            analysis_date = datetime.strptime(analysis_date, "%Y-%m-%d")
        campaign = request.GET.get('campaign', '')

        assetindex = AssetIndexMongo(MONGO_CONNSTR, MONGO_EXO_DB)
        storage = EXOStorage(MONGO_CONNSTR, MONGO_EXO_DB)
        futures_limit = 3
        options_limit = 20
        datasource = DataSourceMongo(MONGO_CONNSTR, MONGO_EXO_DB, assetindex, futures_limit, options_limit, storage)

        payoff = PayoffAnalyzer(datasource, raise_exceptions=True)
        payoff.load_campaign(campaign, date=analysis_date)
        pos_info = payoff.position_info()
        payoffdf = payoff.calc_payoff(strikes_to_analyze=strikes_on_graph)

        payoff_series = []
        delta_series = []
        for i in range(len(payoffdf)):
            stike_payoff = payoffdf.iloc[i]
            payoff_series.append({
                "px": stike_payoff.name,
                "curr": stike_payoff['current_payoff'],
                "exp": stike_payoff['expiration_payoff']
            })
            delta_series.append({
                "px": stike_payoff.name,
                "curr": stike_payoff['current_delta'],
                "expir": stike_payoff['expiration_delta']
            })

        return Response({
            'status': 'OK',
            "campaign": campaign,
            "date": analysis_date if analysis_date is not None else datetime.now().date(),
            "current_future_price": pos_info['current_ulprice'],
            "positions": pos_info['whatif_positions'],
            "payoff_series": payoff_series,
            "delta_series": delta_series,
        })
    except Exception as exc:
        return return_error(str(exc), traceback=traceback.format_exc())