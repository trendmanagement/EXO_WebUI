/**
 * Created by ubertrader on 12/26/16.
 */
import React from "react";
import PreloadAnimation from '../common/preload_animation.jsx';

var moment = require('moment');

class EventsLogComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            data: {},
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

        console.log('Requesting events log')
        return $.getJSON('/api/events-log/')
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

        const listItems = Object.keys(this.state.data.exo_info).map((key) =>
            <ExoList key={key} exo_data={this.state.data.exo_info[key]} exo_asset={key}/>
        );

        return (
            <div>
                {listItems}
            </div>
        );
    }
}

function EventsList(props) {
    const listItems = Object.keys(props.exo_data).map((key) =>
            <ExoItem key={key} xinfo={props.exo_data[key]}/>
    );

    return (
        <div>
            <h2>{props.exo_asset}</h2>

            <table className="table table-stripped">
                <thead>
                <tr>
                    <th rowSpan="2">EXO Name</th>
                    <th rowSpan="2">Updated</th>
                    <th rowSpan="2">Last rollover</th>
                    <th colSpan="2">EXO last quote</th>
                </tr>
                <tr>
                    <th>quote date</th>
                    <th>price</th>
                </tr>
                </thead>
                <tbody>

                {listItems}

                </tbody>
            </table>
        </div>
    );
}

function EventItem(props) {
    return (
        <tr>
            <td>{ props.xinfo.exo_name }</td>
            <td>{ moment(props.xinfo.calc_date).format("DD MMM HH:mm") }</td>
            <td>{ moment(props.xinfo.last_rollover_date).format("DD MMM HH:mm") }</td>
            <td>{ moment(props.xinfo.exo_last_date).format("DD MMM HH:mm") }</td>
            <td>{ props.xinfo.exo_last_quote.toFixed(2) }</td>
        </tr>
    )

}

export default EventsLogComponent;