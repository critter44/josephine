class Player:

    def __init__ (self, userid, charname, nick=False, icon=False, emoji=False):
        self.userid = userid
        self.charname = charname
        self.proc = False
        if nick:
            self.nick = nick
        if icon:
            self.icon = icon
        else:
            self.icon = ":bust_in_silhouette:"
        if emoji:
            self.emoji = emoji
        else:
            self.emoji = ":metal:"
        self.note = ""
    #@snoop
    def reset(self):
        # this is so people can easily reset their nickname, icon, and emoji to sane defaults.
        DEFAULT_USERS = {}
        DEFAULT_USERS['474622152264384512'] = Player('474622152264384512D', 'Lucy', 'D', ':crystal_ball:', ':flower_playing_cards:')
        DEFAULT_USERS['A Real Life Cat'] = Player('A Real Life Cat', 'Yas', 'Sophia', ':mag:', ':stuck_out_tongue_winking_eye:')
        DEFAULT_USERS['Uuneya'] = Player('Uuneya', 'Meredith', 'Uuneya', ':wolf:', ':nail_care:')
        DEFAULT_USERS['ren_nerd'] = Player('ren_nerd', 'Storyteller', 'Tiffany', ':book:', ':sparkles:')

        self.charname = DEFAULT_USERS[self.userid].charname
        self.icon = DEFAULT_USERS[self.userid].icon
        self.emoji = DEFAULT_USERS[self.userid].emoji
