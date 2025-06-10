## Automate and Document Building my-languages.so for Tree-sitter Sidecar

Currently, building the `my-languages.so` file for the tree-sitter API sidecar is a manual and brittle process. This makes it hard to add new grammars or update existing ones, and is a barrier for contributors and CI/CD automation.

**Goals:**
- Provide a robust, documented, and repeatable process for building new `my-languages.so` files.
- Make it easy to add/update grammars and regenerate the shared library.
- Optionally, provide a script or Docker-based build process for cross-platform compatibility.

**Acceptance Criteria:**
- [ ] A documented process (in README or a dedicated doc) for building `my-languages.so`.
- [ ] (Optional) A script or Dockerfile that builds the `.so` file from a list of grammars.
- [ ] Clear instructions for updating the sidecar Docker build context with the new `.so` file.
- [ ] CI/CD can be extended to build/test new grammars if desired.
