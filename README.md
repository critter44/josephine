# Josephine

This is a re-implementation of an old Discord bot that my friend group was using to play Vampire: The Masquerade 5th Edition. It used to be a daemonized python process that would behave like a normal user, and had all the limitations you'd expect from that.  Now it's a REST API running on AWS Lambda and keeping its state in DynamoDB.  It might not be the most impressive thing, but it can roll dice for you.  See this fork's parent for information on how to get it running.

### Commands (all working, after a fashion)

- name: rouse
  - description: Perform a rouse check.

- name: roll
  - description: Roll the bones.
  - options:
    - name: dice
     -  description: The dice to roll, in the format Xd[hX] (e.g. 3d, 5dh2).
     -  required: yes

- name: register
  - description: Introduce yourself to Josephine.  She'll remember your character's name and address you by it.
  - options:
    - name: charname
     -  description: The character name to register.
     -  required: yes

- name: unregister
  - description: Ask Josephine to forget your character.

- name: icon
  - description: Set a discord emoji to show up next to your character's name when you use commands.
  - options:
    - name: message
     -  description: The icon to use.  Make sure to include the : on either side of the emoji name (e.g. :crystal_ball:).
     -  required: yes

- name: crit
  - description: Set a discord emoji to show up next to your character's name when you roll a critical success.
  - options:
    - name: message
     -  description: "The icon to use.  Make sure to include the : on either side of the emoji name (e.g. :crystal_ball:)."
     -  required: yes

- name: reset
  - description: Reset your nickname, icon, and emoji to the hardcoded defaults.

- name: remember
  - description: Ask Josephine to remember something for you.
  - options:
    - name: message
     -  description: The message to remember.
     -  required: yes

- name: recall
  - description: Ask Josephine to recall what she remembered for you.

- name: help
  - description: Print help text for this bot's commands.
  - options:
    - name: topic
     -  description: That which befuddles you.
     -  required: no


### To-do
??  Maybe sort out which commands should be guild-specific and which should be global.




