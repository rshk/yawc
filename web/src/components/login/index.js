import React from 'react';
import {Redirect} from 'react-router-dom';
import styles from './index.scss';


export default function LoginPage() {
    return <div className={styles.LoginPage}>
        <LoginForm />
    </div>;
}


class LoginForm extends React.Component {
    constructor(...args) {
        super(...args);
        this.state = {email: '', password: '', submitted: false};
    }

    render() {
        if (this.state.submitted) {
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
            this.setState({email: '', password: '', submitted: true});
        };
        const {email, password} = this.state;
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
                <button type="submit" className="btn btn-primary">
                    Login
                </button>
            </form>
        </div>;
    }
}
