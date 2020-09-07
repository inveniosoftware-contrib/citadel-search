# Citadel Search as a Service

Citadel Search provides enterprise search capabilities on demand. You can set up your own search instance, submit your
documents and search among them when needed!

- User documentation [here](http://cern-search.docs.cern.ch/cernsearchdocs/).
- Administration documentation [here](https://cern-search-admin.docs.cern.ch/cernsearch-admin-docs/).


# Local Development options

## Docker (recommended)
1. Run `make env MODE=test`
2. Follow [instructions](#tls---how-to-install-certificate) to install certificate.
3. Chrome https:://localhost

Read more on the makefile.

## Docker (connected to cern sso)

1. Edit /etc/hosts and add line:

`127.0.0.1 dev-cern-search.web.cern.ch`

2. Edit docker-compose.test.yml and add `- .env-staging` under:

 ```
    env_file:
      - .env
 ```

3. Run `make env-staging MODE=test`
4. Follow [instructions](#tls---how-to-install-certificate) to install certificate.
5. Chrome https://dev-cern-search.web.cern.ch/ (without proxy to cern on)

 ## docker + pipenv: Read more on the makefile
1. Run `make local-env MODE=test`
2. Follow [instructions](#tls---how-to-install-certificate) to install certificate.

## TLS - How to install certificate
Install generated certificate `nginx/tls/cern.ch.crt` locally.

For mac:
`sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain nginx/tls/cern.ch.crt`
