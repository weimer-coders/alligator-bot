# Alligator Bot

Alligator Bot is a Slack bot that serves as a mini-CMS for the [Independent Florida Alligator](http://www.alligator.org/), a student-run newspaper in Gainesville, Florida. Editors or reporters drop a Markdown file into a designated Slack channel, have it converted to HTML and thrown into an HTML template, and have it uploaded to the Alligator's SFTP server. The bot accepts images as well. 

## How was the Bot Made?

Alligator bot uses Slack's [python developer kit](https://github.com/slackapi/python-slackclient) to connect to the Alligator's slack and Slack's [python slack events API](https://github.com/slackapi/python-slack-events-api) to listen for any file, photos or messages that is intended for Alligator bot.

As mentioned above, the bot converts markdown to HTML. Alligator bot uses [Python Markdown](https://python-markdown.github.io/) to do this conversion. It uses [Jinja](http://jinja.pocoo.org/) to throw that converted file into a [template](https://github.com/weimer-coders/alligator-bot/blob/master/templates/template.html) that includes all the necessary head elements to connect to style sheets for the story to look good. 

After the file is converted and formatted with a template, it needs to be uploaded to the Alligator's SFTP server. To do this, we used [Paramiko](http://www.paramiko.org/). Once completed, the bot copies the destination folder's name and appends it to the end of "alligator.org/". The bot takes this formatted URL and posts a message to the editor or reporter so that they see that everything worked.