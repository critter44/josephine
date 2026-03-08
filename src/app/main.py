import os
import boto3
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator

from roll import Roll
from player import Player

STORYTELLER='critter44'
REPLY_STRING=""

REGISTERED_USERS = {}

# Prepare the DynamoDB client
dynamodb = boto3.resource("dynamodb")
table_name = os.environ["TABLE_NAME"]
table = dynamodb.Table(table_name)

# Get the REGISTERED_USERS from the dynamodb table
response = table.scan()
for item in response["Items"]:
    userid = item["userid"]
    charname = item["charname"]
    nick = item.get("nick", False)
    icon = item.get("icon", False)
    crit = item.get("crit", False)
    note = item.get("note", False)
    REGISTERED_USERS[userid] = Player(userid, charname, nick, icon, crit, note)
    print(f"Loaded character {REGISTERED_USERS[userid].charname} with ID {REGISTERED_USERS[userid].userid} and note {REGISTERED_USERS[userid].note}  from DynamoDB.")

DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app, lifespan = "off")


@app.route("/", methods=["POST"])
async def interactions():
    print(f"👉 Request: {request.json}")
    raw_request = request.json
    return interact(raw_request)


@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):
    if raw_request["type"] == 1:  # PING
        response_data = {"type": 1}  # PONG
    else:
        data = raw_request["data"]
        command_name = data["name"]
        userid = raw_request["member"]["user"]["id"]
        username = raw_request["member"]["user"]["username"]
        print(f"✨User {username} with ID {userid} issued command {command_name}")
        if raw_request["member"]["nick"] is not None:
            username = raw_request["member"]["nick"]
        isRegistered = userid in REGISTERED_USERS.keys()

        match command_name:

            case "hello":
                message_content = "Hello there!"
            case "bye":
                message_content = "Well... bye."
            case "echo":
                original_message = data["options"][0]["value"]
                message_content = f"Echoing: {original_message}"

            case "register":
                if isRegistered:
                    message_content = f"You having a rough night, {REGISTERED_USERS[userid].charname}? We already know each other."
                else:    
                    charname = data["options"][0]["value"]
                    REGISTERED_USERS[userid] = Player(userid, charname)
                    message_content = f"Nice to meet ya, {charname}!  I'm sure we'll be pals in no time."
                    # Put the new registration into DynamoDB table.
                    table.put_item(
                        Item={
                            "userid": userid,
                            "charname": charname,
                        }                    )

            case "unregister":
                if isRegistered:
                    message_content = f"Yeah, alright.  Slip back into the shadows, {REGISTERED_USERS[userid].charname}, and I'll forget you ever existed.  Maybe."
                    del REGISTERED_USERS[userid]
                    # remove the registration from DynamoDB table.
                    table.delete_item(
                        Key={
                            "userid": userid,
                        }                    )
                else:
                    message_content = f"Well, I don't know you in the first place, so okay!  Continuing to have no idea who you are, champ."

            case "icon":
                if isRegistered:
                    new_icon = data["options"][0]["value"]
                    REGISTERED_USERS[userid].icon = new_icon
                    message_content = f"Got it, {REGISTERED_USERS[userid].charname}!  I'll use {new_icon} as your icon from now on."
                    # add the new icon to DynamoDB table.
                    table.update_item(
                        Key={
                            "userid": userid,
                        },
                        UpdateExpression="set icon = :i",
                        ExpressionAttributeValues={
                            ":i": new_icon,
                        },
                    )
                else:
                    message_content = f"Sorry, but I don't know you well enough!  Register with /register <Name> and maybe I'll let you set an icon for yourself."

            case "crit":
                if isRegistered:
                    new_crit_icon = data["options"][0]["value"]
                    REGISTERED_USERS[userid].crit_icon = new_crit_icon
                    message_content = f"Got it, {REGISTERED_USERS[userid].charname}!  I'll use {new_crit_icon} as your critical icon from now on."
                    # add the new crit icon to DynamoDB table.
                    table.update_item(
                        Key={
                            "userid": userid,
                        },
                        UpdateExpression="set crit = :c",
                        ExpressionAttributeValues={
                            ":c": new_crit_icon,
                        },
                    )
                else:
                    message_content = f"Sorry, but I don't know you well enough!  Register with /register <Name> and maybe I'll let you set a critical icon for yourself."

            case "remember":
                message_to_remember = data["options"][0]["value"]
                if isRegistered:
                    REGISTERED_USERS[userid].note = message_to_remember
                    message_content = f"Sure thing.  I'll remember '{message_to_remember}' for ya."
                    # add the new note to DynamoDB table.
                    table.update_item(
                        Key={
                            "userid": userid,
                        },
                        UpdateExpression="set note = :n",
                        ExpressionAttributeValues={
                            ":n": message_to_remember,
                        },
                    )
                else:
                    message_content = f"Sorry, but I don't know you well enough!  Register with /register <Name> and maybe I'll remember things for you."

            case "recall":
                if isRegistered:
                    if REGISTERED_USERS[userid].note:
                        message_content = f"Let me think... Oh, right!  You asked me to remember '{REGISTERED_USERS[userid].note}'"
                    else:
                        message_content = "Did you ask me to remember something?  Rhetorical question.  You didn't."
                else:
                    message_content = f"Sorry, but I don't know you well enough!  Register with /register <Name> and maybe I'll remember things for you."

            case "rouse":
                rouse_result = ""
                roll = Roll("1d")
                roll.rollem()

                if roll.results[0] < 6:
                    rouse_result = "\nThe Beast within stirs. *The hunger grows.*"
                else:
                    rouse_result = "\nThe vitae is theirs to command."                

                if isRegistered:
                    message_content = f"{REGISTERED_USERS[userid].icon} {REGISTERED_USERS[userid].charname} rouses the blood.\nResult: {roll.results[0]}{rouse_result}"
                else:
                    message_content = f"{username} rouses the blood.\nResult: {roll.results[0]}{rouse_result}"
                #message_content = f"Rouse result: {roll.results[0]}\n{rouse_result}"

            case "roll":
                dicestring = data["options"][0]["value"]
                if dicestring.find(' as ') != -1:
                    charname = dicestring.partition(' as ')[2]
                    REGISTERED_USERS['mook'] = Player(userid, charname)
                    roll = Roll((dicestring.partition(' as ')[0]))
                    roll.rollem()
                    if roll.hungry:
                        roll.check_successes(roll.results+roll.hun_results)
                        message_content = f"{REGISTERED_USERS['mook'].charname} rolls {roll.numdice} dice.\n{roll.num_successes} successes. {roll.results}{roll.hun_results}."
                        del REGISTERED_USERS['mook']
                    else:
                        roll.check_successes(roll.results)
                        message_content = f"{REGISTERED_USERS['mook'].charname} rolls {roll.numdice} dice.\n{roll.num_successes} successes. {roll.results}."
                        del REGISTERED_USERS['mook']
                elif userid in REGISTERED_USERS.keys():
                    roll = Roll(dicestring)
                    roll.rollem()
                    if roll.hungry:
                        roll.check_successes(roll.results+roll.hun_results)
                        if roll.critical:
                            message_content = f"{REGISTERED_USERS[userid].icon} {REGISTERED_USERS[userid].charname} {REGISTERED_USERS[userid].crit_icon} rolls {roll.numdice} dice.\n{roll.num_successes} successes. {roll.results}{roll.hun_results}."
                        else:
                            message_content = f"{REGISTERED_USERS[userid].icon} {REGISTERED_USERS[userid].charname} rolls {roll.numdice} dice.\n{roll.num_successes} successes. {roll.results}{roll.hun_results}."
                        if roll.hunger_ten and roll.critical:
                            message_content += " :smiling_imp: **MESSY CRITICAL** :smiling_imp:"
                        elif roll.num_successes == 0 and roll.hunger_one:
                            message_content += " :skull: ***beSTiaL faiLuRE*** :skull:"
                    else:
                        roll.check_successes(roll.results)
                        if roll.critical:
                            message_content = f"{REGISTERED_USERS[userid].icon} {REGISTERED_USERS[userid].charname} {REGISTERED_USERS[userid].crit_icon} rolls {roll.numdice} dice.\n{roll.num_successes} successes. {roll.results}."
                        else:
                            message_content = f"{REGISTERED_USERS[userid].icon} {REGISTERED_USERS[userid].charname} rolls {roll.numdice} dice.\n{roll.num_successes} successes. {roll.results}."

                else:
                    REGISTERED_USERS['mook'] = Player(userid, username)
                    print(f"Created temporary player for unregistered user {username} with ID {userid} to roll as. User {REGISTERED_USERS['mook'].charname} has ID {REGISTERED_USERS['mook'].userid}.")
                    roll = Roll((dicestring.partition(' as ')[0]))
                    roll.rollem()
                    if roll.hungry:
                        roll.check_successes(roll.results+roll.hun_results)
                        message_content = f"{REGISTERED_USERS['mook'].charname} rolls {roll.numdice} dice.\n{roll.num_successes} successes. {roll.results}{roll.hun_results}."
                        del REGISTERED_USERS['mook']
                    else:
                        roll.check_successes(roll.results)
                        message_content = f"{REGISTERED_USERS['mook'].charname} rolls {roll.numdice} dice.\n{roll.num_successes} successes. {roll.results}."
                        del REGISTERED_USERS['mook']


            case "reset":
                try:
                    REGISTERED_USERS[userid].reset()
                    message_content = f"Okay, {REGISTERED_USERS[userid].charname}, you're back to how I remember you!"
                    # reset the registration in DynamoDB table.
                    table.update_item(
                        Key={
                            "userid": userid,
                        },
                        UpdateExpression="set charname = :c, icon = :i, crit = :k",
                        ExpressionAttributeValues={
                            ":c": REGISTERED_USERS[userid].charname,
                            ":i": REGISTERED_USERS[userid].icon,
                            ":k": REGISTERED_USERS[userid].crit_icon,
                        },
                    )
                except:
                    message_content = f"Sorry, {REGISTERED_USERS[userid].charname}, that didn't work! Bummer!"

            case "help":
                if "options" in data:
                    topic = data["options"][0]["value"]
                    match topic:
                        case "rouse":
                            message_content = "/rouse\nPerform a rouse check.  Succeeds on a roll of 6 or higher.  Failure increases your Hunger by one, but the desired effect still resolves.\nExample: `/rouse`"
                        case "roll":
                            message_content = "/roll <X>d[h<X>] [as <Name>]\nRoll X number of 10-sided dice. Add 'hX' after roll to add hunger dice. Add 'as <Name>' to roll for another character.\nExamples:\n`/roll 3d` (rolls 3d10)\n`/roll 7dh2 as Erika` (rolls 5 regular dice and 2 hunger dice for Erika)"
                        case "register":
                            message_content = "/register <Name>\nRegister whoever sent the command as <Character Name>.\nJosephine will remember registration from one session to the next.\nExample:\n`/register Nandor`"
                        case "unregister":
                            message_content = "/unregister\nClear any registrations for whoever sent the command.\nExample: `/unregister`"
                        case "icon":
                            message_content = "/icon :<Discord emoji>:\nSet icon for current registered character.\nJosephine will remember icon from one session to the next.\nExample:\n`/icon :squid:`"
                        case "crit":
                            message_content = "/crit :<Discord emoji>:\nSet crit icon for current registered character. This appears when a critical is rolled.\nJosephine will remember emoji from one session to the next.\nExample:\n`/crit :crossed_swords:`"
                        case "reset":
                            message_content = "/reset\nReset character name, icon, and emoji to the way Josephine prefers them.\nExample: `/reset`"
                        case "remember":
                            message_content = "/remember <message>\nAsk Josephine to remember something for you.  She'll recall it for you later, when asked.\nExample: `/remember I have to pick up Dennis from vampire school.`"
                        case "recall":
                            message_content = "/recall\nAsk Josephine to recall the thing you asked her to remember.\nExample: `/recall`"

                        case _:
                            message_content = "Sorry, I don't have help information for that command. Try /help to see a list of commands."
                else:
                    message_content = "/help <command>\nCommands are: rouse, roll, register, unregister, icon, crit, reset, remember, recall"

        response_data = {
            "type": 4,
            "data": {"content": message_content},
        }

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True)
