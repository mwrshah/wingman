# Using the python script
The main python scripts are in /files, and of those the one to run is wingman.py, which imports functions from the other scripts.
html_walk.py defines the Zendesk ticket parsing
printing_funk.py defines functions to print to screen/terminal as the program runs

# Using the tool 1-2-3-Paste:

1. Initialize it
2. Click bookmarklet
3. Switch to terminal
4. Press Enter (if it is the first or last prompt) to reload
5. Type 're' or 'restart' and Enter if you want to reload from the 'Clue' input.
6. Enter an instruction
7. Enter a clue to help it shape the PR. 
8. Paste: Wait till the DS is populated and paste (Ctrl/Cmd + v) in the IN on Zendesk.

Note: Applying the "Send to QC _[TEMPO]Work)" macro is still necessary. You will have to apply the macro and Ctrl+A/Cmd+A, and remove. Then paste the DS from Wingman.

## Instruction examples:

- Send to customer.
- cust.
- cst
- saas chg req
- Escalate to SaaS incident
- Elevate to Account manager via SC
- Escalate to account manager via bizops
- Escalate to product vp no escalation
- Send to bu no pr yes escalation
- Summarize this chat (this will not ask you for a clue)
- Summary (this will not ask you for a clue)
- Close chat no pr
- Send to account manager via bizops jira
- Send to bu don't elevate send via sc
- Send to bu by elevating
- Send to the bu
- Send to account manager no escalation yes pr
- Pr update in escalation
- Send to bu on jira without a pr

Note: Instructions can be small or capitalized, doesn't matter. Try short hand, try long hand. It will parse intention from what you saying; for example, if you say "send to", "escalate to" etc. it understands that you want to do an escalation.

Note: If in the rare case you get an error. Try one of the following:

Example1: "send to bu via escalation no pr" will error out with "Wingman doesn't know what to do". What works:
- "send to bu by escalating via jira don't write a pr"
- Even better: "send to bu by escalating via ztps no pr"
- "send to bu via sc with a pr"
- "escalate to acct mgr sc no pr"
- "elevation to bu"

Example2: "acct mgr sc" will error out
What works:
- "send an sc to account manager" (note that no pr cheatcode means it will not populate the sc)
- "esc sc acc mgr no pr"

Example3: "send to saas" will not error out but default to SaaS Incident.
What works:
- "send to saas chg req" or "send to saas inc"

Cheat codes: 

- "no pr" - this will produce a DS without going to openAI. Output is just the DS format with the PR and escalation fields excluded.
- "no esc" - will produce the PR but without going the extra step of producing the escalation. Useful when updating on an old ticket that is already pending with an external team but the customer has to be replied to.
- "force elevation" - anything to suggest you want to "send to the bu directly"
- "force escalation" - anything to suggest you want to "send via escalation" e.g. "send to bu not on jira but on sc"

Note: For cheat codes above you don't need to remember the exact words: 'don't write a pr', 'without pr', 'excluding a pr', will also work the same way. Similarly 'dont escalate', 'no escalate', 'don't escalate', 'without escalation' are all the same.


Clue Examples: 

- I have now added the phone number. To activate ask the user to enter the number and PIN 12345.
- To solve this, change your SMTP settings and try again. See article <link>. Otherwise submit logs.
- The following articles might help: <links>
- I am escalating to our Infra team.
- This is a known issue that our Dev team is working on. We will let you know when there is a fix.
