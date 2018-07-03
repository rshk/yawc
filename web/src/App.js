import React from 'react';
import {BrowserRouter, Switch, Route, Redirect} from 'react-router-dom';

import ChatUI from 'components/chat';
import LoginUI from 'components/login';

import styles from './App.scss';


export default function App() {
    return <BrowserRouter>
        <div className={styles.App}>
            <Switch>
                <Route exact path="/" component={HomeComponent} />
                <Route exact path="/chat"
                       render={({match: {params: {channel}}}) =>
                           <ChatUI channel={null} />} />
                <Route exact path="/chat/:channel"
                       render={({match: {params: {channel}}}) =>
                           <ChatUI channel={channel} />} />
                <Route exact path="/login" component={LoginUI} />
                <Route component={HomeComponent} />
            </Switch>
        </div>
    </BrowserRouter>;
}


function HomeComponent() {
    return <Redirect to="/chat" />;
}
