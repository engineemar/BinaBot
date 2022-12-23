In order to get the group chat id, do as follows:

Add the Telegram BOT to the group.

Get the list of updates for your BOT:

https://api.telegram.org/bot<YourBOTToken>/getUpdates
Ex:

https://api.telegram.org/bot123456789:jbd78sadvbdy63d37gda37bd8/getUpdates
Look for the "chat" object:
{"update_id":8393,"message":{"message_id":3,"from":{"id":7474,"first_name":"AAA"},"chat":{"id":<group_ID>,"title":""},"date":25497,"new_chat_participant":{"id":71,"first_name":"NAME","username":"YOUR_BOT_NAME"}}}