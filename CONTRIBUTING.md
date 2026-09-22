# Contributing

Thanks for looking. This repo is the system for using a big pile of agent tools without breaking your agent. It is not a mirror of those tools.

## Suggesting a tool

Open an issue with the **Suggest a tool** template. Include the repo link and what it actually does, in your own words. If you found it in a video, paste the video link too. The toolbox checks the repo's code against what the video claimed before anything gets listed.

A tool won't be listed if it:
- runs itself every session to steer you toward a paid plan
- advertises inside your terminal
- asks the agent to install, update or star something on its own
- has no license, or a license that doesn't allow listing it

## Changing the system

Pull requests are welcome for `bin/`, `my-skills/`, `docs/` and `capabilities.md`.

- Keep the one rule: nothing installs into the agent's live config.
- Never commit a credential, a token in a URL, or a home-folder path. `bin/sync.sh` scans for all three and will refuse the commit.
- Keep third-party code out. Link to it in `manifest.json` with its license and pinned commit.
