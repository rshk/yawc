import React from 'react';
import {NavLink} from 'react-router-dom';
import styles from './index.scss';
import gql from 'graphql-tag';
import {Query, Mutation} from 'react-apollo';


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
        return <div className={styles.ChatChannel} key={channel} />;
    }

    return <div className={styles.ChatChannel}>
        <ChatMessages channel={channel} />
        <ChatInputBar channel={channel} />
    </div>;
}


const QUERY_MESSAGES = gql`
    query getMessages($channel: String!) {
        messages(channel: $channel) {
            edges {
                id
                timestamp
                channel
                user {
                    name
                }
                text
            }
        }
    }
`;


function ChatMessages({channel}) {
    return <div key={channel} className={styles.ChatMessages}>
        <Query query={QUERY_MESSAGES} variables={{channel}} fetchPolicy="cache-and-network">
            {({loading, error, data}) => {
                 if (loading) {
                     return <div>Loading...</div>;
                 }
                 if (error) {
                     return <div>{`Error: ${error}`}</div>;
                 }
                 return <div>{
                     data.messages.edges.map(({id, timestamp, user, text}) =>
                         <div key={id}>
                             <strong>{user.name}:</strong> {text}
                         </div>
                     )}
                 </div>;
            }}
        </Query>
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
