import React from 'react';
import {ApolloProvider} from 'react-apollo';

import client from './apollo';


export default ({children})=> (
    <ApolloProvider client={client}>
        {children}
    </ApolloProvider>);
