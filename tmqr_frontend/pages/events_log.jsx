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
            data: {events_info:{}},
            is_loading: false,
            active_page: 1,
        };
        this.getData = this.getData.bind(this);
        this.changePage = this.changePage.bind(this);
    }

    componentDidMount(){
        this.getData(1);
    }

    getData(new_active_page){
        //
        // Show pre-load animation
        //
        this.setState({
                    is_loading: true,
                });


        console.log('Requesting events log')

        return $.getJSON('/api/events-log/?page='+new_active_page)
            .done((result) => {
                this.setState({
                    data: result,
                    is_loading: false,
                    active_page: new_active_page,
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

    changePage(page_increment){
        let new_active_page = this.state.active_page + page_increment;
        this.getData(new_active_page);
        console.log("new_active_page: " + new_active_page);
    }

    render() {
        if (this.state.is_loading){
            return (<PreloadAnimation/>)
        }
        let page_prev = null;

        if(this.state.active_page > 1){
            page_prev = <a href="#" onClick={() => this.changePage(-1)}>&lt;&lt; Previous | </a>;
        }

        let page_next = <a href="#" onClick={() => this.changePage(1)}>Next &gt; &gt;</a>;

        let page_no = null;
        if (this.state.active_page > 1){
            page_no = <p>Page: {this.state.active_page}</p>;
        }

        return (
            <div>
                <h2>Event log</h2>
                {page_no}
                <EventsList event_data={this.state.data.events_info}/>
                <div>
                    {page_no}
                    {page_prev} {page_next}
                </div>
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
            <table className="table table-stripped">
                <thead>
                <tr>
                    <th>Date</th>
                    <th>EventType</th>
                    <th>Class</th>
                    <th>AppName</th>
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
            <td>{ props.einfo.msgtype }</td>
            <td>{ props.einfo.appclass }</td>
            <td>{ props.einfo.appname }</td>
            <td>{ props.einfo.text }</td>
        </tr>
    )
}

export default EventsLogComponent;