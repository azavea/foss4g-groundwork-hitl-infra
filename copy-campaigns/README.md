`copy-campaigns`
=====

This repo contains a script that was useful for the FOSS4G workshop. You can ignore it if you're spinning this up after the fact, since you won't need to copy a source project for lots of other people. However, its functionality is documented below.

The `clone_project_to_user.py` script is responsible for copying a source project, its tasks, its parent campaign, and its parent campaign's class mappings to a new user, with
the new user assuming full control of the project. It's not _sharing_ as occurs in the GroundWork app, but creating a project owned by someone else.

To run the script, you'll need a few things:

- an `RF_REFRESH_TOKEN` environment variable -- this must be a refresh token for a user with superuser access, because no one else can create objects owned by another user
- an Auth0 `CLIENT_ID` environment variable -- this should match the client ID for the Raster Foundry production application
- an Auth0 `CLIENT_SECRET` environment variable -- this should match the client secret for the Raster Foundry production application

You'll also need:

- a source project ID -- pick whatever project you want to turn into a template for other users
- an email -- this email will be used to look up a user in Auth0 to find out their user ID

With those you can run:

```bash
python clone_project_to_user.py <source id> <email>
```

To create a campaign for another user.

Python versions
-----

This script has only been tested with Python 3.9 because I only needed it to run
locally. If you want easy sandboxed python environments without the overhead of
Docker, you should try out `nix-shell` -- if you
[install `nix`](https://nixos.org/download.html), you can run `nix-shell` from
this directory and be all set.