# Citadel Search as a Service

Citadel Search provides enterprise search capabilities on demand. You can set up your own search instance, submit your
documents and search among them when needed!

- User documentation [here](http://cern-search.docs.cern.ch/cernsearchdocs/).
- Administration documentation [here](https://cern-search-admin.docs.cern.ch/cernsearch-admin-docs/).


# Local Development options

- **Docker (recommended)**
1. Run `make env MODE=test`
2. Follow [instructions](#tls---how-to-install-certificate) to install certificate.
3. Chrome https://localhost

Read more on the makefile.

- **Docker + Poetry: Read more on the makefile**
1. Run `make local-env MODE=test`
2. Follow [instructions](#tls---how-to-install-certificate) to install certificate.

## [NOTE: CERN ADMINS ONLY]

-  **Docker (connected to cern sso)**

1. Use Teigi to obtain oauth credentials

`tbag show --hg cernsearch oauth_dev-cern-search`

2. Open `.env-staging` and edit `INVENIO_CERN_APP_CREDENTIALS`: replace `secret` with the key you just obtained.

3. Edit /etc/hosts and add line:

`127.0.0.1 dev-cern-search.web.cern.ch`

4. Edit docker-compose.test.yml and add `- .env-staging` under `env_file`:

 ```yaml
    env_file:
      - .env
      - .env-staging
 ```

5. Run `make env-staging MODE=test`
6. Follow [instructions](#tls---how-to-install-certificate) to install certificate.
7. Chrome https://dev-cern-search.web.cern.ch/ (without proxy to cern on)

## TLS - How to install certificate
Install generated certificate `nginx/tls/cern.ch.crt` locally.

For mac:
`sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain nginx/tls/cern.ch.crt`
