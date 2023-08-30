# Contributing

If you wish to contribute to this project, feel free to fork the repository and submit a pull request.

## Setup

To get ready to work on the codebase, please make sure to have [NodeJS](https://nodejs.org/en/) & [npm](https://npmjs.com) installed.  Then, run the following command to install the dependencies:

```bash
npm install
```

This will install Husky (for git commit hooks), which will update the README files per chart and make sure all chart dependencies are up to date pre-commit.  We are using the [Bitnami README generator for Helm](https://github.com/bitnami-labs/readme-generator-for-helm) to update our chart README files.

Sometimes you might still need to amend the generated README files manually to the commit.
