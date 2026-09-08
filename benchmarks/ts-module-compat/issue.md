# Incident

The service was migrated to native ESM. `package.json` and source imports are ESM-correct, but TypeScript now fails with an incompatible `module`/`moduleResolution` combination.

Repair the compiler configuration without reverting the package to CommonJS or weakening type checking.
