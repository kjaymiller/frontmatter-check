# Frontmatter Check

![Frontmatter Check Logo](./assets/images/frontmatter-check-logo.jpeg)

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
frontmatter-check pages/sample_markdown_file.md

Checking File: pages/sample_markdown_file.md
ERROR - Missing field: 'description'
```

### CLI Advanced Usage Field Validation

#### Modifying check levels

Each rule has two checks:

- `is_missing`: Does the field exist?
- `is_null`: Is the value of the field `null`

If either of the checks fail **FOR ANY RULE**, the command-line will continue to run but will exit after all tests have run. Failures will result in an exit code of `1`.

You can change the level of each check.

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

#### Matching multiple rules

You can have as many patterns as you like but rules will run for each matching pattern.

Since Frontmatter Check will test all matching patterns, there is no difference in order.

> [!NOTE]
> There is a plan to implement a `fail_fast` setting that would make order more important

#### Calling multiple files

You can also pass a directory in and it will match all the markdown (_.md) and text (_.txt) files. You can modify the pattern to check with `--file_pattern`.

```shell
frontmatter-check pages --file-pattern *.md

Checking File: pages/sample_markdown_file.md
ERROR - Missing field: 'description'
```

You can also be more specific and pass in multiple files and folders

```shell
frontmatter-check pages another_file.md --file-pattern pages/blog/*.md

Checking File: pages/sample_markdown_file.md
ERROR - Missing field: 'description'

Checking File: pages/sample_markdown_file.md
```

## Frontmatter Check with Pre-Commit

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

## Frontmatter Check as a Python package

Using this as a package means that you can validate your frontmatter at runtime.

### Simple rule validation letters

For checking for a few fields, you can use the `ValidationRule` and the `RulesetValidator`. This is great when the data being checked it pretty consistent.

A single field is identified in a `ValidationRule`.

You can bundle `ValidationRule`s into a `RulesetValidator`. You can then validate your rules using `RulesetValidator.validate(frontmatter_metadata)`.

> [!NOTE]
> Since you are checking only the metadata of the frontmatter, it is expected that you pass in the metadata and not the file itself.

```python
from frontmatter import ValidationRule, RulesetValidator

title = ValidationRule(field_name="title")
description = ValidationRule(field_name="description")

RulesetValidator(rules=[title, description])
```

### Advances rule validation letters

```python
from frontmatter_check import  PatternRuleset

rule_set = PatternRuleset(field_name="title") # you can also pass
```

There are parallels between the cli and the Python package (because the CLI uses the packages behind the scenes).

This means that you can use the serialized version of your config for patterns and pass it using the `to_dict` classmethod.

```py
ruleset_config = {
        "name": "Docs"
        "pattern": "docs/*.md"
        "rules": [
                {
                    "field_name": "title",
                    "level": "error",
                },
                {
                    "field_name": "author",
                    "level": "error",
                },
        ],
    }

rule_set = PatternRuleset.from_dict(ruleset_config)
```

You can match multiple `PatternRuleset`s to a `FrontmatterPatternMatchCheck` object.

```python
from frontmatter_check import PatternRuleset, FrontmatterPatternMatchCheck

rule_set = PatternRuleset(pattern="**/*.md", field_name="title")
pattern_check = FrontmatterPatternMatchCheck(rule_set, ...) # you can pass in multiple rule_sets
```

You can also pass a yaml file.

```python
from frontmatter_check import FrontmatterPatternMatchCheck

pattern_check = FrontmatterPatternMatchCheck.from_yaml_config(config_file=YAML_CONFIG_FILE_PATH)
```

Check against the pattern.

## Development

### Code of Conduct

By contributing to this project, you agree to abide by the [CODE of CONDUCT](https://github.com/kjaymiller/frontmatter-check?tab=coc-ov-file/).

### Contributing

Please checkout [CONTRIBUTING.md](CONTRIBUTING.md) prior to suggesting contributions.

### Security

For Security concerns, check out the [SECURITY.md](SECURITY.md) file.

[markdown]: https://daringfireball.net/projects/markdown/syntax
[frontmatter]: https://frontmatter.codes/docs/markdown
