import React from 'react';
import {Redirect} from 'react-router-dom';
import styles from './index.scss';
import gql from 'graphql-tag';
import {Mutation} from 'react-apollo';
import {doLogin} from 'lib/auth';


export default function LoginPage() {
    return <div className={styles.LoginPage}>
        <Mutation mutation={AUTHENTICATE}>
            {(authenticate) => <LoginForm authenticate={authenticate} />}
        </Mutation>
    </div>;
}


const AUTHENTICATE = gql`
    mutation authenticate($email: String!, $password: String!) {
        auth(email: $email, password: $password) {
            ok, token
        }
    }
`;


class LoginForm extends React.Component {
    constructor(...args) {
        super(...args);
        this.state = {
            email: '',
            password: '',
            error: false,
            success: false,
        };
    }

    render() {
        const {authenticate} = this.props;

        if (this.state.success) {
            return <Redirect to="/" />;
        }

        const _onEmailChange = evt=> {
            this.setState({email: evt.target.value});
        };

        const _onPasswordChange = evt=> {
            this.setState({password: evt.target.value});
        };

        const _onSubmit = evt=> {
            evt.preventDefault();

            const {email, password} = this.state;

            if (!email) {
                this.setState({error: 'Email is required'});
                return;
            }

            if (!password) {
                this.setState({error: 'Password is required'});
                return;
            }

            authenticate({variables:  {email, password}})
                .then(({data: {auth: {ok, token}}})=> {
                    if (!ok) {
                        this.setState({password: '', error: 'Bad email or password'});
                        return;
                    }
                    this.setState({success: true, error: ''});
                    doLogin(token);
                });
        };

        const {email, password, error} = this.state;
        return <div className={styles.LoginForm}>
            <form onSubmit={_onSubmit}>
                <div className="form-group">
                    <label htmlFor="input-email">Email address</label>
                    <input type="email" className="form-control" id="input-email"
                           aria-describedby="emailHelp" placeholder="Enter email"
                           onChange={_onEmailChange} value={email} />
                    {/* <small id="emailHelp" className="form-text text-muted">
                        We'll never share your email with anyone else.
                        </small> */}
                </div>
                <div className="form-group">
                    <label htmlFor="input-password">Password</label>
                    <input type="password" className="form-control"
                           id="input-password" placeholder="Password"
                           onChange={_onPasswordChange} value={password} />
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                <button type="submit" className="btn btn-primary">
                    Login
                </button>
            </form>
        </div>;
    }
}
