class Player:

    def __init__ (self, userid, charname, nick=False, icon=False, crit=False, note=False):
        self.userid = userid
        self.charname = charname
        self.proc = False
        if nick:
            self.nick = nick
        if icon:
            self.icon = icon
        else:
            self.icon = ":bust_in_silhouette:"
        if crit:
            self.crit_icon = crit
        else:
            self.crit_icon = ":metal:"
        if note:
            self.note = note
        else:
            self.note = ""
    #@snoop
    def reset(self):
        # this is so people can easily reset their nickname, icon, and emoji to sane defaults.
        DEFAULT_USERS = {}
        DEFAULT_USERS['474622152264384512'] = Player('474622152264384512D', 'Lucy', 'D', ':crystal_ball:', ':flower_playing_cards:')
        DEFAULT_USERS['160191749757599745'] = Player('160191749757599745', 'Yas', 'Sophia', ':mag:', ':stuck_out_tongue_winking_eye:')
        DEFAULT_USERS['222137245853941763'] = Player('222137245853941763', 'Uuneya', 'Uuneya', ':wolf:', ':nail_care:')
        DEFAULT_USERS['399831312019619840'] = Player('399831312019619840', 'Storyteller', 'Tiffany', ':book:', ':sparkles:')

        self.charname = DEFAULT_USERS[self.userid].charname
        self.icon = DEFAULT_USERS[self.userid].icon
        self.emoji = DEFAULT_USERS[self.userid].emoji
