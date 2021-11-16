# Pascal

Pascal is a bot that can handle youtube audio streaming over Discord, and temp channels. 

Users can ask for music using `!music <something>`. They can directly set the URL of a YouTube vidéo, or keywords that will be sent to the search engine of YouTube. 

Users can be temporarily banned automatically for bad behavior (ex. using the command without being in the voice channel). 

## Building (Docker)

```bash
cat env.sample >.env
# please fill the fields of the .env file
docker build -t pascal .
```

## Running (Docker)

```bash
docker run --env-file=.env pascal
```

### Env var

- `DISCORD_TOKEN` : the Discord API token
- `YOUTUBE_TOKEN` : the YouTube API token (so that your user can search for music, download is done through youtube-dl)
- `VOICE_CHANNEL` : the ID of the targeted voice channel
- `TEXT_CHANNEL` : the ID of the channel where users can ask for music
- `BANNED_ROLE` : the ID of the role that cannot use the music feature of the bot
- `ADMIN_ROLE` : the ID of the role that can do admin actions for the musical features of this bot
- `TEMP_CHANNEL` : the ID of the channel that would have all its messages suppressed after a certain amount of time (pinned messages excluded)
- `MAX_TEMP_MESSAGE_DURATION` : duration of the previous feature, in seconds