---
name: email-triage-classifier
display_name: "Email Triage & Classifier"
description: "Classifies, prioritizes, and drafts professional replies for a batch of customer support emails using only the input data."
category: communication
icon: mail-check
skill_type: sandbox
catalog_type: addon
tool_schema:
  name: email_triage_classifier
  description: "Accepts a list of customer email objects and returns structured triage results: category, priority, draft reply, urgency flag, and a one-liner summary for each email."
  parameters:
    type: object
    properties:
      emails:
        type: array
        description: "List of email objects to triage."
        items:
          type: object
          properties:
            sender:
              type: string
              description: "Sender's email address or name."
            subject:
              type: string
              description: "Email subject line."
            body:
              type: string
              description: "Full email body text."
            thread_id:
              type: string
              description: "Thread identifier."
            message_id:
              type: string
              description: "Unique message identifier."
          required: [sender, subject, body, thread_id, message_id]
    required: [emails]
---
# Email Triage & Classifier
Classifies, prioritizes, and drafts professional replies for a batch of customer support emails using only the input data.

## Be Proactive
When the user provides a list of customer support emails and wants them sorted, replied to, or assessed for urgency, call this skill immediately — no external APIs or credentials required.