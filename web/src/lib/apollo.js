import {ApolloClient} from 'apollo-client';
import {InMemoryCache} from 'apollo-cache-inmemory';
import {onError} from 'apollo-link-error';
import {ApolloLink} from 'apollo-link';
import {createUploadLink} from 'apollo-upload-client';
import {createHttpLink} from 'apollo-link-http';
import {setContext} from 'apollo-link-context';
import {split} from 'apollo-link';
import {WebSocketLink} from 'apollo-link-ws';
import {getMainDefinition} from 'apollo-utilities';

import {doLogout, getToken} from './auth';


// TODO load from process.env.API_URL or similar
const API_URL = process.env.API_URL || 'https://graphqlbin.org/graphql';
const WEBSOCKET_URL = (
    API_URL.replace(/^http(s?):\/\/(.*)/, 'ws$1://$2')
    .replace(/\/graphql$/, '/subscriptions')  // HACK
);

const ENABLE_UPLOADS = true;


const onErrorLink = onError(({graphQLErrors, networkError}) => {
    if (graphQLErrors)
        graphQLErrors.map(({ message, locations, path }) =>
            console.log(
                `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`,
            ),
        );

    if (networkError) console.log(`[Network error]: ${networkError}`);

    if (networkError) {
        console.log(`[Network error]: ${networkError}`);

        if (networkError.statusCode === 401) {
            doLogout();  // Force re-login
        }
    }
});


const httpLink = (() => {
    const config = {
        uri: API_URL,
        credentials: 'same-origin'
    };

    if (ENABLE_UPLOADS) {
        return createUploadLink(config);
    }
    return createHttpLink(config);
})();


const authLink = setContext((_, {headers: extraHeaders}) => {
    const token = getToken();
    const headers = {...extraHeaders};
    if (token) {
        headers.authorization = `Bearer ${token}`;
    }
    return {headers};
});


const wsLink = new WebSocketLink({
    uri: WEBSOCKET_URL,
    options: {
        reconnect: true
    }
});


// using the ability to split links, you can send data to each link
// depending on what kind of operation is being sent
const link = split(
    // split based on operation type
    ({ query }) => {
        const {kind, operation} = getMainDefinition(query);
        // console.log('SPLIT LINK', kind, operation);
        return kind === 'OperationDefinition' && operation === 'subscription';
    },
    wsLink,
    ApolloLink.from([
        onErrorLink,
        authLink,
        httpLink,
    ]),
);


const cache = new InMemoryCache();

const client = new ApolloClient({link, cache});

export default client;
