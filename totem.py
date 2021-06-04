# MIT License
#
# Copyright (c) 2021 Ferhat Geçdoğan All Rights Reserved.
# Distributed under the terms of the MIT License.
#
# Totem[dot]py - Python3 implementation of Totem (lib, exec)
#
# github.com/ferhatgec/totem
# github.com/ferhatgec/totem.py
# github.com/ferhatgec/freud

import os
import sys
import termios
import tty

escape = 27
up = 65
down = 66


class Totem:
    def __init__(self, filename: str):
        self.file_data: str = ''
        self.__up__: int = 0
        self.__down__: int = 0
        self.__full_length__: int = 0
        with open(filename) as __file_data__:
            for line in __file_data__:
                self.file_data += f'{line}'
                self.__down__ += 1
        self.__full_length__ = self.__down__
        self.__w__, self.__h__ = Totem.get_terminal_size()
        self.old__ = termios.tcgetattr(sys.stdin.fileno())
        self.new__ = termios.tcgetattr(sys.stdin.fileno())

    def init_buffer(self):
        self.clear()
        self.to_up()
        self.__down__ = (self.__h__ / 3.95)
        self.__from__(False)
        self.disable_cursor()

        self.new__[3] = self.new__[3] & ~termios.ECHO
        try:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, self.new__)
            while True:
                ch = self.getchar()

                if ch.lower() == 'q':
                    break

                ch = self.getchar()
                ch = self.getchar()
                if ch == 'A':
                    if 1 <= self.__up__:
                        self.__up__ -= 1
                        self.__down__ -= 1
                        self.__from__(False)
                        continue
                if ch == 'B':
                    if self.__down__ < self.__full_length__:
                        self.__down__ += 1
                        self.__up__ += 1
                        self.__from__(False)
                        continue
        finally:
            self.enable_cursor()
            self.clear()
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, self.old__)

    def __from__(self, is_up: bool):
        i = 0
        __new: str = ''
        if is_up:
            for line in self.file_data.splitlines():
                if i >= self.__up__:
                    __new += f'{line}\n'

            i += 1
        else:
            for line in self.file_data.splitlines():
                if i < self.__down__:
                    __new += f'{line}\n'

                i += 1

        self.clear()
        print(end=__new)
        self.up_to(self.__up__)

    @staticmethod
    def getchar():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    @staticmethod
    def refresh():
        print(end='\x1b[2J')

    @staticmethod
    def clear():
        Totem.refresh()
        print(end='\x1b[H')

    @staticmethod
    def to_up():
        print(end='\x1b[0A')

    @staticmethod
    def up_to(n: int):
        print(end='\x1b[' + str(n) + 'A')

    @staticmethod
    def disable_cursor():
        print(end='\x1b[?25l')

    @staticmethod
    def enable_cursor():
        print(end='\x1b[?25h')

    @staticmethod
    def get_terminal_size() -> (int, int):
        from fcntl import ioctl
        from struct import pack, unpack

        with open(os.ctermid(), 'r') as fd:
            packed = ioctl(fd, termios.TIOCGWINSZ, pack('HHHH', 0, 0, 0, 0))
            rows, cols, h_pixels, v_pixels = unpack('HHHH', packed)

        return rows, cols


if len(sys.argv) < 2:
    exit(1)

init = Totem(sys.argv[len(sys.argv) - 1])

init.init_buffer()
