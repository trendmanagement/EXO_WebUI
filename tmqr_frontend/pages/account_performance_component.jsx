
import React from "react";
import DateRangePickerForDataCall from '../common/daterange.jsx';

var moment = require('moment');

class GMIAccountComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            data: {account_info: {}},
            is_loading: false,
            startDate: moment().format('YYYY-MM-DD'),
            endDate: moment().format('YYYY-MM-DD'),
        };
        this.getData = this.getData.bind(this);
        this.sendData = this.sendData.bind(this);
    }

    componentDidMount(){
        this.getData();
    }

    sendData(startDate, endDate){
        this.state.startDate = startDate;
        this.state.endDate = endDate;

        this.getData();
    }

    getData(){
        //
        // Show pre-load animation
        //
        //this.props.start_date


        this.setState({
            is_loading: true,
        });

        console.log('Requesting exo data ' + this.state.startDate)
        return $.getJSON('/api/gmiaccountperformance/'+ this.state.startDate + '/' + this.state.endDate)
            .done((result) => {
                this.setState({
                    data: result,
                    is_loading: false
                });
            })
            .fail(function( jqxhr, textStatus, error ) {
                var err = textStatus + ', ' + error;
                console.log( "Request Failed: " + err);
                this.setState({
                    is_loading: false
                });
            })
    }


    render() {
        //if (this.state.is_loading){
        //    return (<PreloadAnimation/>)
       //}

        const listItems = Object.keys(this.state.data.account_info).map((key) =>
            <ContractQuotesItem key={key} fee_data={this.state.data.account_info[key]}/>
        );

        return (
            <div>
            <small>
                <h1>Account Performance</h1>
                <DateRangePickerForDataCall onMagicClick={this.sendData}/>
                <div>

                    <table className="table table-bordered account-performance">

                        <thead>
                        <tr>
                            <th><span title='FCM'>FCM</span></th>
                            <th><span title='Summary Detail Flag'>SDF</span></th>
                            <th><span title='Ccy'>Ccy</span></th>
                            <th><span title='Firm'>Frm</span></th>
                            <th><span title='Office'>Ofc</span></th>
                            <th><span title='Account'>Act</span></th>
                            <th><span title='Date'>Dte</span></th>
                            <th><span title='Account Type'>AT</span></th>
                            <th><span title='Commission'>Cms</span></th>
                            <th><span title='Total Fees'>TF</span></th>
                            <th><span title='Transactions Commissions Fees'>TFC</span></th>
                            <th><span title='Exchange Code'>ExC</span></th>
                            <th><span title='Traded Quantity Buy'>TQB</span></th>
                            <th><span title='Traded Quantity Sell'>TQS</span></th>
                            <th><span title='Current Position'>CP</span></th>
                            <th><span title='Total Equity'>TE</span></th>
                            <th><span title='Current OTE'>Cur OTE</span></th>
                            <th><span title='Current OV'>Cur OV</span></th>
                            <th><span title='Change in AV At MD Converted'>Chg in AV At MD Cvt</span></th>
                            <th><span title='Converted Account Value At Market'>Cvt Act Val At Mkt</span></th>
                            <th><span title='Converted Prior Account Value At Market'>Cvt Pri Act Val At Mkt</span></th>
                            <th><span title='Converted Change In Account Value At Market'>Cvt Chg In Act Val At Mkt</span></th>
                            <th><span title='Initial Margin Requirement'>Int Mgn Rqt</span></th>
                            <th><span title='Maintenance Margin Requirement'>Mtn Mrg Req</span></th>
                            <th><span title='Margin Excess'>Mgn Exs</span></th>
                            <th><span title='Security Master ID'>Sec Mstr ID</span></th>
                            <th><span title='Sector Id'>Sctr Id</span></th>
                            <th><span title='Sector'>Sctr</span></th>
                            <th><span title='Security Master Desc'>Scty Mstr Desc</span></th>

                        </tr>
                        </thead>
                        <tbody>

                        {listItems}

                        </tbody>

                    </table>

                </div>
            </small>

            </div>
        );
    }
}


function ContractQuotesItem(props) {

    var qi = props.fee_data;

    //var date_now = moment(qi.date_now);

    return (
        <tr>
            <td>{ qi.FCM }</td>
            <td>{ qi.SummaryDetailFlag }</td>
            <td>{ qi.Ccy }</td>
            <td>{ qi.Firm }</td>
            <td>{ qi.Office }</td>
            <td>{ qi.Account }</td>
            <td>{ qi.Batchid }</td>
            <td>{ qi.AccountType }</td>
            <td>{ qi.Commission }</td>
            <td>{ qi.TotalFees }</td>
            <td>{ qi.TransactionsCommissionsFees }</td>
            <td>{ qi.ExchangeCode }</td>
            <td>{ qi.TradedQuantityBuy }</td>
            <td>{ qi.TradedQuantitySell }</td>
            <td>{ qi.CurrentPosition }</td>
            <td>{ qi.TotalEquity }</td>
            <td>{ qi.CurrentOTE }</td>
            <td>{ qi.CurrentOV }</td>
            <td>{ qi.ChangeInAV_At_MD_Converted }</td>
            <td>{ qi.ConvertedAccountValueAtMarket }</td>
            <td>{ qi.ConvertedPriorAccountValueAtMarket }</td>
            <td>{ qi.ConvertedChangeInAccountValueAtMarket }</td>
            <td>{ qi.InitialMarginRequirement }</td>
            <td>{ qi.MaintenanceMarginRequirement }</td>
            <td>{ qi.MarginExcess }</td>
            <td>{ qi.SecurityMasterID }</td>
            <td>{ qi.SectorId }</td>
            <td>{ qi.Sector }</td>
            <td>{ qi.SecurityMasterDesc }</td>
        </tr>
    )

}

// var GMIFeeComponent = React.createClass({
//
//     //this.refs.
//
//     render() {
//         return <div>
//             <DateRangePickerForDataCall/>
//             <GMIFeeComponentTable start_date="2016-11-05"/>
//         </div>;
//     }
// });

export default GMIAccountComponent;
