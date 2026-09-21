# SageAsk

CLI tool for posting questions to Discord and grading replies.

## Installation

### NixOS (as a package)

**Option 1: From your main flake (recommended)**

Add `sageask` as a local input to your flake:

```nix
# In your flake.nix inputs:
sageask = {
  url = "github:L3ungj/sageask";
  inputs.nixpkgs.follows = "nixpkgs";
};
```

Then add the package to your system or home configuration:

**System-wide (configuration.nix):**
```nix
environment.systemPackages = with pkgs; [
  inputs.sageask.packages.${pkgs.stdenv.hostPlatform.system}.default
];
```

**User-level (home-manager in your flake):**
```nix
home-manager.users.your-user = { pkgs, ... }: {
  home.packages = with pkgs; [
    inputs.sageask.packages.${pkgs.stdenv.hostPlatform.system}.default
  ];
};
```

**Option 2: From the source directory**

```bash
nix build
# Run the built binary:
./result/bin/sageask --help

# Or install to your user profile:
nix profile install .
sageask --help
```

**Option 3: Development shell (Recommend for testing)**

```bash
nix develop
# SAGEASK_DATA=. is set automatically
# Place .env and questions.db in your working directory
# Run PYTHONPATH=src python3 -m sageask --help
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

`sageask --help`:
```
usage: sageask [-h] {status,post,check,grade,add,list} ...

SageAsk: post questions to Discord, check replies

positional arguments:
  {status,post,check,grade,add,list}
    status              Show question bank status
    post                Post next unanswered (or specified) question
    check               Check for user's reply
    grade               Grade a student's reply
    add                 Add a course, topic, or question
    list                List courses, topics, or questions

options:
  -h, --help            show this help message and exit
```
