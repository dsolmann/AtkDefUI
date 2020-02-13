import digitalocean
import random
import rkn_logic
import time
from tok import token

BACKUPS_ENABLED = False
DEF_REGION = "ams3"

manager = digitalocean.Manager(token=token)
possible_images = [
    "ubuntu-16-04-x64"
]

words = [
    "cat",
    "bear",
    "moose",
    "octopus",
    "beetle",
    "ant",
    "bee",
    "penguin"
]


def create_srv(team_name, cloud_config="", is_admin=False):
    keys = manager.get_all_sshkeys()
    droplet = digitalocean.Droplet(
        token=token,
        name=f"{team_name}-{random.choice(words)}",
        image=random.choice(possible_images),
        region=DEF_REGION,
        size_slug='512mb',
        user_data=cloud_config,
        backups=BACKUPS_ENABLED,
        keys=keys if is_admin else []
    )
    droplet.create()
    actions = droplet.get_actions()

    active = False

    while not active:
        for action in actions:
            action.load()
            if action.status == "completed":
                active = True
        time.sleep(2)

    if rkn_logic.is_it_blocked(droplet.ip_address):
        droplet.destroy()
        try:
            return create_srv(team_name)
        except RecursionError:
            return None

    return droplet
