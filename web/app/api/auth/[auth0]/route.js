import { handleAuth, handleLogin } from '@auth0/nextjs-auth0';

export const GET = handleAuth({
    login: handleLogin({
        authorizationParams: {
            audience: 'https://shredit.com/api',
            // Add the `offline_access` scope to also get a Refresh Token
            scope: 'openid profile email offline_access read write' // or AUTH0_SCOPE
        }
    })
});