/**
 * Created by ubertrader on 11/7/16.
 */
/*
 * Created by ubertrader on 11/7/16.
 */
import React from "react";
import PreloadAnimation from '../common/preload_animation.jsx';

var moment = require('moment');

class QuotesContractsComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            data: {quotes_info: {}},
            is_loading: false,
        };
        this.getData = this.getData.bind(this);
    }

    componentDidMount(){
        this.getData();
    }

    getData(){
        //
        // Show pre-load animation
        //
        this.setState({
            is_loading: true,
        });

        console.log('Requesting exo data')
        return $.getJSON('/api/contracts/')
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
        if (this.state.is_loading){
            return (<PreloadAnimation/>)
        }

        const listItems = Object.keys(this.state.data.quotes_info).map((key) =>
            <ContractQuotesItem key={key} contract_data={this.state.data.quotes_info[key]}/>
        );

        return (
            <div>
                <h1>Quotes monitor index page</h1>
                <div>
                    <table className="table table-stripped">

                        <thead>
                        <tr>
                            <th rowSpan="2">Instrument</th>
                            <th rowSpan="2">Date</th>
                            <th rowSpan="2">Contract</th>
                            <th rowSpan="2">Opt. Expiration</th>
                            <th colSpan="3">Execution time / price</th>
                            <th colSpan="3">Decision time / price</th>
                        </tr>
                        <tr>
                            <th>time</th>
                            <th>quote time</th>
                            <th>price</th>
                            <th>time</th>
                            <th>quote time</th>
                            <th>price</th>
                        </tr>
                        </thead>
                        <tbody>

                        {listItems}

                        </tbody>

                    </table>

                </div>
            </div>
        );
    }
}


function ContractQuotesItem(props) {

    var qi = props.contract_data;

    var date_now = moment(qi.date_now);

    return (
        <tr>
            <td>{ qi.instrument }</td>
            <td>{ date_now.format("DD MMM HH:mm") }</td>
            <td>{ qi.fut_contract }</td>
            <td>{ qi.opt_series}</td>
            <td>{ moment(qi.exec_time).format("HH:mm") }</td>

            {
                date_now.date() == moment(qi.exec_time_quote_date).date() ?
                    (<td>{moment(qi.exec_time_quote_date).format("HH:mm")}</td>) :
                    (<td className="warning">{moment(qi.exec_time_quote_date).format("DD MMM HH:mm")}</td>)
            }

            <td>{ qi.exec_price_fut_price }</td>
            <td>{moment(qi.decision_time).format("HH:mm")}</td>
            {
                date_now.date() == moment(qi.decision_time_quote_date).date() ?
                    (<td>{moment(qi.decision_time_quote_date).format("HH:mm")}</td>) :
                    (<td className="warning">{moment(qi.decision_time_quote_date).format("DD MMM HH:mm")}</td>)
            }

            <td>{qi.decision_time_fut_price}</td>
        </tr>
    )

}

export default QuotesContractsComponent;
