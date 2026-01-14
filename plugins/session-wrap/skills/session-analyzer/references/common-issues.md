# Common Issues and Troubleshooting

Known issues when analyzing Claude Code sessions and how to diagnose them.

---

## Session File Issues

### Issue: Debug Log Not Found

**Symptom**: `~/.claude/debug/{sessionId}.txt` doesn't exist

**Possible Causes**:
1. Session was too old and debug logs were cleaned up
2. Debug logging was disabled
3. Session ID is incorrect

**Workaround**:
- Use the main session log (`.jsonl`) for limited analysis
- Main log contains tool calls but not detailed hook execution

### Issue: Large Debug Log (>50MB)

**Symptom**: Log file too large to read entirely

**Solution**:
- Use `grep` with specific patterns instead of reading entire file
- Use `tail` to get recent entries
- Use `offset` and `limit` when reading with Read tool

---

## SubAgent Analysis Issues

### Issue: SubAgent Not Recorded

**Symptom**: Expected subagent call not found in logs

**Possible Causes**:
1. SubAgent was never actually called
2. SubAgent type name differs from expected (case-sensitive)
3. Log was truncated

**Diagnosis**:
```bash
# List all unique subagent types
grep "SubagentStart with query:" debug.txt | sed 's/.*query: //' | sort | uniq
```

### Issue: Missing SubAgent Result

**Symptom**: `SubagentStart` found but no `SubagentStop`

**Possible Causes**:
1. SubAgent is still running (background task)
2. SubAgent crashed
3. Session ended before subagent completed

**Diagnosis**:
```bash
# Count starts vs stops
grep -c "SubagentStart" debug.txt
grep -c "SubagentStop" debug.txt
```

---

## Hook Analysis Issues

### Issue: Hook Not Triggered

**Symptom**: Expected hook not found in `Getting matching hook commands` entries

**Possible Causes**:
1. Matcher pattern doesn't match the tool name
2. Hook not registered (skill not loaded)
3. Hook has wrong event type

**Diagnosis**:
```bash
# Check if skill hooks were registered
grep "Registered.*hooks from skill" debug.txt

# Check what hooks are being queried
grep "Getting matching hook commands for" debug.txt | head -20
```

### Issue: Hook Triggered But No Effect

**Symptom**: Hook matched (count > 0) but expected behavior didn't occur

**Possible Causes**:
1. Hook script returned error
2. Hook returned `allow` when should have returned `deny`
3. Prompt hook condition was not met

**Diagnosis**:
```bash
# Check hook execution result
grep -A5 "Matched.*unique hooks" debug.txt | grep -E "permissionDecision|ok"
```

### Issue: Prompt Hook Always Returns False

**Symptom**: `Prompt hook condition was not met` consistently

**Possible Causes**:
1. Prompt is too vague for model to understand
2. Context doesn't contain expected information
3. Model misinterprets the criteria

**Diagnosis**:
```bash
# See the full model response
grep -A20 "Hooks: Model response:" debug.txt
```

---

## Artifact Issues

### Issue: File Not Created

**Symptom**: Expected artifact file not in `written atomically` logs

**Possible Causes**:
1. Write was blocked by PreToolUse hook
2. Path was wrong
3. Write tool was never called

**Diagnosis**:
```bash
# Check if Write was attempted
grep "executePreToolHooks called for tool: Write" debug.txt

# Check permission decision
grep -A10 "executePreToolHooks called for tool: Write" debug.txt | grep "permissionDecision"
```

### Issue: File Exists But Should Be Deleted

**Symptom**: Draft file still exists after session ended

**Possible Causes**:
1. Bash `rm` command was never executed
2. Skill ended before cleanup step
3. Wrong file path in rm command

**Diagnosis**:
```bash
# Check for rm commands
grep "Bash" debug.txt | grep -i "rm"
```

---

## Reviewer-Specific Issues

### Issue: Reviewer Never Returns OKAY

**Symptom**: Multiple REJECT responses, no OKAY

**Possible Causes**:
1. Plan genuinely has issues that weren't fixed
2. Reviewer criteria too strict
3. Plan edits not addressing reviewer feedback

**Diagnosis**:
```bash
# Extract all reviewer responses
grep -B2 -A10 "Hooks: Model response:" debug.txt | grep -E '"ok"|"reason"'
```

### Issue: Reviewer Called But No Hook Result

**Symptom**: `SubagentStart with query: reviewer` found but no `Prompt hook condition` result

**Possible Causes**:
1. Reviewer subagent has no Stop hook configured
2. Hook conversion to SubagentStop failed
3. Reviewer is still running

**Diagnosis**:
```bash
# Check if Stop hook was converted
grep "Converting Stop hook to SubagentStop for agent 'reviewer'" debug.txt
```

---

## Timing Issues

### Issue: Events Out of Order

**Symptom**: Timeline doesn't make sense (e.g., Stop before Start)

**Possible Causes**:
1. Parallel operations (intended behavior)
2. Log entries from different sessions mixed
3. Clock synchronization issues

**Solution**:
- Filter by session ID if multiple sessions in same timeframe
- Look at specific operation sequences, not global order

### Issue: Large Time Gaps

**Symptom**: Long pauses between operations

**Possible Causes**:
1. User interaction (AskUserQuestion waiting)
2. API rate limiting
3. Model thinking time

**Diagnosis**:
```bash
# Find gaps > 30 seconds
awk -F'T|Z' '{print $2}' debug.txt | sort | uniq -c | sort -rn | head
```

---

## Analysis Script Issues

### Issue: Script Returns Empty JSON

**Symptom**: Scripts return `{ "summary": { "total": 0 } }`

**Possible Causes**:
1. Debug log path is wrong
2. Log format changed
3. No matching events in this session

**Solution**:
- Verify debug log path exists and has content
- Manually grep for expected patterns to verify format

### Issue: Script Permission Denied

**Symptom**: `Permission denied` when running scripts

**Solution**:
```bash
chmod +x scripts/*.sh
```

---

## Validation Checklist

When analysis seems wrong, verify:

1. **Correct Session ID**: Double-check the UUID
2. **Files Exist**: Run `find-session-files.sh` first
3. **Skill Was Loaded**: Look for "Registered.*hooks from skill"
4. **Right Timeframe**: Check timestamps match expected session time
5. **Complete Session**: Session ended normally (not interrupted)
