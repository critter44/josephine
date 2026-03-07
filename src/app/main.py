from email.mime import message
import os
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator

from roll import Roll
from player import Player

STORYTELLER='ren_nerd'
REPLY_STRING=""

REGISTERED_USERS = {}
REGISTERED_USERS['474622152264384512'] = Player('474622152264384512', 'Lucy', 'D', ':crystal_ball:', ':flower_playing_cards:')


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
        user_id = raw_request["member"]["user"]["id"]
        username = raw_request["member"]["user"]["username"]
        if "nick" in raw_request["member"]:
            username = raw_request["member"]["nick"]
        isRegistered = user_id in REGISTERED_USERS.keys()

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
                    message_content = f"You having a rough night, {REGISTERED_USERS[user_id].charname}? We already know each other."
                else:    
                    char_name = data["options"][0]["value"]
                    REGISTERED_USERS[user_id] = Player(user_id, char_name)
                    message_content = f"Nice to meet ya, {char_name}!  I'm sure we'll be pals in no time."

            case "unregister":
                if isRegistered:
                    message_content = f"Yeah, alright.  Slip back into the shadows, {REGISTERED_USERS[user_id].charname}, and I'll forget you ever existed.  Maybe."
                    del REGISTERED_USERS[user_id]
                else:
                    message_content = f"Well, I don't know you in the first place, so okay!  Continuing to have no idea who you are, champ."

            case "icon":
                if isRegistered:
                    new_icon = data["options"][0]["value"]
                    REGISTERED_USERS[user_id].icon = new_icon
                    message_content = f"Got it, {REGISTERED_USERS[user_id].charname}!  I'll use {new_icon} as your icon from now on."
                else:
                    message_content = f"Sorry, but I don't know you well enough!  Register with /register <Name> and maybe I'll let you set an icon for yourself."

            case "crit":
                if isRegistered:
                    new_crit_icon = data["options"][0]["value"]
                    REGISTERED_USERS[user_id].crit_icon = new_crit_icon
                    message_content = f"Got it, {REGISTERED_USERS[user_id].charname}!  I'll use {new_crit_icon} as your critical icon from now on."
                else:
                    message_content = f"Sorry, but I don't know you well enough!  Register with /register <Name> and maybe I'll let you set a critical icon for yourself."

            case "remember":
                message_to_remember = data["options"][0]["value"]
                if isRegistered:
                    REGISTERED_USERS[user_id].note = message_to_remember
                    message_content = f"Sure thing.  I'll remember '{message_to_remember}' for ya."
                else:
                    message_content = f"Sorry, but I don't know you well enough!  Register with /register <Name> and maybe I'll remember things for you."

            case "recall":
                if isRegistered:
                    if REGISTERED_USERS[user_id].note:
                        message_content = f"Let me think... Oh, right!  You asked me to remember '{REGISTERED_USERS[user_id].note}'"
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
                    message_content = f"{REGISTERED_USERS[user_id].icon} {REGISTERED_USERS[user_id].charname} rouses the blood.\nResult: {roll.results[0]}{rouse_result}"
                else:
                    message_content = f"{username} rouses the blood.\nResult: {roll.results[0]}{rouse_result}"
                #message_content = f"Rouse result: {roll.results[0]}\n{rouse_result}"

            case "roll":
                dicestring = data["options"][0]["value"]
                if dicestring.find(' as ') != -1:
                    char_name = dicestring.partition(' as ')[2]
                    REGISTERED_USERS['mook'] = Player(user_id, char_name)
                    roll = Roll((dicestring.partition(' as ')[0]))
                    roll.rollem()
                    if roll.hungry:
                        roll.check_successes(roll.results+roll.hun_results)
                        message_content = f"{REGISTERED_USERS['mook'].charname} rolls {roll.num_successes} successes. {roll.results}{roll.hun_results}."
                        del REGISTERED_USERS['mook']
                    else:
                        roll.check_successes(roll.results)
                        message_content = f"{REGISTERED_USERS['mook'].charname} rolls {roll.num_successes} successes. {roll.results}."
                        del REGISTERED_USERS['mook']
                elif user_id in REGISTERED_USERS.keys():
                    roll = Roll(dicestring)
                    roll.rollem()
                    if roll.hungry:
                        roll.check_successes(roll.results+roll.hun_results)
                        if roll.critical:
                            message_content = f"{REGISTERED_USERS[user_id].icon} {REGISTERED_USERS[user_id].charname} {REGISTERED_USERS[user_id].crit_icon} rolls {roll.num_successes} successes. {roll.results}{roll.hun_results}."
                        else:
                            message_content = f"{REGISTERED_USERS[user_id].icon} {REGISTERED_USERS[user_id].charname} rolls {roll.num_successes} successes. {roll.results}{roll.hun_results}."
                        if roll.hunger_ten and roll.critical:
                            message_content += " :smiling_imp: **MESSY CRITICAL** :smiling_imp:"
                        elif roll.num_successes == 0 and roll.hunger_one:
                            message_content += " :skull: ***beSTiaL faiLuRE*** :skull:"
                    else:
                        roll.check_successes(roll.results)
                        if roll.critical:
                            message_content = f"{REGISTERED_USERS[user_id].icon} {REGISTERED_USERS[user_id].charname} {REGISTERED_USERS[user_id].crit_icon} rolls {roll.num_successes} successes. {roll.results}."
                        else:
                            message_content = f"{REGISTERED_USERS[user_id].icon} {REGISTERED_USERS[user_id].charname} rolls {roll.num_successes} successes. {roll.results}."

                else:
                    REGISTERED_USERS['mook'] = Player(user_id, username)
                    roll = Roll((dicestring.partition(' as ')[0]))
                    roll.rollem()
                    if roll.hungry:
                        roll.check_successes(roll.results+roll.hun_results)
                        message_content = f"{REGISTERED_USERS['mook'].charname} rolls {roll.num_successes} successes. {roll.results}{roll.hun_results}."
                        del REGISTERED_USERS['mook']
                    else:
                        roll.check_successes(roll.results)
                        message_content = f"{REGISTERED_USERS['mook'].charname} rolls {roll.num_successes} successes. {roll.results}."
                        del REGISTERED_USERS['mook']


            case "reset":
                try:
                    REGISTERED_USERS[user_id].reset()
                    message_content = f"Okay, {REGISTERED_USERS[user_id].charname}, you're back to how I remember you!"
                except:
                    message_content = f"Sorry, {REGISTERED_USERS[user_id].charname}, that didn't work! Bummer!"

            case "help":
                if "options" in data:
                    topic = data["options"][0]["value"]
                    match topic:
                        case "roll":
                            message_content = "/roll <X>d[h<X>] [as <Name>]\nRoll X number of 10-sided dice. Add 'hX' after roll to add hunger dice. Add 'as <Name>' to roll for another character.\nExamples:\n/roll 3d (rolls 3d10)\n/roll 7dh2 as Erika (rolls 5 regular dice and 2 hunger dice for Erika)"
                        case "register":
                            message_content = "/register <Name>\nRegister whoever sent the command as <Character Name>.\nJosephine will remember registration from one session to the next."
                        case "icon":
                            message_content = "/icon :<base Discord emoji>:\nSet icon for current registered character. Can only use the base Discord emoji.\nJosephine will remember icon from one session to the next.\nExample:\n,icon :squid:"
                        case "crit":
                            message_content = "/crit :<base Discord emoji>:\nSet crit icon for current registered character. This appears when a critical is rolled. Can only use the base Discord emoji.\nJosephine will remember emoji from one session to the next.\nExample:\n,emoji :crossed_swords:"
                        case "reset":
                            message_content = "/reset\nReset character name, icon, and emoji to the way Josephine prefers them."
                        case "unregister":
                            message_content = "/unregister\nClear any registrations for whoever sent the command."
                        case _:
                            message_content = "Sorry, I don't have help information for that command. Try /help to see a list of commands."
                else:
                    message_content = "/help <command>\nCommands are: roll, register, unregister, icon, emoji, reset"

        response_data = {
            "type": 4,
            "data": {"content": message_content},
        }

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True)
