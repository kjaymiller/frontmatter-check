# Frontmatter Check

<!--toc:start-->

- [Frontmatter Check](#frontmatter-check)
  - [Overview](#overview)
  - [The Problem](#the-problem)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Configuration Structure](#configuration-structure)
    - [Basic Frontmatter Validation](#basic-frontmatter-validation)
    - [Advanced Field Validation](#advanced-field-validation)
    - [Frontmatter Check as a Python package](#frontmatter-check-as-a-python-package)
    - [Frontmatter Check as a cli](#frontmatter-check-as-a-cli)
    - [Frontmatter Check with Pre-Commit](#frontmatter-check-with-pre-commit)
  - [Development](#development) - [Code of Conduct](#code-of-conduct) - [Contributing](#contributing) - [Security](#security)
  <!--toc:end-->

## Overview

This validation system ensures the presence and format of frontmatter fields in your content files. It ensures that required metadata is present.

## The Problem

[Markdown][markdown] is incredibly flexible (you're reading it now!) and [frontmatter][frontmatter] adds even more flexibility. That said there is no built-in validation and any issues in your configuration can result in websites, docs, and content not appearing as expected.

We can't do much about the validation but we ensure that you include the frontmatter metadata that your application expects.

## Installation

You can install this package via pip:

```shell
pip install https://git@github.com:kjaymiller/frontmatter-check.git
```

## Usage

### Configuration Structure

Let's look at a simple markdown document with some frontmatter

```markdown
---
title: Hello World
---

This is a sample blog post
```

### Basic Frontmatter Validation

The simplest configuration checks for the presence of a required frontmatter field:

```yaml
# FRONTMATTER_CHECK_CONFIG.YAML

title:
```

This configuration ensures that the frontmatter contains a `title` field.

What if our blog occaisionally has guest posts and we want to make sure that an `author` flag is always included. We can add another entry to our config.

```yaml
# FRONTMATTER_CHECK_CONFIG.YAML

title:
author:
```

### Advanced Field Validation

Fields can have additional properties. The `default` flag that supplies a default value when one is missing. The other value is the `warning` flag that will let you know that something you've mentioned should be included is missing.

```yaml
# FRONTMATTER_CHECK_CONFIG.YAML
name:
  default: Jay Miller # Default value if field is missing
  warning: true # Show warning instead of failing pre-commit
```

### Frontmatter Check as a Python package

Using this as a package means that you can validate your frontmatter at runtime.

#### 1. Import the `FrontmatterValidator` object

```python
from frontmatter-check import FrontmatterValidator
```

#### 2. Initialize your `FrontmatterValidator`

This will look for a configuration file. If your file is at `.frontmatter_check_config.yaml` or the filename in the `FRONTMATTER_CHECK_CONFIG` environment variable it will be autodetected (environment variable takes priority). You can also pass in a `config_file` as a `pathlib.Path` as well.

```Python
validator = FrontmatterValidator() # optional config_file = <YOUR_CONFIG.YAML>
```

#### 3. [Optional] Add any additional rules

Rules are kept in the `ruleset` attribute. Rules are a dictionary where the key is the `frontmatter_key` to check with the `default` and `warning` attributes as dictionary values.

```Python
validator.ruleset['newrule'] = {
  # These are required if adding them outside the configuration
  "default": None,
  "warning: False"
}
```

#### 4. Check a frontmatter contained file with `validates`

`validator` looks for a [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path). While normally frontmatter is often paired with markdown. You can pass any filetype. Files with no frontmatter will be skipped.

### Frontmatter Check as a cli

Frontmatter Uses [typer](https://typer.tiangolo.com) to check files.

You can access the cli with the `frontmatter-check` command. You can pass in as many files to check as arguments and the optional config-file (obeys the same rules as in a [python package](#frontmatter-check-as-a-python-package)).

```shell
frontmatter-check <FILE1> <FILE2> <etc> --config-file <OPTIONAL_CONFIG_FILE>
```

You can pass in `frontmatter-check` with no arguments or `frontmatter-check --help` to access the help.

### Frontmatter Check with Pre-Commit

Arguably the most convenient way to use Frontmatter Check is with [pre-commit](https://github.com/pre-commit/pre-commit).

Add the following to your `.pre_commit_config.yaml`:

```yaml
repos:
  - repo: ../frontmatter-check/
    rev: "2024.11.2"
    hooks:
      - id: frontmatter-check
      # - args: [--config-file <OPTIONAL_CONFIG_FILE>]
```

## Development

### Code of Conduct

By contributing to this project, you agree to abide by the [CODE of CONDUCT](https://github.com/kjaymiller/frontmatter-check?tab=coc-ov-file/).

### Contributing

Please checkout [CONTRIBUTING.md](CONTRIBUTING.md) prior to suggesting contributions.

### Security

For Security concerns, check out the [SECURITY.md](SECURITY.md) file.

[markdown]: https://daringfireball.net/projects/markdown/syntax
[frontmatter]: https://frontmatter.codes/docs/markdown
