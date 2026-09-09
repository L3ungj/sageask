# SageAsk

CLI tool for posting questions to Discord and grading replies.

## Installation

### NixOS (as a package)

**Option 1: From your main flake (recommended)**

Add `sageask` as a local input to your flake:

```nix
# In your flake.nix inputs:
inputs.sageask = {
  url = "path:/home/kazu/dev/sageask";
  inputs.nixpkgs.follows = "nixpkgs";  # share your flake's nixpkgs
};
```

Then add the package to your system or home configuration:

**System-wide (configuration.nix):**
```nix
environment.systemPackages = with pkgs; [
  inputs.sageask.packages.x86_64-linux.default
];
```

**User-level (home-manager in your flake):**
```nix
home-manager.users.your-user = { pkgs, ... }: {
  home.packages = with pkgs; [
    inputs.sageask.packages.x86_64-linux.default
  ];
};
```

**Option 2: From the source directory**

```bash
cd /home/kazu/dev/sageask
nix build
# Run the built binary:
./result/bin/sageask --help

# Or install to your user profile:
nix profile install .
sageask --help
```

**Option 3: Development shell**

```bash
cd /home/kazu/dev/sageask
nix develop
# SAGEASK_DATA=. is set automatically
# Place .env and questions.db in your working directory
```

### Setup

1. Create the data directory and copy the config:
   ```bash
   mkdir -p ~/.local/share/sageask
   cp .env.example ~/.local/share/sageask/.env
   ```

2. Edit `~/.local/share/sageask/.env` with your Discord bot token and channel ID:
   ```bash
   nano ~/.local/share/sageask/.env
   ```

3. Test it works:
   ```bash
   sageask status
   ```

### Overrides

Use `SAGEASK_DATA` to point to a different data directory containing `.env` and `questions.db`:

```bash
SAGEASK_DATA=/path/to/data sageask status
```

## Usage

```bash
# View question bank
sageask status [course_id]

# Post next unanswered question
sageask post

# Post a specific question
sageask post --id <question_id> --course <course_id>

# Check for replies
sageask check
sageask check --question <discord_message_id>

# Grade a reply
sageask grade <mark> <comment>
sageask grade <mark> <comment> --question <discord_message_id>

# Add a new question to the bank
sageask add <part> <course_name> "question text"
```
