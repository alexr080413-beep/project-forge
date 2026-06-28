# Release Process

Forge releases should be planned, tested, documented, and reviewable.

## 1. Planning

- Confirm release goals.
- Confirm included milestones, epics, and features.
- Confirm RFC and ADR status.
- Confirm Project Sentinel validation expectations.

## 2. Development

- Implement scoped changes.
- Keep changes modular and reviewable.
- Preserve human review and audit principles.
- Avoid hidden external calls.

## 3. Testing

- Run relevant test subsets.
- Run full test suite when feasible.
- Validate Project Sentinel workflows when applicable.
- Capture screenshots when UI changes.

## 4. Documentation

- Update product docs.
- Update Forge Academy.
- Update task guides.
- Update reference docs.
- Update troubleshooting docs.
- Update architecture docs, ADRs, or RFCs when required.

## 5. Review

- Validate Definition of Done.
- Review security and human-in-the-loop implications.
- Review documentation and release notes.

## 6. Release

- Confirm repository status.
- Confirm tests pass.
- Confirm release notes are ready.

## 7. Tagging

Use semantic version tags when releases begin:

```text
vMAJOR.MINOR.PATCH
```

## 8. GitHub Release

GitHub releases should include:

- Summary.
- Added, changed, fixed, deprecated, removed, and security notes.
- Project Sentinel validation notes.
- Documentation and Academy update notes.

## 9. Academy Update

Every release should confirm whether Forge Academy needs:

- New lessons.
- Updated walkthroughs.
- Updated task guides.
- Updated troubleshooting.
- Updated reference pages.
