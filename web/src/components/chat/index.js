import React from 'react';
import {NavLink} from 'react-router-dom';
import styles from './index.scss';
import gql from 'graphql-tag';
import {Query, Mutation, Subscription} from 'react-apollo';
import {DateTime} from 'luxon';


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
                user { name }
                text
            }
        }
    }
`;

/*
 * const SUBSCRIBE_MESSAGES = gql`
 *     subscription newMessages($channel: String!) {
 *         message: messages(channel: $channel) {
 *             id
 *             text
 *         }
 *     }
 * `;
 *  */

const SUBSCRIBE_MESSAGES = gql`
    subscription newMessages($channel: String!) {
        message: newMessages(channel: $channel) {
            id
            channel
            text
            timestamp
            user { name }
        }
    }
`;


function ChatMessages({channel}) {
    return <div className={styles.ChatMessages}>
        <div style={{textAlign:'center',borderBottom:'solid 1px #ddd'}}>
            This is the beginning of chat history for #{channel}
        </div>
        <Query query={QUERY_MESSAGES} variables={{channel}} fetchPolicy="cache-and-network">
            {props => <MessagesList channel={channel} {...props} />}
        </Query>
    </div>;
}


class MessagesList extends React.Component {

    render() {
        const {loading, error, data} = this.props;

        if (loading) {
            return <div>Loading...</div>;
        }
        if (error) {
            return <div>{`Error: ${error}`}</div>;
        }
        return <div>{
            data.messages.edges.map((props) =>
                <ChatMessage key={props.id} {...props} />
            )}
        </div>;
    }

    componentDidMount() {
        const {subscribeToMore, channel} = this.props;
        console.log('=====> SUBSCRIBE TO MESSAGES', channel);
        this.unsubscribe = subscribeToMore({
            document: SUBSCRIBE_MESSAGES,
            variables: {channel},
            updateQuery: (prev={}, newData) => {

                console.log('===> UPDATE', prev, newData);

                const {subscriptionData: {data: {message}}} = newData;

                // Merge new message to collection
                const {messages = {}, ...extra} = prev;
                const {edges = []} = messages;
                return {
                    messages: {
                        ...messages,
                        edges: [...edges, message],
                    },
                    ...extra,
                };
            }
        });
    }

    componentWillUnmount() {
        if (this.unsubscribe) {
            this.unsubscribe();
        }
    }
}


function ChatMessage({id, timestamp, user, text}) {
    const ts = DateTime.fromISO(timestamp);
    return <div>
        <small>{ts.toLocaleString(DateTime.DATETIME_FULL)}</small>{' '}
        <strong>{user ? user.name : '???'}</strong> {text}
    </div>;
}


const POST_MESSAGE = gql`
    mutation postMessage($channel: String!, $text: String!) {
        postMessage(channel: $channel, text: $text) {
            ok
        }
    }
`;


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
            <Mutation mutation={POST_MESSAGE}>
                {(postMessage) =>
                    <form onSubmit={this._onSubmit.bind(this, postMessage)}>
                        <input type="text" value={this.state.text}
                               onChange={_onTextChange} ref={_ref} />
                    </form>}
            </Mutation>
        </div>;
    }

    _onSubmit(postMessage, evt) {
        evt.preventDefault();
        const {channel} = this.props;
        const {text} = this.state;
        postMessage({variables: {channel, text}})
            .then(({data: {postMessage: {ok}}}) => {
                if (ok) {
                    this.setState({text: ''});
                }
            });
    }
}


function FuckingClock() {
    return <Subscription subscription={SUBSCRIBE_MESSAGES}
                         variables={{channel:'hello'}}>
        {(props) => (
            <h4>Shite: {JSON.stringify(props)}</h4>
        )}
    </Subscription>;
}
