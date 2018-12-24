# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.users import FilebasedUserManager, User
import requests
import random
import json
import uuid

class BookedSchedulerUserManager(FilebasedUserManager,
                                 octoprint.plugin.StartupPlugin,
                                 octoprint.plugin.SettingsPlugin,
                                 octoprint.plugin.TemplatePlugin):

	singletonInstance = None

	class __BookedSchedulerUserManager():
		def __init__(self, settings):
			self.settings = settings

		def getSettings(self):
			return self.settings

	def on_after_startup(self):
		BookedSchedulerUserManager.singletonInstance = BookedSchedulerUserManager.__BookedSchedulerUserManager(self._settings)

	def loginBooked(self, username, password):
		try:
			req = requests.post(self.singletonInstance.getSettings().get(["url"]) + "/Web/Services/Authentication/Authenticate", data=json.dumps({"username":username, "password":password}))
			resp = json.loads(req.text)
			if resp["isAuthenticated"]:
				return {"X-Booked-SessionToken": resp["sessionToken"], "X-Booked-UserId": resp["userId"]}
		except:
			self._logger.info("BookedScheduler: Login request failed.")
		return None

	def checkPassword(self, username, password):
		try:
			headers = self.loginBooked(username, password)
			if headers is not None:
				return True
			else:
				self._logger.info("BookedScheduler: username or password is incorrect.")
		except:
			self._logger.error("BookedScheduler: request failed.")
		return FilebasedUserManager.checkPassword(self, username, password)

	def changeUserPassword(self, username, password):
		if FilebasedUserManager.findUser(self, username) is not None:
			return FilebasedUserManager.changeUserPassword(self, username, password)

	def checkPermissions(self, user):
		groups = str(self.singletonInstance.getSettings().get(["groups"]))
		if groups == "":
			return True
		try:
			grouplist = groups.split(",")
			for group in user["groups"]:
				for groupId in grouplist:
					if int(group["id"]) == int(groupId):
						return True
		except:
			pass
		self._logger.info("BookedScheduler: account is inactive due to missing group membership.")
		return False

	def findUser(self, userid=None, apikey=None, session=None):
		local_user = FilebasedUserManager.findUser(self, userid=userid, apikey=apikey, session=session)
		if userid and not local_user:
			headers = self.loginBooked(self.singletonInstance.getSettings().get(["api_user"]), self.singletonInstance.getSettings().get(["api_user_password"]))
			if headers is not None:
				try:
					req = requests.get(self.singletonInstance.getSettings().get(["url"]) + "/Web/Services/Users/", headers=headers)
					users = json.loads(req.text)
					for user in users["users"]:
						if user["userName"] == userid or user["emailAddress"] == userid:
							r = requests.get(self.singletonInstance.getSettings().get(["url"]) + "/Web/Services/Users/" + user["id"], headers=headers)
							u = json.loads(r.text)
							return User(user["userName"], str(uuid.uuid4()), self.checkPermissions(u), ["user"])
					self._logger.info("BookedScheduler: user not found.")
				except:
					self._logger.error("BookedScheduler: error while fetching userlist.")
		else :
			self._logger.debug("Local user found")
			return local_user

	# Softwareupdate hook

	def get_update_information(self):
		return dict(
			auth_bookedscheduler=dict(
				displayName="Auth BookedScheduler",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="soundstorm",
				repo="OctoPrint-BookedScheduler",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/soundstorm/OctoPrint-BookedScheduler/archive/{target_version}.zip"
			)
		)

	# UserManager hook

	def booked_user_factory(components, settings, *args, **kwargs):
		return BookedSchedulerUserManager()

	# SettingsPlugin

	def get_settings_defaults(self):
		return dict(
			url=None,
			api_user="OctoPrintAPI",
			api_user_password="Password",
			groups=None
		)

	def get_settings_restricted_paths(self):
		return dict(
			never=[["booked_api_user"],["booked_api_user_password"]]
		)

	def get_settings_version(self):
		return 1.2

	# TemplatePlugin

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False))
		]


__plugin_name__ = "Auth BookedScheduler"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = BookedSchedulerUserManager()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.users.factory": __plugin_implementation__.booked_user_factory,
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
	}
