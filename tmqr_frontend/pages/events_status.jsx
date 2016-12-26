/**
 * Created by ubertrader on 12/26/16.
 */
/**
 * Created by ubertrader on 12/26/16.
 */
import React from "react";
import PreloadAnimation from '../common/preload_animation.jsx';

var moment = require('moment');

class EventsStatusComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            data: {events_info:{}},
            is_loading: false,
        };
        this.getData = this.getData.bind(this);
    }

    componentDidMount(){
        this.getData();
    }

    getData(new_active_page){
        //
        // Show pre-load animation
        //
        this.setState({
                    is_loading: true,
                });


        console.log('Requesting events log')

        return $.getJSON('/api/events-status/')
            .done((result) => {
                this.setState({
                    data: result,
                    is_loading: false,
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

        return (
            <div>
                <EventsList event_data={this.state.data.events_info}/>
            </div>
        );
    }
}

function EventsList(props) {
    const listItems = Object.keys(props.event_data).map((key) =>
            <EventItem key={key} einfo={props.event_data[key]}/>
    );

    return (
        <div>
            <h2>Event status summary</h2>

            <table className="table table-stripped">
                <thead>
                <tr>
                    <th>Date</th>
                    <th>Class</th>
                    <th>AppName</th>
                    <th>Status</th>
                    <th>Text</th>
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
            <td>{ moment(props.einfo.date).format("DD MMM HH:mm") }</td>
            <td>{ props.einfo.appclass }</td>
            <td>{ props.einfo.appname }</td>
            <td>{ props.einfo.status }</td>
            <td>{ props.einfo.text }</td>
        </tr>
    )
}

export default EventsStatusComponent;