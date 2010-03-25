###
# Copyright (c) 2010, quantumlemur
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import time
import string
import random
import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.schedule as schedule
import supybot.callbacks as callbacks


class Timebomb(callbacks.Plugin):
    """Add the help for "@plugin help Timebomb" here
    This should describe *how* to use this plugin."""
    threaded = True
    
    def __init__(self, irc):
        self.__parent = super(Timebomb, self)
        self.__parent.__init__(irc)
        self.rng = random.Random()
        self.rng.seed()
        self.bombs = {}
        self.lastBomb = ""
        self.talktimes = {}


    def doPrivmsg(self, irc, msg):
        self.talktimes[msg.nick] = time.time()


#    def doJoin(self, irc, msg):
#        self.talktimes[msg.nick] = time.time()


    class Bomb():
        def __init__(self, irc, victim, wires, detonateTime, goodWire, channel, sender):
            self.victim = victim
            self.detonateTime = detonateTime
            self.wires = wires
            self.goodWire = goodWire
            self.active = True
            self.channel = channel
            self.sender = sender
            self.irc = irc
            self.thrown = False
            self.responded = False
            def detonate():
                self.detonate(irc)
            schedule.addEvent(detonate, time.time() + self.detonateTime, 'bomb')
            s = 'stuffs a bomb down %s\'s pants.  The timer is set for %s seconds!  There are %s wires.  They are: %s.' % (self.victim, self.detonateTime, len(wires), utils.str.commaAndify(wires))
            self.irc.queueMsg(ircmsgs.action(self.channel, s))

        def cutwire(self, irc, cutWire):
            self.cutWire = cutWire
            self.responded = True
            if self.goodWire.lower() == self.cutWire.lower():
                self.irc.queueMsg(ircmsgs.privmsg(self.channel, '%s has cut the %s wire!  This has defused the bomb!' % (self.victim, self.cutWire)))
                self.irc.queueMsg(ircmsgs.privmsg(self.channel, 'He then quickly rearms the bomb and throws it back at %s with just seconds on the clock!' % self.sender))
                self.victim = self.sender
                self.thrown = True
                schedule.rescheduleEvent('bomb', time.time() + 5)
            else:
                schedule.removeEvent('bomb')
                self.detonate(irc)

        def duck(self, irc, ducker):
            if self.thrown and ircutils.nickEqual(self.victim, ducker):
                self.irc.queueMsg(ircmsgs.privmsg(self.channel, '%s ducks!  The bomb misses, and explodes harmlessly a few meters away.' % self.victim))
                self.active = False
                self.thrown = False
                schedule.removeEvent('bomb')

        def detonate(self, irc):
            self.active = False
            self.thrown = False
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x031,1.....\x0315,1_.\x0314,1-^^---....,\x0315,1,-_\x031,1.......'))
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x031,1.\x0315,1_--\x0314,1,.\';,`.,\';,.;;`;,.\x0315,1--_\x031,1...'))
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x0315,1<,.\x0314,1;\'`".,;`..,;`*.,\';`.\x0315,1;\'>)\x031,1.'))
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x0315,1I.:;\x0314,1.,`;~,`.;\'`,.;\'`,..\x0315,1\';`I\x031,1.'))
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x031,1.\x0315,1\\_.\x0314,1`\'`..`\';.,`\';,`\';,\x0315,1_../\x031,1..'))
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x031,1....\x0315,1```\x0314,1--. . , ; .--\x0315,1\'\'\'\x031,1.....'))
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x031,1..........\x034,1I\x031,1.\x038,1I\x037,1I\x031,1.\x038,1I\x034,1I\x031,1...........'))
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x031,1..........\x034,1I\x031,1.\x037,1I\x038,1I\x031,1.\x037,1I\x034,1I\x031,1...........'))
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x031,1.......,\x034,1-=\x034,1II\x037,1..I\x034,1.I=-,\x031,1........'))
            self.irc.sendMsg(ircmsgs.privmsg(self.channel, '\x031,1.......\x034,1`-=\x037,1#$\x038,1%&\x037,1%$#\x034,1=-\'\x031,1........'))
            self.irc.queueMsg(ircmsgs.kick(self.channel, self.victim, 'BOOM!'))
            def reinvite():
                if not self.victim in irc.state.channels[self.channel].users:
                    self.irc.queueMsg(ircmsgs.invite(self.victim, self.channel))
            if not self.responded:
                schedule.addEvent(reinvite, time.time()+5)
                
    
    def duck(self, irc, msg, args):
        """takes no arguments

        DUCK!"""
        try:
            if not self.bombs[0].active:
                return
        except KeyError:
            return
        self.bombs[0].duck(irc, msg.nick)
        irc.noReply()
    duck = wrap(duck)

   
    def randombomb(self, irc, msg, args, channel, nicks):
        """takes no arguments

        Bombs a random person in the channel
        """
        try:
            if self.bombs[0].active:
                irc.reply('There\'s already an active bomb, in %s\'s pants!' % self.bombs[0].victim)
                return
        except KeyError:
            pass
        if len(nicks) == 0:
            nicks = list(irc.state.channels[channel].users)
