# redditcrossposter
A bot to crosspost using reddit's native crossposting feature from a source sub to a destination sub
(May add option to source from multiple later)
Complete with a check of whether the bot has seen and crossposted content already tracked with a local sqlite3 db file.

Usage:

1. Visit https://www.reddit.com/prefs/apps on your account of choice and create an application, select "Script" for your type.
2. Run the script once for it to copy main.ini.default for you automatically.
3. Populate main.ini (Actually json) with the account's username and password as well as the client_id and client_secret of this newly defined application.
4. Don't forget to also define your subreddit_source and subreddit_dest above this section.
5. Fire away, set up a cronjob or systemd service timer to call this script every so often.

Known gotchas:

1. "This community doesn't allow videos"

You may run into this if your bot is not an approved submitter or "allow video uploads" is unchecked in your subreddit settings. Otherwise you can add them as a moderator to your community while it's trying to crosspost videos there.
