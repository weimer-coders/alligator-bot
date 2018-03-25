from flask import Flask
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from jinja2 import Environment, FileSystemLoader
import urllib.request, json, markdown, io, paramiko, requests, re, os, time
from help_message import help_message

# Heroku Variables. You define these in Heroku's dashboard.
token = os.environ.get('SLACK_APP_TOKEN')
verification_token = os.environ.get('SLACK_VERIFICATION_TOKEN')
host = os.environ.get('FTP_HOST')
port = os.environ.get('FTP_PORT')
password = os.environ.get('FTP_PASSWORD')
username = os.environ.get('FTP_USERNAME')

slack = SlackClient(token)

# A python list of photo extensions that will be used to determine if the user uploaded a photo of not.
photo_ext = [".jpeg", ".jpg", ".png"]

# A function that downloads files from Slack.
def download_file(url, local_filename):
	print("Saving " + local_filename)
	headers = {'Authorization': 'Bearer '+ token}
	r = requests.get(url, headers=headers)
	with open(local_filename, 'wb') as f:
		for chunk in r:
			if chunk:
				f.write(chunk)

app = Flask(__name__)

slack_events_adapter = SlackEventAdapter(verification_token, "/slack/events", app)

# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "Help" in message.get('text'):
        channel = message["channel"]
        message = "You need help <@%s>?" % message["user"]
        slack.api_call("chat.postMessage", channel=channel, text=help_message)

@slack_events_adapter.on("file_created")
def handle_file(event_data):
	event = event_data["event"]
	file_id = event.get("file_id")

	# Grabs the private download URL from Slack and stores the name of the file.
	with urllib.request.urlopen("https://slack.com/api/files.info?token=" + token + "&file=" + file_id + "&pretty=1") as url:
		data = json.loads(url.read().decode())
		download_url = data["file"]["url_private_download"]
		file_name = download_url.rsplit('/', 1)[-1]
		download_file(download_url, file_name)

		# If it is a text file, convert it from Markdown to HTML, parse the file name and store it as a title, then throw both of those into template.html.
		try:
			print(file_name)
			input_file = io.open(file_name, mode="r", encoding="utf-8")
			text = input_file.read()
			input_file.close()
			print(text)
			content = markdown.markdown(text)
			print(content)
			final_file_name = file_name.strip('.md') + '.html'
			title = file_name.strip(".md")
			title = re.sub("_", " ", title)
			title = re.sub("-", " ", title)
			file = open(final_file_name, "w+")
			file.write(content)
			file.close()
			print(final_file_name)

			# Template time
			env = Environment(loader=FileSystemLoader('templates'))
			template = env.get_template('template.html')
			output_from_parsed_template = template.render(content=content, title=title)
			with open(final_file_name, "w") as fh:
				fh.write(output_from_parsed_template)
			pass
		except UnicodeDecodeError as e:
			pass

		# Opens a connection with the Alligator's SFTP server. If the file uploaded was a markdown file, send it to the "articles" folder. If it is an image, send it to the "media" folder. Post a message after the file was uploaded. Delete the file after the upload and the message is completed.
		transport = paramiko.Transport((host, port))
		transport.connect(username = username, password = password)
		sftp = paramiko.SFTPClient.from_transport(transport)
		print('Connection Successful')

		# Article/Photo upload handling.
		if file_name.lower().endswith('.md'):
			destination = '/articles/' + final_file_name
			slack.api_call("chat.postMessage", channel="C9D6V65V1", text="Upload successful. Here is the URL: alligator.org/app" + destination )
			sftp.put(final_file_name, destination)
			time.sleep(2)
			os.remove(file_name)
			os.remove(final_file_name)
		elif file_name.lower().endswith(tuple(photo_ext)):
			slack.api_call("chat.postMessage", channel="C9D6V65V1", text="I uploaded your photo :+1:")
			destination = '/articles/media/' + file_name
			sftp.put(file_name, destination)	
			time.sleep(2)
			os.remove(file_name)
		else:
			slack.api_call("chat.postMessage", channel="C9D6V65V1", text="So, uh, this is awkward. I don't actually support that file type. If you're trying to upload an article, make sure it is a markdown (.md) file. If you're trying to upload a photo, make sure it is a .jpg, .jpeg or .png.")

if __name__ == "__main__":
  app.run(port=33507, use_reloader=True)