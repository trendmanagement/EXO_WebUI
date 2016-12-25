/**
 * Created by ubertrader on 11/5/16.
 */

import React from 'react';

import QuotesEXOComponent from './quotes_exo_component.jsx';
import QuotesAlphasComponent from './quote_alphas_component.jsx'
import QuotesContractsComponent from './quote_contracts_component.jsx'
import GMIFeeComponent from './fee_analysis_component.jsx'
import GMIAccountComponent  from './account_performance_component.jsx'

import PreloadAnimation from '../common/preload_animation.jsx'


class PageRouter extends React.Component {
    /*
     Routes the pages of the dashboard application
    */

    constructor(props) {
        super(props);
    }

    render() {
        switch (this.props.page_name){
            case 'index':
                return (<h1>Index page</h1>);
            case 'quotes_exo':
                return (<QuotesEXOComponent/>);
            case 'quotes_contracts':
                return (<QuotesContractsComponent/>);
            case 'quotes_alphas':
                return (<QuotesAlphasComponent/>);
            case 'gmi_fees':
                return (<GMIFeeComponent/>);
            case 'gmi_accounts':
                return (<GMIAccountComponent/>);
            default:
                return (<h1>Page not found</h1>);
        }
    }
}

export default PageRouter;