#            items = self.talktimes.iteritems()
#            nicks = []
#            for i in range(0, len(self.talktimes)):
#                try:
#                    item = items.next()
#                    if time.time() - item[1] < 60*60 and item[0] in irc.state.channels[channel].users:
#                        nicks.append(item[0])
#                except StopIteration:
#                    irc.reply('hey quantumlemur, something funny happened... I got a StopIteration exception')
#            if len(nicks) == 1 and nicks[0] == msg.nick:
#                nicks = []
#        if len(nicks) == 0:
#            irc.reply('Well, no one\'s talked in the past hour, so I guess I\'ll just choose someone from the whole channel')
#            nicks = list(irc.state.channels[channel].users)
#        elif len(nicks) == 2:
#            irc.reply('Well, it\'s just been you two talking recently, so I\'m going to go ahead and just bomb someone at random from the whole channel')
#            nicks = list(irc.state.channels[channel].users)
#        irc.reply('These people are eligible: %s' % utils.str.commaAndify(nicks))
        victim = self.rng.choice(nicks)
        while victim == self.lastBomb or victim in self.registryValue('exclusions'):
            victim = self.rng.choice(nicks)
        self.lastBomb = victim
        detonateTime = self.rng.randint(self.registryValue('minTime')*2, self.registryValue('maxTime')*2)
        wireCount = self.rng.randint(self.registryValue('minWires'), self.registryValue('maxWires'))
        if wireCount < 12:
            colors = self.registryValue('shortcolors')
        else:
            colors = self.registryValue('colors')
        wires = self.rng.sample(colors, wireCount)
        goodWire = self.rng.choice(wires)
        self.bombs[0] = self.Bomb(irc, victim, wires, detonateTime, goodWire, channel, msg.nick)
        try:
            irc.noReply()
        except AttributeError:
            pass
    randombomb = wrap(randombomb, ['Channel', ('checkChannelCapability', 'timebombs'), any('NickInChannel')])

 
    def timebomb(self, irc, msg, args, channel, victim):
        """<nick>

        For bombing people!"""
        irc.noReply()
        try:
            if self.bombs[0].active:
                irc.reply('There\'s already an active bomb, in %s\'s pants!' % self.bombs[0].victim)
                return
        except KeyError:
            pass
        if victim == irc.nick:
            irc.reply('You really expect me to bomb myself?   Stuffing explosives into my own pants isn\'t exactly my idea of fun.')
            return
        victim = string.lower(victim)
        found = False
        for nick in list(irc.state.channels[channel].users):
            if victim == string.lower(nick):
                victim = nick
                found = True
        if not found:
            irc.reply('Error: nick not found.')
            return
        detonateTime = self.rng.randint(self.registryValue('minTime'), self.registryValue('maxTime'))
        wireCount = self.rng.randint(self.registryValue('minWires'), self.registryValue('maxWires'))
        if wireCount < 12:
            colors = self.registryValue('shortcolors')
        else:
            colors = self.registryValue('colors')
        wires = self.rng.sample(colors, wireCount)
        goodWire = self.rng.choice(wires)
        self.bombs[0] = self.Bomb(irc, victim, wires, detonateTime, goodWire, channel, msg.nick)
    timebomb = wrap(timebomb, ['Channel', ('checkChannelCapability', 'timebombs'), 'somethingWithoutSpaces'])


    def cutwire(self, irc, msg, args, cutWire):
        """<colored wire>

        Will cut the given wire if you've been timebombed."""
        try:
            if not self.bombs[0].active:
                return
            if not ircutils.nickEqual(self.bombs[0].victim, msg.nick):
                irc.reply('You can\'t cut the wire on someone else\'s bomb!')
                return
        except KeyError:
            pass
        self.bombs[0].cutwire(irc, cutWire)
        irc.noReply()
    cutwire = wrap(cutwire, ['something'])


    def detonate(self, irc, msg, args, channel):
        """Takes no arguments

        Detonates the active bomb."""
        if self.bombs[0].active:
            schedule.rescheduleEvent('bomb', time.time())
        irc.noReply()
    detonate = wrap(detonate, [('checkChannelCapability', 'op')])


Class = Timebomb


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79: