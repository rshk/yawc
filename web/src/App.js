import {Component} from 'react';

import styles from './App.scss';

export default class App extends Component {
    state = {
        name: 'web'
    };

    render () {
        return (
            <div className={styles.App}>
                <h1>Welcome to {this.state.name}</h1>
            </div>
        )
    }
}
