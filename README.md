# accounting_system
A project for M122 TBZ that handles some simple automated accounting tasks

Template for config:
```toml
# TOML config for accounting system M122

title = "Accounting system"

[client_server]
address = 'server.com' # REQUIRED
user = 'anonymous' # REQUIRED
pw = 'anonymous' # REQUIRED

[accounting_server]
address = 'server.com' # REQUIRED
user = 'anonymous' # REQUIRED
pw = 'anonymous' # REQUIRED

[data]
email_address = 'foo@bar.com' # REQUIRED

[email]
[email.sender]
    email = 'foo@bar.com' # REQUIRED
    pw = 'secretbaz' # REQUIRED
[email.sender.smtp]
    server = 'smtp.mail.com' # REQUIRED
    port = 587 # REQUIRED
```