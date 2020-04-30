import Amplify, { Auth } from 'aws-amplify';

Amplify.configure({
    Auth: {
        region: 'eu-west-1',
        identityPoolId: '',
        userPoolId: 'eu-west-1_mEMQgFWkJ',
        userPoolWebClientId:'3fuov3suubf1331c1qeddt5r4r',
        mandatorySignIn: true,
    }
});

window.AuthFnGlobal = Auth  
