import React from 'react';
import {NavLink} from 'react-router-dom';
import styles from './index.scss';


export default function ChatUI({channel}) {
    return <div className={styles.Container}>
        <div className={styles.Title}>
            <div>
                <h1>YAWC</h1>
            </div>
            <div>Hello $user</div>
            <div>
                <button type="button" className="btn btn-link">Logout</button>
            </div>
        </div>
        <div className={styles.Chat}>
            <ChannelSelector channel={channel} />
            <ChatChannel key={channel} channel={channel} />
        </div>
    </div>;
}


function ChannelSelector() {
    const channels = [
        'default',
        'hello',
        'foobar',
        'random',
        'serious',
        'silly',
    ];

    return <div className={styles.ChannelSelector + ' nav flex-column'}>
        {channels.map(channel =>
            <NavLink key={channel} to={`/chat/${channel}`} className="nav-link nav-item">
                #{channel}
            </NavLink>)}
    </div>;
}


function ChatChannel({channel}) {
    if (!channel) {
        return <div className={styles.ChatChannel} />;
    }

    return <div className={styles.ChatChannel}>
        <ChatMessages channel={channel} />
        <ChatInputBar channel={channel} />
    </div>;
}


function ChatMessages({channel}) {
    return <div className={styles.ChatMessages}>
        Chat messages for #{channel}
    </div>;
}


class ChatInputBar extends React.Component {
    constructor(...args) {
        super(...args);
        this.state = {text: ''};
    }

    render() {
        const _onTextChange = (evt)=> {
            this.setState({text: evt.target.value});
        };
        const _ref = (el) => {
            if (el) {
                el.focus();
            };
        };
        return <div className={styles.ChatInputBar}>
            <form onSubmit={this._onSubmit.bind(this)}>
                <input type="text" value={this.state.text} onChange={_onTextChange} ref={_ref} />
            </form>
        </div>;
    }

    _onSubmit(evt) {
        evt.preventDefault();
        this.setState({text: ''});
    }
}
