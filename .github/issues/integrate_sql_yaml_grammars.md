## Integrate SQL and YAML Grammars into Tree-sitter Sidecar

SQL and YAML grammars are not currently included in the sidecar due to build or runtime issues. This limits language coverage for AST-based extraction.

**Goals:**
- Investigate and resolve build/runtime issues with SQL and YAML grammars.
- Integrate these grammars into the `my-languages.so` build and the sidecar API.
- Add tests and documentation for these new language endpoints.

**Acceptance Criteria:**
- [ ] SQL and YAML grammars are included in the sidecar and available via the API.
- [ ] Any build or compatibility issues are documented and resolved.
- [ ] Example usage and supported `lang_id` values are updated in the README.
- [ ] Tests cover SQL and YAML parsing via the API.
