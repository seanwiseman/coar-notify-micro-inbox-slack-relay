# coar-notify-micro-inbox-slack-relay

A simple microservice to relay notifications from the COAR Notify Micro Inbox to a target Slack channel.

This will allow senders to send COAR Notify messages to your inbox endpoint, these will be not be stored, 
instead they will be immediately consumed and relayed to a target Slack channel.

The only two endpoints implemented are:

- `OPTIONS /inbox` - Returns the options meta for the inbox.
- `POST /inbox` - to send a notification to the inbox which will be replayed to the Slack channel

The notifications are validated through [coar-notify-validator](https://pypi.org/project/coar-notify-validator/) library.

----

## Environment variables

The app requires the following environment variables to be set:

- `SLACK_CHANNEL` - the channel to send the message to e.g. `#notifications`
- `SLACK_API_TOKEN` - the API token for your Slack app
----

## Setting up Slack

- Create a new App in Slack https://api.slack.com/apps/
- Add a chat:write bot token scope
- Add OAuth token for your workspace
- Add the token to your environment variables
- In Slack create your target channel if required
- Then invite your bot into the channel `/invite @<your-bot-name>`
- You should now be able to send messages to the channel using the bot


The Slack message is sent via the `chat.postMessage` API call. 
See https://api.slack.com/methods/chat.postMessage for more details.

----

## Running the app

### Hosting on [fly.io](https://fly.io)

#### Set up your account and the cli tool:

- Sign up for a fly.io account https://fly.io/app/sign-up
- Download the `flyctl` CLI tool https://fly.io/docs/getting-started/installing-flyctl/
- Login to fly.io
```bash
> fly auth login
```


#### Deploy the app:

**Make sure you are in the project root directory**
- Create a new app:
```bash
> fly launch
```
- When you asked to deploy now, enter `N` to skip the initial deploy, we need to set some secrets first.
- Set the Slack channel environment variable (fly secret):
```bash
> fly secrets set SLACK_CHANNEL=#<you-target-channel> --stage
```

- Set the Slack API token environment variable (fly secret):
```bash
> fly secrets set SLACK_API_TOKEN=<your-api-token> --stage
```

- Now deploy the app:
```bash
> fly deploy
```

After the deployment is complete you should see your external URL:
```bash
Visit your newly deployed app at https://<the-app-name-you-choose>.fly.dev/
```

----