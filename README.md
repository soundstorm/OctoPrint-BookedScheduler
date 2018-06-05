# OctoPrint Booked Scheduler Auth Plugin

Authorization via Booked Scheduler for OctoPrint

## Usage

You need a [Booked Scheduler installation](https://sourceforge.net/projects/phpscheduleit/) installation with a (super-)user that can access all users (and their groups).

The OctoPrint settings interface allows the configuration via the frontend; you can also configure it directly in the config.yaml:

```yaml
plugins:
  auth_bookedscheduler:
    _config_version: 1
    api_user: user
    api_user_password: Password
    groups: '1,2,3'
    url: https://foo.bar/booked
```

`groups` can contain several groupIds seperated by commas, if any of these matches the user can login. Otherwise a "user is inactive" warning will be shown. Leave empty if all users of your instance should be allowed to access OctoPrint.

## Installation

`pip install https://github.com/soundstorm/OctoPrint-BookedScheduler/archive/master.zip`

Or use the Pluginmanager of OctoPrint 