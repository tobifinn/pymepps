# -*- coding: utf-8 -*-
"""
Created on 17.05.16
Created for pyMepps

@author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de

    Copyright (C) {2016}  {Tobias Sebastian Finn}

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# System modules
import abc
from abc import abstractmethod
import urllib.request
import urllib.parse
import urllib.error
import shutil
import shlex
from subprocess import Popen, PIPE

# External modules
import paramiko

# Internal modules
from .file import File

__version__ = "0.1"


class ServerClient(object):
    __meta__ = abc.ABCMeta

    def __init__(self):
        """
        This class representing a common server.
        Args:
            base_path (str): Server base path (e.g. myserver/home/name/data/).
        """
        self.server = None

    def close(self):
        self.server = None

    @abstractmethod
    def connect(self, server, username=None, password=None):
        pass

    @abstractmethod
    def getFile(self, file_path, save_path):
        """
        Method to download the file from the server and to save it to save_path.
        Args:
            file_path (str): File path on the server.
            save_path (str): Path where the file should be saved.

        Returns:
            success (bool): If the download was successful.
            error (str): If the download wasn't successful,
                there will be an error.
        """
        pass


class InternetClient(ServerClient):
    """
    This class represents an internet server.
    """
    def connect(self, server, username=None, password=None):
        self.server = server

    def getFile(self, file_path, save_path):
        file_path = urllib.parse.urljoin(self.server, file_path)
        save_path = File(save_path)
        save_path.create_dir()
        try:
            with urllib.request.urlopen(file_path) as response, \
                    save_path.open() as out_file:
                try:
                    shutil.copyfileobj(response, out_file)
                    if save_path.available:
                        return True, None
                    else:
                        return False, response
                except:
                    return False, response
        except urllib.error.HTTPError:
            return False, 404


class Samba(ServerClient):
    """
    This class represents a samba server
    """
    def __init__(self):
        self.connected = False
        self.server = ["smbclient", "-u", None, None, "-c"]

    def connect(self, server, user=None, password=None):
        self.connected = True
        self.server[2] = "{0:s}%{1:s}".format(user, password)
        self.server[3] = "{0:s}".format(server)

    def getCommand(self, command):
        if self.connected:
            server = self.server.append(command)
            return " ".join(server)
        else:
            raise ValueError("Please connect firstly to a server!")

    def getFile(self, file_path, save_path):
        if self.connected:
            cmd_chain = self.server.append('"get {0:s} {1:s}"'.format(file_path, save_path))
            connection = Popen(cmd_chain, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            if return_code == 0:
                return True, 0
            else:
                return False, return_code
        else:
            return False, "Please connect firstly to a server!"


class SSH(Server):
    def __init__(self, servers=["",], login={"user": None, "pass": None}):
        if isinstance(servers, str):
            self.servers = [servers,]
        else:
            self.servers = servers
        self.login = login
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())

    def command(self, command):
        return_chain = ""
        for server in self.servers:
            try:
                with self.ssh.connect(server, username=self.login["user"], password=self.login["pass"]) as ssh:
                    stdin, stdout, stderr = ssh.exec_command(command)
                return_chain +=
            except Exception as e:
                return_chain += e
        return False, "The command didn't worked"

    def getFile(self, file_path, save_path):
        for server in self.servers:
            ssh_cmd_chain = "scp" + self._server_connect(
                server) + ":/{0:s} {1:s}".format(file_path, save_path)
            ssg_cmd = shlex.split(ssh_cmd_chain)
            return_code = call(ssg_cmd)
            if return_code == 0:
                return True, 0
        return False, "didn't worked"
