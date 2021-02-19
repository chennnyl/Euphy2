# Euphy2

Euphy2 is a successor to an earlier bot I made, [EuphoriaBot](https://github.com/Spirati/EuphoriaBot) with a slimmer, but more robust feature set as well as a better deployment process. Euphy2, like its predecessor, is designed to help members of Discord servers, particularly those in the trans, nonbinary, and questioning communities try out new names and pronouns quickly and easily.

## Environment setup

Before getting started with a fork of Euphy2, you should create a Discord application from [the developer portal](https://discord.com/developers/applications) and create a bot user via the Bot tab.

Euphy2 is designed to be deployed via Heroku; all you need to do is link your repository to a Heroku app, set the config variable `DBOT_TOKEN` to your bot user's token, and create a worker Dyno based on the Procfile if it's not there already.

## More info

There's a comprehensive listing in progress of Euphy2's features over on [my personal website](https://www.lynnux.org/projects/euphy2/), the source code of which is accessible [here](https://github.com/Spirati/Spirati.github.io).
