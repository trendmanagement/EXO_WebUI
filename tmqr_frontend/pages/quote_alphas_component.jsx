/*
 * Created by ubertrader on 11/7/16.
 */
import React from "react";
import PreloadAnimation from '../common/preload_animation.jsx';

var moment = require('moment');

class QuotesAlphasComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            data: {alphas_info: {}},
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
        return $.getJSON('/api/alphas/')
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

        const listItems = Object.keys(this.state.data.alphas_info).map((key) =>
            <AlphasList key={key} alpha_data={this.state.data.alphas_info[key]} campaign_name={key}/>
        );

        return (
            <div>
                <h1>Actual alphas state monitoring</h1>
                {listItems}
            </div>
        );
    }
}

function AlphasList(props) {
    const listItems = Object.keys(props.alpha_data).map((key) =>
        <AlphaItem key={key} xinfo={props.alpha_data[key]}/>
    );

    return (
        <div>
            <h2>Campaign: {props.campaign_name}</h2>
            <table className="table table-stripped">
                <thead>
                <tr>
                    <th>Alpha Name</th>
                    <th>Updated</th>
                    <th>Last series date</th>
                    <th>Last rebalance date</th>
                    <th>Last exposure</th>
                    <th>Prev exposure</th>
                </tr>
                </thead>
                <tbody>

                {listItems}

                </tbody>
            </table>

        </div>
    );
}

function AlphaItem(props) {

    if (props.xinfo == false)
    {
        return (
            <tr>
                <td>{ props.xinfo.swarm_name }</td>
                <td colSpan="5">Swarm data is not found in the DB.</td>
            </tr>
        )
    }
    else
    {
        return (
            <tr>
                <td>{ props.xinfo.swarm_name }</td>
                <td>{ moment(props.xinfo.calc_date).format("DD MMM HH:mm") }</td>
                <td>{ moment(props.xinfo.last_date).format("DD MMM") }</td>
                <td>{ moment(props.xinfo.last_rebalance_date).format("DD MMM") }</td>
                <td>{ props.xinfo.last_exposure.toFixed(2) }</td>
                <td>{ props.xinfo.last_prev_exposure.toFixed(2) }</td>
            </tr>
        )
    }
}

export default QuotesAlphasComponent;
