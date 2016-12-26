
import React from "react";
import DateRangePickerForDataCall from '../common/daterange.jsx';

var moment = require('moment');

class GMIFeeComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            data: {fee_info: {}},
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
        return $.getJSON('/api/gmifees/'+ this.state.startDate + '/' + this.state.endDate)
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

        const listItems = Object.keys(this.state.data.fee_info).map((key) =>
            <ContractQuotesItem key={key} fee_data={this.state.data.fee_info[key]}/>
        );

        return (
            <div>
            <small>
                <h1>GMI Fees</h1>
                <DateRangePickerForDataCall onMagicClick={this.sendData}/>
                <div>

                    <table className="table table-bordered">

                        <thead>
                        <tr>
                            <th><span title='FCM'>FCM</span></th>
                            <th><span title='Office'>Office</span></th>
                            <th><span title='Account'>Acct</span></th>
                            <th><span title='Traded Qty Buy'>Trd Qty Buy</span></th>
                            <th><span title='Traded Qty Sell'>Trd Qty Sell</span></th>
                            <th><span title='Commission'>Commiss</span></th>
                            <th><span title='Clearing Fees'>Clear. Fees</span></th>
                            <th><span title='Exchange Fees'>Exch Fees</span></th>
                            <th><span title='Transaction Fees'>Trans Fees</span></th>
                            <th><span title='NFA Fees'>NFA Fees</span></th>
                            <th><span title='Brokerage Fees'>Brkrge Fees</span></th>
                            <th><span title='Trade Processing Fees'>Trd Process Fees</span></th>
                            <th><span title='CBOT Globex Fee'>CBOT Glbx Fee</span></th>
                            <th><span title='CME Globex Fee'>CME Glbx Fee</span></th>
                            <th><span title='Give In Fee'>Give In Fee</span></th>
                            <th><span title='Total Fees'>Ttl Fee</span></th>
                            <th><span title='Total Fees & Commissions'>Ttl Fee & Commiss</span></th>
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
            <td>{ qi.Office }</td>
            <td>{ qi.Account }</td>
            <td>{ qi.TradedQuantityBuy }</td>
            <td>{ qi.TradedQuantitySell }</td>
            <td>{ qi.Commission }</td>
            <td>{ qi.ClearingFees }</td>
            <td>{ qi.ExchangeFees }</td>
            <td>{ qi.TransactionFees }</td>
            <td>{ qi.NFAFees }</td>
            <td>{ qi.BrokerageFees }</td>
            <td>{ qi.TradeProcessingFees }</td>
            <td>{ qi.CBOT_Globex_Fee }</td>
            <td>{ qi.CME_Globex_Fee }</td>
            <td>{ qi.Give_In_Fee }</td>
            <td>{ qi.TotalFees }</td>
            <td>{ qi.SumOfFeesAndCommission }</td>

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

export default GMIFeeComponent;
