/**
 * Created by ubertrader on 11/5/16.
 */

import React from 'react';


class PreloadAnimation extends React.Component {
    /*
     Shows preload animation for long running tasks
    */

    constructor(props) {
        super(props);
    }

    render() {
        return(<div className="preloader"></div>);
    }
}

export default PreloadAnimation;