# Frontmatter Check

![Frontmatter Check Logo](./assets/images/frontmatter-check-logo.jpeg)

<!--toc:start-->

- [Frontmatter Check](#frontmatter-check)
  - [Overview](#overview)
  - [The Problem](#the-problem)
  - [Installation](#installation)
  - [Using the CLI](#using-the-cli)
    - [Configuration Structure](#configuration-structure)
    - [Check your frontmatter files](#check-your-frontmatter-files)
    - [Advanced Field Validation](#advanced-field-validation)
    - [Matching multiple rules](#matching-multiple-rules)
    - [Frontmatter Check as a Python package](#frontmatter-check-as-a-python-package)
      - [1. Import the `FrontmatterValidator` object](#1-import-the-frontmattervalidator-object)
      - [2. Initialize your `FrontmatterValidator`](#2-initialize-your-frontmattervalidator)
      - [3. [Optional] Add any additional rules](#3-optional-add-any-additional-rules)
    - [Frontmatter Check with Pre-Commit](#frontmatter-check-with-pre-commit)
      - [4. Check a frontmatter contained file with `validates`](#4-check-a-frontmatter-contained-file-with-validates)
    - [Frontmatter Check as a cli](#frontmatter-check-as-a-cli)
  - [Development](#development) - [Code of Conduct](#code-of-conduct) - [Contributing](#contributing) - [Security](#security)
  <!--toc:end-->

## Overview

It ensures that required metadata is present.

## The Problem

[Markdown][markdown] is incredibly flexible (you're reading it now!) and [frontmatter][frontmatter] adds even more flexibility. That said there is no built-in validation and any issues in your configuration can result in websites, docs, and content not appearing as expected.

We can't do much about the validation but we ensure that you include the frontmatter metadata that your application expects.

## Installation

You can install this package via pip:

```shell
pip install --pre https://git@github.com:kjaymiller/frontmatter-check.git
```

## Using the CLI

The most common usage for this tool would be to use the CLI.

Let's look at a simple markdown document with some frontmatter

```markdown
---
title: Hello World
---

This is a sample blog post
```

### Configuration Structure

To use Frontmatter Check, you need to pass in a configuration file. This is a yaml file that you can point to directly with your:

The simplest configuration checks is to create a pattern:

```yaml
# .frontmatter_check.YAML

# Pattern-specific rules
patterns:
  - name: "Global Defaults"
    pattern: "**/*.md" # match ALL `.md` files
    rules:
      - field_name: title
      - field_name: description
```

The `pattern` field will be checked against the file path. Paths are relative to where the CLI is ran.

- `*` wildcard
- `**/` recursive wildcard

The example above will pass for ALL markdown files.

### Check your frontmatter files

Test a frontmatter file running the command:

```shell
frontmatter-check <FILE>
```

You can also pass a directory in and it will match all the markdown (_.md) and text (_.txt) files. You can modify the pattern to check with `--file_pattern`.

```shell
frontmatter-check <FOLDER> --file-pattern pages/blog/*.md
```

You can also be more specific and pass in multiple files

```shell
frontmatter-check <FILE1> <FILE2> --file-pattern pages/blog/*.md
```

You can also mix and match Files and Folders.

```shell
frontmatter-check <FILE1> <FOLDER> <FILE2> --file-pattern pages/blog/*.md
```

### Advanced Field Validation

Each rule has two checks:

- `is_missing`: Does the field exist?
- `is_null`: Is the value of the field `null`

If either of the checks fail **FOR ANY RULE**, the command-line will continue to run but will exit after all tests have run. Failures will result in an exit code of `1`.

You can also change the level of the checks.

If you set the value of a check to `warn`. The Error message will still appear but the check will not affect the exit code.

Setting a check to `skip` will suppress the message and not affect the exit code.

```yaml
# .frontmatter_check.YAML

# Pattern-specific rules
patterns:
  - name: "Global Defaults"
    pattern: "**/*.md" # Careful this will hit ALL markdown files
    rules:
      - field_name: title
        is_missing: skip # do not raise an error
      - field_name: description
        is_null: warn # show error but do not fail the check
```

### Matching multiple rules

You can have as many patterns as you like but rules will run for each matching pattern.

Since Frontmatter Check will test all matching patterns, there is no difference in order.

> [!NOTE]
> There is a plan to implement a `fail_fast` setting that would make order more important

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

You can pass in `frontmatter-check` with no arguments or `frontmatter-check --help` to access the help.

### Frontmatter Check with Pre-Commit

Arguably the most convenient way to use Frontmatter Check is with [pre-commit](https://github.com/pre-commit/pre-commit).

Add the following to your `.pre_commit_config.yaml`:

```yaml
repos:
  - repo: https://github.com/kjaymiller/frontmatter-check
    rev: "2025.1.1a2"
    hooks:
      - id: frontmatter-check
      # - args: [--config-file <OPTIONAL_CONFIG_FILE>]
```

#### 4. Check a frontmatter contained file with `validates`

`validator` looks for a [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path). While normally frontmatter is often paired with markdown. You can pass any filetype. Files with no frontmatter will be skipped.

### Frontmatter Check as a cli

## Development

### Code of Conduct

By contributing to this project, you agree to abide by the [CODE of CONDUCT](https://github.com/kjaymiller/frontmatter-check?tab=coc-ov-file/).

### Contributing

Please checkout [CONTRIBUTING.md](CONTRIBUTING.md) prior to suggesting contributions.

### Security

For Security concerns, check out the [SECURITY.md](SECURITY.md) file.

[markdown]: https://daringfireball.net/projects/markdown/syntax
[frontmatter]: https://frontmatter.codes/docs/markdown
