## Issue: Automate and Document Building New my-languages.so Files for Tree-sitter Sidecar

### Problem
Currently, building the `my-languages.so` file for the tree-sitter API sidecar is a manual and brittle process. This makes it hard to add new grammars or update existing ones, and is a barrier for contributors and CI/CD automation.

### Goals
- Provide a robust, documented, and repeatable process for building new `my-languages.so` files.
- Make it easy to add/update grammars and regenerate the shared library.
- Optionally, provide a script or Docker-based build process for cross-platform compatibility.

### Acceptance Criteria
- [ ] A documented process (in README or a dedicated doc) for building `my-languages.so`.
- [ ] (Optional) A script or Dockerfile that builds the `.so` file from a list of grammars.
- [ ] Clear instructions for updating the sidecar Docker build context with the new `.so` file.
- [ ] CI/CD can be extended to build/test new grammars if desired.

---

## Issue: Integrate SQL and YAML Grammars into Tree-sitter Sidecar

### Problem
SQL and YAML grammars are not currently included in the sidecar due to build or runtime issues. This limits language coverage for AST-based extraction.

### Goals
- Investigate and resolve build/runtime issues with SQL and YAML grammars.
- Integrate these grammars into the `my-languages.so` build and the sidecar API.
- Add tests and documentation for these new language endpoints.

### Acceptance Criteria
- [ ] SQL and YAML grammars are included in the sidecar and available via the API.
- [ ] Any build or compatibility issues are documented and resolved.
- [ ] Example usage and supported `lang_id` values are updated in the README.
- [ ] Tests cover SQL and YAML parsing via the API.
