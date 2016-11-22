import React from 'react';
import {render} from 'react-dom';

import PageRouter from './pages/page_router.jsx';

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {current_page : 'index'};
        this.onNewPageClick = this.onNewPageClick.bind(this);
    }
    onNewPageClick (page_name) {
        this.setState({current_page : page_name});
    }

    render () {
        return <div>
            <nav className="navbar navbar-inverse navbar-fixed-top">
                <div className="container-fluid">
                    <div>
                        <a className="navbar-brand" href="/">TMQR OnlineManager</a>
                    </div>
                    <div id="navbar" className="navbar-collapse collapse">
                        <ul className="nav navbar-nav navbar-right">
                            <li><a href="/documentation/out/html/index.html">Documentation</a></li>
                            <li><a href="/admin/">Settings</a></li>
                        </ul>
                    </div>
                </div>
            </nav>

            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-3 col-md-2 sidebar">
                        <ul className="nav nav-sidebar">
                            <li><a onClick={() => this.onNewPageClick('index')}>Dashboard</a></li>
                        </ul>
                        <h4>Quotes monitoring</h4>
                        <ul className="nav nav-sidebar">
                            <li><a onClick={() => this.onNewPageClick('quotes_contracts')}>Contracts quotes</a></li>
                            <li><a onClick={() => this.onNewPageClick('quotes_exo')}>EXO quotes</a></li>
                            <li><a onClick={() => this.onNewPageClick('quotes_alphas')}>Actual alphas</a></li>
                        </ul>
                    </div>
                    <div className="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
                        <PageRouter page_name={this.state.current_page}/>
                    </div>
                </div>
            </div>

        </div>;
    }
}

render(<App/>, document.getElementById('app'));