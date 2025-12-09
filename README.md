# Gumloop Fork of the Official MCP Python SDK

This fork was created because there were some changes and PRs that had functionality necessary for guMCP, and the official package was not up to date.

The main src/ folder should be rebased from `main` of the official repository from time to time.

## Official Repository

[Official Repository URL](https://github.com/modelcontextprotocol/python-sdk)

## Building and Deploying

### Building the Package

To build the package:

   ```bash
python -m build --verbose --no-isolation
   ```

This will create distribution packages in the `dist/` directory.

### Deploying to Artifact Registry

To deploy to Google Artifact Registry:

```bash
python -m twine upload --repository-url https://us-west1-python.pkg.dev/agenthub-dev/gumloop/ dist/* --skip-existing
```

You'll need appropriate authentication credentials configured for the Artifact Registry repository.
